from tools.llm_tool import call_llm, test_connection
from graph import research_graph

class ResearchAgent:
    def __init__(self):
        self.result = {}

    def check_ollama(self) -> bool:
        return test_connection()

    def validate_topic(self, topic: str) -> dict:
        prompt = f"""You are a research topic validator. Analyze this input and respond ONLY in this exact format:

VALID: true or false
CORRECTED: the corrected topic if valid, or original if invalid
REASON: one sentence explanation

Input: "{topic}"

Rules:
- Valid means it is a real academic/scientific research topic
- Fix minor spelling errors only if the topic is valid
- Gibberish, food items, random text, offensive content = false
- Examples of INVALID: "butter chicken", "wadawknafkadwa", "asdfgh", "pizza"
- Examples of VALID: "autonomous AI agents", "deep learning for medical imaging", "natural language processing"

Response:"""

        response = call_llm(prompt).strip()

        try:
            lines = response.split("\n")
            valid = False
            corrected = topic
            reason = "Invalid research topic"

            for line in lines:
                if line.startswith("VALID:"):
                    valid = "true" in line.lower()
                elif line.startswith("CORRECTED:"):
                    corrected = line.replace("CORRECTED:", "").strip()
                elif line.startswith("REASON:"):
                    reason = line.replace("REASON:", "").strip()

            return {"valid": valid, "corrected": corrected, "reason": reason}
        except:
            return {"valid": False, "corrected": topic, "reason": "Could not validate topic"}

    def run(self, topic: str, callback=None) -> dict:
        """Run the full LangGraph pipeline."""

        initial_state = {
            "topic": topic,
            "original_topic": topic,
            "papers": [],
            "summaries": [],
            "gaps": "",
            "research_questions": "",
            "hypotheses": "",
            "paper_draft": "",
            "logs": [],
            "retry_count": 0
        }

        # Node callbacks with index
        node_order = [
            "fetch_papers",
            "summarize_papers", 
            "identify_gaps",
            "generate_questions",
            "write_draft"
        ]

        if callback:
            callback("🚀 Starting LangGraph research pipeline...", -1)

        # Stream node by node
        for i, node_name in enumerate(node_order):
            if callback:
                callback(f"⚙️ Running node: {node_name}...", i)

        self.result = research_graph.invoke(initial_state)

        if callback:
            for log in self.result.get("logs", []):
                callback(log, 5)

        return self.result
    def run_phase1(self, topic: str, callback=None) -> dict:
        """Run Phase 1: Fetch, Summarize, Identify Gaps."""
        initial_state = {
            "topic": topic,
            "original_topic": topic,
            "papers": [],
            "summaries": [],
            "gaps": "",
            "research_questions": "",
            "hypotheses": "",
            "paper_draft": "",
            "logs": [],
            "retry_count": 0
        }

        if callback:
            callback("🚀 Starting Phase 1: Fetching & Analyzing papers...", 0)

        from graph import phase1_graph
        result = phase1_graph.invoke(initial_state)

        if callback:
            for log in result.get("logs", []):
                callback(log, 3)

        return result

    def run_phase2(self, state: dict, callback=None) -> dict:
        """Run Phase 2: Generate Questions & Write Draft."""
        if callback:
            callback("🚀 Starting Phase 2: Generating questions & writing draft...", 3)

        from graph import phase2_graph
        result = phase2_graph.invoke(state)

        if callback:
            for log in result.get("logs", []):
                callback(log, 5)

        return result