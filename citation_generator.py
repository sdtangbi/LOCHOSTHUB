import streamlit as st
from utils import text_utils
import re

def show_citation_interface():
    st.header("📑 Citation Generator")
    st.write("Fill in the details below to generate an APA citation.")
    # Fields for citation
    col1, col2 = st.columns(2)
    with col1:
        authors = st.text_input("Authors (separate by semicolon ';' or comma):", help="e.g. John Doe; Jane Smith")
        title = st.text_input("Title of work:")
        year = st.text_input("Year of publication:")
    with col2:
        source = st.text_input("Source (Journal/Book/Website):", help="Journal name or publisher")
        vol_issue = st.text_input("Volume(Issue):", help="e.g. 12(3) or just 12")
        pages = st.text_input("Pages:", help="e.g. 123-130")
    if st.button("Generate Citation"):
        if not title or not year:
            st.warning("Please provide at least a title and year.")
        else:
            # Split volume and issue if provided
            vol = None
            issue = None
            if vol_issue:
                # parse patterns like 12(3)
                m = re.match(r"(\d+)\s*\(?(\d+)?\)?", vol_issue)
                if m:
                    vol = m.group(1)
                    if m.group(2):
                        issue = m.group(2)
            citation = text_utils.format_apa_citation(authors, year, title, source, vol, issue, pages)
            st.write("**APA Citation:**")
            st.write(citation)
            st.success("Citation copied to clipboard!" if st.button("Copy to clipboard") else "")
