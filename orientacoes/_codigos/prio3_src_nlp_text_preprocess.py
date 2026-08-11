import unicodedata, spacy

# Load the Portuguese model once
nlp = spacy.load("pt_core_news_sm", disable=["ner", "parser"])

def strip_accents(text: str) -> str:
    """Remove accents so 'produção' → 'producao'.  Optional but helps matching."""
    return unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode()

def preprocess(text: str) -> str:
    """
    Lower-case, accent-strip (optional), tokenize, lemmatise,
    drop stop-words & non-alpha tokens, then return a clean string.
    """
    text = strip_accents(text.lower())

    doc = nlp(text)

    tokens = [
        tok.lemma_                       # lemmatised base form
        for tok in doc
        if tok.is_alpha                  # keep purely alphabetic tokens
        and not tok.is_stop              # remove stop-words
    ]

    return " ".join(tokens)