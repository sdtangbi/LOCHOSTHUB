import os, re
import fitz  # PyMuPDF for PDF reading

from utils import search_utils

def extract_text_from_pdf(pdf_path):
    """Extract full text from PDF using PyMuPDF (fitz)."""
    text = ""
    try:
        doc = fitz.open(pdf_path)
        for page in doc:
            text += page.get_text()  # extract text from each page
        doc.close()
    except Exception as e:
        print(f"Error reading {pdf_path}: {e}")
    return text

def get_pdf_metadata(pdf_path):
    """Extract basic metadata (title, authors, year) from PDF file, if available."""
    metadata = {"title": None, "authors": None, "year": None}
    try:
        doc = fitz.open(pdf_path)
        meta = doc.metadata
        # Title
        title = meta.get("title")
        if title:
            # Clean title (remove newlines, etc.)
            title = title.strip()
            # Avoid empty or default titles
            if len(title) == 0 or title.lower().startswith("microsoft word"):
                title = None
        metadata["title"] = title
        # Authors
        authors = meta.get("author")
        if authors:
            authors = authors.strip()
            if authors == "":
                authors = None
        metadata["authors"] = authors
        # Year: try metadata first (creation date)
        year = None
        creation_date = meta.get("creationDate")
        if creation_date:
            # PyMuPDF gives creationDate like 'D:20230101...' 
            match = re.search(r"D:(\d{4})", creation_date)
            if match:
                year = match.group(1)
        # If not found, try modification date
        if not year:
            mod_date = meta.get("modDate")
            if mod_date:
                match = re.search(r"D:(\d{4})", mod_date)
                if match:
                    year = match.group(1)
        # If still not found, try searching in text (e.g., year in first page)
        if not year:
            first_page_text = ""
            try:
                first_page_text = doc.load_page(0).get_text()
            except: 
                first_page_text = ""
            # search for a year between 1900-2099
            m = re.search(r"(19|20)\d{2}", first_page_text)
            if m:
                year = m.group(0)
        metadata["year"] = year
        doc.close()
    except Exception as e:
        print(f"Error extracting metadata from {pdf_path}: {e}")
    return metadata

def load_pdfs(folder_path, embedder):
    """
    Load all PDFs from the given folder, extract their text and metadata,
    compute embeddings for search. Returns a list of docs and a list of chunks.
    """
    docs = []
    chunks = []
    for filename in os.listdir(folder_path):
        if filename.lower().endswith(".pdf"):
            pdf_path = os.path.join(folder_path, filename)
            text = extract_text_from_pdf(pdf_path)
            meta = get_pdf_metadata(pdf_path)
            # If no title from metadata, use filename (without extension) as title
            if not meta["title"]:
                meta["title"] = os.path.splitext(filename)[0]
            # If no authors, leave as None or could set "Unknown"
            # Compute embedding for the entire document (could be used for broad similarity)
            doc_vector = embedder.encode(text)
            # Normalize the document vector for cosine similarity
            import numpy as np
            if isinstance(doc_vector, list):
                doc_vector = np.array(doc_vector)
            norm = np.linalg.norm(doc_vector)
            if norm > 0:
                doc_vector = doc_vector / norm
            doc_entry = {
                "filename": filename,
                "title": meta["title"],
                "authors": meta["authors"],
                "year": meta["year"],
                "text": text,
                "vector": doc_vector
            }
            docs.append(doc_entry)
            # Split text into chunks for fine-grained search
            chunk_texts = search_utils.split_text_to_chunks(text, chunk_size=300)  # approx 300 words per chunk
            for chunk in chunk_texts:
                vec = embedder.encode(chunk)
                if isinstance(vec, list):
                    vec = np.array(vec)
                norm = np.linalg.norm(vec)
                if norm > 0:
                    vec = vec / norm
                chunks.append({
                    "doc_index": len(docs)-1,  # index of this doc in docs list
                    "text": chunk,
                    "vector": vec
                })
    return docs, chunks