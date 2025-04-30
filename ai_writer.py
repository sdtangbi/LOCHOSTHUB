import streamlit as st
from utils import text_utils

def show_writer_interface():
    st.header("✍️ AI Writer")
    st.write("Generate or refine your writing with AI assistance. Enter a prompt or some text to continue, and the AI will suggest the next part.")
    
    prompt = st.text_area("Enter a title, heading, or start of a paragraph:", height=100)
    if st.button("Generate"):
        if not prompt or prompt.isspace():
            st.warning("Please enter a prompt or some text to start with.")
        else:
            output = text_utils.generate_text(prompt, st.session_state.gpt2_model, st.session_state.gpt2_tokenizer, max_length=200)
            st.write("**AI Output:** " + output)
            st.info("*(Note: The AI Writer is using a local GPT-2 model. For more coherent and context-aware writing, larger models or fine-tuning would be beneficial.)*")
