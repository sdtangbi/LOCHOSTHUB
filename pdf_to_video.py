import streamlit as st
from utils import text_utils

def show_video_interface():
    st.header("🎞️ PDF to Video")
    st.write("Generate a storyboard for a video summary of a PDF.")
    if not st.session_state.docs:
        st.info("No PDFs available. Please add a PDF to use this feature.")
        return
    titles = [doc["title"] for doc in st.session_state.docs]
    choice = st.selectbox("Choose a PDF to summarize:", [""] + titles)
    if choice and choice in titles:
        idx = titles.index(choice)
        doc = st.session_state.docs[idx]
        text = doc["text"]
        # Split the text into ~5 segments for slides
        num_slides = 5
        segments = []
        n = len(text) // num_slides if len(text) >= num_slides else len(text)
        for i in range(num_slides):
            segment = text[i*n : (i+1)*n]
            if i < num_slides - 1:
                # Cut at last period for better segmentation
                last_period = segment.rfind('.')
                if last_period != -1:
                    segment = segment[:last_period+1]
            segments.append(segment.strip())
        st.subheader(f"Video Summary Outline – {doc['title']}")
        for i, segment in enumerate(segments, start=1):
            if not segment:
                continue
            summary = text_utils.summarize_text(segment, st.session_state.summarizer, max_len=50)
            st.write(f"**Slide {i}:** {summary}")
        st.info("*(This outline lists key points from the paper, which can be turned into slides with narration. Full video generation would involve text-to-speech and visuals.)*")
