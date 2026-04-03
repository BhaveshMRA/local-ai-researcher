import requests
import time

SEMANTIC_SCHOLAR_URL = "https://api.semanticscholar.org/graph/v1/paper/search"

def fetch_semantic_scholar_papers(topic: str, max_results: int = 4) -> list[dict]:
    """Fetch papers from Semantic Scholar API."""
    try:
        time.sleep(2)  # avoid rate limiting
        params = {
            "query": topic,
            "limit": max_results,
            "fields": "title,authors,abstract,year,externalIds,url"
        }
        headers = {
            "User-Agent": "LocalAIResearcher/1.0",
        }
        response = requests.get(
            SEMANTIC_SCHOLAR_URL,
            params=params,
            headers=headers,
            timeout=15
        )

        if response.status_code == 429:
            time.sleep(5)  # wait and retry once
            response = requests.get(
                SEMANTIC_SCHOLAR_URL,
                params=params,
                headers=headers,
                timeout=15
            )

        response.raise_for_status()
        data = response.json()
        papers = []
        for p in data.get("data", []):
            if not p.get("abstract"):
                continue
            authors = [a.get("name", "") for a in p.get("authors", [])[:3]]
            year = str(p.get("year", "N/A"))
            arxiv_id = p.get("externalIds", {}).get("ArXiv", "")
            url = f"https://arxiv.org/abs/{arxiv_id}" if arxiv_id else p.get("url", "")
            papers.append({
                "title": p.get("title", ""),
                "authors": authors,
                "abstract": p.get("abstract", "")[:800],
                "url": url,
                "published": year,
                "categories": [],
                "source": "Semantic Scholar"
            })
        return papers
    except Exception as e:
        return [{"error": f"Semantic Scholar failed: {str(e)}"}]