from dataclasses import dataclass, field
from typing import Any, Dict, Iterable, List, Mapping, Optional, Union

from .candidate_retriever import CandidateRetriever, CandidateRetrieverConfig
from .ner import FlairToponymExtractor, RegexToponymExtractor, StanzaToponymExtractor, ToponymExtractor
from .ranker import RankerConfig, rank_toponyms
from .types import ToponymMention


@dataclass
class GeoparsingConfig:
    ner_backend: str = "regex"
    flair_model: str = "flair/ner-multi-fast"
    ranker: RankerConfig = field(default_factory=RankerConfig)
    candidate_retriever: CandidateRetrieverConfig = field(default_factory=CandidateRetrieverConfig)
    fill_missing_candidates_with_retriever: bool = True


class GeoparsingPipeline:
    def __init__(
        self,
        extractor: ToponymExtractor,
        ranker_config: Optional[RankerConfig] = None,
        retriever: Optional[CandidateRetriever] = None,
        fill_missing_candidates_with_retriever: bool = True,
    ) -> None:
        self.extractor = extractor
        self.ranker_config = ranker_config or RankerConfig()
        self.retriever = retriever
        self.fill_missing_candidates_with_retriever = fill_missing_candidates_with_retriever

    @classmethod
    def from_config(cls, config: GeoparsingConfig) -> "GeoparsingPipeline":
        backend = config.ner_backend.strip().lower()
        if backend == "stanza":
            extractor = StanzaToponymExtractor(default_language="en", download_if_missing=False)
        elif backend == "flair":
            extractor = FlairToponymExtractor(model=config.flair_model)
        elif backend == "regex":
            extractor = RegexToponymExtractor()
        else:
            raise ValueError(f"Unsupported NER backend: {config.ner_backend}")

        retriever = CandidateRetriever(config.candidate_retriever)
        return cls(
            extractor=extractor,
            ranker_config=config.ranker,
            retriever=retriever,
            fill_missing_candidates_with_retriever=config.fill_missing_candidates_with_retriever,
        )

    def parse(
        self,
        text: str,
        language: Optional[str] = None,
        toponyms: Optional[Iterable[Union[ToponymMention, Mapping[str, Any]]]] = None,
        candidates_by_toponym: Optional[Mapping[str, List[Mapping[str, Any]]]] = None,
    ) -> Dict[str, Any]:
        if toponyms is None:
            mentions = self.extractor.extract(text, language=language)
        else:
            mentions = [
                m if isinstance(m, ToponymMention) else ToponymMention.from_dict(dict(m))
                for m in toponyms
            ]

        if candidates_by_toponym is None:
            if not self.retriever:
                raise ValueError(
                    "No candidates were provided and no CandidateRetriever is configured."
                )
            candidate_map = self.retriever.get_candidates_for_toponyms([m.text for m in mentions])
        else:
            candidate_map = {k.strip().lower(): list(v) for k, v in candidates_by_toponym.items()}
            if self.fill_missing_candidates_with_retriever and self.retriever:
                missing = [
                    m.text
                    for m in mentions
                    if m.text.strip().lower() not in candidate_map or not candidate_map[m.text.strip().lower()]
                ]
                if missing:
                    candidate_map.update(self.retriever.get_candidates_for_toponyms(missing))

        result = rank_toponyms(
            text=text,
            toponyms=mentions,
            candidates_by_toponym=candidate_map,
            config=self.ranker_config,
        )
        result["language"] = language
        result["num_mentions"] = len(mentions)
        result["num_unique_toponyms"] = len({m.text.strip().lower() for m in mentions})
        return result
