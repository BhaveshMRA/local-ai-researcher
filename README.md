# 🔬 Local AI Researcher

An autonomous research pipeline powered by open-source LLMs that takes a research topic and executes the full academic research process — entirely using open-source models and a LangGraph agent framework.

## 🚀 Live Demo
👉 [https://local-ai-researcher-09.streamlit.app](https://local-ai-researcher-09.streamlit.app)

## 🧠 What it does

Given a research topic, the autonomous agent:

1. 🔍 **Fetches papers** from arXiv API
2. 📄 **Summarizes** each paper using Llama 3.1 8B
3. 🔬 **Identifies research gaps** across the literature
4. 💡 **Generates research questions** grounded in the gaps
5. ✍️ **Writes a full paper draft** (title, abstract, intro, methodology, contributions)
6. 📥 **Exports** the report as a downloadable PDF

## 🏗️ Architecture

Built with **LangGraph** — each step is a graph node with shared typed state flowing through the pipeline:
```
[Fetch Papers] → [Summarize Papers] → [Identify Gaps] → [Generate Questions] → [Write Draft] → END
```

Each node updates a shared `ResearchState` object, enabling:
- ✅ Stateful execution across nodes
- ✅ Conditional branching (extensible)
- ✅ Human-in-the-loop checkpoints (extensible)
- ✅ Visual pipeline monitoring in real-time

## 🛠️ Tech Stack

| Component | Technology |
|---|---|
| Agent Framework | LangGraph |
| LLM | Llama 3.1 8B (via Groq API) |
| Paper Source | arXiv API |
| Topic Validation | LLM-based validator |
| UI | Streamlit |
| Deployment | Streamlit Cloud |

## 📁 Project Structure
```
local-ai-researcher/
├── app.py              ← Streamlit UI + live graph visualization
├── agent.py            ← LangGraph pipeline orchestrator
├── graph.py            ← LangGraph state machine definition
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

## 💡 Key Features

- **Topic Validation** — LLM validates input before running, rejects gibberish/non-academic topics
- **Real-time Graph** — Pipeline architecture diagram updates live as each node executes
- **PDF Export** — Download the full research report as a formatted PDF
- **100% Open Source** — Uses Llama 3.1 8B, no proprietary models required

## 👤 Author

**Bhavesh Maurya**
MS Computer Science, Stevens Institute of Technology
[GitHub](https://github.com/BhaveshMRA) | bmaurya@stevens.edu