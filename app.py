import streamlit as st
from streamlit_option_menu import option_menu  # for a styled sidebar menu (if installed)
# If streamlit_option_menu is not available offline, we can use st.sidebar.radio as a fallback.

# Import our feature modules
import chat_pdf, literature_review, ai_writer, find_topics
import paraphraser, citation_generator, extract_data, ai_detector, pdf_to_video

from utils import pdf_utils, search_utils, text_utils

# ----- Page Config -----
st.set_page_config(page_title="LOCHOSTHUB - AI Research Assistant", layout="wide")

# Apply custom CSS for style (mimicking SciSpace light theme and rounded elements)
custom_css = """
<style>
/* General */
body { background-color: #f8f9fa; }
section.main > div { padding-top: 2rem; }
/* Sidebar */
[data-testid="stSidebar"] { background-color: #ffffff; }
[data-testid="stSidebar"] .css-1d391kg { padding: 1rem 0.5rem; }  /* adjust sidebar padding */
[data-testid="stSidebar"] h2 { font-size: 1.2rem; margin: 0.5em 0; }
/* Option menu or radio in sidebar */
.stButton > button, .stRadio > div, .stSelectbox > div { border-radius: 0.5rem; }
/* Main search box */
.big-search-input > div:first-child { border-radius: 0.5rem; border: 2px solid #e0e0e0; }
.big-search-input input::placeholder { font-size: 1rem; color: #888; }
/* Result cards */
.result-card { background: #fff; padding: 1rem; border-radius: 0.5rem; margin-bottom: 1rem; }
.result-title { font-weight: bold; font-size: 1rem; }
.result-summary { font-size: 0.95rem; margin: 0.5em 0; }
.result-citation { font-size: 0.9rem; color: #555; }
</style>
"""
st.markdown(custom_css, unsafe_allow_html=True)

# ----- Initialize Models and Data (run once) -----
# Use session state to avoid reloading on each interaction
if "models_loaded" not in st.session_state:
    # Load sentence transformer for embeddings
    st.session_state.embedder = search_utils.load_embedding_model()  # uses MiniLM-L6-v2
    # Load summarization model (T5-small) pipeline
    st.session_state.summarizer = text_utils.load_summarizer_model()
    # Load GPT-2 model for AI writer & detector
    st.session_state.gpt2_model, st.session_state.gpt2_tokenizer = text_utils.load_gpt2_model()
    # Load local PDFs from sample_pdfs folder
    docs, chunks = pdf_utils.load_pdfs("data", st.session_state.embedder)
    st.session_state.docs = docs       # list of document metadata (with vectors)
    st.session_state.chunks = chunks   # list of text chunks (with vectors) for search
    st.session_state.models_loaded = True

# Sidebar: Logo/Title and Menu
st.sidebar.title("🔍 LOCHOSTHUB")
st.sidebar.write("**Offline AI Research Hub**")  # a short tagline

# Define menu options and icons (if using option_menu for better styling)
menu_options = ["Home", "Chat with PDF", "Literature Review", "AI Writer",
                "Find Topics", "Paraphraser", "Citation Generator",
                "Extract Data", "AI Detector", "PDF to Video"]
menu_icons = ["house", "file-earmark-text", "journal-text", 
              "pen", "lightbulb", "arrow-repeat", 
              "bookmark-check", "table", "shield-shaded", "camera-video"]

# Using option_menu for a nicer look (if available), otherwise fallback to radio
try:
    choice = option_menu("Menu", menu_options, icons=menu_icons, menu_icon="cast", default_index=0,
                         orientation="vertical", styles={
                             "container": {"padding": "0!important"},
                             "icon": {"font-size": "16px"}, 
                             "nav-link": {"font-size": "14px", "text-align": "left", "margin":"0px"}
                         })
except Exception as e:
    # Fallback: simple radio buttons
    choice = st.sidebar.radio("Navigate", menu_options, index=0)

# Main area: load the selected page
if choice == "Home":
    literature_review.show_home()  # Home will show the main search interface (same as literature search, but with welcome text)
elif choice == "Chat with PDF":
    chat_pdf.show_chat_interface()
elif choice == "Literature Review":
    literature_review.show_search_interface()
elif choice == "AI Writer":
    ai_writer.show_writer_interface()
elif choice == "Find Topics":
    find_topics.show_topics_interface()
elif choice == "Paraphraser":
    paraphraser.show_paraphraser_interface()
elif choice == "Citation Generator":
    citation_generator.show_citation_interface()
elif choice == "Extract Data":
    extract_data.show_extraction_interface()
elif choice == "AI Detector":
    ai_detector.show_detector_interface()
elif choice == "PDF to Video":
    pdf_to_video.show_video_interface()
