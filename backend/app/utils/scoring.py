from typing import List
import math

def calculate_value_score(
    review_text: str,
    product_description: str,
    keypoints: List[str],
    matched_keypoints: List[str],
    is_verified_purchase: bool,
    sentiment_score: float,
    semantic_similarity: float
) -> float:
    """
    Calculate the value score for a review based on multiple factors.
    
    Formula: V = 0.30*K + 0.25*D + 0.15*L + 0.10*P + 0.10*S + 0.10*U
    
    Where:
    - K: Semantic similarity to product description (0-1)
    - D: Number of matched product keypoints (normalized)
    - L: Length score (normalized)
    - P: Verified purchase bonus (0 or 1)
    - S: Sentiment depth/confidence score
    - U: Usefulness factor (placeholder, can be updated based on user feedback)
    """
    
    # K: Semantic similarity (0-1) - 30%
    K = semantic_similarity
    
    # D: Matched keypoints score (0-1) - 25%
    if keypoints and len(keypoints) > 0:
        D = min(len(matched_keypoints) / len(keypoints), 1.0)
    else:
        D = 0.5  # Default if no keypoints
    
    # L: Length score (0-1) - 15%
    # Optimal length is 100-500 characters
    text_length = len(review_text)
    if text_length < 50:
        L = text_length / 50  # Penalize very short reviews
    elif text_length <= 500:
        L = 1.0
    else:
        # Slight penalty for very long reviews
        L = max(0.7, 1.0 - (text_length - 500) / 1000)
    
    # P: Verified purchase (0 or 1) - 10%
    P = 1.0 if is_verified_purchase else 0.0
    
    # S: Sentiment depth/confidence (0-1) - 10%
    S = sentiment_score
    
    # U: Usefulness (placeholder, defaults to 0.5) - 10%
    # This can be updated based on user "helpful" votes
    U = 0.5
    
    # Calculate final score
    V = (0.30 * K) + (0.25 * D) + (0.15 * L) + (0.10 * P) + (0.10 * S) + (0.10 * U)
    
    # Normalize to 0-100 scale
    return round(V * 100, 2)

def normalize_score(score: float, min_val: float = 0, max_val: float = 100) -> float:
    """Normalize a score to a 0-100 scale."""
    return max(min_val, min(score, max_val))
