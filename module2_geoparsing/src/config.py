from pathlib import Path
import os

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "data"
OUTPUT_DIR = PROJECT_ROOT / "outputs"
RESULTS_DIR = OUTPUT_DIR / "results"
MAPS_DIR = OUTPUT_DIR / "maps"

GEONAMES_BASE_URL = os.getenv(
    "GEONAMES_BASE_URL",
    "http://dw-mir-postgis.intra.dlr.de:8091/location",
)

PHOTON_BASE_URL = os.getenv(
    "PHOTON_BASE_URL",
    "http://photon.intra.dlr.de:2322/api/",
)

LLM_RAG_BASE_URL = os.getenv("LLM_RAG_BASE_URL", "")
REQUEST_TIMEOUT = float(os.getenv("REQUEST_TIMEOUT", "10"))

