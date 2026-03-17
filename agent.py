from tools.arxiv_tool import fetch_papers, format_papers_for_llm
from tools.llm_tool import call_llm, test_connection
from prompts import (
    SYSTEM_PROMPT,
    summarize_prompt,
    gap_analysis_prompt,
    research_questions_prompt,
    paper_draft_prompt
)


class ResearchAgent:
    def __init__(self):
        self.papers = []
        self.summaries = []
        self.gaps = ""
        self.research_questions = ""
        self.paper_draft = ""

    def check_ollama(self) -> bool:
        """Check if Ollama is running with the model loaded."""
        return test_connection()
    
    def validate_topic(self, topic: str) -> dict:
        """Validate if the topic is a legitimate research topic."""
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

            return {
                "valid": valid,
                "corrected": corrected,
                "reason": reason
            }
        except:
            return {
                "valid": False,
                "corrected": topic,
                "reason": "Could not validate topic"
            }

    def step1_fetch_papers(self, topic: str, callback=None) -> list[dict]:
        """Step 1: Fetch papers from arXiv."""
        if callback:
            callback("🔍 Searching arXiv for papers on: " + topic)
        
        self.papers = fetch_papers(topic, max_results=8)
        
        if callback:
            callback(f"✅ Found {len(self.papers)} papers")
        
        return self.papers

    def step2_summarize_papers(self, callback=None) -> list[str]:
        """Step 2: Summarize each paper using LLM."""
        self.summaries = []
        
        for i, paper in enumerate(self.papers):
            if "error" in paper:
                continue
            
            if callback:
                callback(f"📄 Summarizing paper {i+1}/{len(self.papers)}: {paper['title'][:60]}...")
            
            prompt = summarize_prompt(paper["title"], paper["abstract"])
            summary = call_llm(prompt, SYSTEM_PROMPT)
            
            self.summaries.append({
                "title": paper["title"],
                "url": paper["url"],
                "published": paper["published"],
                "authors": paper["authors"],
                "summary": summary
            })
        
        if callback:
            callback(f"✅ Summarized {len(self.summaries)} papers")
        
        return self.summaries

    def step3_identify_gaps(self, topic: str, callback=None) -> str:
        """Step 3: Identify research gaps across all papers."""
        if callback:
            callback("🔬 Analyzing research gaps...")
        
        papers_text = format_papers_for_llm(self.papers)
        prompt = gap_analysis_prompt(papers_text, topic)
        self.gaps = call_llm(prompt, SYSTEM_PROMPT)
        
        if callback:
            callback("✅ Research gaps identified")
        
        return self.gaps

    def step4_generate_questions(self, topic: str, callback=None) -> str:
        """Step 4: Generate research questions from gaps."""
        if callback:
            callback("💡 Generating research questions...")
        
        prompt = research_questions_prompt(self.gaps, topic)
        self.research_questions = call_llm(prompt, SYSTEM_PROMPT)
        
        if callback:
            callback("✅ Research questions generated")
        
        return self.research_questions

    def step5_write_draft(self, topic: str, callback=None) -> str:
        """Step 5: Write a full academic paper draft."""
        if callback:
            callback("✍️ Writing academic paper draft...")
        
        papers_text = format_papers_for_llm(self.papers)
        prompt = paper_draft_prompt(
            topic,
            papers_text,
            self.gaps,
            self.research_questions
        )
        self.paper_draft = call_llm(prompt, SYSTEM_PROMPT)
        
        if callback:
            callback("✅ Paper draft complete!")
        
        return self.paper_draft

    def run(self, topic: str, callback=None) -> dict:
        """Run the full pipeline end to end."""
        # Clean topic first
        # Validate topic first
        if callback:
            callback("🔎 Validating research topic...")
        validation = self.validate_topic(topic)
        
        if not validation["valid"]:
            if callback:
                callback(f"❌ Invalid topic: {validation['reason']}")
            return {"error": validation["reason"]}
        
        topic = validation["corrected"]
        if callback:
            callback(f"✅ Topic confirmed: {topic}")

        # Step 1
        papers = self.step1_fetch_papers(topic, callback)
        
        # Step 2
        summaries = self.step2_summarize_papers(callback)
        
        # Step 3
        gaps = self.step3_identify_gaps(topic, callback)
        
        # Step 4
        questions = self.step4_generate_questions(topic, callback)
        
        # Step 5
        draft = self.step5_write_draft(topic, callback)
        
        return {
            "topic": topic,
            "papers": papers,
            "summaries": summaries,
            "gaps": gaps,
            "research_questions": questions,
            "paper_draft": draft
        }