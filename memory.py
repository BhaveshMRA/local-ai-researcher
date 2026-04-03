import json
import os
from datetime import datetime

MEMORY_FILE = "research_memory.json"

def load_memory() -> list:
    """Load all saved research sessions."""
    if not os.path.exists(MEMORY_FILE):
        return []
    try:
        with open(MEMORY_FILE, "r") as f:
            return json.load(f)
    except:
        return []


def save_session(topic: str, papers: list, gaps: str, 
                 questions: str, hypotheses: str, draft: str) -> dict:
    """Save a research session to memory."""
    sessions = load_memory()
    
    session = {
        "id": datetime.now().strftime("%Y%m%d_%H%M%S"),
        "topic": topic,
        "date": datetime.now().strftime("%B %d, %Y at %I:%M %p"),
        "papers_count": len(papers),
        "paper_titles": [p.get("title", "")[:60] for p in papers[:3] if "error" not in p],
        "gaps": gaps,
        "questions": questions,
        "hypotheses": hypotheses,
        "draft": draft,
        "papers": papers
    }
    
    sessions.insert(0, session)  # newest first
    sessions = sessions[:10]  # keep last 10 sessions
    
    with open(MEMORY_FILE, "w") as f:
        json.dump(sessions, f, indent=2)
    
    return session


def delete_session(session_id: str) -> bool:
    """Delete a specific session from memory."""
    sessions = load_memory()
    sessions = [s for s in sessions if s.get("id") != session_id]
    with open(MEMORY_FILE, "w") as f:
        json.dump(sessions, f, indent=2)
    return True


def clear_all_sessions():
    """Clear all saved sessions."""
    with open(MEMORY_FILE, "w") as f:
        json.dump([], f)