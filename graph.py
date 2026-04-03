import time
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
    original_topic: str
    papers: List[dict]
    summaries: List[dict]
    gaps: str
    research_questions: str
    paper_draft: str
    logs: List[str]
    retry_count: int


# ── Retry Wrapper ─────────────────────────────────────────────
def with_retry(func, state, max_retries=2):
    """Wrap a node function with retry logic."""
    last_error = None
    for attempt in range(max_retries):
        try:
            return func(state)
        except Exception as e:
            last_error = e
            logs = state.get("logs", [])
            logs.append(f"⚠️ Attempt {attempt + 1} failed: {str(e)[:100]}. Retrying...")
            state = {**state, "logs": logs}
            time.sleep(2)

    # All retries failed — log and return state unchanged
    logs = state.get("logs", [])
    logs.append(f"❌ Node failed after {max_retries} attempts: {str(last_error)[:100]}")
    return {**state, "logs": logs}


# ── Core Node Logic ───────────────────────────────────────────

def _fetch_papers_node(state: ResearchState) -> ResearchState:
    topic = state["topic"]
    papers = fetch_papers(topic, max_results=8)
    logs = state.get("logs", [])
    logs.append(f"✅ Fetched {len(papers)} papers for: {topic}")
    return {**state, "papers": papers, "logs": logs}


def _broaden_query_node(state: ResearchState) -> ResearchState:
    logs = state.get("logs", [])
    retry_count = state.get("retry_count", 0)
    prompt = f"""The research topic "{state['topic']}" returned too few papers.
Generate a broader, more general version of this topic for an arXiv search.
Return ONLY the new search query, nothing else.
Original topic: {state['topic']}
Broader query:"""
    broader_topic = call_llm(prompt).strip().split("\n")[0]
    logs.append(f"🔄 Too few papers found — broadening query to: {broader_topic}")
    return {**state, "topic": broader_topic, "logs": logs, "retry_count": retry_count + 1}


def _summarize_papers_node(state: ResearchState) -> ResearchState:
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


def _identify_gaps_node(state: ResearchState) -> ResearchState:
    logs = state.get("logs", [])
    papers_text = format_papers_for_llm(state["papers"])
    prompt = gap_analysis_prompt(papers_text, state["topic"])
    gaps = call_llm(prompt, SYSTEM_PROMPT)
    logs.append("🔬 Research gaps identified")
    return {**state, "gaps": gaps, "logs": logs}


def _generate_questions_node(state: ResearchState) -> ResearchState:
    logs = state.get("logs", [])
    prompt = research_questions_prompt(state["gaps"], state["topic"])
    questions = call_llm(prompt, SYSTEM_PROMPT)
    logs.append("💡 Research questions generated")
    return {**state, "research_questions": questions, "logs": logs}


def _write_draft_node(state: ResearchState) -> ResearchState:
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


# ── Wrapped Node Functions (with retry) ───────────────────────

def fetch_papers_node(state: ResearchState) -> ResearchState:
    return with_retry(_fetch_papers_node, state)

def broaden_query_node(state: ResearchState) -> ResearchState:
    return with_retry(_broaden_query_node, state)

def summarize_papers_node(state: ResearchState) -> ResearchState:
    return with_retry(_summarize_papers_node, state)

def identify_gaps_node(state: ResearchState) -> ResearchState:
    return with_retry(_identify_gaps_node, state)

def generate_questions_node(state: ResearchState) -> ResearchState:
    return with_retry(_generate_questions_node, state)

def write_draft_node(state: ResearchState) -> ResearchState:
    return with_retry(_write_draft_node, state)


# ── Conditional Edge ──────────────────────────────────────────

def check_papers_count(state: ResearchState) -> str:
    """Decide: enough papers found or need to broaden query?"""
    papers = state.get("papers", [])
    retry_count = state.get("retry_count", 0)
    valid_papers = [p for p in papers if "error" not in p]
    if len(valid_papers) < 3 and retry_count < 2:
        return "broaden_query"
    else:
        return "summarize_papers"


# ── Full Graph ────────────────────────────────────────────────

def build_research_graph():
    graph = StateGraph(ResearchState)

    graph.add_node("fetch_papers", fetch_papers_node)
    graph.add_node("broaden_query", broaden_query_node)
    graph.add_node("summarize_papers", summarize_papers_node)
    graph.add_node("identify_gaps", identify_gaps_node)
    graph.add_node("generate_questions", generate_questions_node)
    graph.add_node("write_draft", write_draft_node)

    graph.set_entry_point("fetch_papers")
    graph.add_conditional_edges(
        "fetch_papers",
        check_papers_count,
        {
            "broaden_query": "broaden_query",
            "summarize_papers": "summarize_papers"
        }
    )
    graph.add_edge("broaden_query", "fetch_papers")
    graph.add_edge("summarize_papers", "identify_gaps")
    graph.add_edge("identify_gaps", "generate_questions")
    graph.add_edge("generate_questions", "write_draft")
    graph.add_edge("write_draft", END)

    return graph.compile()


# ── Phase 1 Graph ─────────────────────────────────────────────

def build_phase1_graph():
    graph = StateGraph(ResearchState)

    graph.add_node("fetch_papers", fetch_papers_node)
    graph.add_node("broaden_query", broaden_query_node)
    graph.add_node("summarize_papers", summarize_papers_node)
    graph.add_node("identify_gaps", identify_gaps_node)

    graph.set_entry_point("fetch_papers")
    graph.add_conditional_edges(
        "fetch_papers",
        check_papers_count,
        {
            "broaden_query": "broaden_query",
            "summarize_papers": "summarize_papers"
        }
    )
    graph.add_edge("broaden_query", "fetch_papers")
    graph.add_edge("summarize_papers", "identify_gaps")
    graph.add_edge("identify_gaps", END)

    return graph.compile()


# ── Phase 2 Graph ─────────────────────────────────────────────

def build_phase2_graph():
    graph = StateGraph(ResearchState)

    graph.add_node("generate_questions", generate_questions_node)
    graph.add_node("write_draft", write_draft_node)

    graph.set_entry_point("generate_questions")
    graph.add_edge("generate_questions", "write_draft")
    graph.add_edge("write_draft", END)

    return graph.compile()


# ── Compiled Instances ────────────────────────────────────────
research_graph = build_research_graph()
phase1_graph = build_phase1_graph()
phase2_graph = build_phase2_graph()