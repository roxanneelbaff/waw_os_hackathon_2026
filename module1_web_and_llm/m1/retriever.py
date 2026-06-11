# ── 4.1  retrieve_local — Local MOSAIC index 
from m1.utils.mosaic_tools import retrieve, display_results

import os
import time

import httpx
from langchain_community.document_loaders import WebBaseLoader
from langchain_community.document_transformers import Html2TextTransformer


OURSS_API_URL = os.getenv("OURSS_API_URL", "https://ourrs.eu/api/public/v1/search")
OURRS_API_KEY = os.getenv("OURRS_API_KEY", "")



def retrieve_local(queries, top: int = 10):
    return retrieve(queries, top=top, base_url= "http://localhost:8008/search") 


def retrieve_remote(queries, top: int = 10):
    return retrieve(queries, top=top, base_url= "https://mosaic.ows.eu/service/api/search", index_name="science") 


def search_ourrs_api(queries: list, top: int = 10) -> list:
    results = []
    failed = []

    for q in queries:
        for attempt in range(3):
            try:
                r = httpx.post(
                    OURSS_API_URL,
                    headers={"Authorization": f"Bearer {OURRS_API_KEY}"},
                    json={"query": q, "limit": top, "languages": ["en"]},
                    timeout=20,
                )
                r.raise_for_status()
                results.append(r.json())
                break
            except (httpx.HTTPStatusError, httpx.TimeoutException, httpx.ConnectError) as e:
                if attempt < 2:
                    time.sleep(1)
        else:
            failed.append(q)

    if not results:
        raise RuntimeError(f"OURRS failed for all queries: {failed}")

    return results


def retrieve_ourss(queries, top: int = 10):
    if isinstance(queries, str):
        queries = [queries]

    records = search_ourrs_api(queries, top)

    urls = {
        hit.get("url")
        for concept in records
        for hit in concept.get("data", {}).get("hits", [])
    }

    loader = WebBaseLoader(
        web_paths=list(urls),
        requests_per_second=10,
        continue_on_failure=True,
    )

    raw_context_web = [
        doc for doc in loader.lazy_load() if doc.page_content.strip()
    ]

    transformer = Html2TextTransformer()
    documents_web = transformer.transform_documents(raw_context_web)

    return [
        {
            "id": i,
            "text": doc.page_content,
            "url": doc.metadata.get("source", ""),
            "title": doc.metadata.get("title", ""),
        }
        for i, doc in enumerate(documents_web)
    ]


