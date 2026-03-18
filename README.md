# 🔬 Local AI Researcher

An autonomous research pipeline powered by open-source LLMs that takes a research topic and executes the full academic research process — entirely using open-source models.

## 🚀 Live Demo
👉 [https://local-ai-researcher-09.streamlit.app](https://local-ai-researcher-09.streamlit.app)

## 🧠 What it does

Given a research topic, the pipeline autonomously:

1. 🔍 **Fetches papers** from arXiv API
2. 📄 **Summarizes** each paper using Llama 3.1 8B
3. 🔬 **Identifies research gaps** across the literature
4. 💡 **Generates research questions** grounded in the gaps
5. ✍️ **Writes a full paper draft** (title, abstract, intro, methodology, contributions)
6. 📥 **Exports** the report as a downloadable PDF

## 🛠️ Tech Stack

| Component | Technology |
|---|---|
| LLM | Llama 3.1 8B (via Groq API) |
| Paper Source | arXiv API |
| Framework | Python |
| UI | Streamlit |
| Deployment | Streamlit Cloud |

## 📁 Project Structure
```
local-ai-researcher/
├── app.py              ← Streamlit UI
├── agent.py            ← Pipeline orchestrator
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

## 👤 Author

**Bhavesh Maurya**  
MS Computer Science, Stevens Institute of Technology  
[GitHub](https://github.com/BhaveshMRA)