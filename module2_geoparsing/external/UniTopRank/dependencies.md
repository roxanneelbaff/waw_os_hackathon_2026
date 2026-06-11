# Dependencies

This file records direct dependencies and their purpose and source.
Core dependencies come from `requirements.txt`.
Optional NER backend dependencies come from `requirements-ner.txt`.
License information for both scopes is in `THIRD_PARTY_LICENSES.md`.
`Version constraint` is copied from requirements files; `Resolved version` is the installed/exported version from `THIRD_PARTY_LICENSES.md`.
Both requirements files are pinned to exact versions (`==`) for deterministic builds.

## Core direct dependencies (`requirements.txt`)

| Package | Version constraint | Resolved version | Purpose (one sentence) | Source (URL) |
|---|---|---|---|---|
| numpy | numpy==2.4.2 | 2.4.2 | Used in `thread_weight_rank_algorithm_3_beam.py` for vectorized distance and matrix calculations in ranking. | https://pypi.org/project/numpy/ |
| rapidfuzz | rapidfuzz==3.14.3 | 3.14.3 | Used in `thread_weight_rank_algorithm_3_beam.py` (`rapidfuzz.distance.Levenshtein`) for name-similarity scoring. | https://pypi.org/project/rapidfuzz/ |
| requests | requests==2.32.5 | 2.32.5 | Used in `unitoprank/candidate_retriever.py` to call GeoNames/Photon HTTP endpoints. | https://pypi.org/project/requests/ |

## Optional NER backend direct dependencies (`requirements-ner.txt`)

| Package | Version constraint | Resolved version | Purpose (one sentence) | Source (URL) |
|---|---|---|---|---|
| stanza | stanza==1.11.1 | 1.11.1 | Optional NER backend used by `StanzaToponymExtractor` when `ner_backend="stanza"`. | https://pypi.org/project/stanza/ |
| flair | flair==0.15.1 | 0.15.1 | Optional NER backend used by `FlairToponymExtractor` when `ner_backend="flair"`. | https://pypi.org/project/flair/ |
