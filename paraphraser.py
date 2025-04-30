import streamlit as st
from utils import text_utils

def show_paraphraser_interface():
    st.header("🔄 Paraphraser")
    st.write("Improve clarity and originality by rephrasing your text.")
    text = st.text_area("Enter text to paraphrase:")
    if st.button("Paraphrase"):
        if not text or text.isspace():
            st.warning("Please enter some text to paraphrase.")
        else:
            result = text_utils.paraphrase_text(text, st.session_state.summarizer)
            st.write("**Paraphrased Text:**")
            st.write(result)
            st.info("*(Note: This paraphraser uses a general summarization model. Results may not preserve all nuances. Consider refining the output.)*")
