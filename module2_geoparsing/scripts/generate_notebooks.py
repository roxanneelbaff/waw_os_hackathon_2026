from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
NOTEBOOK_DIR = ROOT / "notebooks"


def md(source: str) -> dict:
    return {"cell_type": "markdown", "metadata": {}, "source": source.strip().splitlines(True)}


def code(source: str) -> dict:
    return {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": source.strip().splitlines(True),
    }


def write_notebook(name: str, cells: list[dict]) -> None:
    nb = {
        "cells": cells,
        "metadata": {
            "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
            "language_info": {"name": "python", "pygments_lexer": "ipython3"},
        },
        "nbformat": 4,
        "nbformat_minor": 5,
    }
    path = NOTEBOOK_DIR / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(nb, indent=2, ensure_ascii=False), encoding="utf-8")


COMMON_SETUP = """
from pathlib import Path
import sys

PROJECT_ROOT = Path.cwd()
if not (PROJECT_ROOT / "src").exists():
    PROJECT_ROOT = PROJECT_ROOT.parent
sys.path.insert(0, str(PROJECT_ROOT))
"""


def notebook_00() -> list[dict]:
    return [
        md("# Setup and Overview\n\n## Goal\n\nPrepare the core notebook environment and introduce the geoparsing workflow."),
        md("## What you will do\n\n- Confirm that the notebook is running from the project.\n- Install or verify the lightweight core packages.\n- Understand when NER-specific packages are installed.\n- Load sample texts and test service reachability."),
        code("""from pathlib import Path
import importlib.util
import platform
import subprocess
import sys

PROJECT_ROOT = Path.cwd()
if not (PROJECT_ROOT / "src").exists():
    PROJECT_ROOT = PROJECT_ROOT.parent

print("Project root:", PROJECT_ROOT)
print("Python executable:", sys.executable)
print("Python version:", platform.python_version())"""),
        md("## Step 1: Geoparsing workflow\n\nRaw text -> Place-name extraction -> Toponym resolution -> Coordinates -> Map visualization -> Applications"),
        md("## Step 2: Check folders"),
        code("required = ['notebooks', 'src', 'data', 'outputs', 'external']\nfor folder in required:\n    path = PROJECT_ROOT / folder\n    print(f'{folder:10s}', 'OK' if path.exists() else 'missing')"),
        md("## Step 3: Install core packages if needed\n\nNotebook 00 installs only the lightweight core dependencies. NER packages are installed in Notebook 01 because users first need to choose which NER backend they want to run."),
        code("""RUN_CORE_INSTALL = False  # change to True if any core package is missing below

if RUN_CORE_INSTALL:
    subprocess.check_call([
        sys.executable,
        "-m",
        "pip",
        "install",
        "-r",
        str(PROJECT_ROOT / "requirements-core.txt"),
    ])
else:
    print("Core install skipped. Set RUN_CORE_INSTALL = True if a core package is missing.")"""),
        md("## Step 4: Check required core packages\n\nThese packages are needed for the basic workshop path. If one is missing, run the install cell above, then restart the kernel and rerun this notebook."),
        code("core_packages = {'pandas': 'pandas', 'requests': 'requests', 'folium': 'folium', 'python-dotenv': 'dotenv'}\nfor label, import_name in core_packages.items():\n    status = 'available' if importlib.util.find_spec(import_name) else 'missing - run the core install cell above'\n    print(f'{label:16s} {status}')"),
        md("## Step 5: NER installation policy\n\nDo not install NER tools in this setup notebook. Notebook 01 introduces spaCy, Stanza, Flair, and Transformers one by one. Each tool section has its own install cell immediately before its example."),
        code("print('Next step: open Notebook 01. Install each NER tool only in the section where you use it.')"),
        md("## Step 6: Load project helpers after core packages are ready"),
        code("""sys.path.insert(0, str(PROJECT_ROOT))

from src.config import RESULTS_DIR, GEONAMES_BASE_URL, PHOTON_BASE_URL, REQUEST_TIMEOUT
from src.data_utils import load_sample_texts, save_dataframe
import requests"""),
        md("## Step 7: Load sample texts"),
        code("texts = load_sample_texts()\ntexts"),
        md("## Step 8: Save sample texts for later notebooks"),
        code("out = save_dataframe(texts, RESULTS_DIR / 'sample_texts.csv')\nprint('Saved:', out)"),
        md("## Step 9: Check internal service reachability\n\nThese services may require the DLR internal network or VPN. You can still continue with sample outputs."),
        code("def check_service(url, params):\n    try:\n        r = requests.get(url, params=params, timeout=min(REQUEST_TIMEOUT, 3))\n        return r.status_code, r.url\n    except Exception as exc:\n        return 'unreachable', str(exc)\n\nprint('GeoNames:', check_service(GEONAMES_BASE_URL, {'location': 'Berlin'}))\nprint('Photon:', check_service(PHOTON_BASE_URL, {'q': 'Berlin', 'limit': 1}))"),
        md("## Exercise\n\nAdd one text about your own research topic to the sample list and save it to `outputs/results/sample_texts.csv`."),
        code("my_text = 'Add your own text here.'\n# texts.loc[len(texts)] = {'text_id': 'my_text_1', 'text': my_text}\n# save_dataframe(texts, RESULTS_DIR / 'sample_texts.csv')"),
        md("## Common issues\n\n- A DLR service may be unreachable outside the internal network or VPN.\n- Optional NER packages are not required for this setup notebook.\n- If imports from `src` fail, start Jupyter from the project root."),
    ]


def notebook_01() -> list[dict]:
    return [
        md("# Toponym Recognition\n\n## Goal\n\nExtract candidate place names from text with public NER tools."),
        md("## What you will do\n\n- Learn what each NER tool is useful for.\n- Install a tool only when you want to run that section.\n- Run small examples with spaCy, Stanza, Flair, and Transformers.\n- Compare outputs and save mentions to `outputs/results/ner_mentions.csv`."),
        code(COMMON_SETUP + "\nimport subprocess\nimport sys\nimport pandas as pd\nfrom src.config import RESULTS_DIR\nfrom src.data_utils import load_sample_texts, save_dataframe\nfrom src.ner_utils import extract_locations_spacy, extract_locations_stanza, extract_locations_flair, extract_locations_transformers, normalize_ner_results, combine_and_deduplicate_mentions, LOCATION_LABELS"),
        md("## Step 1: NER labels\n\nNER tools use different labels. This project treats `LOC`, `LOCATION`, `GPE`, `FAC`, `FACILITY`, and `NEL` as location-like labels.\n\n`GPE` usually means countries, cities, or states. `LOC` usually means natural or general locations. `FAC` can mean buildings, airports, bridges, or other facilities."),
        md("## Step 2: Load example texts"),
        code("texts = load_sample_texts()\nall_mentions = []\ntexts"),
        md("## Step 3: spaCy\n\nspaCy is the recommended first tool for the workshop: it is lightweight, fast, and easy to explain. Run the install cell once if spaCy or the small models are missing."),
        code("""RUN_SPACY_INSTALL = False

if RUN_SPACY_INSTALL:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "spacy"])
    subprocess.check_call([sys.executable, "-m", "spacy", "download", "en_core_web_sm"])
    subprocess.check_call([sys.executable, "-m", "spacy", "download", "de_core_news_sm"])
else:
    print("Skipped spaCy install. Set RUN_SPACY_INSTALL = True to install spaCy and the small English/German models.")"""),
        code("""rows = []
for _, row in texts.iterrows():
    results = extract_locations_spacy(row["text"], model_name="en_core_web_sm")
    rows.append(normalize_ner_results(results, source_text_id=row["text_id"]))

spacy_mentions = combine_and_deduplicate_mentions(rows)
all_mentions.append(spacy_mentions)
spacy_mentions"""),
        code("""german_text = texts.loc[texts["text_id"] == "sample_3", "text"].iloc[0]
german_spacy_mentions = normalize_ner_results(
    extract_locations_spacy(german_text, model_name="de_core_news_sm"),
    source_text_id="sample_3_de_spacy",
)
german_spacy_mentions"""),
        md("## Step 4: Stanza\n\nStanza is useful when you want a Stanford NLP pipeline and broad language coverage. Its language models are downloaded separately."),
        code("""RUN_STANZA_INSTALL = False

if RUN_STANZA_INSTALL:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "stanza"])
    import stanza
    stanza.download("en")
else:
    print("Skipped Stanza install. Set RUN_STANZA_INSTALL = True to install Stanza and download the English model.")"""),
        code("""stanza_results = extract_locations_stanza("The earthquake affected Izmir and nearby villages.", lang="en")
stanza_mentions = normalize_ner_results(stanza_results, source_text_id="stanza_demo")
all_mentions.append(stanza_mentions)
stanza_mentions"""),
        md("## Step 5: Flair\n\nFlair provides strong sequence labeling models. It is heavier than spaCy, so use it when you want to compare model behavior."),
        code("""RUN_FLAIR_INSTALL = False

if RUN_FLAIR_INSTALL:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "flair"])
else:
    print("Skipped Flair install. Set RUN_FLAIR_INSTALL = True to install Flair.")"""),
        code("""flair_results = extract_locations_flair("Paris and Berlin are often mentioned in European news.")
flair_mentions = normalize_ner_results(flair_results, source_text_id="flair_demo")
all_mentions.append(flair_mentions)
flair_mentions"""),
        md("## Step 6: Hugging Face Transformers\n\nTransformers are useful for multilingual or domain-specific NER models. They can be large, so install them only if this section is relevant to your task."),
        code("""RUN_TRANSFORMERS_INSTALL = False

if RUN_TRANSFORMERS_INSTALL:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "transformers", "torch"])
else:
    print("Skipped Transformers install. Set RUN_TRANSFORMERS_INSTALL = True to install Transformers and Torch.")"""),
        code("""transformer_results = extract_locations_transformers(
    "Nach dem Hochwasser wurden Schäden in Bayern und Passau gemeldet."
)
transformer_mentions = normalize_ner_results(transformer_results, source_text_id="transformer_demo")
all_mentions.append(transformer_mentions)
transformer_mentions"""),
        md("## Step 7: Compare and deduplicate mentions"),
        code("combined = combine_and_deduplicate_mentions(all_mentions)\ncombined"),
        md("## Step 8: Save mentions\n\nNER only extracts candidate place names. It does not resolve them to coordinates."),
        code("out = save_dataframe(combined, RESULTS_DIR / 'ner_mentions.csv')\nprint('Saved:', out)"),
        md("## Exercise\n\nAdd your own text and run it with at least two tools. Compare which place names are found and which labels they receive."),
        code("""my_text = "I travelled from Munich to Zurich and then to Vienna."
my_spacy = normalize_ner_results(extract_locations_spacy(my_text), source_text_id="my_text_spacy")
my_stanza = normalize_ner_results(extract_locations_stanza(my_text), source_text_id="my_text_stanza")
combine_and_deduplicate_mentions([my_spacy, my_stanza])"""),
        md("## Common issues\n\n- If a package is missing, run the install cell in that tool's section.\n- If spaCy is installed but the model is missing, rerun the spaCy install cell.\n- Stanza, Flair, and Transformers may download larger models on first use.\n- Some `FAC` entities are useful locations; others are not, depending on the application."),
    ]


def notebook_02() -> list[dict]:
    return [
        md("# DLR Geocoding Services\n\n## Goal\n\nRetrieve candidate locations from DLR GeoNames and Photon services."),
        md("## What you will do\n\n- Build service URLs.\n- Call services through Python.\n- Compare candidate tables.\n- Save candidates to `outputs/results/geocoder_candidates.csv`."),
        code(COMMON_SETUP + "\nimport pandas as pd\nfrom src.config import GEONAMES_BASE_URL, PHOTON_BASE_URL, RESULTS_DIR\nfrom src.data_utils import save_dataframe\nfrom src.geocoder_clients import geocode_geonames, geocode_photon, compare_geocoders"),
        md("## Step 1: Browser URL examples"),
        code("print('GeoNames:', f'{GEONAMES_BASE_URL}?location=Berlin')\nprint('Photon:', f'{PHOTON_BASE_URL}?q=Berlin&limit=5')"),
        md("## Step 2: Query examples"),
        code("queries = ['Berlin', 'Paris', 'Cambridge', 'Springfield', 'Izmir', 'Bayern', 'Rhine', 'Danube']\nqueries"),
        md("## Step 3: Call GeoNames defensively"),
        code("geonames_berlin = geocode_geonames('Berlin', limit=5)\ngeonames_berlin"),
        md("## Step 4: Call Photon defensively"),
        code("photon_berlin = geocode_photon('Berlin', limit=5)\nphoton_berlin"),
        md("## Step 5: Compare candidates\n\nDifferent geocoders may return different JSON structures and ranking orders."),
        code("frames = []\nfor query in queries:\n    frames.append(compare_geocoders(query, limit=5))\ncandidates = pd.concat([f for f in frames if not f.empty], ignore_index=True) if any(not f.empty for f in frames) else pd.DataFrame()"),
        md("## Step 6: Use built-in candidates if services are unavailable"),
        code("if candidates.empty:\n    candidates = pd.DataFrame([\n        {'query': 'Berlin', 'source': 'mock', 'name': 'Berlin', 'country': 'Germany', 'state': 'Berlin', 'county': '', 'lat': 52.52, 'lon': 13.405, 'feature_class': 'P', 'feature_code': 'PPLC', 'population': 3769000, 'raw': '{}'},\n        {'query': 'Paris', 'source': 'mock', 'name': 'Paris', 'country': 'France', 'state': 'Ile-de-France', 'county': '', 'lat': 48.8566, 'lon': 2.3522, 'feature_class': 'P', 'feature_code': 'PPLC', 'population': 2140526, 'raw': '{}'},\n    ])\ncandidates.head(10)"),
        md("## Step 7: Save candidate results\n\nThese candidates are not final toponym resolution yet."),
        code("out = save_dataframe(candidates, RESULTS_DIR / 'geocoder_candidates.csv')\nprint('Saved:', out)"),
        md("## Exercise\n\nTry an ambiguous place name such as `Springfield`, `Cambridge`, or a local place from your own data."),
        code("exercise_query = 'Cambridge'\ncompare_geocoders(exercise_query, limit=5)"),
        md("## Common issues\n\n- Internal endpoints may require DLR network or VPN.\n- Raw JSON is preserved for debugging.\n- Missing fields are expected; parsers should not assume every service returns the same schema."),
    ]


def notebook_03() -> list[dict]:
    return [
        md("# UniTopRank Resolution\n\n## Goal\n\nUse UniTopRank to rank candidate locations for place names extracted from raw text."),
        md("## What you will do\n\n- Understand the principle of UniTopRank.\n- Download and install the official repository.\n- Reuse any NER tool from Notebook 01: spaCy, Stanza, Flair, or Transformers.\n- Choose GeoNames only or UniTopRank's GeoNames+Photon fallback behavior for candidates.\n- Rank candidates with UniTopRank.\n- Try your own texts and discuss where the method is strong or weak."),
        code(COMMON_SETUP + "\nimport importlib.util\nimport subprocess\nimport sys\nimport pandas as pd\nfrom pathlib import Path\nfrom src.config import RESULTS_DIR, GEONAMES_BASE_URL, PHOTON_BASE_URL, REQUEST_TIMEOUT\nfrom src.data_utils import save_dataframe\nfrom src.ner_utils import extract_locations_spacy, extract_locations_stanza, extract_locations_flair, extract_locations_transformers, normalize_ner_results, combine_and_deduplicate_mentions"),
        md("## Step 1: Method idea\n\nUniTopRank is a fast, CPU-friendly, multilingual toponym resolution method. It is rule-based and interpretable: it ranks candidate places using signals such as name similarity, administrative importance, population, and spatial coherence between places mentioned in the same document.\n\nThis makes it useful when you need a strong practical baseline, fast inference, multilingual behavior, or deployment without GPU-heavy LLMs. It is not magic: it still depends on good NER and good candidate retrieval, and very ambiguous texts may need richer context."),
        md("## Step 2: Download and install UniTopRank\n\nThe official repository is `https://gitlab.com/dlr-dw/UniTopRank`. Run the cell only when UniTopRank is not already installed. After installation, restart the notebook kernel if imports still fail."),
        code("""RUN_UNITOPRANK_INSTALL = False

unitoprank_dir = PROJECT_ROOT / "external" / "UniTopRank"

if RUN_UNITOPRANK_INSTALL:
    (PROJECT_ROOT / "external").mkdir(exist_ok=True)
    if not unitoprank_dir.exists():
        subprocess.check_call([
            "git",
            "clone",
            "https://gitlab.com/dlr-dw/UniTopRank.git",
            str(unitoprank_dir),
        ])
    requirement_candidates = [
        unitoprank_dir / "requirements.txt",
        unitoprank_dir / "api" / "requirements.txt",
    ]
    requirements_file = next((path for path in requirement_candidates if path.exists()), None)
    if requirements_file is None:
        raise FileNotFoundError(
            "Could not find UniTopRank requirements.txt. Checked: "
            + ", ".join(str(path) for path in requirement_candidates)
        )
    print("Installing UniTopRank requirements from:", requirements_file)
    subprocess.check_call([
        sys.executable,
        "-m",
        "pip",
        "install",
        "-r",
        str(requirements_file),
    ])
else:
    print("Skipped UniTopRank install. Set RUN_UNITOPRANK_INSTALL = True if needed.")"""),
        md("## Step 3: Make the UniTopRank API importable"),
        code("""possible_api_dirs = [
    PROJECT_ROOT / "external" / "UniTopRank",
    PROJECT_ROOT / "external" / "UniTopRank" / "api",
    PROJECT_ROOT / "UniTopRank",
    PROJECT_ROOT / "UniTopRank" / "api",
    PROJECT_ROOT / "third_party" / "UniTopRank",
    PROJECT_ROOT / "third_party" / "UniTopRank" / "api",
]

for path in possible_api_dirs:
    if path.exists() and str(path) not in sys.path:
        sys.path.insert(0, str(path))

def add_unitoprank_alias_if_needed():
    # Some repository snapshots contain package folder `unitorank`,
    # while geo_rank_api.py imports `unitoprank`. This alias is only for
    # the current notebook session; it does not edit the external repo.
    if importlib.util.find_spec("unitoprank") is not None:
        return
    if importlib.util.find_spec("unitorank") is None:
        return
    import importlib as importlib_module
    import unitorank
    sys.modules.setdefault("unitoprank", unitorank)
    for name in ["types", "ranker", "candidate_retriever", "ner", "pipeline"]:
        try:
            module = importlib_module.import_module(f"unitorank.{name}")
            sys.modules.setdefault(f"unitoprank.{name}", module)
        except Exception:
            pass

add_unitoprank_alias_if_needed()

try:
    from geo_rank_api import resolve_toponyms
    from geoparsing_api import CandidateRetriever, CandidateRetrieverConfig
    unitoprank_available = True
    unitoprank_import_error = None
except Exception as exc:
    unitoprank_available = False
    unitoprank_import_error = exc

print("geo_rank_api available:", unitoprank_available)"""),
        md("## Step 4: Extract toponyms from raw text\n\nUse any NER tool introduced in Notebook 01. The default is spaCy because it is lightweight. If a tool or model is missing, go back to Notebook 01 and run that tool's install cell."),
        code("""text = "The flood affected Passau and nearby communities along the Danube in Bavaria."
NER_TOOL = "spacy"  # options: "spacy", "stanza", "flair", "transformers"

def extract_toponyms_with_selected_ner(text, ner_tool="spacy", source_text_id="unitoprank_demo"):
    if ner_tool == "spacy":
        results = extract_locations_spacy(text, model_name="en_core_web_sm")
    elif ner_tool == "stanza":
        results = extract_locations_stanza(text, lang="en")
    elif ner_tool == "flair":
        results = extract_locations_flair(text)
    elif ner_tool == "transformers":
        results = extract_locations_transformers(text)
    else:
        raise ValueError("NER_TOOL must be one of: spacy, stanza, flair, transformers")
    return normalize_ner_results(results, source_text_id=source_text_id)

ner_rows = extract_toponyms_with_selected_ner(text, NER_TOOL)
ner_rows"""),
        md("## Step 5: Convert NER output to UniTopRank mentions"),
        code("""def mentions_from_ner(df):
    mentions = []
    for _, row in df.dropna(subset=["mention"]).iterrows():
        if pd.isna(row.get("start")) or pd.isna(row.get("end")):
            continue
        mentions.append({
            "LOC": str(row["mention"]),
            "start": int(row["start"]),
            "end": int(row["end"]),
        })
    return mentions

mentions = mentions_from_ner(ner_rows)
mentions"""),
        md("## Step 6: Choose candidate source\n\nUniTopRank ranks candidates; it does not create coordinates from nothing. The official repository uses `CandidateRetriever` with `CandidateRetrieverConfig` before calling `resolve_toponyms(...)`.\n\nUse one of two modes:\n\n- `geonames`: GeoNames only.\n- `geonames_photon`: UniTopRank's default two-geocoder strategy. GeoNames is tried first. Photon is used only when GeoNames returns no candidates or no high-quality name match. This follows `photon_enabled=True` with `bool_merge=False` in the UniTopRank repository.\n\nThere is also a `bool_merge=True` option in the repository that always merges Photon with GeoNames, but this notebook keeps the default UniTopRank behavior."),
        code("""CANDIDATE_SOURCE = "geonames"  # options: "geonames", "geonames_photon"

def unitoprank_geonames_prefix(base_url):
    base = str(base_url).strip()
    if "location=" in base:
        return base
    separator = "&" if "?" in base else "?"
    return f"{base}{separator}location="

def unitoprank_photon_prefix(base_url):
    base = str(base_url).strip()
    if "q=" in base:
        return base
    separator = "&" if "?" in base else "?"
    return f"{base}{separator}q="

use_photon = CANDIDATE_SOURCE == "geonames_photon"
force_photon_merge = False  # keep UniTopRank default behavior

if not unitoprank_available:
    raise ImportError(
        "UniTopRank is not available. Run the install cell in Step 2, then rerun Step 3. "
        f"Import error was: {unitoprank_import_error!r}"
    )

def make_candidate_retriever(candidate_source):
    use_photon = candidate_source == "geonames_photon"
    if candidate_source not in ("geonames", "geonames_photon"):
        raise ValueError("candidate_source must be 'geonames' or 'geonames_photon'")
    return CandidateRetriever(
        CandidateRetrieverConfig(
            geonames_enabled=True,
            photon_enabled=use_photon,
            bool_merge=False,  # UniTopRank default: Photon is fallback/supplement, not always merged.
            geonames_url=unitoprank_geonames_prefix(GEONAMES_BASE_URL),
            photon_url=unitoprank_photon_prefix(PHOTON_BASE_URL),
            geonames_limit=40,
            photon_limit=300,
            timeout_seconds=int(REQUEST_TIMEOUT),
            deduplicate_by_address=False,
        )
    )

retriever = make_candidate_retriever(CANDIDATE_SOURCE)

print("Candidate source:", CANDIDATE_SOURCE)
print("Photon enabled:", retriever.config.photon_enabled)
print("Force Photon merge:", retriever.config.bool_merge)
print("GeoNames URL prefix:", retriever.config.geonames_url)
print("Photon URL prefix:", retriever.config.photon_url if use_photon else "(disabled)")"""),
        md("## Step 7: Retrieve candidates with UniTopRank's retriever"),
        code("""OFFLINE_CLASSROOM_CANDIDATES = {
    "passau": [
        {"address": "Passau, Bavaria, Germany", "lat": 48.5667, "lon": 13.4319, "name": "Passau", "alt_names": [], "population": 52803, "admin_level": "PPLA3"},
    ],
    "danube": [
        {"address": "Danube", "lat": 45.22, "lon": 29.73, "name": "Danube", "alt_names": [], "population": 0, "admin_level": "STM"},
    ],
    "bavaria": [
        {"address": "Bavaria, Germany", "lat": 48.7904, "lon": 11.4979, "name": "Bavaria", "alt_names": ["Bayern"], "population": 13076721, "admin_level": "ADM1"},
    ],
    "paris": [
        {"address": "Paris, Ile-de-France, France", "lat": 48.8566, "lon": 2.3522, "name": "Paris", "alt_names": [], "population": 2140526, "admin_level": "PPLC"},
        {"address": "Paris, Texas, United States", "lat": 33.6609, "lon": -95.5555, "name": "Paris", "alt_names": [], "population": 24699, "admin_level": "PPL"},
    ],
    "texas": [
        {"address": "Texas, United States", "lat": 31.0, "lon": -100.0, "name": "Texas", "alt_names": [], "population": 29145505, "admin_level": "ADM1"},
    ],
    "berlin": [
        {"address": "Berlin, Germany", "lat": 52.52, "lon": 13.405, "name": "Berlin", "alt_names": [], "population": 3769000, "admin_level": "PPLC"},
    ],
}

def retrieve_candidates_for_mentions(mentions, retriever, use_offline_if_empty=True):
    names = [m["LOC"] for m in mentions]
    candidates_by_toponym = retriever.get_candidates_for_toponyms(names)
    has_any = any(bool(v) for v in candidates_by_toponym.values())
    if not has_any and use_offline_if_empty:
        print("GeoNames/Photon returned no candidates. Using a tiny offline classroom candidate table.")
        candidates_by_toponym = {
            name.casefold(): OFFLINE_CLASSROOM_CANDIDATES.get(name.casefold(), [])
            for name in names
        }
    return candidates_by_toponym

def preview_candidates(candidates_by_toponym):
    rows = []
    for query, candidates in candidates_by_toponym.items():
        for rank, cand in enumerate(candidates, start=1):
            rows.append({
                "query": query,
                "rank": rank,
                "name": cand.get("name"),
                "address": cand.get("address"),
                "lat": cand.get("lat"),
                "lon": cand.get("lon"),
                "population": cand.get("population"),
                "admin_level": cand.get("admin_level"),
            })
    return pd.DataFrame(rows)

candidates_by_toponym = retrieve_candidates_for_mentions(mentions, retriever)
preview_candidates(candidates_by_toponym).head(30)"""),
        md("## Step 8: Rank with UniTopRank\n\nThis is the core method call. If UniTopRank is not installed yet, install it in Step 2 and rerun from Step 3."),
        code("""if not unitoprank_available:
    raise ImportError(
        "UniTopRank is not available. Run the install cell in Step 2, then rerun Step 3. "
        f"Import error was: {unitoprank_import_error!r}"
    )

resolved_mentions, ranked_results = resolve_toponyms(
    text=text,
    mentions=mentions,
    candidates_by_toponym=candidates_by_toponym,
    top_n=10,
)

resolved_mentions"""),
        md("## Step 9: Save the selected locations"),
        code("""rows = []
for item in resolved_mentions:
    rows.append({
        "mention": item.get("LOC") or item.get("text") or item.get("mention"),
        "selected_name": item.get("name") or item.get("address"),
        "country": item.get("country"),
        "lat": item.get("lat"),
        "lon": item.get("lon"),
        "score": item.get("score"),
        "method": f"unitoprank_{CANDIDATE_SOURCE}",
    })

results = pd.DataFrame(rows)
out = save_dataframe(results, RESULTS_DIR / "unitoprank_results.csv")
print("Saved:", out)
results"""),
        md("## Step 10: Play with your own text\n\nTry a short text with ambiguous places. Good examples: `Paris` in France vs Texas, `Cambridge` in the UK vs US, or `Springfield` in the US. Choose whether to use GeoNames only or UniTopRank's GeoNames+Photon fallback behavior, then discuss whether the ranking used context well."),
        code("""my_text = "I visited Paris during a road trip through Texas and later flew to Berlin."
MY_NER_TOOL = "spacy"  # options: "spacy", "stanza", "flair", "transformers"
MY_CANDIDATE_SOURCE = "geonames_photon"  # options: "geonames", "geonames_photon"

my_ner = extract_toponyms_with_selected_ner(
    my_text,
    ner_tool=MY_NER_TOOL,
    source_text_id="my_unitoprank_text",
)
my_mentions = mentions_from_ner(my_ner)

my_retriever = make_candidate_retriever(MY_CANDIDATE_SOURCE)
my_candidates_by_toponym = retrieve_candidates_for_mentions(my_mentions, my_retriever)

display(preview_candidates(my_candidates_by_toponym).head(30))

my_resolved, my_ranked = resolve_toponyms(
    text=my_text,
    mentions=my_mentions,
    candidates_by_toponym=my_candidates_by_toponym,
    top_n=10,
)
my_resolved"""),
        md("## Discussion\n\nUniTopRank is strong when candidate lists are reasonable and the document has useful geographic context. It is often attractive for multilingual, CPU-only, large-scale, or near-real-time workflows.\n\nIt can struggle when NER misses a place, candidate retrieval returns poor candidates, the text is very short, or the correct place requires external world knowledge not present in the text."),
        md("## Reference\n\n- UniTopRank repository: https://gitlab.com/dlr-dw/UniTopRank\n- Hu, X., Sun, Y., Hecking, T., Kersten, J., & Klan, F. (2026). *UniTopRank: a scalable and language-independent method for toponym resolution*. International Journal of Geographical Information Science. https://doi.org/10.1080/13658816.2026.2645831"),
    ]


def notebook_04() -> list[dict]:
    return [
        md("# LLM-RAG Resolution Service\n\n## Goal\n\nCall the LLM- and RAG-based toponym resolution service for difficult toponym resolution cases."),
        md("## What you will do\n\n- Understand the principle of the LLM-RAG method.\n- Configure the service endpoint.\n- Extract toponyms with one of the NER tools from Notebook 01.\n- Choose GeoNames only or GeoNames plus Photon candidates.\n- Call `/resolve` and inspect the returned locations.\n- Try your own challenging texts and save results."),
        code(COMMON_SETUP + "\nimport pandas as pd\nimport requests\nfrom src.config import LLM_RAG_BASE_URL, REQUEST_TIMEOUT, RESULTS_DIR\nfrom src.data_utils import load_dataframe_if_exists, save_dataframe\nfrom src.ner_utils import extract_locations_spacy, extract_locations_stanza, extract_locations_flair, extract_locations_transformers, normalize_ner_results"),
        md("## Step 1: Method idea\n\nThis service uses a fine-tuned lightweight LLM together with retrieval-augmented generation. For each text, the service receives already detected toponyms and uses the full context plus candidate locations from geocoders to infer the intended place.\n\nCompared with UniTopRank, this method can be stronger on difficult and challenging cases because the LLM can use richer textual semantics and world knowledge. Typical examples include short ambiguous names, fine-grained places, and cases where local context is needed. The tradeoff is that it needs a running model service and is heavier than the CPU-friendly UniTopRank method."),
        md("## Step 2: Configure the service endpoint\n\nSet `SERVICE_BASE_URL` to the running LLM-RAG service. The client calls `POST {SERVICE_BASE_URL}/resolve`."),
        code("""SERVICE_BASE_URL = LLM_RAG_BASE_URL  # example: "http://geoparser.intra.dlr.de:8282"

print("SERVICE_BASE_URL:", SERVICE_BASE_URL or "(not set yet)")"""),
        md("## Step 3: Extract toponyms from raw text\n\nUse any NER tool introduced in Notebook 01. The default is spaCy because it is lightweight. If a tool or model is missing, go back to Notebook 01 and run that tool's install cell."),
        code("""text = "I visited Paris during a road trip through Texas and later flew to Berlin."
NER_TOOL = "spacy"  # options: "spacy", "stanza", "flair", "transformers"

def extract_toponyms_with_selected_ner(text, ner_tool="spacy", source_text_id="llm_rag_demo"):
    if ner_tool == "spacy":
        results = extract_locations_spacy(text, model_name="en_core_web_sm")
    elif ner_tool == "stanza":
        results = extract_locations_stanza(text, lang="en")
    elif ner_tool == "flair":
        results = extract_locations_flair(text)
    elif ner_tool == "transformers":
        results = extract_locations_transformers(text)
    else:
        raise ValueError("NER_TOOL must be one of: spacy, stanza, flair, transformers")
    return normalize_ner_results(results, source_text_id=source_text_id)

def mentions_for_service(df, full_text):
    rows = []
    for _, row in df.dropna(subset=["mention"]).iterrows():
        if pd.isna(row.get("start")) or pd.isna(row.get("end")):
            continue
        rows.append({
            "text_id": row.get("source_text_id"),
            "full_text": full_text,
            "mention": str(row["mention"]),
            "start": int(row["start"]),
            "end": int(row["end"]),
        })
    return pd.DataFrame(rows)

ner_rows = extract_toponyms_with_selected_ner(text, NER_TOOL)
mentions = mentions_for_service(ner_rows, text)
mentions"""),
        md("## Step 4: Choose geocoder support\n\n`use_geonames=True` is required. `use_photon=True` is optional and is useful when Photon/OSM may contain candidates that GeoNames misses, especially fine-grained places."),
        code("""USE_GEONAMES = True  # required
USE_PHOTON = False    # set True to also use Photon candidates

print("use_geonames:", USE_GEONAMES)
print("use_photon:", USE_PHOTON)"""),
        md("## Step 5: Define the client\n\nThe client sends the text, extracted toponyms, and geocoder switches to the `/resolve` endpoint."),
        code("""def resolve_with_llm_rag(full_text, mention_df, base_url, use_geonames=True, use_photon=False):
    if not base_url:
        print("SERVICE_BASE_URL is not configured. Returning empty result.")
        return []
    if not use_geonames:
        raise ValueError("use_geonames must be True for this service setup.")

    payload = {
        "text": full_text,
        "toponyms": [
            {"text": row["mention"], "start": int(row["start"]), "end": int(row["end"])}
            for _, row in mention_df.iterrows()
        ],
        "use_geonames": True,
        "use_photon": bool(use_photon),
    }

    try:
        response = requests.post(
            f"{base_url.rstrip('/')}/resolve",
            json=payload,
            timeout=max(REQUEST_TIMEOUT, 60),
        )
        response.raise_for_status()
        return response.json().get("results", [])
    except Exception as exc:
        print(f"LLM-RAG service call failed: {exc}")
        return []"""),
        md("## Step 6: Call the service"),
        code("""raw_results = resolve_with_llm_rag(
    full_text=text,
    mention_df=mentions,
    base_url=SERVICE_BASE_URL,
    use_geonames=USE_GEONAMES,
    use_photon=USE_PHOTON,
)

if not raw_results:
    raw_results = [
        {"text": "Paris", "address": "Paris, Texas, United States", "lat": 33.6609, "lon": -95.5555, "score": None},
        {"text": "Texas", "address": "Texas, United States", "lat": 31.0, "lon": -100.0, "score": None},
        {"text": "Berlin", "address": "Berlin, Germany", "lat": 52.52, "lon": 13.405, "score": None},
    ]

raw_results"""),
        md("## Step 7: Normalize and save results\n\nOnly use fields actually returned by the service. If confidence or explanation are not returned, leave them empty."),
        code("""def normalize_llm_rag_results(raw_results, service_base_url, use_photon):
    rows = []
    for item in raw_results:
        rows.append({
            "mention": item.get("text") or item.get("mention"),
            "selected_name": item.get("address") or item.get("full_name"),
            "country": item.get("country"),
            "lat": item.get("lat"),
            "lon": item.get("lon"),
            "confidence": item.get("confidence"),
            "explanation": item.get("explanation"),
            "method": "llm_rag_geonames_photon" if use_photon else "llm_rag_geonames",
            "service_base_url": service_base_url,
        })
    return pd.DataFrame(rows)

results = normalize_llm_rag_results(raw_results, SERVICE_BASE_URL, USE_PHOTON)
out = save_dataframe(results, RESULTS_DIR / "llm_rag_results.csv")
print("Saved:", out)
results"""),
        md("## Step 8: Play with your own text\n\nTry a difficult case where UniTopRank may struggle: repeated names, fine-grained places, or place names that require context. Choose the NER tool, service endpoint, and whether Photon candidates should be used."),
        code("""my_text = "The report mentions Victoria Park near London, Ontario, not London in the UK."
MY_NER_TOOL = "spacy"  # options: "spacy", "stanza", "flair", "transformers"
MY_SERVICE_BASE_URL = SERVICE_BASE_URL
MY_USE_PHOTON = True

my_ner_rows = extract_toponyms_with_selected_ner(
    my_text,
    ner_tool=MY_NER_TOOL,
    source_text_id="my_llm_rag_text",
)
my_mentions = mentions_for_service(my_ner_rows, my_text)

display(my_mentions)

my_raw_results = resolve_with_llm_rag(
    full_text=my_text,
    mention_df=my_mentions,
    base_url=MY_SERVICE_BASE_URL,
    use_geonames=True,
    use_photon=MY_USE_PHOTON,
)

normalize_llm_rag_results(my_raw_results, MY_SERVICE_BASE_URL, MY_USE_PHOTON)"""),
        md("## Discussion\n\nThis service is designed for cases where simple rule-based ranking may not be enough. UniTopRank is fast and interpretable, but it relies on candidate quality and compact ranking signals. The LLM-RAG service can use richer textual context and retrieved geocoder candidates, so it can be stronger on challenging ambiguity. It is also heavier operationally because it requires a running LLM inference service."),
        md("## References\n\n- Hu, X., Kersten, J., Klan, F., & Farzana, S. M. (2024). *Toponym resolution leveraging lightweight and open-source large language models and geo-knowledge*. International Journal of Geographical Information Science. https://doi.org/10.1080/13658816.2024.2405182\n- Hu, X., Kersten, J., & Klan, F. (2025). *Scalable Toponym Resolution with LLMs: Accuracy and Speed Optimizations*. GeoExT 2025. https://elib.dlr.de/221349/1/paper6.pdf"),
        md("## Common issues\n\n- `SERVICE_BASE_URL` is empty or points to a service that is not running.\n- The service may require the DLR internal network or VPN.\n- If the selected NER tool is missing, install it in Notebook 01 and rerun the extraction cell here.\n- `use_geonames` must stay `True`; `use_photon` is the optional switch."),
    ]


def notebook_05() -> list[dict]:
    return [
        md("# Map Visualization\n\n## Goal\n\nVisualize resolved locations on an interactive Folium map."),
        md("## What you will do\n\n- Load resolved outputs if available.\n- Validate coordinates.\n- Create an interactive map.\n- Save it to `outputs/maps/sample_geoparsing_map.html`."),
        code(COMMON_SETUP + "\nimport pandas as pd\nfrom src.config import RESULTS_DIR, MAPS_DIR\nfrom src.data_utils import load_dataframe_if_exists\nfrom src.visualization_utils import validate_coordinates, create_location_map, save_map"),
        md("## Step 1: Load available result files"),
        code("candidate_files = [\n    RESULTS_DIR / 'unitoprank_results.csv',\n    RESULTS_DIR / 'llm_rag_results.csv',\n    RESULTS_DIR / 'geocoder_candidates.csv',\n]\ndf = None\nfor path in candidate_files:\n    df = load_dataframe_if_exists(path)\n    if df is not None and not df.empty:\n        print('Loaded:', path)\n        break\nif df is None or df.empty:\n    df = pd.DataFrame([\n        {'mention': 'Paris', 'selected_name': 'Paris', 'country': 'France', 'lat': 48.8566, 'lon': 2.3522, 'method': 'built_in_example'},\n        {'mention': 'Berlin', 'selected_name': 'Berlin', 'country': 'Germany', 'lat': 52.52, 'lon': 13.405, 'method': 'built_in_example'},\n    ])\ndf.head()"),
        md("## Step 2: Validate coordinates"),
        code("valid = validate_coordinates(df)\nvalid"),
        md("## Step 3: Choose popup columns\n\nPopups should show enough context to interpret the point without making the marker hard to read."),
        code("popup_cols = [col for col in ['mention', 'selected_name', 'name', 'country', 'method'] if col in valid.columns]\npopup_cols"),
        md("## Step 4: Create the map"),
        code("fmap = create_location_map(valid, popup_cols=popup_cols)\nfmap"),
        md("## Step 5: Save the map"),
        code("out = save_map(fmap, MAPS_DIR / 'sample_geoparsing_map.html')\nprint('Saved:', out)"),
        md("## Exercise\n\nChange the popup columns or visualize only one resolution method."),
        code("if 'method' in valid.columns:\n    one_method = valid[valid['method'] == valid['method'].iloc[0]]\n    create_location_map(one_method, popup_cols=popup_cols)"),
        md("## Common issues\n\n- Rows without valid latitude and longitude are skipped.\n- If there are no valid coordinates, the map opens at a world view.\n- Folium maps are saved as standalone HTML files."),
    ]


def notebook_06() -> list[dict]:
    return [
        md("# Application Challenge\n\n## Goal\n\nApply the geoparsing workflow to two real datasets and then design your own application idea."),
        md("## What you will do\n\n- Inspect the Hurricane Harvey tweet dataset.\n- Inspect the hydrology-related scientific paper dataset.\n- Geoparse a controlled subset with the NER tools and geoparsing methods from earlier notebooks.\n- Save intermediate mentions and resolved locations.\n- Use the instructor demonstrations as inspiration for your own application.\n- Bring or prepare your own data for a new use case."),
        code(COMMON_SETUP + "\nimport json\nimport importlib.util\nimport re\nimport pandas as pd\nimport requests\nfrom src.config import RESULTS_DIR, MAPS_DIR, GEONAMES_BASE_URL, PHOTON_BASE_URL, LLM_RAG_BASE_URL, REQUEST_TIMEOUT\nfrom src.data_utils import save_dataframe\nfrom src.ner_utils import extract_locations_spacy, extract_locations_stanza, extract_locations_flair, extract_locations_transformers, normalize_ner_results, combine_and_deduplicate_mentions\nfrom src.visualization_utils import create_location_map, save_map"),
        md("## Step 1: Dataset 1 - Hurricane Harvey tweets\n\nThe file `data/disaster_tweets/harvey.json` contains raw tweet text from the Hurricane Harvey crisis. Each record has a tweet id, raw text, a category, and category scores. The category was produced by an unsupervised method and can be used as weak thematic context, not as ground truth."),
        code("""harvey_path = PROJECT_ROOT / "data" / "disaster_tweets" / "harvey.json"
with harvey_path.open("r", encoding="utf-8") as handle:
    harvey_raw = json.load(handle)

harvey_df = pd.DataFrame([
    {
        "text_id": str(tweet_id),
        "text": item.get("text", ""),
        "category": item.get("category", ""),
        "category_scores": item.get("category_scores", {}),
    }
    for tweet_id, item in harvey_raw.items()
])

print("Harvey tweet records:", len(harvey_df))
display(harvey_df.head())
display(harvey_df["category"].value_counts().rename_axis("category").reset_index(name="count"))"""),
        md("## Step 2: Dataset 2 - Hydrology scientific papers\n\nThe file `data/scientific_paper/scientific_paper.jsonl` contains one paper per line. The records describe scientific publications related to hydrology and hazard events such as floods, landslides, cyclones, drought, and water resources. The source field for geoparsing is `abstract_text`. In this file, `abstract_text` starts with a repeated article title, so the notebook removes that duplicated prefix and uses the remaining abstract body as `geoparsing_text`. Fields such as publication year, title, journal, topic, DOI, and existing location metadata are kept as metadata for filtering and interpretation."),
        code("""paper_path = PROJECT_ROOT / "data" / "scientific_paper" / "scientific_paper.jsonl"
paper_records = []
with paper_path.open("r", encoding="utf-8") as handle:
    for line in handle:
        if line.strip():
            paper_records.append(json.loads(line))

paper_df = pd.DataFrame(paper_records)
paper_df["text_id"] = paper_df["id"].astype(str)
paper_df["abstract_text"] = paper_df["abstract_text"].fillna("").astype(str)

def abstract_body_from_source(raw_abstract, article_title):
    text = str(raw_abstract or "").strip()
    title = str(article_title or "").strip()
    if title and text.startswith(title):
        text = text[len(title):].strip()
    text = re.sub(r"^(ABSTRACT|Abstract)\\s*:?", "", text).strip()
    return text

paper_df["abstract_body"] = [
    abstract_body_from_source(raw, title)
    for raw, title in zip(paper_df["abstract_text"], paper_df["article_title"])
]
paper_df["abstract_chars"] = paper_df["abstract_text"].str.len()
paper_df["abstract_body_chars"] = paper_df["abstract_body"].str.len()

print("Scientific paper records:", len(paper_df))
display(paper_df[["text_id", "pub_year", "article_title", "abstract_body", "journal", "topic", "abstract_body_chars", "locations_count"]].head())
display(paper_df["topic"].value_counts().head(12).rename_axis("topic").reset_index(name="count"))
display(paper_df["pub_year"].value_counts().sort_index().tail(15).rename_axis("pub_year").reset_index(name="count"))"""),
        md("## Step 3: Processing controls\n\nProcessing all records can take time, especially if you call internal services or the LLM-RAG service. Start with a small threshold such as 20 or 50 texts, then increase it after the workflow is correct. The full selected text is used for each record: tweet text for Harvey, and the cleaned abstract body derived from `abstract_text` for scientific papers."),
        code("""DATASET_NAME = "scientific_papers"  # options: "harvey", "scientific_papers"
MAX_TEXTS = 50

NER_TOOL = "spacy"  # options: "spacy", "stanza", "flair", "transformers"
GEOPARSING_METHOD = "unitoprank"  # options: "unitoprank", "llm_rag"

USE_GEONAMES = True  # required candidate source
USE_PHOTON = False   # False: GeoNames only; True: GeoNames + Photon

LLM_RAG_SERVICE_URL = LLM_RAG_BASE_URL  # used only when GEOPARSING_METHOD = "llm_rag"

print("Dataset:", DATASET_NAME)
print("MAX_TEXTS:", MAX_TEXTS)
print("NER_TOOL:", NER_TOOL)
print("GEOPARSING_METHOD:", GEOPARSING_METHOD)
print("Candidate sources:", "GeoNames + Photon" if USE_PHOTON else "GeoNames only")"""),
        md("## Step 4: Prepare a processing table"),
        code("""def prepare_dataset(name, max_texts=50):
    if name == "harvey":
        out = harvey_df[["text_id", "text", "category"]].copy()
        out = out.rename(columns={"text": "geoparsing_text"})
        out["application_context"] = out["category"]
    elif name == "scientific_papers":
        cols = ["text_id", "abstract_body", "pub_year", "article_title", "journal", "topic", "doi"]
        out = paper_df[cols].copy()
        out = out.rename(columns={"abstract_body": "geoparsing_text"})
        out["application_context"] = out["topic"]
    else:
        raise ValueError("DATASET_NAME must be 'harvey' or 'scientific_papers'")

    out = out.dropna(subset=["geoparsing_text"]).head(max_texts).copy()
    out["geoparsing_text"] = out["geoparsing_text"].astype(str)
    return out.reset_index(drop=True)

texts = prepare_dataset(DATASET_NAME, MAX_TEXTS)
texts.head()"""),
        md("## Step 5: Define and preview toponym extraction\n\nThis reuses the NER tools introduced in Notebook 01. If a package or model is missing, run that tool's install cell in Notebook 01. This step defines the extraction function and previews only the first few records. The full `MAX_TEXTS` subset is processed later in Step 7."),
        code("""def extract_toponyms_with_selected_ner(text, ner_tool="spacy", source_text_id=None):
    if ner_tool == "spacy":
        results = extract_locations_spacy(text, model_name="en_core_web_sm")
    elif ner_tool == "stanza":
        results = extract_locations_stanza(text, lang="en")
    elif ner_tool == "flair":
        results = extract_locations_flair(text)
    elif ner_tool == "transformers":
        results = extract_locations_transformers(text)
    else:
        raise ValueError("NER_TOOL must be one of: spacy, stanza, flair, transformers")
    out = normalize_ner_results(results, source_text_id=source_text_id)
    if not out.empty and source_text_id is not None:
        out["source_text_id"] = out["source_text_id"].fillna(source_text_id)
    return out

def extract_mentions_for_texts(texts_df, ner_tool, dataset_name, save=True):
    mention_frames = []
    for i, row in texts_df.iterrows():
        if i and i % 10 == 0:
            print(f"NER processed {i}/{len(texts_df)} texts")
        mention_frames.append(
            extract_toponyms_with_selected_ner(
                row["geoparsing_text"],
                ner_tool=ner_tool,
                source_text_id=row["text_id"],
            )
        )

    out = combine_and_deduplicate_mentions(mention_frames)
    if out.empty:
        print("No toponyms were extracted. Check the selected NER tool and input texts.")
        return out
    if out["source_text_id"].isna().any():
        missing = int(out["source_text_id"].isna().sum())
        raise ValueError(f"{missing} extracted mentions are missing source_text_id.")

    out = out.merge(
        texts_df[["text_id", "geoparsing_text", "application_context"]].rename(
            columns={"text_id": "source_text_id", "geoparsing_text": "full_text"}
        ),
        on="source_text_id",
        how="left",
    )

    if save:
        mention_path = RESULTS_DIR / f"{dataset_name}_challenge_mentions.csv"
        save_dataframe(out, mention_path)
        print("Saved mentions:", mention_path)
    return out

preview_texts = texts.head(min(3, len(texts))).copy()
preview_mentions = extract_mentions_for_texts(preview_texts, NER_TOOL, DATASET_NAME, save=False)
preview_mentions.head(20)"""),
        md("## Step 6: Resolution helpers\n\nChoose one geoparsing method. `unitoprank` uses the UniTopRank workflow from Notebook 03. `llm_rag` uses the LLM-RAG resolution service from Notebook 04. GeoNames is required; Photon is an optional additional candidate source."),
        code("""def check_candidate_sources(use_geonames=True):
    if not use_geonames:
        raise ValueError("USE_GEONAMES must stay True for these geoparsing workflows.")

def candidate_source_label(use_photon=False):
    return "geonames_photon" if use_photon else "geonames"

def resolve_with_llm_rag(texts_df, mentions_df, service_base_url, use_geonames=True, use_photon=False):
    check_candidate_sources(use_geonames)
    if not service_base_url:
        print("LLM_RAG_SERVICE_URL is not configured.")
        return pd.DataFrame()
    rows = []
    for _, text_row in texts_df.iterrows():
        group = mentions_df[mentions_df["source_text_id"] == text_row["text_id"]]
        if group.empty:
            continue
        payload = {
            "text": text_row["geoparsing_text"],
            "toponyms": [
                {"text": r["mention"], "start": int(r["start"]), "end": int(r["end"])}
                for _, r in group.iterrows()
                if pd.notna(r.get("start")) and pd.notna(r.get("end"))
            ],
            "use_geonames": True,
            "use_photon": bool(use_photon),
        }
        try:
            response = requests.post(f"{service_base_url.rstrip('/')}/resolve", json=payload, timeout=max(REQUEST_TIMEOUT, 60))
            response.raise_for_status()
            for item in response.json().get("results", []):
                rows.append({
                    "source_text_id": text_row["text_id"],
                    "mention": item.get("text") or item.get("mention"),
                    "selected_name": item.get("address") or item.get("full_name"),
                    "country": item.get("country"),
                    "lat": item.get("lat"),
                    "lon": item.get("lon"),
                    "method": "llm_rag_geonames_photon" if use_photon else "llm_rag_geonames",
                })
        except Exception as exc:
            print(f"LLM-RAG failed for {text_row['text_id']}: {exc}")
    return pd.DataFrame(rows)

def add_unitoprank_paths():
    for path in [PROJECT_ROOT / "external" / "UniTopRank", PROJECT_ROOT / "external" / "UniTopRank" / "api"]:
        if path.exists() and str(path) not in sys.path:
            sys.path.insert(0, str(path))
    if importlib.util.find_spec("unitoprank") is None and importlib.util.find_spec("unitorank") is not None:
        import importlib as importlib_module
        import unitorank
        sys.modules.setdefault("unitoprank", unitorank)
        for name in ["types", "ranker", "candidate_retriever", "ner", "pipeline"]:
            try:
                sys.modules.setdefault(f"unitoprank.{name}", importlib_module.import_module(f"unitorank.{name}"))
            except Exception:
                pass

def resolve_with_unitoprank(texts_df, mentions_df, use_geonames=True, use_photon=False):
    check_candidate_sources(use_geonames)
    candidate_source = candidate_source_label(use_photon)
    add_unitoprank_paths()
    try:
        from geo_rank_api import resolve_toponyms
        from geoparsing_api import CandidateRetriever, CandidateRetrieverConfig
    except Exception as exc:
        print("UniTopRank is not available. Run Notebook 03 setup first.", exc)
        return pd.DataFrame()

    def prefix(base_url, param):
        base = str(base_url).strip()
        if f"{param}=" in base:
            return base
        separator = "&" if "?" in base else "?"
        return f"{base}{separator}{param}="

    retriever = CandidateRetriever(CandidateRetrieverConfig(
        geonames_enabled=True,
        photon_enabled=use_photon,
        bool_merge=False,
        geonames_url=prefix(GEONAMES_BASE_URL, "location"),
        photon_url=prefix(PHOTON_BASE_URL, "q"),
        timeout_seconds=int(REQUEST_TIMEOUT),
    ))

    rows = []
    candidate_queries = 0
    total_candidates = 0
    for _, text_row in texts_df.iterrows():
        group = mentions_df[mentions_df["source_text_id"] == text_row["text_id"]]
        toponyms = [
            {"LOC": r["mention"], "start": int(r["start"]), "end": int(r["end"])}
            for _, r in group.iterrows()
            if pd.notna(r.get("start")) and pd.notna(r.get("end"))
        ]
        if not toponyms:
            continue
        candidates_by_toponym = retriever.get_candidates_for_toponyms([m["LOC"] for m in toponyms])
        candidate_queries += len(candidates_by_toponym)
        total_candidates += sum(len(candidates) for candidates in candidates_by_toponym.values())
        try:
            resolved, _ = resolve_toponyms(text=text_row["geoparsing_text"], mentions=toponyms, candidates_by_toponym=candidates_by_toponym, top_n=10)
            for item in resolved:
                selected_name = item.get("address")
                lat = item.get("lat")
                lon = item.get("lon")
                if not selected_name or lat in (None, 0, 0.0) or lon in (None, 0, 0.0):
                    continue
                rows.append({
                    "source_text_id": text_row["text_id"],
                    "mention": item.get("LOC") or item.get("text"),
                    "selected_name": selected_name,
                    "lat": lat,
                    "lon": lon,
                    "method": f"unitoprank_{candidate_source}",
                })
        except Exception as exc:
            print(f"UniTopRank failed for {text_row['text_id']}: {exc}")
    print(f"UniTopRank candidate lookup: {candidate_queries} mention queries, {total_candidates} candidates returned.")
    if candidate_queries and total_candidates == 0:
        print("No candidates were returned by GeoNames/Photon. Check DLR network/VPN and the configured candidate service URLs.")
    return pd.DataFrame(rows)"""),
        md("## Step 7: Run the complete geoparsing workflow\n\nRun this cell after changing the configuration in Step 3. It prepares the selected records, extracts toponyms with the selected NER tool, resolves them with the selected geoparsing method, and saves both intermediate mentions and final resolved locations."),
        code("""texts = prepare_dataset(DATASET_NAME, MAX_TEXTS)
print(f"Running full geoparsing workflow on {len(texts)} {DATASET_NAME} records")

mentions = extract_mentions_for_texts(texts, NER_TOOL, DATASET_NAME)
print("Extracted mentions:", len(mentions))

if mentions.empty:
    resolved = pd.DataFrame()
elif GEOPARSING_METHOD == "unitoprank":
    resolved = resolve_with_unitoprank(
        texts,
        mentions,
        use_geonames=USE_GEONAMES,
        use_photon=USE_PHOTON,
    )
elif GEOPARSING_METHOD == "llm_rag":
    resolved = resolve_with_llm_rag(
        texts,
        mentions,
        LLM_RAG_SERVICE_URL,
        use_geonames=USE_GEONAMES,
        use_photon=USE_PHOTON,
    )
else:
    raise ValueError("GEOPARSING_METHOD must be unitoprank or llm_rag")

if resolved.empty:
    print("No resolved locations returned. Check NER output, UniTopRank setup, service access, or candidate-source connectivity.")
else:
    if "source_text_id" in resolved.columns and "application_context" not in resolved.columns:
        resolved = resolved.merge(
            texts[["text_id", "application_context"]],
            left_on="source_text_id",
            right_on="text_id",
            how="left",
        )
    resolved_path = RESULTS_DIR / f"{DATASET_NAME}_{GEOPARSING_METHOD}_challenge_results.csv"
    save_dataframe(resolved, resolved_path)
    print("Saved:", resolved_path)

resolved.head(20)"""),
        md("## Step 8: Summarize and visualize"),
        code("""if not resolved.empty and {"lat", "lon"}.issubset(resolved.columns):
    summary_cols = [col for col in ["application_context", "country", "method"] if col in resolved.columns]
    if summary_cols:
        display(resolved.groupby(summary_cols, dropna=False).size().reset_index(name="count").head(30))
    else:
        display(resolved["mention"].value_counts().head(20).rename_axis("mention").reset_index(name="count"))

    fmap = create_location_map(resolved, popup_cols=[c for c in ["mention", "selected_name", "application_context", "method"] if c in resolved.columns])
    map_path = save_map(fmap, MAPS_DIR / f"{DATASET_NAME}_{GEOPARSING_METHOD}_challenge_map.html")
    print("Saved map:", map_path)
    display(fmap)
else:
    print("No valid coordinates available for mapping.")"""),
        md("## Instructor demonstrations\n\nThe workshop includes two demonstrations built from these raw datasets:\n\n- A Hurricane Harvey tweet exploration demo that uses tweet text, unsupervised categories, and geoparsed locations to support crisis-situation awareness.\n- A hydrology scientific-paper exploration demo that uses publication metadata, abstracts, topics, and geoparsed study locations to support location-aware literature discovery.\n\nThe demo code is not included here. Use the ideas and outputs from this notebook as inspiration for your own application."),
        md("## Bring your own data\n\nYou can use the same workflow with your own dataset. Prepare a table with `text_id` and `geoparsing_text` columns. Metadata columns such as category, year, topic, source, or author can be kept and used later for filtering or visualization."),
        code("""my_data = pd.DataFrame([
    {"text_id": "my_1", "geoparsing_text": "Add your own text here.", "application_context": "my use case"}
])

# Example: replace `texts` with your own table and rerun Step 5 onward.
# texts = my_data.head(MAX_TEXTS).copy()
my_data"""),
        md("## Exercise\n\nChoose one dataset and process a small subset. Then design one application view or analysis question:\n\n- Which categories or topics contain the most place references?\n- Which places appear repeatedly?\n- Which geoparsing method works best for your use case?\n- What would an end user need to see on a map or dashboard?"),
        code("""feedback = {
    "Dataset used": DATASET_NAME,
    "NER tool used": NER_TOOL,
    "Geoparsing method used": GEOPARSING_METHOD,
    "Candidate sources": "GeoNames + Photon" if USE_PHOTON else "GeoNames only",
    "Application idea": "",
    "What worked well": "",
    "What was difficult": "",
}
feedback"""),
        md("## Common issues\n\n- Processing all records can take time; start with `MAX_TEXTS = 20` or `MAX_TEXTS = 50`.\n- Optional NER packages or models may be missing; install them in Notebook 01.\n- GeoNames, Photon, UniTopRank, and LLM-RAG services may require setup or DLR network/VPN access.\n- Scientific papers use the full `abstract_text` field for geoparsing."),
    ]


def main() -> None:
    notebooks = {
        "00_setup_and_overview.ipynb": notebook_00(),
        "01_toponym_recognition.ipynb": notebook_01(),
        "02_dlr_geocoding_services.ipynb": notebook_02(),
        "03_unitoprank_resolution.ipynb": notebook_03(),
        "04_llm_rag_resolution_service.ipynb": notebook_04(),
        "05_map_visualization.ipynb": notebook_05(),
        "06_application_challenge.ipynb": notebook_06(),
    }
    for name, cells in notebooks.items():
        write_notebook(name, cells)


if __name__ == "__main__":
    main()
