"""
Sentiment scorer for Portuguese financial headlines (PRIO3 project)

• primary model  : lucas-leme/FinBERT-PT-BR = labels POSITIVE / NEGATIVE / NEUTRAL
• numeric score  : {+0.5, -0.5, 0}
"""

from transformers import pipeline
from nltk.sentiment import SentimentIntensityAnalyzer
import unicodedata, re

# PT-BR FinBERT pipeline
_pt_pipeline = pipeline(
    task="text-classification",
    model="lucas-leme/FinBERT-PT-BR",
    tokenizer="lucas-leme/FinBERT-PT-BR",
    truncation=True,
    max_length=512,
)

LABEL2COMP = {"POSITIVE": 0.5, "NEGATIVE": -0.5, "NEUTRAL": 0.0}

# English fallback (VADER)
_sia = SentimentIntensityAnalyzer()

def _score_en(text: str) -> dict:
    """Very small helper for English-only lines"""
    comp_raw = _sia.polarity_scores(text)["compound"]
    comp = 0.5 if comp_raw >  0.2 else -0.5 if comp_raw < -0.2 else 0.0
    label = "Positive" if comp > 0 else "Negative" if comp < 0 else "Neutral"
    return {"compound": comp, "sentiment": label}

# Simple language heuristic
_pt_regex = re.compile(r"[áàâãéèêíìîóòôõúùüç]")

def score(text: str) -> dict:
    """
    Returns
        compound : float in { -0.5, 0.0, +0.5 }
        sentiment: 'Negative' | 'Neutral' | 'Positive'
    """
    # if the headline has PT accents, assume Portuguese → FinBERT-PT-BR
    try:
        if _pt_regex.search(text.lower()):
            pred = _pt_pipeline(text[:512])[0]     
            label = pred["label"].upper()
            return {
                "compound": LABEL2COMP.get(label, 0.0),
                "sentiment": label.capitalize(),
            }
        # else fallback to English VADER
        return _score_en(text)
    except Exception:  
        return _score_en(text)