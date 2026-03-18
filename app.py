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

def show_graph(active_node: int = -1):
    nodes = [
        "🔍 Fetch Papers",
        "📄 Summarize Papers", 
        "🔬 Identify Gaps",
        "💡 Generate Questions",
        "✍️ Write Draft",
        "🏁 END"
    ]
    
    boxes = ""
    for i, label in enumerate(nodes):
        if i < active_node:
            border = "#238636"
            bg = "#0d1f0d"
            color = "#3fb950"
        elif i == active_node:
            border = "#f0c000"
            bg = "#2d2500"
            color = "#f0c000"
        else:
            border = "#1f6feb" if i < len(nodes) - 1 else "#238636"
            bg = "#161b22"
            color = "white"

        arrow = "<span style='color:#58a6ff;font-size:20px;margin:0 6px;'>→</span>" if i < len(nodes) - 1 else ""
        
        boxes += f"""
        <div style='
            border: 2px solid {border};
            background: {bg};
            color: {color};
            border-radius: 8px;
            padding: 10px 14px;
            text-align: center;
            font-size: 13px;
            font-weight: bold;
            min-width: 100px;
            line-height: 1.4;
            white-space: pre-line;
        '>{label.replace(' ', '<br>')}</div>{arrow}
        """
    
    status = "⏳ Running..." if 0 <= active_node < len(nodes) else ("✅ Complete!" if active_node >= len(nodes) else "Ready to run")
    
    html = f"""
    <div style='
        background: #0e1117;
        padding: 20px;
        border-radius: 12px;
        display: flex;
        align-items: center;
        justify-content: center;
        flex-wrap: wrap;
        gap: 4px;
    '>
        {boxes}
    </div>
    <p style='text-align:center; color:#8b949e; font-size:12px; margin-top:8px;'>
        LangGraph State Machine &nbsp;|&nbsp; {status}
    </p>
    """
    return html

st.title("🔬 Local AI Researcher")
st.markdown("*Autonomous research pipeline powered by Llama 3.1 running 100% locally*")
st.divider()
st.markdown("### 🗺️ Pipeline Architecture")
graph_placeholder = st.empty()
graph_placeholder.html(show_graph(-1))
st.caption("Built with LangGraph — each box is a graph node, state flows left to right")

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
    
    def update_log(message: str, node_index: int = -1):
        logs.append(message)
        log_container.markdown("\n\n".join(logs))
        graph_placeholder.html(show_graph(node_index))
    
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

    # ── Run LangGraph Pipeline ──
    progress.progress(10, text="🚀 Running LangGraph pipeline...")
    with st.spinner("⏳ Agent is working... this takes 2-3 minutes. Please wait!"):
        result = agent.run(topic, callback=update_log)
    graph_placeholder.html(show_graph(6))  # all nodes complete
    progress.progress(100, text="✅ Pipeline Complete!")

    papers = result.get("papers", [])
    summaries = result.get("summaries", [])
    gaps = result.get("gaps", "")
    questions = result.get("research_questions", "")
    draft = result.get("paper_draft", "")

    # Show papers found
    if papers:
        with st.expander(f"📚 {len(papers)} Papers Found", expanded=False):
            for i, p in enumerate(papers, 1):
                if "error" not in p:
                    st.markdown(f"**{i}. [{p['title']}]({p['url']})**")
                    st.caption(f"👥 {', '.join(p['authors'])} | 📅 {p['published']}")
                    st.markdown(f"> {p['abstract'][:200]}...")
                    st.divider()

    with st.expander("📝 Paper Summaries", expanded=False):
        for s in summaries:
            st.markdown(f"**{s['title']}**")
            st.caption(f"👥 {', '.join(s['authors'])} | 📅 {s['published']} | 🔗 [Link]({s['url']})")
            st.markdown(s["summary"])
            st.divider()

    with st.expander("🔬 Research Gaps Identified", expanded=True):
        st.markdown(gaps)

    with st.expander("💡 Research Questions", expanded=True):
        st.markdown(questions)
    
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
        from fpdf import FPDF
        import re

        def clean(text):
            text = re.sub(r'\*\*(.*?)\*\*', r'\1', text)
            text = re.sub(r'\*(.*?)\*', r'\1', text)
            text = re.sub(r'#{1,6}\s*', '', text)
            return unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode("ascii")

        pdf = FPDF()
        pdf.set_margins(15, 15, 15)
        pdf.set_auto_page_break(auto=True, margin=15)
        pdf.add_page()

        W = pdf.epw  # effective page width after margins
        print(f"DEBUG: pdf.w={pdf.w}, pdf.epw={pdf.epw}, margins: l={pdf.l_margin} r={pdf.r_margin}")

        # ── Cover Header ──
        pdf.set_fill_color(15, 31, 107)
        pdf.rect(0, 0, 210, 42, 'F')
        pdf.set_xy(15, 8)
        pdf.set_font("Helvetica", "B", 18)
        pdf.set_text_color(255, 255, 255)
        pdf.cell(W, 10, "RESEARCH REPORT", new_x="LMARGIN", new_y="NEXT", align="C")
        pdf.set_font("Helvetica", "", 11)
        pdf.cell(W, 8, clean(topic.title()), new_x="LMARGIN", new_y="NEXT", align="C")
        pdf.set_font("Helvetica", "I", 9)
        pdf.multi_cell(W, 5, "Generated by Local AI Researcher | Bhavesh Maurya | Stevens Institute of Technology", align="C")
        pdf.set_text_color(0, 0, 0)
        pdf.set_y(50)

        def section_title(title):
            pdf.set_font("Helvetica", "B", 12)
            pdf.set_fill_color(220, 228, 255)
            pdf.set_text_color(15, 31, 107)
            pdf.cell(W, 8, f"  {title}", new_x="LMARGIN", new_y="NEXT", fill=True)
            pdf.set_text_color(0, 0, 0)
            pdf.ln(3)

        def body_text(text):
            pdf.set_font("Helvetica", "", 10)
            pdf.set_text_color(40, 40, 40)
            for line in text.split("\n"):
                line = clean(line).strip()
                if not line:
                    pdf.ln(2)
                    continue
                pdf.set_x(pdf.l_margin)
                if line.startswith(("Gap", "RQ")):
                    pdf.ln(1)
                    pdf.set_font("Helvetica", "B", 10)
                    pdf.set_x(pdf.l_margin)
                    pdf.multi_cell(pdf.epw, 6, line)
                    pdf.set_font("Helvetica", "", 10)
                elif line.startswith(("•", "-")):
                    pdf.multi_cell(pdf.epw, 6, "  " + line)
                else:
                    pdf.multi_cell(pdf.epw, 6, line)
            pdf.ln(2)

        def divider():
            pdf.set_draw_color(210, 210, 210)
            pdf.line(15, pdf.get_y(), 15 + W, pdf.get_y())
            pdf.ln(4)

        # ── Papers Reviewed ──
        section_title("PAPERS REVIEWED")
        for i, s in enumerate(summaries, 1):
            pdf.set_x(pdf.l_margin)
            pdf.set_font("Helvetica", "B", 10)
            pdf.set_text_color(15, 31, 107)
            pdf.multi_cell(pdf.epw, 6, f"{i}. {clean(s['title'])}")
            pdf.set_x(pdf.l_margin)
            pdf.set_font("Helvetica", "I", 9)
            pdf.set_text_color(120, 120, 120)
            authors = ", ".join(s['authors'][:2]) if s['authors'] else "N/A"
            pdf.multi_cell(pdf.epw, 5, f"Authors: {clean(authors)}  |  Published: {s['published']}")
            pdf.set_text_color(40, 40, 40)
            body_text(s["summary"])
            divider()

        # ── Research Gaps ──
        pdf.add_page()
        section_title("RESEARCH GAPS IDENTIFIED")
        body_text(gaps)
        divider()

        # ── Research Questions ──
        section_title("RESEARCH QUESTIONS")
        body_text(questions)
        divider()

        # ── Paper Draft ──
        pdf.add_page()
        section_title("GENERATED PAPER DRAFT")
        body_text(draft)

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