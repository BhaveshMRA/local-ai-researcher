# 🔬 Local AI Researcher

A fully autonomous research pipeline agent that takes a research topic and executes the complete academic research process — built with LangGraph, open-source LLMs, human-in-the-loop checkpoints, and persistent memory.

## 🚀 Live Demo
👉 [https://local-ai-researcher-09.streamlit.app](https://local-ai-researcher-09.streamlit.app)

## 🧠 What it does

Given a research topic, the autonomous LangGraph agent:

1. 🔎 **Validates** the topic — rejects gibberish or non-academic input
2. 🔍 **Fetches papers** from arXiv + Semantic Scholar APIs
3. ⭐ **Scores & ranks** papers by relevance (1-10) before summarizing
4. 🔄 **Conditionally broadens** search query if fewer than 3 papers found
5. 📄 **Summarizes** each paper using Llama 3.1 8B
6. 🔬 **Identifies research gaps** across the literature
7. 🧠 **Pauses for human review** — user can edit or re-analyze gaps
8. 💡 **Generates research questions** grounded in approved gaps
9. 🧪 **Generates testable hypotheses** for each research question
10. ✍️ **Writes a full paper draft** (title, abstract, intro, methodology, contributions)
11. 📋 **Formats APA citations** for all papers analyzed
12. 📥 **Exports** the full report as a formatted downloadable PDF
13. 💾 **Saves sessions** — revisit past research from the sidebar

## 🏗️ Architecture

Built with **LangGraph** — each step is a graph node with a shared typed `ResearchState` flowing through the pipeline:
```
Phase 1:
[Fetch Papers] → Score & Rank by Relevance → Check: enough papers?
                                                    ↓ NO (<3 papers)
                                             [Broaden Query] → [Fetch Again]
                                                    ↓ YES
                              [Summarize Papers] → [Identify Gaps] → ⏸️ HUMAN CHECKPOINT

Phase 2 (after human approval):
[Generate Questions] → [Generate Hypotheses] → [Write Draft] → END
```

### Key Agent Capabilities
- ✅ **Conditional branching** — auto-broadens query if fewer than 3 papers found
- ✅ **Human-in-the-loop checkpoint** — user reviews/edits gaps before draft generation
- ✅ **Stateful execution** — typed `ResearchState` shared across all nodes
- ✅ **Topic validation** — LLM validates and corrects input before pipeline runs
- ✅ **Real-time graph visualization** — pipeline diagram updates live as nodes execute
- ✅ **Retry logic** — all nodes wrapped with automatic retry (max 2 attempts)
- ✅ **Relevance scoring** — papers scored 1-10 and sorted before summarization
- ✅ **Hypothesis generation** — testable hypotheses generated from research questions
- ✅ **APA citation formatter** — export citations as .txt file
- ✅ **Session memory** — save, load, and delete past research sessions

## 🛠️ Tech Stack

| Component | Technology |
|---|---|
| Agent Framework | LangGraph |
| LLM | Llama 3.1 8B (via Groq API) |
| Paper Sources | arXiv API + Semantic Scholar API |
| Relevance Scoring | LLM-based 1-10 scorer |
| Topic Validation | LLM-based validator |
| Session Memory | Local JSON storage |
| UI | Streamlit |
| PDF Export | fpdf2 |
| Deployment | Streamlit Cloud |

## 📁 Project Structure
```
local-ai-researcher/
├── app.py                       ← Streamlit UI + live graph + human-in-the-loop
├── agent.py                     ← LangGraph pipeline orchestrator
├── graph.py                     ← LangGraph state machine + conditional branching
├── prompts.py                   ← LLM prompt templates
├── memory.py                    ← Session memory (save/load/delete)
├── tools/
│   ├── arxiv_tool.py            ← arXiv paper fetcher + relevance scorer
│   ├── semantic_scholar_tool.py ← Semantic Scholar paper fetcher
│   └── llm_tool.py              ← Groq LLM wrapper
└── requirements.txt
```

## ⚙️ Run Locally
```bash
# Clone the repo
git clone https://github.com/BhaveshMRA/local-ai-researcher.git
cd local-ai-researcher

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Add your API keys
echo 'GROQ_API_KEY="your_key_here"' > .env
echo 'SEMANTIC_SCHOLAR_API_KEY="your_key_here"' >> .env

# Run the app
streamlit run app.py
```

## 🔑 Environment Variables

Create a `.env` file:
```
GROQ_API_KEY=your_groq_api_key
SEMANTIC_SCHOLAR_API_KEY=your_semantic_scholar_key  # optional
```

- Free Groq API key: [console.groq.com](https://console.groq.com)
- Free Semantic Scholar key: [semanticscholar.org/product/api](https://www.semanticscholar.org/product/api)

## 💡 Example Topics
```
autonomous AI agents using large language models
federated learning in healthcare
graph neural networks for drug discovery
transformer models for time series forecasting
vision language models for medical imaging
```

## 👤 Author

**Bhavesh Maurya**  
MS Computer Science, Stevens Institute of Technology  
[GitHub](https://github.com/BhaveshMRA) | bmaurya@stevens.edu