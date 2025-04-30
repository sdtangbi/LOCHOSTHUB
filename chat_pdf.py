import streamlit as st
from utils import pdf_utils, search_utils, text_utils

def show_chat_interface():
    st.header("🤖 Chat with PDF")
    st.write("Upload a PDF or select one from your library, then ask any question about its content.")
    
    # File uploader for new PDF
    uploaded_file = st.file_uploader("Choose a PDF file", type=["pdf"])
    selected_doc_index = None
    if uploaded_file:
        # Save the uploaded file to a temp location and load it
        file_path = f"temp_{uploaded_file.name}"
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        # Extract text and metadata
        text = pdf_utils.extract_text_from_pdf(file_path)
        meta = pdf_utils.get_pdf_metadata(file_path)
        # If not already in library, add to docs
        doc_entry = {
            "filename": uploaded_file.name,
            "title": meta.get("title") or uploaded_file.name,
            "authors": meta.get("authors"),
            "year": meta.get("year"),
            "text": text,
            "vector": None  # we can set a doc-level vector if needed
        }
        # Compute and store embedding chunks for this PDF separately
        chunks = []
        chunk_texts = search_utils.split_text_to_chunks(text, chunk_size=300)
        for chunk in chunk_texts:
            vec = st.session_state.embedder.encode(chunk)
            import numpy as np
            vec = np.array(vec)
            norm = np.linalg.norm(vec)
            if norm > 0:
                vec = vec / norm
            chunks.append({"doc_index": None, "text": chunk, "vector": vec})
        # Use session state to store current PDF chunks
        st.session_state.chat_pdf_chunks = chunks
        st.session_state.chat_pdf_meta = doc_entry
        st.success(f"Uploaded and processed {uploaded_file.name}. Now ask a question!")
    else:
        # If no file uploaded, allow choosing from existing library
        if st.session_state.docs:
            titles = [doc["title"] for doc in st.session_state.docs]
            choice = st.selectbox("Or select a PDF from your library:", [""] + titles)
            if choice and choice in titles:
                selected_doc_index = titles.index(choice)
                # Prepare chunks for the selected doc from precomputed data
                chunks = [c for c in st.session_state.chunks if c["doc_index"] == selected_doc_index]
                st.session_state.chat_pdf_chunks = chunks
                st.session_state.chat_pdf_meta = st.session_state.docs[selected_doc_index]
        else:
            st.info("No PDFs in library. Please upload a PDF to chat with.")
    
    if "chat_pdf_chunks" in st.session_state:
        query = st.text_input("Ask a question about this PDF:")
        if query:
            # Perform semantic search on chunks of this PDF
            results = search_utils.semantic_search(query, st.session_state.chat_pdf_chunks, st.session_state.embedder, top_k=1)
            if results:
                doc_idx, chunk_text, score = results[0]
                # Summarize the answer chunk (or just return the chunk text if small)
                answer = chunk_text
                if len(chunk_text.split()) > 50:
                    answer = text_utils.summarize_text(chunk_text, st.session_state.summarizer, max_len=80)
                st.write(f"**Answer:** {answer}")
                # Optionally, provide the exact snippet as quote and citation
                meta = st.session_state.chat_pdf_meta
                cite_authors = meta.get("authors") or "Unknown"
                cite_year = meta.get("year") or "n.d."
                # Show snippet with citation
                st.write(f"*- from **{meta['title']}** ({cite_authors}, {cite_year})*")
            else:
                st.write("Sorry, I couldn't find an answer in the document.")
