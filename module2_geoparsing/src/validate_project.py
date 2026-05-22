from __future__ import annotations

import json
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]

REQUIRED_FOLDERS = [
    "notebooks",
    "src",
    "data",
    "data/sample_texts",
    "data/disaster_tweets",
    "data/disease_news",
    "data/scientific_paper",
    "outputs",
    "outputs/results",
    "outputs/maps",
    "external",
]

REQUIRED_NOTEBOOKS = [
    "00_setup_and_overview.ipynb",
    "01_toponym_recognition.ipynb",
    "02_dlr_geocoding_services.ipynb",
    "03_unitoprank_resolution.ipynb",
    "04_llm_rag_resolution_service.ipynb",
    "05_map_visualization.ipynb",
    "06_application_challenge.ipynb",
]

REQUIRED_HELPERS = [
    "__init__.py",
    "config.py",
    "ner_utils.py",
    "geocoder_clients.py",
    "visualization_utils.py",
    "data_utils.py",
    "validate_project.py",
]


def validate() -> bool:
    ok = True

    for folder in REQUIRED_FOLDERS:
        path = PROJECT_ROOT / folder
        if not path.is_dir():
            print(f"Missing folder: {folder}")
            ok = False

    for notebook in REQUIRED_NOTEBOOKS:
        path = PROJECT_ROOT / "notebooks" / notebook
        if not path.is_file():
            print(f"Missing notebook: {notebook}")
            ok = False
            continue
        try:
            with path.open("r", encoding="utf-8") as handle:
                json.load(handle)
        except Exception as exc:
            print(f"Invalid notebook JSON: {notebook}: {exc}")
            ok = False

    for helper in REQUIRED_HELPERS:
        path = PROJECT_ROOT / "src" / helper
        if not path.is_file():
            print(f"Missing helper: src/{helper}")
            ok = False

    if ok:
        print("Project validation passed.")
    return ok


if __name__ == "__main__":
    raise SystemExit(0 if validate() else 1)

