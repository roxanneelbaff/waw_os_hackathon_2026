"""Convenience import module for UniTopRank APIs."""

try:
    # Package import: from api.geoparsing_api import ...
    from .unitoprank import (
        Candidate,
        CandidateRetriever,
        CandidateRetrieverConfig,
        GeoparsingConfig,
        GeoparsingPipeline,
        RankerConfig,
        ToponymMention,
        rank_toponyms,
    )
except ImportError:
    # Direct module import when `api/` is on PYTHONPATH:
    # from geoparsing_api import ...
    from unitoprank import (
        Candidate,
        CandidateRetriever,
        CandidateRetrieverConfig,
        GeoparsingConfig,
        GeoparsingPipeline,
        RankerConfig,
        ToponymMention,
        rank_toponyms,
    )

__all__ = [
    "Candidate",
    "ToponymMention",
    "RankerConfig",
    "rank_toponyms",
    "CandidateRetriever",
    "CandidateRetrieverConfig",
    "GeoparsingConfig",
    "GeoparsingPipeline",
]
