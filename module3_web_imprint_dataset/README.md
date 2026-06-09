# Module 3 — Web Imprint Dataset

## Goal:
Get familiar with the [German Imprints Dataset](https://openwebindex.eu/corpora/4057d6a0-0bd9-11f1-89ba-02a47ca5d9fd) — its structure, geospatial content, and thematic classification — and learn how to use enriched web data for your own geospatial research.

![OWI dataset overview](https://gitlab.dlr.de/opensearch/wawopensearch3_hackathon/-/raw/main/module3_web_imprint_dataset/images/OWI_overview.png)

## Overview:  
This module guides you through the end-to-end pipeline of working with web-extracted, geocoded, and thematically classified data from the OWS Legal Imprint Dataset. You'll learn how to:

* Learn how to use a data corpus from teh OWI platform
* Extract and filter web-based legal imprint data
* Learn how to use [DuckDB](https://duckdb.org/) to filter easy large data sets 
* Process and enrich text with geolocation and topic tags
* Perform geospatial analysis using Python
* Visualize results and explore research applications


## How: 

1. Data Filtering: Select relevant websites from the OWS dataset (e.g., by country, domain, or legal status) using [DuckDB](https://duckdb.org/).
2. Data Processing: Clean, enrich, and classify web text (e.g., extract themes like "privacy policy", "contact info").
3. Geospatial Analysis: Use coordinates to map websites, cluster locations, or analyze spatial distribution.
4. Example Output: Interactive maps, thematic heatmaps, or statistical insights.


## Data: 
The sample data sets used in this tutorial can be downloaded via this link: 
* Sample of the OWS [German Imprints Dataset](https://openwebindex.eu/corpora/4057d6a0-0bd9-11f1-89ba-02a47ca5d9fd)(with coordinates and thematic labels)
* Example Jupyter notebook: WAW_OpenSearch_LegalImprint.ipynb
* Pre-configured environment setup
* Spatial administrative vector layers from Germany


The Imprint Data set includes:
* Website URL
* Legal imprint text
* Geolocation (latitude/longitude)
* Thematic classification (e.g., "privacy", "contact", "terms")


---
## System Overview

<img src="https://gitlab.dlr.de/opensearch/wawopensearch3_hackathon/-/raw/main/module3_web_imprint_dataset/images/overview.png" alt="OWI dataset overview" width="700">

---
## Prerequisites
| Requirement | Version |
|---|---|
| Python | 3.10 or 3.11 recommended |
| pip | latest |
| Jupyter | included via requirements |
| Git | For cloning the repo |
---
## Environment Setup
### 1. Get the repository
#### 1.1 Clone the repository (only availalbe if your have access to DLR Gitlab)
Navigate to the directory of your choise to download the repository
```bash
git clone https://gitlab.dlr.de/opensearch/wawopensearch3_hackathon.git #<repo-url>
#Navigate to modlue 3 folder
cd wawopensearch3_hackathon/module3_web_imprint_dataset
```
Please download the folder with the sample data from the following link
Link: https://gigamove.rwth-aachen.de/de/download/74c05f2c031992a01e553431e8dbca1c
The downloaded data_folder has to be saved and unzipped within the repository folder structure 

#### 1.2 Dowlonad zip File of repository form gigamove
Follow the link to download the zipped repository file from Giga Move, within this folder structure the sample data folder is already integrated, no need of an additional download
Navigate to your preferred directory to unpack the folder
Link: 
The downloaded data_folder has to be saved within the repository folder structure

### 2. Create a environment
**Linux / macOS**
```bash
mamba create -n waw_os_legal_imprint python=3.10
```


**Windows (Command Prompt)**
```cmd
mamba create -n waw_os_legal_imprint python=3.10
```

**Windows (PowerShell)**
```powershell
mamba create -n waw_os_legal_imprint python=3.10
```

> If you see a PowerShell execution-policy error, run:  
> `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser`

### 3. Activate envorinment

mamba activate waw_os_legal_imprint

### 4. Install dependencies

```bash
pip install -r requirements.txt
```
#other option: Install packages
mamba install -c conda-forge jupyter pandas geopandas duckdb mapclassify matplotlib

### 5. Launch Jupyter

```bash
jupyter notebook WAW_OpenSearch_LegalImprint.ipynb
```

#If you wish to install the packages in jupyter use this command
!pip install pandas geopandas duckdb mapclassify matplotlib

# Once you are done working in the environemnt close your environment
mamba deactivate

---

## Notebook Structure

The notebook `WAW_OpenSearch_LegalImprint.ipynb` is divided into the following sections:

#### Section 0 — Setup & Sanity Check

#### Section 1 — Data Source Information 

#### Section 2 — Data Extraction Using DuckDB

#### Section 3 — Data Filtering

#### Section 4 — Geopsatial Analysis

#### Section 5 — DIY


### Example Use Cases

* Map the geographic spread of websites with "privacy policies"
* Compare legal imprint presence across EU vs. non-EU countries
* Identify clusters of websites with similar thematic content
* Study digital governance patterns in urban vs. rural areas

