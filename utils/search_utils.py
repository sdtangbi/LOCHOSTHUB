import numpy as np
from sentence_transformers import SentenceTransformer

def load_embedding_model(model_name="sentence-transformers/all-MiniLM-L6-v2"):
    """Load or initialize the sentence-transformer model for embeddings."""
    try:
        model = SentenceTransformer(model_name)
    except Exception as e:
        # If offline and model not found in cache, prompt user to run setup to download it
        print("Embedding model not found. Please run setup.sh to download the model.")
        raise e
    return model

def split_text_to_chunks(text, chunk_size=300):
    """
    Split a large text into smaller chunks of approximately chunk_size words.
    We'll split by sentences to preserve meaning and ensure chunks aren't cut awkwardly.
    """
    # Simple splitting by whitespace for now, can be improved to sentence splitting
    words = text.split()
    chunks = []
    for i in range(0, len(words), chunk_size):
        chunk_words = words[i:i+chunk_size]
        chunk = " ".join(chunk_words)
        chunks.append(chunk)
    return chunks

def semantic_search(query, chunks, embedder, top_k=5):
    """
    Perform semantic search: encode the query and return top_k matching chunks.
    Returns a list of (doc_index, chunk_text, score) sorted by relevance.
    """
    # Encode query
    query_vec = embedder.encode(query)
    if isinstance(query_vec, list):
        query_vec = np.array(query_vec)
    # Normalize query vector
    norm = np.linalg.norm(query_vec)
    if norm > 0:
        query_vec = query_vec / norm
    # Stack all chunk vectors for dot product
    all_vecs = np.array([c["vector"] for c in chunks])
    # Compute cosine similarity as dot product (since vectors are normalized)
    scores = np.dot(all_vecs, query_vec)
    # Get indices of top scores
    if top_k <= 0:
        top_k = len(chunks)
    top_idx = np.argsort(scores)[::-1][:top_k * 2]  # take top 2*top_k to allow filtering distinct docs
    seen_docs = set()
    results = []
    for idx in top_idx:
        doc_idx = chunks[idx]["doc_index"]
        if doc_idx in seen_docs:
            continue  # skip if we already have a chunk from this doc
        seen_docs.add(doc_idx)
        results.append((doc_idx, chunks[idx]["text"], float(scores[idx])))
        if len(results) >= top_k:
            break
    return results
