# WAWOpenSearch3 Hackathon

Welcome! This hackathon explores the **EU OpenWebSearch at DLR (OWS)** ecosystem through three independent modules. Pick the one that fits your interest and dive in.

**No prior experience required** — only a basic knowledge of Python is needed.
The modules are designed for all levels:

- **Beginners** will follow guided steps to set up a working pipeline end-to-end
- **Advanced participants** can go further by tuning prompts, swapping components, experimenting with retrieval strategies, or bringing their own data and research questions

---

## Choose Your Module

| | Module | Topic | Skills |
|---|---|---|---|
| 1 | [Web Data & LLM](module1_web_and_llm/) | RAG pipeline on web crawl data | Python, LangChain, NLP |
| 2 | [Geoparsing](module2_geoparsing/) | Extract and resolve place names from text | NER, geocoding, maps |
| 3 | [Web Imprint Dataset](module3_web_imprint_dataset/) | Explore a geolocated legal imprint dataset | Geospatial analysis, data exploration |

---

## Module 1 — Web Data & LLM

Build a full **RAG (Retrieval-Augmented Generation)** pipeline on top of European Open Web Index (OWI) data.

**What you will do:**
1. Load and clean a sample of OWI web crawl data
2. Index it locally using MOSAIC to create a searchable data bank
3. Query that data bank — from your local index, a remote MOSAIC index, or the ourrs.eu API
4. Feed retrieved results to an LLM to answer questions (hybrid, specific, or agentic mode)
5. Evaluate answer quality with an **LLM-as-a-judge**

**Initial Stack:** Python, LangChain, Jupyter, OpenAI-compatible API ( We will help you set everything up)

→ [Go to Module 1](module1_web_and_llm/)

---

## Module 2 — Geoparsing

Learn to **extract place names from text and put them on a map** using NER tools, DLR geocoding APIs, and an LLM-RAG resolution service.

**What you will do:**
1. Extract toponyms (place names) from text using NER
2. Resolve them to coordinates using DLR GeoNames / Photon geocoders
3. Compare resolution methods: standard geocoding vs. UniTopRank vs. LLM-RAG
4. Visualize geolocated texts on an interactive map
5. Apply the pipeline to real datasets (disaster tweets, disease news, scientific papers)

**Initial Stack:** Python, Jupyter, DLR geocoding APIs

→ [Go to Module 2](module2_geoparsing/)

---

## Module 3 — Web Imprint Dataset

Explore a ready-made, **thematically classified and geolocated dataset** derived from legal imprint pages of websites crawled by OWS.

**What you will do:**
1. Load and understand the OWS Imprint Dataset (coordinates + thematic labels)
2. Explore its content and spatial distribution
3. Apply it to a research question of your choice (geospatial analysis, domain classification, etc.)

**Initial Stack:** Python, Jupyter, geospatial libraries

→ [Go to Module 3](module3_web_imprint_dataset/)

---

## Common Setup

All modules use **Python 3.1X+** and **Jupyter Notebooks**. Each module folder contains its own `requirements.txt` and setup instructions.

```bash
cd <module-folder>
python -m venv .venv
source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -r requirements.txt
jupyter notebook
```

> We will help you set things up.

API keys (where needed) will be provided by the organizers on the day.
