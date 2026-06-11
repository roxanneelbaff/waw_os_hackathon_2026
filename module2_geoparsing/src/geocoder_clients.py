from __future__ import annotations

import json
from typing import Any

import pandas as pd
import requests

from .config import GEONAMES_BASE_URL, PHOTON_BASE_URL, REQUEST_TIMEOUT


def _safe_get(url: str, params: dict[str, Any], timeout: float) -> dict[str, Any] | list[Any] | None:
    try:
        response = requests.get(url, params=params, timeout=timeout)
        response.raise_for_status()
        return response.json()
    except Exception as exc:
        print(f"Service request failed for {url}: {exc}")
        return None


def _standard_row(query: str, source: str, raw: dict[str, Any]) -> dict[str, Any]:
    return {
        "query": query,
        "source": source,
        "name": raw.get("name") or raw.get("Name") or raw.get("toponymName") or raw.get("display_name") or raw.get("address"),
        "country": raw.get("country") or raw.get("Country") or raw.get("countryName") or raw.get("country_code") or raw.get("countrycode"),
        "state": raw.get("state") or raw.get("State") or raw.get("adminName1"),
        "county": raw.get("county") or raw.get("County") or raw.get("adminName2"),
        "lat": raw.get("lat") or raw.get("latitude") or raw.get("Latitude"),
        "lon": raw.get("lon") or raw.get("lng") or raw.get("longitude") or raw.get("Longitude"),
        "feature_class": raw.get("feature_class") or raw.get("fclass") or raw.get("class") or raw.get("Class"),
        "feature_code": raw.get("feature_code") or raw.get("fcode") or raw.get("type") or raw.get("Code"),
        "population": raw.get("population") or raw.get("Population"),
        "raw": json.dumps(raw, ensure_ascii=False),
    }


def geocode_geonames(query: str, limit: int = 5, timeout: float | None = None) -> pd.DataFrame:
    data = _safe_get(GEONAMES_BASE_URL, {"location": query, "limit": limit}, timeout or REQUEST_TIMEOUT)
    return standardize_geonames_response(query, data).head(limit).reset_index(drop=True)


def geocode_photon(query: str, limit: int = 5, timeout: float | None = None) -> pd.DataFrame:
    data = _safe_get(PHOTON_BASE_URL, {"q": query, "limit": limit}, timeout or REQUEST_TIMEOUT)
    return standardize_photon_response(query, data).head(limit).reset_index(drop=True)


def standardize_geonames_response(query: str, response_json: dict[str, Any] | list[Any] | None) -> pd.DataFrame:
    if response_json is None:
        return pd.DataFrame(columns=_columns())

    if isinstance(response_json, list):
        records = response_json
    else:
        records = (
            response_json.get("geonames")
            or response_json.get("records")
            or response_json.get("results")
            or response_json.get("locations")
            or response_json.get("data")
            or []
        )
    rows = [_standard_row(query, "geonames", item) for item in records if isinstance(item, dict)]
    return pd.DataFrame(rows, columns=_columns())


def standardize_photon_response(query: str, response_json: dict[str, Any] | list[Any] | None) -> pd.DataFrame:
    if response_json is None:
        return pd.DataFrame(columns=_columns())

    features = response_json.get("features", []) if isinstance(response_json, dict) else response_json
    rows = []
    for feature in features:
        if not isinstance(feature, dict):
            continue
        props = feature.get("properties", {}) or {}
        coords = (feature.get("geometry", {}) or {}).get("coordinates", [None, None])
        raw = dict(props)
        raw["lon"] = coords[0] if len(coords) > 0 else None
        raw["lat"] = coords[1] if len(coords) > 1 else None
        rows.append(_standard_row(query, "photon", raw))
    return pd.DataFrame(rows, columns=_columns())


def compare_geocoders(query: str, limit: int = 5) -> pd.DataFrame:
    frames = [geocode_geonames(query, limit=limit), geocode_photon(query, limit=limit)]
    frames = [frame for frame in frames if frame is not None and not frame.empty]
    return pd.concat(frames, ignore_index=True) if frames else pd.DataFrame(columns=_columns())


def _columns() -> list[str]:
    return [
        "query",
        "source",
        "name",
        "country",
        "state",
        "county",
        "lat",
        "lon",
        "feature_class",
        "feature_code",
        "population",
        "raw",
    ]
