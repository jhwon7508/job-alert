from typing import List, Tuple
from .config import KeywordsConfig, ScoringConfig

def score_job(
    title: str, 
    body: str, 
    keywords: KeywordsConfig, 
    scoring: ScoringConfig
) -> Tuple[int, str]:
    """
    Score a job based on title and body keywords.
    Returns (score, reason).
    """
    score = 0
    matched_includes = []
    
    title_lower = title.lower()
    body_lower = body.lower()
    
    # Check exclude keywords first
    for word in keywords.exclude:
        if word.lower() in title_lower or word.lower() in body_lower:
            return scoring.exclude_penalty, f"Excluded by keyword: {word}"
            
    # Score include keywords
    for word in keywords.include:
        word_lower = word.lower()
        if word_lower in title_lower:
            score += scoring.title_hit
            matched_includes.append(f"{word}(title)")
        elif word_lower in body_lower:
            score += scoring.body_hit
            matched_includes.append(f"{word}(body)")
            
    reason = "Matched keywords: " + ", ".join(matched_includes) if matched_includes else "No specific matches"
    return score, reason
