# Geoparsing Hackathon with Jupyter Notebooks

## Goal

The hackathon will introduce participants to geoparsing through short explanations and hands-on Jupyter Notebook exercises.

The main workflow is:

```text
Raw text → Place-name extraction → Toponym resolution → Coordinates → Map visualization → Applications
```

## Format

The hackathon will use a simple pattern:

```text
Introduce each step → Run example code → Let participants try it → Discuss results
```

Jupyter Notebooks will be the main teaching material.  

## Main Topics

1. **Introduction to geoparsing**
   - What is geoparsing?
   - Toponym recognition
   - Toponym resolution

2. **Toponym recognition**
   - Use public NER tools to extract place names from text
   - Provide simple Python examples

3. **DLR geocoders**
   - Introduce DLR GeoNames-based geocoder
   - Introduce DLR Photon / OSM-based geocoder
   - Show how to test them in a browser
   - Show how to call them with Python APIs

4. **UniTopRank resolution method**
   - Introduce the idea of the method
   - Run the CPU-based method locally
   - Use the DLR GeoNames and Photon geocoders for candidate retrieval

5. **LLM- and RAG-based resolution service**
   - Introduce the basic idea
   - Show how DLR members can call the service
   - Compare it with standard geocoding and UniTopRank

6. **Map visualization**
   - Show how to visualize geolocated texts on an interactive map

7. **Show Applications**
   - Disaster response
   - Disease surveillance
   - Scientific paper search by location

8. **Hands-on challenge**
   - Participants use prepared datasets or their own data
   - They extract place names, resolve them, visualize them, and think about possible applications

## Prepared Data

Three example datasets will be provided:

1. Disaster-related tweets
2. Disease outbreak news articles
3. Scientific paper about hydrology

Participants may also bring their own text data.

## Material Structure

A simple structure is recommended:

```text
geoparsing-hackathon/
│
├── slides/
│   ├── opening.pdf
│   └── wrap_up.pdf
│
├── notebooks/
│   ├── 00_setup.ipynb
│   ├── 01_toponym_recognition.ipynb
│   ├── 02_geocoding_services.ipynb
│   ├── 03_unitoprank.ipynb
│   ├── 04_llm_rag_service.ipynb
│   ├── 05_map_visualization.ipynb
│   └── 06_hands_on_challenge.ipynb
│
├── data/
│   ├── disaster_tweets/
│   └── disease_news/
│   └── scientific_paper/
└── README.md
```

## Expected Outcomes

After the hackathon, participants should be able to:

- Understand the basic geoparsing workflow
- Extract place names from text
- Use DLR geocoding APIs
- Test UniTopRank and the LLM-RAG resolution service
- Visualize geolocated texts on maps
- Explore practical applications using prepared or personal datasets

## Feedback

At the end, feedback will be collected on:

- API usability
- Notebook clarity
- Code examples
- Service stability
- Geocoding accuracy
- Possible new features
- Potential use cases within DLR