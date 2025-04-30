import streamlit as st
from utils import text_utils

def show_detector_interface():
    st.header("🛡️ AI Content Detector")
    st.write("Check if a given text is likely written by AI.")
    text = st.text_area("Enter text to analyze:", height=150)
    if st.button("Analyze"):
        if not text or text.isspace():
            st.warning("Please paste some text to analyze.")
        else:
            ppl = text_utils.calculate_perplexity(text, st.session_state.gpt2_model, st.session_state.gpt2_tokenizer)
            if ppl is None:
                st.error("Could not calculate perplexity (text may be too short).")
            else:
                st.write(f"**Perplexity Score:** {ppl:.2f}")
                # Heuristic thresholds for demonstration:
                if ppl < 40:
                    result = "The text is very predictable (low perplexity), it *might be AI-generated*."
                elif ppl > 100:
                    result = "The text has high complexity (high perplexity), it is *likely human-written*."
                else:
                    result = "The result is inconclusive – the text has mixed characteristics of human and AI writing."
                st.write(result)
                st.info("*(Note: Perplexity-based AI detection is not fully reliable and should be combined with other method&#8203;:contentReference[oaicite:43]{index=43}&#8203;:contentReference[oaicite:44]{index=44}】.)*")
