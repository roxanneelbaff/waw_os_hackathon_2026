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
data/                      Sample and challenge datasets
outputs/results/           Generated CSV outputs
outputs/maps/              Generated HTML maps
external/                  Local external tools such as UniTopRank
```

## Setup

Create and activate an environment, then install the lightweight workshop dependencies:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements-core.txt
```



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

The GeoNames, Photon, and LLM-RAG service URLs may require the DLR internal network or VPN. If a service is unreachable, the notebooks print the error or return an empty result.

Default URLs are configured in `src/config.py` and can be overridden through environment variables:

```text
GEONAMES_BASE_URL
PHOTON_BASE_URL
LLM_RAG_BASE_URL
REQUEST_TIMEOUT
```


