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
    """Score all papers in one LLM call and sort by relevance."""
    valid_papers = [p for p in papers if "error" not in p]
    if not valid_papers:
        return papers

    # Build one prompt for all papers
    papers_list = ""
    for i, p in enumerate(valid_papers):
        papers_list += f"{i+1}. Title: {p['title']}\nAbstract: {p['abstract'][:200]}\n\n"

    prompt = f"""Score each paper's relevance to "{topic}" from 1-10.
Return ONLY a comma-separated list of integers in order, nothing else.
Example output: 8,6,9,4,7,5,8

Papers:
{papers_list}
Scores:"""

    try:
        response = call_llm_fn(prompt).strip()
        # Parse scores
        scores = [int(s.strip()) for s in response.split(",") if s.strip().isdigit()]
        scores = [max(1, min(10, s)) for s in scores]

        # Assign scores
        for i, paper in enumerate(valid_papers):
            paper["relevance_score"] = scores[i] if i < len(scores) else 5

    except:
        # If scoring fails, assign default scores
        for paper in valid_papers:
            paper["relevance_score"] = 5

    # Sort by score and return top 6
    valid_papers.sort(key=lambda x: x.get("relevance_score", 0), reverse=True)
    return valid_papers[:6]