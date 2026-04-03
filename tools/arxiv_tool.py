import arxiv
import time

def fetch_papers(topic: str, max_results: int = 8) -> list[dict]:
    """Fetch papers from arXiv based on a research topic."""
    
    try:
        client = arxiv.Client()
        
        search = arxiv.Search(
            query=topic,
            max_results=max_results,
            sort_by=arxiv.SortCriterion.Relevance
        )
        
        papers = []
        for result in client.results(search):
            papers.append({
                "title": result.title,
                "authors": [str(a) for a in result.authors[:3]],
                "abstract": result.summary[:800],
                "url": result.entry_id,
                "published": result.published.strftime("%Y-%m-%d"),
                "categories": result.categories[:3],
                "source": "arXiv"
            })
            time.sleep(0.1)  # be polite to arXiv API
        
        return papers
    
    except Exception as e:
        return [{"error": f"Failed to fetch papers: {str(e)}"}]


def format_papers_for_llm(papers: list[dict]) -> str:
    """Format papers into a clean string for LLM context."""
    
    if not papers:
        return "No papers found."
    
    formatted = []
    for i, paper in enumerate(papers, 1):
        if "error" in paper:
            continue
        formatted.append(f"""
Paper {i}:
Title: {paper['title']}
Authors: {', '.join(paper['authors'])}
Published: {paper['published']}
Abstract: {paper['abstract']}
URL: {paper['url']}
---""")
    
    return "\n".join(formatted)

def score_and_sort_papers(papers: list[dict], topic: str, call_llm_fn) -> list[dict]:
    """Score each paper for relevance and sort by score."""
    scored = []
    for paper in papers:
        if "error" in paper:
            continue
        prompt = f"""Score this paper's relevance to the topic "{topic}" on a scale of 1-10.
Return ONLY a single integer between 1 and 10, nothing else.

Paper title: {paper['title']}
Abstract: {paper['abstract'][:300]}

Score:"""
        try:
            score_str = call_llm_fn(prompt).strip()
            score = int(''.join(filter(str.isdigit, score_str[:2])))
            score = max(1, min(10, score))
        except:
            score = 5
        paper["relevance_score"] = score
        scored.append(paper)

    # Sort by score descending, take top 6
    scored.sort(key=lambda x: x.get("relevance_score", 0), reverse=True)
    return scored[:6]