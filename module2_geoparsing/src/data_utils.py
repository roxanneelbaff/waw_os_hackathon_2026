from __future__ import annotations

from pathlib import Path
from typing import Iterable

import pandas as pd

from .config import DATA_DIR, RESULTS_DIR


SAMPLE_TEXTS = [
    "Paris and Berlin are often mentioned in European news.",
    "Apple opened a new office in California.",
    "Nach dem Hochwasser wurden Schäden in Bayern, Passau und Österreich gemeldet.",
    "The earthquake affected Izmir and nearby villages.",
    "Several hydrology studies focus on the Rhine basin and the Danube region.",
]


def load_sample_texts() -> pd.DataFrame:
    """Load workshop sample texts, creating the CSV if it is missing."""
    path = DATA_DIR / "sample_texts" / "sample_texts.csv"
    if path.exists():
        return pd.read_csv(path)

    df = pd.DataFrame(
        {"text_id": [f"sample_{i+1}" for i in range(len(SAMPLE_TEXTS))], "text": SAMPLE_TEXTS}
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=False)
    return df


def load_text_dataset(dataset_name: str) -> pd.DataFrame:
    """Load a simple prepared dataset from data/<dataset_name>/texts.csv."""
    path = DATA_DIR / dataset_name / "texts.csv"
    if not path.exists():
        print(f"No dataset found at {path}. Returning sample texts instead.")
        return load_sample_texts()
    return pd.read_csv(path)


def save_dataframe(df: pd.DataFrame, path: str | Path) -> Path:
    """Save a DataFrame and create parent folders as needed."""
    out_path = Path(path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(out_path, index=False)
    return out_path


def load_dataframe_if_exists(path: str | Path) -> pd.DataFrame | None:
    """Return a DataFrame if the CSV exists, otherwise None."""
    csv_path = Path(path)
    if csv_path.exists():
        return pd.read_csv(csv_path)
    return None


def save_sample_text_outputs() -> Path:
    """Save the standard sample texts to outputs/results for Notebook 00."""
    return save_dataframe(load_sample_texts(), RESULTS_DIR / "sample_texts.csv")


def texts_to_dataframe(texts: Iterable[str]) -> pd.DataFrame:
    text_list = list(texts)
    return pd.DataFrame({"text_id": [f"user_{i+1}" for i in range(len(text_list))], "text": text_list})

