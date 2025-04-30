import os
import streamlit as st
import pdfplumber
import pandas as pd

def show_extraction_interface():
    st.header("📊 Extract Data")
    st.write("Select a PDF to extract tables or data from.")
    if not st.session_state.docs:
        st.info("No PDFs available. Please add a PDF to use this feature.")
        return
    # Select a PDF from library
    titles = [doc["title"] for doc in st.session_state.docs]
    choice = st.selectbox("Choose a PDF", [""] + titles)
    if choice and choice in titles:
        idx = titles.index(choice)
        filename = st.session_state.docs[idx]["filename"]
        file_path = os.path.join("sample_pdfs", filename)
        try:
            with pdfplumber.open(file_path) as pdf:
                tables_found = False
                for page in pdf.pages:
                    tables = page.extract_tables()
                    if tables:
                        tables_found = True
                        for table in tables:
                            # Convert to DataFrame for display (first row as header if possible)
                            if len(table) > 1:
                                df = pd.DataFrame(table[1:], columns=table[0])
                            else:
                                df = pd.DataFrame(table)
                            st.write(f"**Table from page {page.page_number}:**")
                            st.dataframe(df)
                if not tables_found:
                    st.write("No tables were found in this PDF.")
        except Exception as e:
            st.error(f"Error extracting data: {e}")
