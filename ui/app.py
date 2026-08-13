import sys
import os
from pathlib import Path

# 1. Dynamic Root Path Resolution
FILE_PATH = Path(__file__).resolve()
ROOT_DIR = FILE_PATH.parent.parent  # Points to project root

# Ensure both project root and 'app' directory are in sys.path
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

APP_DIR = os.path.join(ROOT_DIR, "app")
if os.path.exists(APP_DIR) and str(APP_DIR) not in sys.path:
    sys.path.insert(0, str(APP_DIR))

# 2. Standard Libraries & Streamlit
import streamlit as st
import json
import subprocess

# 3. RAG Pipeline Import with Robust Fallbacks
try:
    from app.rag.retriever import RAGPipeline
except ModuleNotFoundError:
    try:
        from rag.retriever import RAGPipeline
    except ModuleNotFoundError:
        # Ultimate fallback if relative module execution happens
        sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
        from app.rag.retriever import RAGPipeline

# Page Configuration
st.set_page_config(
    page_title="Enterprise Company Intelligence Platform",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Dark Glassmorphism Styling
st.markdown("""
    <style>
    /* Main Background Theme */
    .stApp {
        background-color: #0F172A;
        color: #F8FAFC;
    }

    /* Hero Header */
    .hero-title {
        font-size: 2.4rem;
        font-weight: 800;
        background: linear-gradient(90deg, #38BDF8 0%, #818CF8 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 4px;
    }
    .hero-subtitle {
        font-size: 1rem;
        color: #94A3B8;
        margin-bottom: 25px;
    }

    /* Modern Metric Cards */
    .metric-card {
        background: rgba(30, 41, 59, 0.7);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 12px;
        padding: 16px;
        text-align: center;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
    }
    .metric-value {
        font-size: 1.8rem;
        font-weight: 700;
        color: #38BDF8;
    }
    .metric-label {
        font-size: 0.8rem;
        color: #94A3B8;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-top: 4px;
    }

    /* Custom Badges */
    .badge {
        background: rgba(99, 102, 241, 0.15);
        color: #A5B4FC;
        border: 1px solid rgba(99, 102, 241, 0.3);
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.85rem;
        display: inline-block;
        margin: 4px;
    }
    .tech-badge {
        background: rgba(16, 185, 129, 0.15);
        color: #6EE7B7;
        border: 1px solid rgba(16, 185, 129, 0.3);
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.85rem;
        display: inline-block;
        margin: 4px;
    }

    /* Content Cards */
    .info-card {
        background: rgba(30, 41, 59, 0.5);
        border: 1px solid rgba(255, 255, 255, 0.05);
        border-radius: 10px;
        padding: 16px;
        margin-bottom: 12px;
    }

    /* Chat Response Container */
    .chat-response-box {
        background: rgba(15, 23, 42, 0.8);
        border-left: 4px solid #38BDF8;
        padding: 16px;
        border-radius: 8px;
        color: #E2E8F0;
        margin-top: 15px;
    }

    /* Streamlit Expander Dark Mode Overrides */
    div[data-testid="stExpander"] {
        border: 1px solid #334155 !important;
        border-radius: 8px !important;
        background-color: #1E293B !important;
    }
    </style>
""", unsafe_allow_html=True)

# Main Hero Section
st.markdown('<div class="hero-title">⚡ Enterprise Company Intelligence & RAG Platform</div>', unsafe_allow_html=True)
st.markdown('<div class="hero-subtitle">Automated Data Extraction & Context-Grounded AI Knowledge Assistant</div>', unsafe_allow_html=True)

# Sidebar Controls
st.sidebar.title("🎯 Control Panel")
url_input = st.sidebar.text_input("Target Company Website URL", "https://bestpeers.com")
start_button = st.sidebar.button("🚀 Analyze & Extract Data", use_container_width=True)

json_file_path = os.path.join(ROOT_DIR, "output", "company_profile.json")

# Pipeline Execution (Dynamic Subprocess Invocation)
if start_button:
    with st.spinner(f"Extracting Data for {url_input}..."):
        try:
            main_script_path = os.path.join(ROOT_DIR, "main.py")
            
            # Subprocess execution with explicit URL argument
            process = subprocess.run(
                [sys.executable, main_script_path, url_input.strip()], 
                capture_output=True, 
                text=True
            )
            
            if process.returncode == 0:
                # Force Cache clear to re-initialize RAG index with new data
                st.cache_resource.clear()
                st.sidebar.success(f"Data Extraction Completed for {url_input}!")
                st.rerun()
            else:
                st.sidebar.error("Execution error! Check logs below:")
                st.sidebar.code(process.stderr)
        except Exception as e:
            st.sidebar.error(f"Pipeline Execution Failed: {e}")

# Render Intelligence Dashboard
if os.path.exists(json_file_path):
    with open(json_file_path, "r", encoding="utf-8") as f:
        company_data = json.load(f)

    # Metric Panel
    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.markdown(f'<div class="metric-card"><div class="metric-value">{company_data.get("company_name", "N/A")}</div><div class="metric-label">Company</div></div>', unsafe_allow_html=True)
    with m2:
        st.markdown(f'<div class="metric-card"><div class="metric-value">{company_data.get("founded_year", "N/A")}</div><div class="metric-label">Founded Year</div></div>', unsafe_allow_html=True)
    with m3:
        st.markdown(f'<div class="metric-card"><div class="metric-value">{len(company_data.get("services", []))}</div><div class="metric-label">Services Extracted</div></div>', unsafe_allow_html=True)
    with m4:
        st.markdown(f'<div class="metric-card"><div class="metric-value">{len(company_data.get("technologies", []))}</div><div class="metric-label">Technologies Detected</div></div>', unsafe_allow_html=True)

    st.write("")
    st.write("")

    # Section Tabs
    tab_rag, tab_dashboard, tab_json = st.tabs([
        "🤖 AI Knowledge Assistant (RAG)", 
        "📊 Intelligence Profile", 
        "📄 Raw Output JSON"
    ])

    # TAB 1: RAG Assistant
    with tab_rag:
        st.subheader("💬 Ask AI Assistant")
        st.caption("Responses are strictly grounded in extracted company profile documents.")

        @st.cache_resource
        def get_rag_pipeline(json_path):
            return RAGPipeline(json_path)

        try:
            rag = get_rag_pipeline(json_file_path)
            user_query = st.text_input("Ask a question (e.g., 'Who is the CEO?', 'What services do they offer?'):")

            if user_query:
                with st.spinner("Searching Vector Database & Synthesizing Answer..."):
                    rag_response = rag.query(user_query)

                    if isinstance(rag_response, dict) and "answer" in rag_response:
                        st.markdown("### 🤖 Response:")
                        st.markdown(f'<div class="chat-response-box">{rag_response["answer"]}</div>', unsafe_allow_html=True)

                        st.divider()
                        with st.expander("🔍 View Retrieved Context Sources"):
                            for idx, res in enumerate(rag_response.get("sources", []), 1):
                                cat = res["document"]["metadata"].get("category", "General")
                                score = res.get("score", 0)
                                st.markdown(f"**Source {idx} | Category: `{cat.upper()}` (Match: {score:.2f})**")
                                st.caption(res["document"]["text"])
                                st.divider()
                    else:
                        SIMILARITY_THRESHOLD = 0.50
                        valid_results = [r for r in rag_response if r.get("score", 0) >= SIMILARITY_THRESHOLD]

                        if valid_results:
                            st.markdown("### 💡 Context Matches:")
                            for idx, res in enumerate(valid_results, 1):
                                cat = res["document"]["metadata"].get("category", "General")
                                score = res.get("score", 0)
                                with st.expander(f"Result {idx} | Category: {cat.upper()} (Similarity: {score:.2f})", expanded=True):
                                    st.write(res["document"]["text"])
                        else:
                            st.warning("⚠️ No relevant information found in extracted company documents for this query.")

        except Exception as err:
            st.error(f"RAG Engine Exception: {err}")

    # TAB 2: Clean Structured Company Profile
    with tab_dashboard:
        col_left, col_right = st.columns([1.2, 0.8])

        with col_left:
            st.markdown('<div class="info-card">', unsafe_allow_html=True)
            st.subheader("ℹ️ Overview")
            st.markdown(f"**Website:** [{company_data.get('website')}]({company_data.get('website')})")
            
            industries = company_data.get("industry", [])
            if isinstance(industries, list) and industries:
                ind_html = " ".join([f'<span class="badge">{ind}</span>' for ind in industries])
                st.markdown(f"**Industries:** {ind_html}", unsafe_allow_html=True)
            
            st.markdown(f"<br>**About:**<br>{company_data.get('about', 'N/A')}", unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

            st.markdown('<div class="info-card">', unsafe_allow_html=True)
            st.subheader("🛠️ Services")
            services_list = company_data.get("services", [])
            if services_list:
                s_html = " ".join([f'<span class="badge">{s}</span>' for s in services_list])
                st.markdown(s_html, unsafe_allow_html=True)
            else:
                st.write("No services extracted.")
            st.markdown('</div>', unsafe_allow_html=True)

            st.markdown('<div class="info-card">', unsafe_allow_html=True)
            st.subheader("💻 Technologies")
            tech_list = company_data.get("technologies", [])
            if tech_list:
                t_html = " ".join([f'<span class="tech-badge">{t}</span>' for t in tech_list])
                st.markdown(t_html, unsafe_allow_html=True)
            else:
                st.write("No technologies detected.")
            st.markdown('</div>', unsafe_allow_html=True)

        with col_right:
            st.markdown('<div class="info-card">', unsafe_allow_html=True)
            st.subheader("👥 Leadership & Team")
            people = company_data.get("people", [])
            if people:
                for p in people:
                    if isinstance(p, dict):
                        st.write(f"- **{p.get('name', 'N/A')}** | {p.get('designation', 'N/A')}")
                    else:
                        st.write(f"- {p}")
            else:
                st.write("No leadership data found.")
            st.markdown('</div>', unsafe_allow_html=True)

            st.markdown('<div class="info-card">', unsafe_allow_html=True)
            st.subheader("📞 Contact Info & Offices")
            st.markdown("**Emails:**<br>" + "<br>".join(company_data.get("email", []) or ["N/A"]), unsafe_allow_html=True)
            st.markdown("<br>**Phones:**<br>" + "<br>".join(company_data.get("phone", []) or ["N/A"]), unsafe_allow_html=True)
            
            st.markdown("<br>**Locations:**", unsafe_allow_html=True)
            locations = company_data.get("locations", [])
            if locations:
                for loc in locations:
                    st.info(loc)
            else:
                st.write("No location info available.")
            st.markdown('</div>', unsafe_allow_html=True)

            st.markdown('<div class="info-card">', unsafe_allow_html=True)
            st.subheader("🔗 Social Media Links")
            socials = company_data.get("social_links", {})
            if socials:
                for platform, links in socials.items():
                    if links:
                        st.write(f"**{platform.capitalize()}:** {links[0]}")
            else:
                st.write("No social links detected.")
            st.markdown('</div>', unsafe_allow_html=True)

    # TAB 3: Raw Output JSON
    with tab_json:
        st.json(company_data)

else:
    st.info("👈 Enter a URL in the sidebar and click Analyze & Extract Data to run the pipeline.")