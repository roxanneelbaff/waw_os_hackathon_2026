from dataclasses import dataclass, field
from typing import Any, Dict, Iterable, List, Mapping, MutableMapping, Optional, Set, Tuple, Union

from thread_weight_rank_algorithm_3_beam import rank_candidates

from .types import Candidate, ToponymMention


def _normalize_name(name: str) -> str:
    return name.strip().lower()


def _build_adjacent_pairs(
    mentions: List[ToponymMention],
    text: str,
    max_gap: int,
    require_comma: bool,
    offset_slack: int,
) -> Set[Tuple[str, str]]:
    if not text:
        return set()

    def adjust_offsets(start: int, end: int, mention_text: str) -> Tuple[int, int]:
        gold = mention_text.lower()
        best = (start, end)
        for ds in range(-offset_slack, offset_slack + 1):
            for de in range(-offset_slack, offset_slack + 1):
                s = max(0, start + ds)
                e = min(len(text), end + de)
                if s >= e:
                    continue
                sub = text[s:e].lower()
                if sub == gold:
                    return (s, e)
                if gold in sub or sub in gold:
                    best = (s, e)
        return best

    items = []
    for m in mentions:
        s, e = adjust_offsets(m.start, m.end, m.text)
        items.append((s, e, _normalize_name(m.text)))
    items.sort(key=lambda x: x[0])
    pairs: Set[Tuple[str, str]] = set()
    for idx in range(len(items) - 1):
        left = items[idx]
        right = items[idx + 1]
        if right[0] < left[1]:
            continue
        between = text[left[1] : right[0]]
        if not (1 <= len(between) <= max_gap):
            continue
        if require_comma:
            if "," not in between:
                continue
            if any(ch not in (" ", ",") for ch in between):
                continue
        pairs.add((left[2], right[2]))
    return pairs


def _normalize_candidates(
    candidates_by_toponym: Mapping[str, Iterable[Union[Mapping[str, Any], Candidate]]],
) -> Dict[str, List[Dict[str, Any]]]:
    normalized: Dict[str, List[Dict[str, Any]]] = {}
    for toponym, candidates in candidates_by_toponym.items():
        norm = _normalize_name(toponym)
        for cand in candidates:
            c = cand if isinstance(cand, Candidate) else Candidate.from_dict(dict(cand))
            if not c.address:
                continue
            normalized.setdefault(norm, []).append(c.to_ranker_dict())
    return normalized


@dataclass
class RankerConfig:
    top_n: int = 17
    base_spatial_weight: float = 0.3
    weight_similarity: float = 0.3
    weight_level: float = 0.1
    weight_population: float = 0.2
    distance_threshold_km: float = 300.0
    sp_score_type: int = 2
    max_population: int = 20_000_000
    max_text_len_fallback: int = 50_000
    comma_adjacency_max_gap_chars: int = 4
    adjacency_offset_slack_chars: int = 2
    require_comma_for_adjacency: bool = True
    skip_toponyms: Set[str] = field(default_factory=set)
    debug: bool = False


def rank_toponyms(
    text: str,
    toponyms: Iterable[Union[ToponymMention, Mapping[str, Any]]],
    candidates_by_toponym: Mapping[str, Iterable[Union[Mapping[str, Any], Candidate]]],
    config: Optional[RankerConfig] = None,
) -> Dict[str, Any]:
    cfg = config or RankerConfig()
    mentions: List[ToponymMention] = [
        m if isinstance(m, ToponymMention) else ToponymMention.from_dict(dict(m))
        for m in toponyms
    ]
    mentions.sort(key=lambda x: x.start)
    normalized_candidates = _normalize_candidates(candidates_by_toponym)

    toponym_text_indices: MutableMapping[str, Union[List[int], Set[Tuple[str, str]]]] = {}
    min_char = min((m.start for m in mentions), default=0)
    max_char = max((m.end for m in mentions), default=cfg.max_text_len_fallback)
    for m in mentions:
        toponym_text_indices.setdefault(_normalize_name(m.text), []).append(m.start)
    toponym_text_indices["__adjacent__"] = _build_adjacent_pairs(
        mentions=mentions,
        text=text,
        max_gap=cfg.comma_adjacency_max_gap_chars,
        require_comma=cfg.require_comma_for_adjacency,
        offset_slack=cfg.adjacency_offset_slack_chars,
    )

    num_with_candidates = sum(1 for cands in normalized_candidates.values() if cands)
    spatial_weight = cfg.base_spatial_weight * (1.0 + min(2.0, num_with_candidates / 15.0))

    ranked, _ = rank_candidates(
        normalized_candidates,
        cfg.top_n,
        toponym_text_indices,  # type: ignore[arg-type]
        debug=cfg.debug,
        max_text_len=max(1, max_char - min_char + 1),
        not_process=[_normalize_name(x) for x in cfg.skip_toponyms],
        spatial_weight=spatial_weight,
        weight_similarity=cfg.weight_similarity,
        weight_level=cfg.weight_level,
        weight_population=cfg.weight_population,
        distance_thres=cfg.distance_threshold_km,
        sp_score_type=cfg.sp_score_type,
        max_population=cfg.max_population,
    )

    ranked_candidates: Dict[str, List[Dict[str, Any]]] = {}
    top1_by_toponym: Dict[str, Optional[Dict[str, Any]]] = {}
    for norm_toponym, items in ranked.items():
        formatted = [
            {"address": addr, "lat": lat, "lon": lon, "score": score}
            for addr, lat, lon, score in items
        ]
        ranked_candidates[norm_toponym] = formatted
        top1_by_toponym[norm_toponym] = formatted[0] if formatted else None

    mentions_with_results = []
    for mention in mentions:
        norm = _normalize_name(mention.text)
        mentions_with_results.append(
            {
                "text": mention.text,
                "start": mention.start,
                "end": mention.end,
                "top1_candidate": top1_by_toponym.get(norm),
                "ranked_candidates": ranked_candidates.get(norm, []),
                "metadata": mention.metadata,
            }
        )

    return {
        "text": text,
        "mentions": mentions_with_results,
        "top1_by_toponym": top1_by_toponym,
        "ranked_candidates_by_toponym": ranked_candidates,
        "used_config": cfg.__dict__.copy(),
    }
