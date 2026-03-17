import streamlit as st
import time
from agent import ResearchAgent
from fpdf import FPDF
import unicodedata

# ── Page config ──────────────────────────────────────────────
st.set_page_config(
    page_title="Local AI Researcher",
    page_icon="🔬",
    layout="wide"
)

# ── Header ───────────────────────────────────────────────────
st.title("🔬 Local AI Researcher")
st.markdown("*Autonomous research pipeline powered by Llama 3.1 running 100% locally*")
st.divider()

# ── Sidebar ──────────────────────────────────────────────────
with st.sidebar:
    st.header("⚙️ Configuration")
    
    agent = ResearchAgent()
    
    if agent.check_ollama():
        st.success("✅ Ollama Connected")
        st.info("Model: Llama 3.1 8B via Groq")
    else:
        st.error("❌ Ollama not running")
        st.code("ollama serve", language="bash")
    
    st.divider()
    st.markdown("### 📋 Pipeline Steps")
    st.markdown("""
    1. 🔍 Fetch papers from arXiv
    2. 📄 Summarize each paper
    3. 🔬 Identify research gaps
    4. 💡 Generate research questions
    5. ✍️ Write paper draft
    """)
    
    st.divider()
    
    st.markdown("*Project by Bhavesh Maurya*")

# ── Main Input ───────────────────────────────────────────────
col1, col2 = st.columns([3, 1])

with col1:
    topic = st.text_input(
        "🎯 Research Topic",
        placeholder="e.g. autonomous AI agents using large language models",
        help="Enter a research topic to analyze"
    )

with col2:
    st.markdown("<br>", unsafe_allow_html=True)
    run_button = st.button("🚀 Run Pipeline", type="primary", use_container_width=True)

# ── Pipeline Execution ───────────────────────────────────────
if run_button and topic:
    
    if not agent.check_ollama():
        st.error("❌ Ollama is not running! Open terminal and run: `ollama serve`")
        st.stop()
    
    # Log container
    st.markdown("### 📡 Pipeline Progress")
    log_container = st.empty()
    logs = []
    
    def update_log(message: str):
        logs.append(message)
        log_container.markdown("\n\n".join(logs))
    
    # Progress bar
    # Progress bar
    progress = st.progress(0, text="Starting pipeline...")

    # ── Validate topic first ──
    update_log("🔎 Validating research topic...")
    validation = agent.validate_topic(topic)
    
    if not validation["valid"]:
        st.error(f"❌ **Invalid research topic:** {validation['reason']}")
        st.warning("💡 Please enter a valid academic research topic (e.g. 'autonomous AI agents using LLMs')")
        st.stop()
    
    topic = validation["corrected"]
    update_log(f"✅ Topic confirmed: **{topic}**")
    st.info(f"🎯 Running pipeline for: **{topic}**")

    # ── Step 1: Fetch Papers ──
    progress.progress(10, text="Step 1/5 — Fetching papers from arXiv...")
    papers = agent.step1_fetch_papers(topic, callback=update_log)
    progress.progress(20, text="Step 1/5 — Done ✅")
    
    # Show papers found
    if papers:
        with st.expander(f"📚 {len(papers)} Papers Found", expanded=False):
            for i, p in enumerate(papers, 1):
                if "error" not in p:
                    st.markdown(f"**{i}. [{p['title']}]({p['url']})**")
                    st.caption(f"👥 {', '.join(p['authors'])} | 📅 {p['published']}")
                    st.markdown(f"> {p['abstract'][:200]}...")
                    st.divider()
    
    # ── Step 2: Summarize ──
    progress.progress(30, text="Step 2/5 — Summarizing papers with LLM...")
    summaries = agent.step2_summarize_papers(callback=update_log)
    progress.progress(50, text="Step 2/5 — Done ✅")
    
    with st.expander("📝 Paper Summaries", expanded=False):
        for s in summaries:
            st.markdown(f"**{s['title']}**")
            st.caption(f"👥 {', '.join(s['authors'])} | 📅 {s['published']} | 🔗 [Link]({s['url']})")
            st.markdown(s["summary"])
            st.divider()
    
    # ── Step 3: Gaps ──
    progress.progress(60, text="Step 3/5 — Identifying research gaps...")
    gaps = agent.step3_identify_gaps(topic, callback=update_log)
    progress.progress(70, text="Step 3/5 — Done ✅")
    
    with st.expander("🔬 Research Gaps Identified", expanded=True):
        st.markdown(gaps)
    
    # ── Step 4: Research Questions ──
    progress.progress(80, text="Step 4/5 — Generating research questions...")
    questions = agent.step4_generate_questions(topic, callback=update_log)
    progress.progress(90, text="Step 4/5 — Done ✅")
    
    with st.expander("💡 Research Questions", expanded=True):
        st.markdown(questions)
    
    # ── Step 5: Paper Draft ──
    progress.progress(95, text="Step 5/5 — Writing paper draft...")
    draft = agent.step5_write_draft(topic, callback=update_log)
    progress.progress(100, text="✅ Pipeline Complete!")
    
    st.success("🎉 Research pipeline completed successfully!")
    
    # ── Paper Draft Display ──
    st.markdown("---")
    st.markdown("## 📄 Generated Paper Draft")
    st.markdown(draft)
    
    # ── PDF Export ──
    st.markdown("---")
    st.markdown("### 📥 Export")

    def clean_text(text):
        return unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode("ascii")

    def generate_pdf(topic, summaries, gaps, questions, draft):
        pdf = FPDF()
        pdf.add_page()
        pdf.set_auto_page_break(auto=True, margin=15)
        pdf.set_font("Helvetica", "B", 16)
        pdf.cell(0, 10, clean_text(f"Research Report: {topic}"), ln=True)
        pdf.set_font("Helvetica", "", 10)
        pdf.cell(0, 8, "Generated by Local AI Researcher |  Project by Bhavesh Maurya", ln=True)
        pdf.ln(5)

        pdf.set_font("Helvetica", "B", 13)
        pdf.cell(0, 8, "Research Gaps", ln=True)
        pdf.set_font("Helvetica", "", 10)
        pdf.multi_cell(0, 6, clean_text(gaps))
        pdf.ln(4)

        pdf.set_font("Helvetica", "B", 13)
        pdf.cell(0, 8, "Research Questions", ln=True)
        pdf.set_font("Helvetica", "", 10)
        pdf.multi_cell(0, 6, clean_text(questions))
        pdf.ln(4)

        pdf.set_font("Helvetica", "B", 13)
        pdf.cell(0, 8, "Paper Draft", ln=True)
        pdf.set_font("Helvetica", "", 10)
        pdf.multi_cell(0, 6, clean_text(draft))

        return bytes(pdf.output())

    pdf_bytes = generate_pdf(topic, summaries, gaps, questions, draft)
    st.download_button(
        label="📄 Download Full Report as PDF",
        data=pdf_bytes,
        file_name=f"research_report_{topic[:30].replace(' ', '_')}.pdf",
        mime="application/pdf"
    )

elif run_button and not topic:
    st.warning("⚠️ Please enter a research topic first!")

# ── Footer ───────────────────────────────────────────────────
st.markdown("---")
st.caption("🔬 Local AI Researcher | Powered by Llama 3.1 8B (Groq) + arXiv API | 100% Open Source")