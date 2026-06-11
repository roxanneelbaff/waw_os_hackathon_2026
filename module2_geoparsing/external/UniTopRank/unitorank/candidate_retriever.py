from dataclasses import dataclass, field
from typing import Any, Dict, Iterable, List, Mapping, Optional, Tuple
from urllib.parse import quote
import re

import requests

from thread_weight_rank_algorithm_3_beam import best_name_similarity1

from .types import Candidate


def _parse_geonames_name(raw_name: str) -> Tuple[str, List[str]]:
    if "(" in raw_name and ")" in raw_name:
        main = raw_name.split("(", 1)[0].strip()
        alt_str = raw_name[raw_name.find("(") + 1 : raw_name.rfind(")")]
        alt_names = [x.strip() for x in alt_str.split(",") if x.strip()]
        return main, alt_names
    return raw_name.strip(), []

def _parse_alt_name_field(value: Any) -> List[str]:
    if value is None:
        return []
    if isinstance(value, list):
        return [str(x).strip() for x in value if str(x).strip()]
    text = str(value).strip()
    if not text:
        return []
    # GeoNames-like fields are commonly comma/semicolon separated.
    sep = ";" if ";" in text else ","
    return [x.strip() for x in text.split(sep) if x.strip()]

def _strip_parentheses_nested(text: str) -> str:
    prev = text
    while True:
        cur = re.sub(r"\([^()]*\)", "", prev)
        if cur == prev:
            return cur
        prev = cur


def _clean_hierarchy(full_hierarchy: str) -> str:
    cleaned = _strip_parentheses_nested((full_hierarchy or "").strip())
    parts = [p.strip() for p in cleaned.split(",") if p.strip()]
    if len(parts) > 1 and parts[0].lower() == parts[1].lower():
        parts = [parts[0]] + parts[2:]
    if len(parts) > 10:
        parts = parts[:10]
    return ", ".join(parts)


def _stable_key(cand: Candidate) -> Tuple[Any, ...]:
    return (
        -(cand.population or 0),
        (cand.admin_level or ""),
        (cand.address or "").lower(),
        (cand.name or "").lower(),
        float(cand.lat),
        float(cand.lon),
    )

def _collect_photon_alt_names(properties: Mapping[str, Any], primary_name: str) -> List[str]:
    alt_names: List[str] = []
    for key in (
        "street",
        "district",
        "suburb",
        "locality",
        "city",
        "county",
        "state",
        "country",
    ):
        value = str(properties.get(key, "") or "").strip()
        if value:
            alt_names.append(value)

    # Photon/OpenStreetMap responses may expose localized names as name:xx.
    for key, value in properties.items():
        if isinstance(key, str) and key.startswith("name:"):
            v = str(value or "").strip()
            if v:
                alt_names.append(v)

    # De-duplicate and remove trivial self-match.
    out: List[str] = []
    seen = set()
    primary = (primary_name or "").strip().lower()
    for name in alt_names:
        norm = name.strip().lower()
        if not norm or norm == primary or norm in seen:
            continue
        seen.add(norm)
        out.append(name.strip())
    return out


@dataclass
class CandidateRetrieverConfig:
    geonames_enabled: bool = True
    photon_enabled: bool = False
    only_photon: bool = False
    bool_merge: bool = False

    geonames_url: str = "http://localhost:8091/location?location="
    photon_url: str = "http://localhost:2322/api/?q="

    geonames_limit: int = 40
    photon_limit: int = 300

    geonames_quality_threshold: float = 0.99
    photon_perfect_match_threshold: float = 1.2
    min_keep_photon: int = 60
    # Keep all candidates by default; same address text can map to records with
    # different feature codes/admin semantics.
    deduplicate_by_address: bool = False
    timeout_seconds: int = 10
    headers: Mapping[str, str] = field(default_factory=dict)


class CandidateRetriever:
    def __init__(
        self,
        config: Optional[CandidateRetrieverConfig] = None,
        geonames_cache: Optional[Dict[str, List[Candidate]]] = None,
        photon_cache: Optional[Dict[str, List[Candidate]]] = None,
    ) -> None:
        self.config = config or CandidateRetrieverConfig()
        self.geonames_cache = geonames_cache or {}
        self.photon_cache = photon_cache or {}
        self._session = requests.Session()
        if self.config.headers:
            self._session.headers.update(dict(self.config.headers))

    def _fetch_geonames(self, name: str) -> List[Candidate]:
        if not self.config.geonames_enabled and not self.config.only_photon:
            return []
        key = name.lower()
        if key in self.geonames_cache:
            return self.geonames_cache[key]
        try:
            url = f"{self.config.geonames_url}{quote(name, safe='')}"
            resp = self._session.get(url, timeout=self.config.timeout_seconds)
            resp.raise_for_status()
            payload = resp.json()
        except Exception:
            self.geonames_cache[key] = []
            return []

        exact_match: List[Candidate] = []
        fuzzy: List[Candidate] = []
        records = payload.get("records", []) if isinstance(payload, dict) else []
        query_lc = name.lower()
        for record in records:
            raw_name = str(record.get("Name", "")).strip()
            cand_name, alt_names = _parse_geonames_name(raw_name)
            alt_names = [x for i, x in enumerate(alt_names) if x and x not in alt_names[:i]]
            address = _clean_hierarchy(str(record.get("FullHierarchy", "")))
            if not address:
                continue
            try:
                lat = float(record.get("Latitude", 0.0))
                lon = float(record.get("Longitude", 0.0))
            except Exception:
                continue
            population = int(record.get("Population", 0) or 0)
            candidate = Candidate(
                address=address,
                lat=lat,
                lon=lon,
                name=cand_name,
                alt_names=alt_names,
                population=population,
                admin_level=str(record.get("Code", "") or ""),
            )
            # Keep behavior close to original `search_geonames7`:
            # "exact" only if the raw `Name` field exactly equals the query.
            if raw_name.lower() == query_lc:
                exact_match.append(candidate)
            else:
                fuzzy.append(candidate)

        # Preserve only one record per address inside exact matches, same as
        # original search logic.
        dedup_exact: List[Candidate] = []
        seen_exact_addr = set()
        for cand in exact_match:
            addr = cand.address.strip().lower()
            if not addr or addr in seen_exact_addr:
                continue
            seen_exact_addr.add(addr)
            dedup_exact.append(cand)

        dedup_exact.sort(key=_stable_key)
        fuzzy.sort(key=_stable_key)

        # Keep all exact matches (even if they exceed geonames_limit),
        # then backfill fuzzy matches up to the configured limit.
        results = list(dedup_exact)
        if len(results) < self.config.geonames_limit:
            results.extend(fuzzy[: self.config.geonames_limit - len(results)])

        self.geonames_cache[key] = results
        return self.geonames_cache[key]

    def _fetch_photon(self, name: str) -> List[Candidate]:
        if not self.config.photon_enabled:
            return []
        key = name.lower()
        if key in self.photon_cache:
            return self.photon_cache[key]
        try:
            url = f"{self.config.photon_url}{quote(name, safe='')}&limit={self.config.photon_limit}"
            resp = self._session.get(url, timeout=self.config.timeout_seconds)
            resp.raise_for_status()
            payload = resp.json()
        except Exception:
            self.photon_cache[key] = []
            return []

        candidates: List[Candidate] = []
        seen = set()
        for feature in payload.get("features", []):
            properties = feature.get("properties", {}) or {}
            geometry = feature.get("geometry", {}) or {}
            coords = geometry.get("coordinates", [0.0, 0.0])
            if len(coords) != 2:
                continue
            lon, lat = float(coords[0]), float(coords[1])
            pname = str(properties.get("name", "") or "").strip()
            city = str(properties.get("city", "") or "").strip()
            county = str(properties.get("county", "") or "").strip()
            state = str(properties.get("state", "") or "").strip()
            country = str(properties.get("country", "") or "").strip()
            if not pname:
                continue
            address_parts = [p for p in [pname, city, county, state, country] if p]
            address = ", ".join(address_parts)
            if not address or address.lower() in seen:
                continue
            seen.add(address.lower())
            candidates.append(
                Candidate(
                    address=address,
                    lat=lat,
                    lon=lon,
                    name=pname,
                    alt_names=_collect_photon_alt_names(properties, pname),
                    population=0,
                    admin_level="none",
                )
            )
        self.photon_cache[key] = candidates
        return candidates

    def get_candidates_for_toponym(self, toponym: str) -> List[Candidate]:
        key = toponym.lower()
        geonames_candidates = [] if self.config.only_photon else self._fetch_geonames(toponym)
        has_good_geonames = any(
            best_name_similarity1(key, c.name, c.alt_names) >= self.config.geonames_quality_threshold
            for c in geonames_candidates
        )
        photon_candidates: List[Candidate] = []
        if self.config.photon_enabled and (
            self.config.bool_merge or not geonames_candidates or not has_good_geonames
        ):
            photon_all = self._fetch_photon(toponym)
            perfect = []
            fuzzy = []
            for cand in photon_all:
                sim = best_name_similarity1(key, cand.name, cand.alt_names)
                if sim > self.config.photon_perfect_match_threshold:
                    perfect.append(cand)
                else:
                    fuzzy.append(cand)
            if len(perfect) < self.config.min_keep_photon:
                perfect.extend(fuzzy[: self.config.min_keep_photon - len(perfect)])
            photon_candidates = perfect

        merged = photon_candidates if self.config.only_photon else geonames_candidates + photon_candidates
        if not self.config.deduplicate_by_address:
            return [c for c in merged if c.address and c.address.strip()]

        unique: Dict[str, Candidate] = {}
        for cand in merged:
            addr = cand.address.strip().lower()
            if addr and addr not in unique:
                unique[addr] = cand
        return list(unique.values())

    def get_candidates_for_toponyms(self, toponyms: Iterable[str]) -> Dict[str, List[Dict[str, Any]]]:
        out: Dict[str, List[Dict[str, Any]]] = {}
        for toponym in toponyms:
            normalized = toponym.strip().lower()
            candidates = [c.to_ranker_dict() for c in self.get_candidates_for_toponym(toponym)]
            out[normalized] = candidates
        return out
