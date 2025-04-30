import streamlit as st
from sklearn.cluster import KMeans
from collections import Counter
import re

def show_topics_interface():
    st.header("🕵️ Find Topics")
    st.write("Analyze your library to discover prevalent topics or research areas.")
    if not st.session_state.docs or len(st.session_state.docs) == 0:
        st.info("Add some PDFs to your library first to analyze topics.")
        return
    # We cluster the document embeddings to find groups of similar papers
    vectors = [doc["vector"] for doc in st.session_state.docs]
    if len(vectors) < 2:
        st.info("Need multiple documents to find topics.")
        return
    import numpy as np
    X = np.vstack(vectors)
    # Decide number of clusters (e.g., sqrt of num docs or 3 by default)
    k = min(5, len(st.session_state.docs))
    kmeans = KMeans(n_clusters=k, random_state=42).fit(X)
    labels = kmeans.labels_
    clusters = {i: [] for i in range(k)}
    for idx, label in enumerate(labels):
        clusters[label].append(st.session_state.docs[idx])
    # For each cluster, derive a topic label by finding common keywords in titles
    st.subheader("Discovered Topics:")
    for label, docs in clusters.items():
        if not docs:
            continue
        # concatenate all titles in cluster
        all_titles = " ".join([d["title"] or "" for d in docs])
        # simple keyword extraction: most frequent nouns or words in titles
        words = re.findall(r'\w+', all_titles.lower())
        common = Counter([w for w in words if len(w)>3 and w not in ["study", "analysis", "research", "paper", "effect"]])
        top_words = [w.capitalize() for w, _ in common.most_common(3)]
        topic_name = " ".join(top_words[:2]) if top_words else "Miscellaneous"
        st.write(f"**Topic {label+1}:** *{topic_name}* – {len(docs)} papers")
        # list the titles under this topic
        for doc in docs:
            st.write(f"- {doc['title']} ({doc.get('year') or 'n.d.'})")
