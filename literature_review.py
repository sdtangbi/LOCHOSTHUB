import streamlit as st
from utils import search_utils, text_utils

def show_home():
    """Show the home page (which is similar to literature review search but with intro text)."""
    st.title("The Fastest Research Platform Ever")
    st.write("_All-in-one AI tools for students and researchers._")  # SciSpace tagline
    st.write("Welcome to **LOCHOSTHUB**, an offline AI research assistant. Use the search below to find answers in your local academic papers.")
    show_search_interface()

def show_search_interface():
    """Show literature review search interface."""
    query = st.text_input("Enter your search query", key="lit_query", placeholder="e.g. How does climate change impact biodiversity?")
    # Toggle for Standard / High Quality / Deep Review
    mode = st.radio("Mode:", ["Standard", "High Quality", "Deep Review"], horizontal=True, index=0)
    go_online = st.checkbox("Go Online for more results")  # if checked, will show external links
    
    if query:
        # Perform semantic search on all chunks
        results = search_utils.semantic_search(query, st.session_state.chunks, st.session_state.embedder, top_k=5)
        if len(results) == 0:
            st.write("No relevant documents found in the local library.")
        else:
            # If Deep Review mode, we will synthesize an overall summary of results
            if mode == "Deep Review":
                all_texts = [text for (_, text, _) in results]
                combined_text = " ".join(all_texts)
                overall_summary = text_utils.summarize_text(combined_text, st.session_state.summarizer, max_len=150)
                st.subheader("Deep Review Summary")
                st.write(overall_summary)
                st.markdown("*References:*")
                # List all results as references
                for i, (doc_idx, _, _) in enumerate(results, start=1):
                    doc = st.session_state.docs[doc_idx]
                    citation = text_utils.format_apa_citation(doc.get("authors"), doc.get("year"), doc.get("title"), source=None)
                    st.markdown(f"{i}. {citation}")
                st.markdown("---")
            
            st.subheader("Search Results")
            for doc_idx, chunk_text, score in results:
                doc = st.session_state.docs[doc_idx]
                title = doc.get("title") or "Untitled"
                # Summarize or truncate the chunk for display
                snippet = chunk_text
                if mode == "High Quality" or mode == "Deep Review":
                    # For high quality, provide a summary of the chunk for a cleaner answer
                    snippet = text_utils.summarize_text(chunk_text, st.session_state.summarizer, max_len=60)
                else:
                    # Standard mode: maybe just show a part of the chunk if it's long
                    if len(snippet) > 300:
                        snippet = snippet[:300] + "..."
                # Citation for this result
                citation = text_utils.format_apa_citation(doc.get("authors"), doc.get("year"), title, source=None)
                # Display result card
                st.markdown(f"<div class='result-card'>", unsafe_allow_html=True)
                st.markdown(f"<div class='result-title'>{title}</div>", unsafe_allow_html=True)
                st.markdown(f"<div class='result-summary'>{snippet}</div>", unsafe_allow_html=True)
                st.markdown(f"<div class='result-citation'>{citation}</div>", unsafe_allow_html=True)
                st.markdown(f"</div>", unsafe_allow_html=True)
            # Optionally show an online search link if requested
            if go_online:
                st.markdown(f"**Online Search:** [Google Scholar](https://scholar.google.com/scholar?q={query}) | " 
                            f"[Semantic Scholar](https://www.semanticscholar.org/search?q={query}) | "
                            f"[SciSpace](https://www.scispace.com/search?query={query})")
