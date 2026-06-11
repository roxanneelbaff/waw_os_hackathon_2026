from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple


@dataclass
class Candidate:
    address: str
    lat: float
    lon: float
    name: str = ""
    alt_names: List[str] = field(default_factory=list)
    population: int = 0
    admin_level: str = ""
    score: Optional[float] = None

    def to_ranker_dict(self) -> Dict[str, Any]:
        cleaned_alt_names = [str(x).strip() for x in self.alt_names if str(x).strip()]
        addr_tuple: Tuple[str, ...] = tuple(
            part.strip().lower() for part in self.address.split(",") if part.strip()
        )
        return {
            "address": self.address,
            "lat": float(self.lat),
            "lon": float(self.lon),
            "name": self.name or self.address.split(",")[0].strip(),
            "alt_names": cleaned_alt_names,
            "population": int(self.population or 0),
            "admin_level": self.admin_level or "",
            "addr_tuple": addr_tuple,
        }

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> "Candidate":
        alt_names = (
            data.get("alt_names")
            or data.get("alternative_names")
            or data.get("alternatives")
            or data.get("aliases")
            or []
        )
        if isinstance(alt_names, str):
            alt_names = [alt_names]
        return Candidate(
            address=str(data.get("address", "")),
            lat=float(data.get("lat", 0.0)),
            lon=float(data.get("lon", 0.0)),
            name=str(data.get("name", "")),
            alt_names=list(alt_names),
            population=int(data.get("population", 0) or 0),
            admin_level=str(data.get("admin_level", "") or ""),
            score=float(data["score"]) if data.get("score") is not None else None,
        )


@dataclass
class ToponymMention:
    text: str
    start: int
    end: int
    metadata: Dict[str, Any] = field(default_factory=dict)

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> "ToponymMention":
        text = data.get("text", data.get("LOC", ""))
        start = data.get("start", data.get("start_idx"))
        end = data.get("end", data.get("end_idx"))
        if text is None or start is None or end is None:
            raise ValueError("Toponym mention must include text, start, and end.")
        return ToponymMention(text=str(text), start=int(start), end=int(end), metadata=dict(data))
