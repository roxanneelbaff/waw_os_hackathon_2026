from __future__ import annotations

from functools import lru_cache
from typing import Any

import pandas as pd


LOCATION_LABELS = {
    "LOC",
    "LOCATION",
    "GPE",
    "FAC",
    "FACILITY",
    "NEL",
}


def _empty_message(tool: str, message: str) -> list[dict[str, Any]]:
    print(f"{tool}: {message}")
    return []


def _row(
    mention: str,
    start: int | None,
    end: int | None,
    label: str,
    tool: str,
    source_text_id: str | None = None,
    sentence: str | None = None,
) -> dict[str, Any]:
    return {
        "mention": mention,
        "start": start,
        "end": end,
        "label": label,
        "tool": tool,
        "source_text_id": source_text_id,
        "sentence": sentence,
    }


@lru_cache(maxsize=8)
def _load_spacy_model(model_name: str):
    import spacy

    return spacy.load(model_name)


def extract_locations_spacy(text: str, model_name: str = "en_core_web_sm") -> list[dict[str, Any]]:
    try:
        nlp = _load_spacy_model(model_name)
    except ImportError:
        return _empty_message("spaCy", "package is not installed. Install optional NER requirements to use it.")
    except OSError:
        return _empty_message("spaCy", f"model '{model_name}' is not installed.")

    doc = nlp(text)
    return [
        _row(ent.text, ent.start_char, ent.end_char, ent.label_, "spacy", sentence=ent.sent.text)
        for ent in doc.ents
        if ent.label_ in LOCATION_LABELS
    ]


@lru_cache(maxsize=8)
def _load_stanza_pipeline(lang: str):
    import stanza

    return stanza.Pipeline(lang=lang, processors="tokenize,ner", verbose=False)


def extract_locations_stanza(text: str, lang: str = "en") -> list[dict[str, Any]]:
    try:
        nlp = _load_stanza_pipeline(lang)
    except ImportError:
        return _empty_message("Stanza", "package is not installed. Install optional NER requirements to use it.")
    except Exception as exc:
        return _empty_message("Stanza", f"model for '{lang}' is not available: {exc}")

    doc = nlp(text)
    rows: list[dict[str, Any]] = []
    for sentence in doc.sentences:
        for ent in sentence.ents:
            if ent.type in LOCATION_LABELS:
                rows.append(_row(ent.text, ent.start_char, ent.end_char, ent.type, "stanza", sentence=sentence.text))
    return rows


@lru_cache(maxsize=8)
def _load_flair_tagger(model_name: str):
    from flair.models import SequenceTagger

    return SequenceTagger.load(model_name)


def extract_locations_flair(text: str, model_name: str = "flair/ner-english") -> list[dict[str, Any]]:
    try:
        from flair.data import Sentence
        tagger = _load_flair_tagger(model_name)
    except ImportError:
        return _empty_message("Flair", "package is not installed. Install optional NER requirements to use it.")
    except Exception as exc:
        return _empty_message("Flair", f"model '{model_name}' is not available: {exc}")

    sentence = Sentence(text)
    tagger.predict(sentence)
    rows: list[dict[str, Any]] = []
    for ent in sentence.get_spans("ner"):
        label = ent.get_label("ner").value
        if label in LOCATION_LABELS:
            rows.append(_row(ent.text, ent.start_position, ent.end_position, label, "flair", sentence=text))
    return rows


@lru_cache(maxsize=8)
def _load_transformers_pipeline(model_name: str):
    from transformers import pipeline

    return pipeline("token-classification", model=model_name, aggregation_strategy="simple")


def extract_locations_transformers(
    text: str, model_name: str = "Davlan/xlm-roberta-base-ner-hrl"
) -> list[dict[str, Any]]:
    try:
        ner = _load_transformers_pipeline(model_name)
    except ImportError:
        return _empty_message("Transformers", "package is not installed. Install optional NER requirements to use it.")
    except Exception as exc:
        return _empty_message("Transformers", f"model '{model_name}' is not available: {exc}")

    rows: list[dict[str, Any]] = []
    for ent in ner(text):
        label = ent.get("entity_group") or ent.get("entity") or ""
        if label in LOCATION_LABELS:
            rows.append(
                _row(ent.get("word", ""), ent.get("start"), ent.get("end"), label, "transformers", sentence=text)
            )
    return rows


def normalize_ner_results(results: list[dict[str, Any]], source_text_id: str | None = None) -> pd.DataFrame:
    rows = []
    for item in results:
        item_source_text_id = item.get("source_text_id")
        row = {
            "mention": item.get("mention") or item.get("text") or item.get("word"),
            "start": item.get("start"),
            "end": item.get("end"),
            "label": item.get("label") or item.get("entity_group") or item.get("entity"),
            "tool": item.get("tool", "unknown"),
            "source_text_id": item_source_text_id if item_source_text_id is not None else source_text_id,
            "sentence": item.get("sentence"),
        }
        rows.append(row)
    return pd.DataFrame(rows, columns=["mention", "start", "end", "label", "tool", "source_text_id", "sentence"])


def combine_and_deduplicate_mentions(results: list[pd.DataFrame] | pd.DataFrame) -> pd.DataFrame:
    if isinstance(results, pd.DataFrame):
        df = results.copy()
    else:
        frames = [frame for frame in results if frame is not None and not frame.empty]
        df = pd.concat(frames, ignore_index=True) if frames else pd.DataFrame()

    if df.empty:
        return pd.DataFrame(columns=["mention", "start", "end", "label", "tool", "source_text_id", "sentence"])

    df["mention_key"] = df["mention"].astype(str).str.casefold()
    out = df.drop_duplicates(subset=["source_text_id", "mention_key", "start", "end"]).drop(columns=["mention_key"])
    return out.reset_index(drop=True)
