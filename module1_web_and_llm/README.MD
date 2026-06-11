# Module 1 — Web Data & LLM (RAG-Based Q&A)

Build a Retrieval-Augmented Generation (RAG) pipeline on top of European Open Web Search data.  
You will ingest web crawl data, index it, retrieve relevant passages, and use an LLM to answer questions — then evaluate the quality of those answers with an LLM-as-a-judge.

---

## System Overview

```
Raw Web Data (OWI sample)
        │
        ▼
  Data Processing
  (clean, normalize)
        │
        ▼
  Indexing (MOSAIC)
        │
        ▼
  Local MOSAIC Index
        │
        │          ┌─────────────────────────┐
        │          │  Remote MOSAIC Index     │
        │          │  (URL provided)          │
        │          ├─────────────────────────┤
        └─────────►│  Local MOSAIC Index      │  ◄── Data Bank
                   ├─────────────────────────┤
                   │  ourrs.eu API            │
                   └────────────┬────────────┘
                                │
                        Query Q, retrieve N
                                │
                                ▼
                   LLM Answer Generation
                   (hybrid / specific / agentic)
                                │
                                ▼
                   LLM-as-a-Judge Evaluation
```

---

## Prerequisites

| Requirement | Version |
|---|---|
| Python | 3.10 or 3.11 recommended |
| pip | latest |
| Jupyter | included via requirements |
| LLM API key | provided by the organizers |

---

## Environment Setup

### 1. Clone the repository

```bash
git clone <repo-url>
cd wawopensearch3_hackathon/module1_web_and_llm
```

### 2. Create a virtual environment

**Linux / macOS**
```bash
python3 -m venv .venv
source .venv/bin/activate
```

**Windows (Command Prompt)**
```cmd
python -m venv .venv
.venv\Scripts\activate.bat
```

**Windows (PowerShell)**
```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

> If you see a PowerShell execution-policy error, run:  
> `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser`

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Set your API key

Create a `.env` file in this folder (it is already in `.gitignore`):

```
LLM_API_KEY=<your-key-here>
LLM_BASE_URL=<provided-by-organizers>
```

### 5. Launch Jupyter

```bash
jupyter notebook module1_notebook.ipynb
```

or open it in your favorite editor.

### 6. Sanity check

The first notebook cell verifies your Python version, installed packages, and makes a test call to the LLM. You should see a short response before moving on.

---

## Notebook Structure

The notebook `module1_notebook.ipynb` is divided into the following sections:

### Section 0 — Setup & Sanity Check
- Load environment variables
- Verify dependencies
- Confirm LLM connectivity with a hello-world call

### Section 1 — Data Acquisition (owilix)
- https://opencode.it4i.eu/openwebsearcheu-public/owi-cli/ 
- install: curl -fsSL https://openwebindex.net/owilix/install.sh | sh
            `This script:

            Installs uv if not present
            Creates a virtual environment at ~/.venv/owilix
            Installs the latest owilix
            Adds to your PATH
            Checks for config migrations`

            'Verify Installation
            owilix --version
            owilix remote doctor
            owilix remote ls all'
- check key commands: 
    - `owilix remote pull all:latest`
- Load the provided OWI (Open Web Index) sample (~few MB, JSONL/WARC format) - `owilix` tool guide
- Inspect raw records: URL, crawl date, raw HTML / extracted text

### Section 2 — Data Processing (owilic)

- basic data cleanup

### Section 3 — Indexing with MOSAIC

https://mosaic.ows.eu
check installation instructions...


> MOSAIC runs locally — no external account required.
- call function 'create_mosaic_index(data_parquet, data_ciff)' These are from OWILIX
- click here (local host for mosaic)
- Verify index by querying for a known term

the files are available here: https://drive.google.com/drive/folders/1WhM9LTesEdeyH4o6-kCuPvyqezyFFWxw?usp=share_link


### Section 4 — Retrieval

Each retrieval source is a standalone function with a consistent interface:

```python
def retrieve(queries: str | list[str], n: int = 5) -> list[dict]:
    """
    queries : a single query string or a list of query strings
    n       : number of top results to return per query
    Returns : list of result dicts with keys: source, score, text, url
    """
```

Three sources are provided:

| Function | Source |
|---|---|
| `retrieve_local(queries, n)` | Local MOSAIC index (built in Section 3) |
| `retrieve_remote(queries, n)` | Remote MOSAIC index (URL provided by organizers)  | 
| `retrieve_ourss(queries, n)` | ourrs.eu API + post-processing |

**Query handling:** pass a single string or a list. For lists, the function loops over each query and returns the union of top-N results.

**Inspect results:** after each retrieval call, a display helper shows result cards (rank, score, snippet, URL).

### Section 5 — LLM Answer Generation

Three retrieval + generation modes, selectable via a `MODE` variable:

| Mode | Behaviour |
|---|---|
| `"hybrid"` | Retrieves from **all three** sources; merges and deduplicates results |
| `"specific"` | Uses one selected source (`local`, `remote`, or `ourss`) |
| `"agentic"` | The LLM decides which source(s) to query (code + prompt provided; modify freely) |

The LangChain RAG chain takes the retrieved context and the user question, then returns a grounded answer with source citations.

### Section 6 — Evaluation (LLM-as-a-Judge)

- Feed question + retrieved context + generated answer to a judge LLM
- Judge scores on: **faithfulness**, **relevance**, **completeness** (1–5 scale)
- Aggregate scores across a small eval set
- Display a results table

---

## Troubleshooting

**`ModuleNotFoundError`** — make sure your virtual environment is activated and you ran `pip install -r requirements.txt`.

**`AuthenticationError` from LLM** — check that `.env` exists in this folder and contains the correct key.

**MOSAIC index not found** — run Section 3 before Section 4's local retrieval cell.

**Windows path issues** — use forward slashes or raw strings (`r"path\to\file"`) in notebook cells.

---

## Tips for Participants

- You can swap the LLM model name in the config cell without changing anything else.
- The agentic mode prompt in Section 5 is intentionally minimal — improving it is a great experiment.
- Try different chunking strategies (size, overlap) in Section 3 and observe the effect on retrieval quality.
- Try your answers with different retrieval mode. 
- The judge prompt in Section 6 can be modified to add custom scoring dimensions.
