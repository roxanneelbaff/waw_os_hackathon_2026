"""Small helper API around UniTopRank toponym ranking."""

from typing import Any, Dict, Iterable, List, Mapping, MutableMapping, Optional, Tuple

try:
    # Package import: from api.geo_rank_api import ...
    from .unitoprank.ranker import RankerConfig, rank_toponyms
except ImportError:
    # Direct module import when `api/` is on PYTHONPATH:
    # from geo_rank_api import ...
    from unitoprank.ranker import RankerConfig, rank_toponyms


def _normalize(s: str) -> str:
    return s.strip().lower()


def resolve_toponyms(
    text: str,
    mentions: Iterable[Mapping[str, Any]],
    candidates_by_toponym: Mapping[str, List[Mapping[str, Any]]],
    *,
    loc_key: str = "LOC",
    start_key: str = "start",
    end_key: str = "end",
    ranker_config: Optional[RankerConfig] = None,
    **ranker_kwargs: Any,
) -> Tuple[List[Dict[str, Any]], Dict[str, List[Tuple[str, float, float, float]]]]:
    """
    Resolve toponyms in text using provided candidate sets.

    Args:
      text: Original text string.
      mentions: Mention dicts with at least {loc_key, start_key, end_key}.
      candidates_by_toponym: Dict keyed by normalized toponym.
      loc_key/start_key/end_key: Mention field names.
      ranker_config: Optional RankerConfig instance.
      ranker_kwargs: Optional overrides for RankerConfig fields.

    Returns:
      resolved_mentions:
        One dict per input mention with top-1 fields: lat, lon, address.
      ranked_results:
        Dict keyed by normalized toponym with full ranking as
        [(address, lat, lon, score), ...].
    """
    if ranker_config is not None and ranker_kwargs:
        raise ValueError("Use either ranker_config or ranker_kwargs, not both.")

    cfg = ranker_config or RankerConfig(**ranker_kwargs)

    mentions_list = list(mentions)
    ranker_mentions: List[Dict[str, Any]] = []
    for m in mentions_list:
        if loc_key not in m or start_key not in m or end_key not in m:
            raise ValueError(
                f"Each mention must contain '{loc_key}', '{start_key}', and '{end_key}'."
            )
        ranker_mentions.append(
            {
                "text": str(m[loc_key]),
                "start": int(m[start_key]),
                "end": int(m[end_key]),
                "raw_mention": dict(m),
            }
        )

    normalized_candidates: MutableMapping[str, List[Mapping[str, Any]]] = {}
    for k, v in candidates_by_toponym.items():
        normalized_candidates[_normalize(str(k))] = list(v)

    result = rank_toponyms(
        text=text,
        toponyms=ranker_mentions,
        candidates_by_toponym=normalized_candidates,
        config=cfg,
    )

    # Convert ranking output to expected tuple format.
    ranked_results: Dict[str, List[Tuple[str, float, float, float]]] = {}
    for norm_loc, cand_list in result["ranked_candidates_by_toponym"].items():
        ranked_results[norm_loc] = [
            (
                str(c["address"]),
                float(c["lat"]),
                float(c["lon"]),
                float(c.get("score", 0.0)),
            )
            for c in cand_list
        ]

    # Attach top-1 to each original mention.
    resolved_mentions: List[Dict[str, Any]] = []
    for m in mentions_list:
        out = dict(m)
        norm_loc = _normalize(str(m[loc_key]))
        top1 = result["top1_by_toponym"].get(norm_loc)
        if top1:
            out["lat"] = float(top1["lat"])
            out["lon"] = float(top1["lon"])
            out["address"] = str(top1["address"])
        else:
            out["lat"] = 0.0
            out["lon"] = 0.0
            out["address"] = ""
        resolved_mentions.append(out)

    return resolved_mentions, ranked_results
