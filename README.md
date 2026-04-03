# 🔬 Local AI Researcher

A fully autonomous research pipeline agent that takes a research topic and executes the complete academic research process — built with LangGraph, open-source LLMs, and a human-in-the-loop checkpoint.

## 🚀 Live Demo
👉 [https://local-ai-researcher-09.streamlit.app](https://local-ai-researcher-09.streamlit.app)

## 🧠 What it does

Given a research topic, the autonomous LangGraph agent:

1. 🔎 **Validates** the topic — rejects gibberish or non-academic input
2. 🔍 **Fetches papers** from arXiv API
3. 🔄 **Conditionally broadens** search query if fewer than 3 papers found
4. 📄 **Summarizes** each paper using Llama 3.1 8B
5. 🔬 **Identifies research gaps** across the literature
6. 🧠 **Pauses for human review** — user can edit or re-analyze gaps
7. 💡 **Generates research questions** grounded in approved gaps
8. ✍️ **Writes a full paper draft** (title, abstract, intro, methodology, contributions)
9. 📥 **Exports** the report as a formatted downloadable PDF

## 🏗️ Architecture

Built with **LangGraph** — each step is a graph node with a shared typed `ResearchState` flowing through the pipeline:
```
Phase 1:
[Fetch Papers] → Check: enough papers?
                      ↓ NO (<3 papers)
                [Broaden Query] → [Fetch Papers again]
                      ↓ YES
         [Summarize Papers] → [Identify Gaps] → ⏸️ HUMAN CHECKPOINT

Phase 2 (after human approval):
[Generate Questions] → [Write Draft] → END
```

### Key Agent Capabilities
- ✅ **Conditional branching** — auto-broadens query if fewer than 3 papers found
- ✅ **Human-in-the-loop checkpoint** — user reviews/edits gaps before draft generation
- ✅ **Stateful execution** — typed `ResearchState` shared across all nodes
- ✅ **Topic validation** — LLM validates and corrects input before pipeline runs
- ✅ **Real-time graph visualization** — pipeline diagram updates live as nodes execute
- ✅ **Retry logic** — maximum 2 retries on query broadening to avoid infinite loops

## 🛠️ Tech Stack

| Component | Technology |
|---|---|
| Agent Framework | LangGraph |
| LLM | Llama 3.1 8B (via Groq API) |
| Paper Source | arXiv API |
| Topic Validation | LLM-based validator |
| UI | Streamlit |
| PDF Export | fpdf2 |
| Deployment | Streamlit Cloud |

## 📁 Project Structure
```
local-ai-researcher/
├── app.py              ← Streamlit UI + live graph + human-in-the-loop
├── agent.py            ← LangGraph pipeline orchestrator
├── graph.py            ← LangGraph state machine + conditional branching
├── prompts.py          ← LLM prompt templates
├── tools/
│   ├── arxiv_tool.py   ← arXiv paper fetcher
│   └── llm_tool.py     ← Groq LLM wrapper
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

# Add your Groq API key
echo 'GROQ_API_KEY="your_key_here"' > .env

# Run the app
streamlit run app.py
```

## 🔑 Environment Variables

Create a `.env` file:
```
GROQ_API_KEY=your_groq_api_key
```

Get a free Groq API key at [console.groq.com](https://console.groq.com)

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