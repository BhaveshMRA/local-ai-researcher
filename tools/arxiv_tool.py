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
                "categories": result.categories[:3]
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