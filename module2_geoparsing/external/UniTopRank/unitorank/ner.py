import re
from dataclasses import dataclass
from typing import Dict, List, Optional, Set

from .types import ToponymMention


LOCATION_LABELS = {
    "LOC",
    "GPE",
    "LOCATION",
    "FAC",
    "FACILITY",
    "S-LOC",
    "B-LOC",
    "I-LOC",
    "E-LOC",
    "S-FAC",
    "B-FAC",
    "I-FAC",
    "E-FAC",
}


class ToponymExtractor(object):
    def extract(self, text: str, language: Optional[str] = None) -> List[ToponymMention]:
        raise NotImplementedError


def _dedupe_mentions(mentions: List[ToponymMention]) -> List[ToponymMention]:
    seen = set()
    deduped = []
    for mention in sorted(mentions, key=lambda m: (m.start, m.end)):
        key = (mention.start, mention.end, mention.text.lower())
        if key in seen:
            continue
        seen.add(key)
        deduped.append(mention)
    return deduped


@dataclass
class RegexToponymExtractor:
    pattern: str = r"\b[A-Z][\w\-]+(?:\s+[A-Z][\w\-]+)*\b"

    def extract(self, text: str, language: Optional[str] = None) -> List[ToponymMention]:
        mentions = [
            ToponymMention(text=m.group(0), start=m.start(), end=m.end(), metadata={"source": "regex"})
            for m in re.finditer(self.pattern, text)
        ]
        return _dedupe_mentions(mentions)


class StanzaToponymExtractor:
    def __init__(self, default_language: str = "en", download_if_missing: bool = False) -> None:
        try:
            import stanza
        except ImportError as exc:
            raise ImportError("Stanza is not installed. Install with: pip install stanza") from exc

        self._stanza = stanza
        self.default_language = default_language
        self.download_if_missing = download_if_missing
        self._pipelines: Dict[str, object] = {}

    def _get_pipeline(self, language: Optional[str]) -> object:
        lang = language or self.default_language
        if lang in self._pipelines:
            return self._pipelines[lang]
        if self.download_if_missing:
            self._stanza.download(lang, processors="tokenize,ner")
        pipeline = self._stanza.Pipeline(
            lang=lang,
            processors="tokenize,ner",
            tokenize_no_ssplit=True,
            verbose=False,
        )
        self._pipelines[lang] = pipeline
        return pipeline

    def extract(self, text: str, language: Optional[str] = None) -> List[ToponymMention]:
        pipeline = self._get_pipeline(language)
        doc = pipeline(text)
        mentions: List[ToponymMention] = []
        for entity in getattr(doc, "entities", []):
            label = str(getattr(entity, "type", "") or "").upper()
            if label not in LOCATION_LABELS:
                continue
            mentions.append(
                ToponymMention(
                    text=getattr(entity, "text"),
                    start=int(getattr(entity, "start_char")),
                    end=int(getattr(entity, "end_char")),
                    metadata={"source": "stanza", "label": label},
                )
            )
        return _dedupe_mentions(mentions)


class FlairToponymExtractor:
    def __init__(self, model: str = "flair/ner-multi-fast") -> None:
        try:
            from flair.models import SequenceTagger
        except ImportError as exc:
            raise ImportError("Flair is not installed. Install with: pip install flair") from exc
        self._Sentence = None
        self._SequenceTagger = SequenceTagger
        self.tagger = self._SequenceTagger.load(model)

    def extract(self, text: str, language: Optional[str] = None) -> List[ToponymMention]:
        if self._Sentence is None:
            from flair.data import Sentence

            self._Sentence = Sentence

        sentence = self._Sentence(text)
        self.tagger.predict(sentence)
        mentions: List[ToponymMention] = []
        for span in sentence.get_spans("ner"):
            label = span.get_label("ner").value.upper()
            if label not in LOCATION_LABELS:
                continue
            start = int(span.start_position)
            end = int(span.end_position)
            mentions.append(
                ToponymMention(
                    text=span.text,
                    start=start,
                    end=end,
                    metadata={"source": "flair", "label": label},
                )
            )
        return _dedupe_mentions(mentions)
