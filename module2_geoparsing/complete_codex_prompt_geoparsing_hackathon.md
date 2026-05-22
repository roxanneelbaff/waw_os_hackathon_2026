# Complete Codex Prompt: Generate Professional Geoparsing Hackathon Jupyter Notebooks

You are working in the root folder of a DLR Geoparsing Hackathon project.

Your task is to generate a clean, user-friendly, professional set of Jupyter Notebooks and supporting files for a hands-on geoparsing hackathon.

The notebooks should follow this teaching style:

```text
Explain one step → Run a small code example → Let participants try → Discuss the output
```

Keep the material practical. Avoid long theory. Avoid one huge notebook. The target users are DLR researchers, engineers, and scientists who may not be geoparsing experts.

---

## 1. First inspect the project

Before creating or editing files:

1. Inspect the current project structure.
2. Check whether these folders already exist:
   - `notebooks/`
   - `src/`
   - `data/`
   - `outputs/`
   - `external/`
3. Check whether UniTopRank is already available in the project, for example:
   - `UniTopRank/`
   - `external/UniTopRank/`
   - `third_party/UniTopRank/`
   - any folder containing `geo_rank_api.py`
   - any folder containing `geoparsing_api.py`
4. Check whether these imports work:

```python
from geo_rank_api import resolve_toponyms
from geoparsing_api import GeoparsingConfig, GeoparsingPipeline
```

5. Try to inspect these local files if accessible:

```text
/home/hu_xk/Documents/kratos/workplace/alpaca-lora/unified_geo_server_multi_ner.py
/home/hu_xk/Documents/kratos/workplace/alpaca-lora/disaster_category.py
/home/hu_xk/Documents/kratos/workplace/alpaca-lora/test_geoparser.py
/home/hu_xk/Documents/kratos/workplace/alpaca-lora/gui_streamlit.py
/home/hu_xk/Documents/kratos/workplace/alpaca-lora/new_geoparsing_server
```

Use those local files only to understand:

- the LLM-RAG resolution service API,
- request format,
- response format,
- endpoint paths,
- useful visualization logic.

Do not delete existing user files.

If something is missing or inaccessible, create a clean placeholder and clearly explain what the user needs to configure.

Do not invent unavailable code internals.

---

## 2. Learning workflow

The notebooks should guide participants through this workflow:

```text
Raw text
→ Place-name extraction
→ Toponym resolution
→ Coordinates
→ Map visualization
→ Applications
```

Main topics:

1. Setup and overview
2. Toponym recognition with public NER tools
3. Toponym resolution using DLR GeoNames and Photon geocoders
4. UniTopRank resolution method
5. LLM- and RAG-based resolution service
6. Map visualization
7. Application challenge with prepared or user-provided data

---

## 3. Create this folder structure

Create or update this structure:

```text
notebooks/
  00_setup_and_overview.ipynb
  01_toponym_recognition.ipynb
  02_dlr_geocoding_services.ipynb
  03_unitoprank_resolution.ipynb
  04_llm_rag_resolution_service.ipynb
  05_map_visualization.ipynb
  06_application_challenge.ipynb

src/
  __init__.py
  config.py
  ner_utils.py
  geocoder_clients.py
  visualization_utils.py
  data_utils.py
  validate_project.py

data/
  sample_texts/
  disaster_tweets/
  disease_news/
  scientific_paper/

outputs/
  results/
  maps/

README.md
requirements-core.txt
requirements-optional-ner.txt
.env.example
```

Do not over-engineer the project.

Do not create a complicated package or framework. This is teaching material for a hackathon.

---

## 4. General notebook style

Each notebook should be short, readable, and workshop-friendly.

For each notebook:

- Start with a title.
- Add a short goal.
- Add a small "What you will do" list.
- Use clear Markdown sections.
- Keep explanations short.
- Keep code cells small.
- Add comments for beginners.
- Add at least one small exercise.
- Add a short troubleshooting section.
- Save important intermediate results to `outputs/results/`.
- Load previous intermediate results if they exist.
- Also include small built-in examples so each notebook can run independently.
- Make optional packages fail gracefully.
- Make DLR internal service calls fail gracefully.
- Avoid hard-coded absolute paths inside notebooks.
- Avoid credentials and secrets.
- Avoid automatic `pip install` or `git clone` in normal notebook cells.
- Put installation/download commands in Markdown or commented cells only.
- Do not invent unavailable project internals.

Recommended notebook section pattern:

```markdown
# Notebook title

## Goal

## What you will do

## Step 1: Short explanation

## Step 2: Run code

## Exercise

## Common issues
```

Target notebook length:

```text
15-25 cells per notebook
```

Avoid very long notebooks.

---

## 5. Configuration

Create `src/config.py`.

It should include:

```python
from pathlib import Path
import os

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "data"
OUTPUT_DIR = PROJECT_ROOT / "outputs"
RESULTS_DIR = OUTPUT_DIR / "results"
MAPS_DIR = OUTPUT_DIR / "maps"

GEONAMES_BASE_URL = os.getenv(
    "GEONAMES_BASE_URL",
    "http://dw-mir-postgis.intra.dlr.de:8091/location"
)

PHOTON_BASE_URL = os.getenv(
    "PHOTON_BASE_URL",
    "http://photon.intra.dlr.de:2322/api/"
)

LLM_RAG_BASE_URL = os.getenv("LLM_RAG_BASE_URL", "")
REQUEST_TIMEOUT = float(os.getenv("REQUEST_TIMEOUT", "10"))
```

Create `.env.example`:

```text
GEONAMES_BASE_URL=http://dw-mir-postgis.intra.dlr.de:8091/location
PHOTON_BASE_URL=http://photon.intra.dlr.de:2322/api/
LLM_RAG_BASE_URL=
REQUEST_TIMEOUT=10
```

---

## 6. Notebook 00: Setup and Overview

Create:

```text
notebooks/00_setup_and_overview.ipynb
```

Purpose:

Give participants the big picture and check whether the environment works.

Include:

- Short explanation of the geoparsing workflow:

```text
Raw text → Place-name extraction → Toponym resolution → Coordinates → Map visualization → Applications
```

- Project folder check.
- Python version check.
- Package availability check.
- Load 3-5 sample texts.
- Test DLR GeoNames and Photon reachability using a short timeout.
- Friendly message if DLR services are not reachable:

```text
This service may require the DLR internal network or VPN. You can still continue with sample outputs.
```

Create or use a helper function for service checking.

Save sample texts to:

```text
outputs/results/sample_texts.csv
```

Sample texts:

```text
Paris and Berlin are often mentioned in European news.
Apple opened a new office in California.
Nach dem Hochwasser wurden Schäden in Bayern, Passau und Österreich gemeldet.
The earthquake affected Izmir and nearby villages.
Several hydrology studies focus on the Rhine basin and the Danube region.
```

---

## 7. Notebook 01: Toponym Recognition

Create:

```text
notebooks/01_toponym_recognition.ipynb
```

Purpose:

Show how to extract candidate place names from text using public NER tools.

Required tools to cover:

1. spaCy
2. Stanza
3. Flair
4. Hugging Face Transformers multilingual NER

Important design:

- Make spaCy the default lightweight path.
- Make Stanza, Flair, and Transformers optional sections.
- If a model is missing, show a friendly message instead of crashing.
- Do not download large models automatically without asking.
- Include English and German/multilingual examples.
- Do not include geocoding in this notebook.

Location-like entity labels:

Use a configurable set in `src/ner_utils.py`:

```python
LOCATION_LABELS = {
    "LOC",
    "LOCATION",
    "GPE",
    "FAC",
    "FACILITY",
    "NEL",
}
```

Explain briefly:

- Different NER tools use different labels.
- `GPE` usually means countries, cities, or states.
- `LOC` usually means natural or general locations.
- `FAC` can mean buildings, airports, bridges, etc.
- Some `FAC` entities may or may not be useful depending on the application.

Create `src/ner_utils.py` with simple reusable functions:

```python
extract_locations_spacy(text, model_name="en_core_web_sm")
extract_locations_stanza(text, lang="en")
extract_locations_flair(text, model_name="flair/ner-english")
extract_locations_transformers(text, model_name="Davlan/xlm-roberta-base-ner-hrl")
normalize_ner_results(results)
combine_and_deduplicate_mentions(results)
```

The functions should:

- return empty lists instead of crashing when optional packages are missing,
- print clear messages about missing models,
- keep original labels,
- normalize output.

Normalize output to:

```text
mention | start | end | label | tool | source_text_id | sentence
```

Example texts:

```text
Paris and Berlin are often mentioned in European news.
Apple opened a new office in California.
Nach dem Hochwasser wurden Schäden in Bayern, Passau und Österreich gemeldet.
The earthquake affected Izmir and nearby villages.
Several hydrology studies focus on the Rhine basin and the Danube region.
```

The notebook should show:

- How to run spaCy.
- How to optionally run Stanza.
- How to optionally run Flair.
- How to optionally run a multilingual Hugging Face NER model.
- How to compare outputs.
- How to combine and deduplicate mentions.
- A short discussion: NER only extracts candidate place names. It does not resolve them to coordinates.

Save output to:

```text
outputs/results/ner_mentions.csv
```

Exercise:

Ask users to add their own text and compare NER tools.

---

## 8. Notebook 02: DLR Geocoding Services

Create:

```text
notebooks/02_dlr_geocoding_services.ipynb
```

Purpose:

Show how to use DLR GeoNames and Photon services to retrieve candidate locations.

DLR endpoints:

```text
GeoNames:
http://dw-mir-postgis.intra.dlr.de:8091/location?location=

Photon:
http://photon.intra.dlr.de:2322/api/?q=
```

Reference projects:

```text
https://github.com/amagge/geonames-service
https://github.com/komoot/photon
```

Create `src/geocoder_clients.py` with:

```python
geocode_geonames(query, limit=5, timeout=None)
geocode_photon(query, limit=5, timeout=None)
standardize_geonames_response(query, response_json)
standardize_photon_response(query, response_json)
compare_geocoders(query, limit=5)
```

Important:

- GeoNames and Photon may return different JSON structures.
- Write parsers defensively.
- Preserve raw JSON in a `raw` column for debugging.
- Do not assume every field exists.
- Do not crash if services are unavailable.

Standard output columns:

```text
query | source | name | country | state | county | lat | lon | feature_class | feature_code | population | raw
```

Include examples:

```text
Berlin
Paris
Cambridge
Springfield
Izmir
Bayern
Rhine
Danube
```

The notebook should show:

- Browser URL example.
- Python `requests` example.
- Candidate comparison table.
- Short discussion: geocoding candidates are not yet final resolution.

Save candidate results to:

```text
outputs/results/geocoder_candidates.csv
```

Exercise:

Ask users to try an ambiguous place name and compare candidates from GeoNames and Photon.

---

## 9. Notebook 03: UniTopRank Resolution

Create:

```text
notebooks/03_unitoprank_resolution.ipynb
```

Purpose:

Demonstrate the UniTopRank toponym resolution workflow.

Reference repository:

```text
https://gitlab.com/dlr-dw/UniTopRank
```

Very important:

Do not invent a fake UniTopRank implementation.

Notebook 03 should be useful in both cases:

1. If UniTopRank is installed, use the real direct ranking API.
2. If UniTopRank is not installed, show setup instructions and continue with a clearly labeled demo baseline.

### 9.1 Check whether UniTopRank is available

First check whether the code is available in the current project.

Search for possible folders such as:

```text
UniTopRank/
external/UniTopRank/
third_party/UniTopRank/
api/
```

Also check whether these imports work:

```python
from geo_rank_api import resolve_toponyms
from geoparsing_api import GeoparsingConfig, GeoparsingPipeline
```

If `geo_rank_api` works, prefer the direct ranking API.

### 9.2 If UniTopRank is not available

Do not automatically download it.

Do not run `git clone` automatically in a normal notebook cell.

Instead, add this Markdown setup instruction in the notebook and README:

```bash
mkdir -p external
git clone https://gitlab.com/dlr-dw/UniTopRank.git external/UniTopRank
cd external/UniTopRank/api

python3 -m venv /tmp/unitoprank_venv
source /tmp/unitoprank_venv/bin/activate

pip install --upgrade pip setuptools wheel
pip install -r requirements.txt
```

Optional NER dependencies:

```bash
pip install -r requirements-ner.txt
```

Explain:

For this hackathon, NER is already covered in Notebook 01, so the recommended path is to use UniTopRank's direct ranking API rather than its full NER pipeline.

You may include a commented cell:

```python
# Optional: run this manually only if UniTopRank is not installed.
# !mkdir -p ../external
# !git clone https://gitlab.com/dlr-dw/UniTopRank.git ../external/UniTopRank
```

### 9.3 Prefer the direct ranking API

If UniTopRank is available, use this style:

```python
from geo_rank_api import resolve_toponyms

resolved_mentions, ranked_results = resolve_toponyms(
    text=text,
    mentions=mentions,
    candidates_by_toponym=candidates_by_toponym,
    top_n=10,
    distance_threshold_km=300,
)
```

Example input:

```python
text = "Ich habe Paris besucht und bin dann nach Berlin geflogen."

mentions = [
    {"LOC": "Paris", "start": 9, "end": 14},
    {"LOC": "Berlin", "start": 42, "end": 48},
]
```

Expected candidate format:

```python
candidates_by_toponym = {
    "paris": [
        {
            "address": "Paris, Ile-de-France, France, Europe",
            "lat": 48.8566,
            "lon": 2.3522,
            "name": "Paris",
            "alt_names": ["Parigi", "París", "Parijs"],
            "admin_level": "PPLC",
            "population": 2140526,
        }
    ]
}
```

If participant NER output uses `mention` or `text` instead of `LOC`, adapt the mention dictionaries.

### 9.4 Candidate retrieval

Use DLR GeoNames and Photon services for candidate retrieval if available:

```text
GeoNames:
http://dw-mir-postgis.intra.dlr.de:8091/location?location=

Photon:
http://photon.intra.dlr.de:2322/api/?q=
```

If DLR services are not reachable, use a small built-in mock candidate set for Paris and Berlin so the notebook still demonstrates the workflow.

### 9.5 Fallback baseline

If UniTopRank is not installed:

- Show a friendly warning.
- Show manual setup commands.
- Continue with a clearly labeled simplified baseline.
- Mark it as:

```text
demo_baseline_not_unitoprank
```

The fallback baseline can rank candidates by:

1. exact or fuzzy name match,
2. population if available,
3. feature type or administrative importance if available.

Clearly state:

```text
This fallback is only for demonstration. It is not the real UniTopRank method.
```

### 9.6 Notebook sections

Notebook 03 should include:

```text
1. Goal
2. What UniTopRank does
3. Check installation
4. Prepare text and mentions
5. Retrieve candidates from DLR geocoders
6. Run UniTopRank direct ranking API if available
7. Use demo fallback if unavailable
8. Compare ranked candidates
9. Save results
10. Exercise
11. Common issues
```

Output table:

```text
mention | selected_name | country | lat | lon | score | method
```

Save output to:

```text
outputs/results/unitoprank_results.csv
```

Common issues to document:

- UniTopRank is not installed.
- The user forgot to activate the UniTopRank virtual environment.
- `geo_rank_api` cannot be imported.
- DLR GeoNames or Photon is not reachable outside the DLR network/VPN.
- Candidate format does not contain required fields such as `lat`, `lon`, `address`, or `name`.
- Optional NER packages are not installed; this is fine because the hackathon uses NER from Notebook 01.

---

## 10. Notebook 04: LLM-RAG Resolution Service

Create:

```text
notebooks/04_llm_rag_resolution_service.ipynb
```

Purpose:

Show how to call the LLM- and RAG-based toponym resolution service.

Very important:

- This notebook is only for resolution.
- Do not include NER methods here.
- Use mentions that were already extracted in Notebook 01 or manually defined.
- Demonstrate client-side usage of the service, not server implementation.
- Do not include credentials.
- Do not invent service fields.

Before writing the client, inspect these files if accessible:

```text
/home/hu_xk/Documents/kratos/workplace/alpaca-lora/unified_geo_server_multi_ner.py
/home/hu_xk/Documents/kratos/workplace/alpaca-lora/disaster_category.py
/home/hu_xk/Documents/kratos/workplace/alpaca-lora/test_geoparser.py
/home/hu_xk/Documents/kratos/workplace/alpaca-lora/gui_streamlit.py
/home/hu_xk/Documents/kratos/workplace/alpaca-lora/new_geoparsing_server
```

Extract from the code if possible:

- service URL,
- endpoint path,
- request JSON format,
- response JSON format,
- required fields,
- optional fields.

If files are not accessible or the API is unclear:

- create a configurable placeholder using `LLM_RAG_BASE_URL`,
- create a function with clearly marked TODOs,
- include a mock example response so participants can still see the workflow.

Expected input format:

```text
text_id | full_text | mention | start | end
```

Expected output table, using only fields actually returned by the service:

```text
mention | selected_name | country | lat | lon | confidence | explanation | method
```

If confidence or explanation is not returned, leave those columns empty. Do not invent values.

Save output to:

```text
outputs/results/llm_rag_results.csv
```

Exercise:

Ask users to compare one ambiguous location using:

- raw GeoNames candidates,
- raw Photon candidates,
- UniTopRank result if available,
- LLM-RAG result if available.

---

## 11. Notebook 05: Map Visualization

Create:

```text
notebooks/05_map_visualization.ipynb
```

Purpose:

Visualize resolved locations on an interactive map.

Reference:

```text
/home/hu_xk/Documents/kratos/workplace/alpaca-lora/gui_streamlit.py
```

If accessible, inspect `gui_streamlit.py` and reuse useful ideas. Adapt them to Jupyter Notebook.

Use Folium as the default visualization library.

Create `src/visualization_utils.py` with:

```python
create_location_map(df, lat_col="lat", lon_col="lon", popup_cols=None)
save_map(map_obj, output_path)
validate_coordinates(df, lat_col="lat", lon_col="lon")
```

The notebook should:

- Load one of these files if available:
  - `outputs/results/unitoprank_results.csv`
  - `outputs/results/llm_rag_results.csv`
  - `outputs/results/geocoder_candidates.csv`
- Otherwise use a small built-in example.
- Create a map.
- Add popups with mention, selected place, country, and original text if available.
- Save map to:

```text
outputs/maps/sample_geoparsing_map.html
```

Handle missing or invalid coordinates gracefully.

Exercise:

Ask users to change popup columns or visualize only one resolution method.

---

## 12. Notebook 06: Application Challenge

Create:

```text
notebooks/06_application_challenge.ipynb
```

Purpose:

Let participants apply the workflow to prepared or own data.

Applications to introduce briefly:

1. Disaster response
2. Disease surveillance
3. Scientific paper search by location

Use this short explanation format for each:

```text
Problem → Text data → What geoparsing extracts → Possible demo
```

Prepared data folders:

```text
data/disaster_tweets/
data/disease_news/
data/scientific_paper/
```

The notebook should provide a simple workflow:

1. Choose dataset.
2. Load texts.
3. Extract or load place-name mentions.
4. Resolve mentions using selected method.
5. Visualize on map.
6. Summarize possible findings.
7. Write feedback.

Include TODO cells:

```python
DATASET_NAME = "disaster_tweets"  # change this
```

```python
my_texts = [
    "Add your own text here."
]
```

Final feedback questions:

- Was the API easy to use?
- Were the notebooks clear?
- Which resolution method was most useful?
- What was missing?
- What DLR use cases could benefit from this?

---

## 13. Helper files

### 13.1 `src/data_utils.py`

Include simple helpers:

```python
load_sample_texts()
load_text_dataset(dataset_name)
save_dataframe(df, path)
load_dataframe_if_exists(path)
```

Keep them simple.

### 13.2 `src/validate_project.py`

Create a simple validation script.

It should check:

- required folders exist,
- required notebooks exist,
- helper files exist,
- notebooks are valid JSON,
- output folders exist.

It does not need to execute all notebooks.

---

## 14. README

Create or update `README.md`.

Keep it practical.

Include:

- What this project is.
- Folder structure.
- Setup steps.
- How to install core requirements.
- How to install optional NER tools.
- How to start Jupyter.
- Notebook running order.
- DLR intranet/VPN note.
- UniTopRank optional setup.
- Troubleshooting.
- Contact/maintainer placeholder.

Mention that DLR services may only work inside the DLR network or VPN.

Include this UniTopRank section:

```markdown
## Optional: UniTopRank setup

The UniTopRank notebook can run in two modes:

1. Real UniTopRank mode, if the UniTopRank repository is installed.
2. Demo fallback mode, if UniTopRank is not installed.

To install UniTopRank:

```bash
mkdir -p external
git clone https://gitlab.com/dlr-dw/UniTopRank.git external/UniTopRank
cd external/UniTopRank/api
python3 -m venv /tmp/unitoprank_venv
source /tmp/unitoprank_venv/bin/activate
pip install --upgrade pip setuptools wheel
pip install -r requirements.txt
```

Optional NER dependencies:

```bash
pip install -r requirements-ner.txt
```

For this hackathon, the recommended path is the direct ranking API because NER is handled in Notebook 01.
```

---

## 15. Requirements files

Create two requirements files.

### `requirements-core.txt`

```text
jupyter
notebook
ipykernel
pandas
requests
python-dotenv
folium
rapidfuzz
```

### `requirements-optional-ner.txt`

```text
spacy
stanza
flair
transformers
torch
```

Do not force every participant to install all heavy NER packages before the basic workshop works.

README should include optional model downloads:

```bash
python -m spacy download en_core_web_sm
python -m spacy download de_core_news_sm
```

For Stanza, provide a notebook cell that checks whether the model exists and then explains how to download it.

---

## 16. Quality rules

Before finishing:

1. Make sure notebooks are valid `.ipynb` files.
2. Make sure helper functions are importable.
3. Make sure no secrets are included.
4. Make sure internal services fail gracefully.
5. Make sure optional heavy NER tools fail gracefully.
6. Make sure every notebook has a small exercise.
7. Make sure intermediate CSV outputs are saved.
8. Make sure README matches the actual files.
9. Make sure paths are relative to the project root.
10. Make sure missing services or missing packages show helpful messages.
11. Make sure no notebook pretends a fallback method is the real method.

---

## 17. Final response after completing the work

When finished, provide a concise summary:

1. Created notebooks.
2. Created helper files.
3. Existing code reused.
4. Local files that could not be accessed.
5. Manual configuration still needed.
6. How to start the first notebook.

Do not provide a long essay. Keep the summary practical.
