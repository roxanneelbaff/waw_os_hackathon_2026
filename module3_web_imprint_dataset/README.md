

# Module 1 — Web Imprint Dataset

##Goal:
We want you to get familiar with the Legal Imprint Dataset its content and explore the potential of how this thematic classified and geolocated dataset can be used for your research question. 

##Overview:  
How to use from the web extracted and enriched data for your own (geopspatial) research analysis

##How: 
Participants can learn about the pipeline to extract enriched data fro web text and learn how to implement geocoded web text information in their analysis

##Data: 
A sample of the OWS Imprint Dataset with coordinates and thematic information of websites is provided and a example use case analysis

---
## System Overview
```
Data Filtering
        │
        ▼
Data Processing
        │
        ▼
Geospatial Analysis
        │
        ▼
Example output
    
```
---
## Prerequisites
| Requirement | Version |
|---|---|
| Python | 3.10 or 3.11 recommended |
| pip | latest |
| Jupyter | included via requirements |
---
## Environment Setup
### 1. Clone the repository
```bash
git clone <repo-url>
cd wawopensearch3_hackathon/module3_web_imprint_dataset
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

### 4. Launch Jupyter

```bash
jupyter notebook module3_notebook.ipynb
```

### 6. Sanity check

The first notebook cell verifies your Python version, installed packages, and makes a test call to the LLM. You should see a short response before moving on.

---

## Notebook Structure

The notebook `module3_notebook.ipynb` is divided into the following sections:

### Section 0 — Setup & Sanity Check

### Section 1 — Data Acquisition

### Section 2 — Data processing

### Section 3 — Indexing

### Section 4 — Retrieval

### Section 5 — 

## File Structure

## Troubleshooting


## Tips for Participants

- You can swap the LLM model name in the config cell without changing anything else.
- The agentic mode prompt in Section 5 is intentionally minimal — improving it is a great experiment.
- Try different chunking strategies (size, overlap) in Section 3 and observe the effect on retrieval quality.
- The judge prompt in Section 6 can be modified to add custom scoring dimensions.

Get Started -- Terms of Use -- Feedback
