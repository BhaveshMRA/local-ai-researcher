SYSTEM_PROMPT = """You are an expert academic researcher and scientific writer. 
You analyze research papers, identify gaps, and generate high-quality academic content.
Always be precise, analytical, and scholarly in your responses."""


def summarize_prompt(paper_title: str, abstract: str) -> str:
    return f"""Summarize this research paper in exactly 3 bullet points.
Each bullet should be one clear, concise sentence.
Focus on: what problem it solves, what method it uses, what result it achieves.

Paper Title: {paper_title}
Abstract: {abstract}

Output format:
- [Problem/Motivation]
- [Method/Approach]  
- [Result/Contribution]"""


def gap_analysis_prompt(papers_text: str, topic: str) -> str:
    return f"""You are analyzing {topic} research papers.

Here are the papers:
{papers_text}

Identify exactly 5 research gaps or open problems NOT addressed by these papers.
Be specific and grounded in what the papers actually say.

Output format:
Gap 1: [title] - [1 sentence explanation]
Gap 2: [title] - [1 sentence explanation]
Gap 3: [title] - [1 sentence explanation]
Gap 4: [title] - [1 sentence explanation]
Gap 5: [title] - [1 sentence explanation]"""


def research_questions_prompt(gaps: str, topic: str) -> str:
    return f"""Based on these research gaps in {topic}:
{gaps}

Generate 3 strong, specific research questions that could lead to publishable work.
Each question should be answerable through empirical study or system building.

Output format:
RQ1: [research question]
RQ2: [research question]  
RQ3: [research question]"""


def paper_draft_prompt(topic: str, papers_text: str, gaps: str, research_questions: str) -> str:
    return f"""Write a structured academic paper draft on: {topic}

Context from existing literature:
{papers_text[:1500]}

Identified gaps:
{gaps}

Research questions:
{research_questions}

Write the following sections:
1. TITLE: A compelling academic paper title
2. ABSTRACT: 150 word abstract
3. INTRODUCTION: 200 word introduction with motivation and contributions
4. RELATED WORK: 150 word summary of existing work and how this paper differs
5. PROPOSED METHODOLOGY: 200 word description of the approach to answer the research questions
6. EXPECTED CONTRIBUTIONS: 3 bullet points of expected contributions

Use formal academic writing style throughout."""

def hypothesis_prompt(research_questions: str, topic: str) -> str:
    return f"""Based on these research questions about {topic}:
{research_questions}

Generate 3 specific, testable hypotheses that could be empirically validated.
Each hypothesis should be falsifiable and directly address one of the research questions.

Output format:
H1: [hypothesis statement]
Expected outcome: [what you expect to find]

H2: [hypothesis statement]
Expected outcome: [what you expect to find]

H3: [hypothesis statement]
Expected outcome: [what you expect to find]"""