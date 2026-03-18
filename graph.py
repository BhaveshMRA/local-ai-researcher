from typing import TypedDict, List
from langgraph.graph import StateGraph, END
from tools.arxiv_tool import fetch_papers, format_papers_for_llm
from tools.llm_tool import call_llm
from prompts import (
    SYSTEM_PROMPT,
    summarize_prompt,
    gap_analysis_prompt,
    research_questions_prompt,
    paper_draft_prompt
)

# ── State Definition ──────────────────────────────────────────
class ResearchState(TypedDict):
    topic: str
    papers: List[dict]
    summaries: List[dict]
    gaps: str
    research_questions: str
    paper_draft: str
    logs: List[str]

# ── Node Functions ────────────────────────────────────────────

def fetch_papers_node(state: ResearchState) -> ResearchState:
    """Node 1: Fetch papers from arXiv."""
    topic = state["topic"]
    papers = fetch_papers(topic, max_results=8)
    logs = state.get("logs", [])
    logs.append(f"✅ Fetched {len(papers)} papers for: {topic}")
    return {**state, "papers": papers, "logs": logs}


def summarize_papers_node(state: ResearchState) -> ResearchState:
    """Node 2: Summarize each paper."""
    papers = state["papers"]
    summaries = []
    logs = state.get("logs", [])

    for i, paper in enumerate(papers):
        if "error" in paper:
            continue
        prompt = summarize_prompt(paper["title"], paper["abstract"])
        summary = call_llm(prompt, SYSTEM_PROMPT)
        summaries.append({
            "title": paper["title"],
            "url": paper["url"],
            "published": paper["published"],
            "authors": paper["authors"],
            "summary": summary
        })
        logs.append(f"📄 Summarized paper {i+1}/{len(papers)}: {paper['title'][:50]}...")

    return {**state, "summaries": summaries, "logs": logs}


def identify_gaps_node(state: ResearchState) -> ResearchState:
    """Node 3: Identify research gaps."""
    logs = state.get("logs", [])
    papers_text = format_papers_for_llm(state["papers"])
    prompt = gap_analysis_prompt(papers_text, state["topic"])
    gaps = call_llm(prompt, SYSTEM_PROMPT)
    logs.append("🔬 Research gaps identified")
    return {**state, "gaps": gaps, "logs": logs}


def generate_questions_node(state: ResearchState) -> ResearchState:
    """Node 4: Generate research questions."""
    logs = state.get("logs", [])
    prompt = research_questions_prompt(state["gaps"], state["topic"])
    questions = call_llm(prompt, SYSTEM_PROMPT)
    logs.append("💡 Research questions generated")
    return {**state, "research_questions": questions, "logs": logs}


def write_draft_node(state: ResearchState) -> ResearchState:
    """Node 5: Write paper draft."""
    logs = state.get("logs", [])
    papers_text = format_papers_for_llm(state["papers"])
    prompt = paper_draft_prompt(
        state["topic"],
        papers_text,
        state["gaps"],
        state["research_questions"]
    )
    draft = call_llm(prompt, SYSTEM_PROMPT)
    logs.append("✍️ Paper draft complete!")
    return {**state, "paper_draft": draft, "logs": logs}


# ── Build Graph ───────────────────────────────────────────────

def build_research_graph():
    """Build and compile the LangGraph research pipeline."""
    
    graph = StateGraph(ResearchState)
    
    # Add nodes
    graph.add_node("fetch_papers", fetch_papers_node)
    graph.add_node("summarize_papers", summarize_papers_node)
    graph.add_node("identify_gaps", identify_gaps_node)
    graph.add_node("generate_questions", generate_questions_node)
    graph.add_node("write_draft", write_draft_node)
    
    # Add edges (sequential flow)
    graph.set_entry_point("fetch_papers")
    graph.add_edge("fetch_papers", "summarize_papers")
    graph.add_edge("summarize_papers", "identify_gaps")
    graph.add_edge("identify_gaps", "generate_questions")
    graph.add_edge("generate_questions", "write_draft")
    graph.add_edge("write_draft", END)
    
    return graph.compile()


# Compiled graph instance
research_graph = build_research_graph()