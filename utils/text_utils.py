import torch
from transformers import pipeline, AutoModelForSeq2SeqLM, AutoTokenizer, GPT2LMHeadModel, GPT2TokenizerFast

def load_summarizer_model():
    """Load a text summarization pipeline (T5-small model)."""
    try:
        summarizer = pipeline("summarization", model="t5-small", tokenizer="t5-small")
    except Exception as e:
        print("Summarization model not found. Run setup.sh to download t5-small.")
        raise e
    return summarizer

def summarize_text(text, summarizer, max_len=100):
    """Summarize the given text using the provided summarizer pipeline."""
    if not text or text.isspace():
        return ""
    # T5-small works better with a prefix
    input_text = "summarize: " + text.strip().replace("\n", " ")
    # T5-small has limited input size; truncate long text to avoid errors
    max_input = 512  # token limit (approx)
    input_text = input_text[:2000]  # truncate raw characters as a rough limit
    summary = summarizer(input_text, max_length=max_len, min_length=30, do_sample=False)
    return summary[0]['summary_text'] if summary else ""

def load_gpt2_model():
    """Load GPT-2 model and tokenizer for text generation and perplexity."""
    try:
        tokenizer = GPT2TokenizerFast.from_pretrained("gpt2")
        model = GPT2LMHeadModel.from_pretrained("gpt2")
    except Exception as e:
        print("GPT-2 model not found. Run setup.sh to download GPT-2.")
        raise e
    # GPT-2 small (117M) loaded.
    model.eval()
    return model, tokenizer

def generate_text(prompt, model, tokenizer, max_length=100):
    """Generate text continuation for the prompt using GPT-2 model."""
    if not prompt:
        return ""
    inputs = tokenizer.encode(prompt, return_tensors='pt')
    # Generate continuation
    outputs = model.generate(inputs, max_length=max_length, num_return_sequences=1, no_repeat_ngram_size=2, 
                              pad_token_id=tokenizer.eos_token_id)
    generated = tokenizer.decode(outputs[0][len(inputs[0]):])
    # Clean up output
    return generated.strip()

def paraphrase_text(text, summarizer):
    """
    Paraphrase text using the summarization model (by re-summarizing or through simple synonym replacement).
    For simplicity, we'll use summarizer to rephrase by summarizing then expanding slightly.
    """
    if not text or text.isspace():
        return ""
    # We attempt a two-step paraphrase: first summarize to condense, then maybe regenerate text.
    short_summary = summarizer("summarize: " + text, max_length=50, min_length=10, do_sample=False)
    short_summary_text = short_summary[0]['summary_text'] if short_summary else text
    # Now perhaps expand the summary back (this time treat summary as prompt for generation or another summary).
    expanded = summarizer("summarize: " + short_summary_text, max_length=len(text.split()), do_sample=False)
    paraphrased = expanded[0]['summary_text'] if expanded else short_summary_text
    return paraphrased

def format_apa_citation(authors, year, title, source=None, vol=None, issue=None, pages=None):
    """
    Format a citation in APA style.
    authors: string of authors (semicolon or comma separated names).
    year: string or int year.
    title: title of the work.
    source: e.g., journal or publisher.
    vol, issue, pages: for journal articles.
    """
    # Process authors into "Last, F. M." format
    author_str = ""
    if authors:
        # Split by ; or , assuming "First Last" names
        # If already in "Last, First" format, we might detect comma
        names = [a.strip() for a in re.split(r';|,', authors) if a.strip()]
        formatted_names = []
        for name in names:
            parts = name.split()
            if len(parts) == 0:
                continue
            if "," in name:
                # Name already like "Last, First"
                last_first = name
            else:
                last = parts[-1]
                first_parts = parts[:-1]
                initials = [p[0].upper() + "." for p in first_parts if p[0].isalpha()]
                last_first = f"{last}, {' '.join(initials)}"
            formatted_names.append(last_first)
        if len(formatted_names) == 0:
            author_str = ""
        elif len(formatted_names) == 1:
            author_str = formatted_names[0]
        elif len(formatted_names) == 2:
            author_str = f"{formatted_names[0]} & {formatted_names[1]}"
        else:
            # More than 2 authors: use Oxford comma and ampersand before last
            author_str = ", ".join(formatted_names[:-1]) + ", & " + formatted_names[-1]
    else:
        author_str = ""
    year_str = f"({year})" if year else "(n.d.)"
    title_str = f"*{title}*" if title else ""
    citation = ""
    if source:
        # Assume source is journal name or publisher
        if vol:
            # Format as Journal, vol(issue), pages.
            issue_part = f"({issue})" if issue else ""
            pages_part = f", {pages}" if pages else ""
            citation = f"{author_str} {year_str}. {title_str}. *{source}*, {vol}{issue_part}{pages_part}."
        else:
            # Book or other source without volume/issue
            citation = f"{author_str} {year_str}. {title_str}. {source}."
    else:
        citation = f"{author_str} {year_str}. {title_str}."
    return citation

def calculate_perplexity(text, model, tokenizer):
    """Calculate the perplexity of the given text using GPT-2 model (for AI detection)."""
    if not text or text.isspace():
        return None
    encodings = tokenizer(text, return_tensors='pt')
    with torch.no_grad():
        outputs = model(**encodings, labels=encodings["input_ids"])
        loss = outputs.loss
    perplexity = float(torch.exp(loss))
    return perplexity
