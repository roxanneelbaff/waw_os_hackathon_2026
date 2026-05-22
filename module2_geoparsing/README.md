# Geoparsing Hackathon Notebooks

This project contains hands-on Jupyter Notebook material for a DLR geoparsing hackathon.

The workflow is:

```text
Raw text -> Place-name extraction -> Toponym resolution -> Coordinates -> Map visualization -> Applications
```

The notebooks are designed for researchers, engineers, and scientists who want practical examples without a large software framework.

## Folder Structure

```text
notebooks/                 Workshop notebooks
src/                       Small reusable helper functions
data/                      Sample and challenge texts
outputs/results/           Intermediate CSV outputs
outputs/maps/              Saved HTML maps
external/                  Optional external tools such as UniTopRank
```

## Setup

Create and activate an environment, then install the lightweight workshop dependencies:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements-core.txt
```

Optional NER tools are separated because some packages and models are large. For workshop participants, the recommended path is to open Notebook 01 and use the per-tool install cells directly before each example.

For pre-building an environment, you can install all optional NER packages with:

```bash
pip install -r requirements-optional-ner.txt
python -m spacy download en_core_web_sm
python -m spacy download de_core_news_sm
```

Copy `.env.example` to `.env` if you need to override service URLs.

## Start Jupyter

```bash
jupyter notebook
```

Run the notebooks in this order:

1. `00_setup_and_overview.ipynb`
2. `01_toponym_recognition.ipynb`
3. `02_dlr_geocoding_services.ipynb`
4. `03_unitoprank_resolution.ipynb`
5. `04_llm_rag_resolution_service.ipynb`
6. `05_map_visualization.ipynb`
7. `06_application_challenge.ipynb`

## DLR Services

The GeoNames, Photon, and LLM-RAG service URLs may require the DLR internal network or VPN. The notebooks catch connection errors and continue with small sample outputs where possible.

Notebook 04 uses `SERVICE_BASE_URL` for the LLM-RAG service endpoint and supports `use_geonames=True` with optional `use_photon=True`.

Default URLs are configured in `src/config.py` and can be overridden through environment variables:

```text
GEONAMES_BASE_URL
PHOTON_BASE_URL
LLM_RAG_BASE_URL
REQUEST_TIMEOUT
```

## Optional: UniTopRank Setup

Notebook 03 uses the official UniTopRank repository to rank GeoNames/Photon candidates. It first extracts place names with the NER setup from Notebook 01, then retrieves candidates, then calls the UniTopRank ranking API.

Notebook 03 has two candidate-source options:

- `geonames`: use GeoNames only.
- `geonames_photon`: follow UniTopRank's default two-geocoder logic: use GeoNames first, then use Photon only when GeoNames has no candidates or no high-quality name match.

To install UniTopRank:

```bash
mkdir -p external
git clone https://gitlab.com/dlr-dw/UniTopRank.git external/UniTopRank
cd external/UniTopRank
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
Current UniTopRank snapshots keep `geo_rank_api.py`, `geoparsing_api.py`, and `requirements.txt` directly in the repository root.

## Troubleshooting

- If an internal service is unreachable, check DLR network or VPN access.
- If core packages are missing, run the controlled install cell in Notebook 00.
- If NER packages or models are missing, run the install cell in the matching tool section in Notebook 01.
- If UniTopRank imports fail, run the install cell in Notebook 03 or install UniTopRank manually.
- If optional NER packages are missing, Notebook 01 will still run the available sections and skip the others.
- Run `python -m src.validate_project` to check that the scaffold is complete.

## Maintainer

Contact/maintainer: TODO
