#!/bin/bash
pip install -r requirements.txt
python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('all-MiniLM-L6-v2')"
python -c "from transformers import AutoModelForSeq2SeqLM, AutoTokenizer; AutoModelForSeq2SeqLM.from_pretrained('t5-small'); AutoTokenizer.from_pretrained('t5-small')"
python -c "from transformers import GPT2LMHeadModel, GPT2TokenizerFast; GPT2LMHeadModel.from_pretrained('gpt2'); GPT2TokenizerFast.from_pretrained('gpt2')"
echo 'Setup complete. Run using: streamlit run app.py'
