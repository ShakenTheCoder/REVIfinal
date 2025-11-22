from typing import List, Dict
import math
import re

def calculate_value_score(
    review_text: str,
    product_description: str,
    keypoints: List[str],
    matched_keypoints: List[str],
    is_verified_purchase: bool,
    sentiment_score: float,
    semantic_similarity: float,
    is_shadow: bool = False
) -> float:
    """
    Enhanced value score calculation that rewards detailed, specific reviews.
    
    Formula: V = 0.25*K + 0.25*D + 0.15*L + 0.10*P + 0.10*S + 0.10*U + 0.05*X
    
    Where:
    - K: Semantic similarity to product description (0-1)
    - D: Matched product keypoints score (0-1)
    - L: Length and detail score (0-1)
    - P: Verified purchase bonus (0 or 1)
    - S: Sentiment depth/confidence score (0-1)
    - U: Usefulness factor (0-1)
    - X: Specificity bonus (0-1) - rewards detailed, specific content
    
    Shadow reviews get a 0.4x multiplier to reduce their weight.
    """
    
    # K: Semantic similarity (0-1) - 25%
    K = semantic_similarity
    
    # D: Enhanced matched keypoints score (0-1) - 25%
    # Give bonus for matching multiple keypoints
    if keypoints and len(keypoints) > 0:
        match_ratio = len(matched_keypoints) / len(keypoints)
        # Bonus for matching multiple points
        if len(matched_keypoints) >= 2:
            D = min(match_ratio + 0.2, 1.0)
        else:
            D = match_ratio
    else:
        D = 0.3  # Lower default if no keypoints available
    
    # L: Enhanced length and detail score (0-1) - 15%
    text_length = len(review_text)
    word_count = len(review_text.split())
    
    # Reward longer, more detailed reviews
    if text_length < 30:
        L = text_length / 30 * 0.5  # Very short reviews penalized heavily
    elif text_length <= 100:
        L = 0.5 + (text_length - 30) / 70 * 0.3  # 0.5 to 0.8
    elif text_length <= 300:
        L = 0.8 + (text_length - 100) / 200 * 0.2  # 0.8 to 1.0
    elif text_length <= 600:
        L = 1.0  # Optimal length
    else:
        # Slight penalty for extremely long reviews but not too harsh
        L = max(0.85, 1.0 - (text_length - 600) / 1500)
    
    # P: Verified purchase (0 or 1) - 10%
    P = 1.0 if is_verified_purchase else 0.4
    
    # S: Sentiment depth/confidence (0-1) - 10%
    S = sentiment_score
    
    # U: Enhanced usefulness score (0-1) - 10%
    # Based on unique words and vocabulary richness
    unique_words = len(set(review_text.lower().split()))
    if word_count > 0:
        vocabulary_richness = min(unique_words / word_count, 1.0)
        U = 0.3 + (vocabulary_richness * 0.7)
    else:
        U = 0.3
    
    # X: NEW - Specificity bonus (0-1) - 5%
    # Rewards references to specific product features, measurements, comparisons
    X = calculate_specificity_score(review_text, product_description, keypoints)
    
    # Calculate base score
    base_score = (0.25 * K) + (0.25 * D) + (0.15 * L) + (0.10 * P) + (0.10 * S) + (0.10 * U) + (0.05 * X)
    
    # Apply shadow penalty
    if is_shadow:
        base_score *= 0.4  # Shadow reviews weigh much less
    
    # Normalize to 0-100 scale
    return round(base_score * 100, 2)


def calculate_specificity_score(review_text: str, product_description: str, keypoints: List[str]) -> float:
    """
    Calculate how specific and detailed a review is based on:
    - References to measurements/numbers
    - Product-specific terminology
    - Comparative language
    - Detailed feature descriptions
    """
    score = 0.0
    review_lower = review_text.lower()
    
    # Check for numbers/measurements (indicates specificity)
    has_numbers = bool(re.search(r'\d+', review_text))
    if has_numbers:
        score += 0.3
    
    # Check for comparative language
    comparative_words = ['better', 'worse', 'compared', 'than', 'versus', 'vs', 'mai bun', 'mai rau', 'comparativ']
    if any(word in review_lower for word in comparative_words):
        score += 0.2
    
    # Check for detailed descriptors (adjectives + nouns)
    detail_patterns = [
        r'very \w+', r'extremely \w+', r'really \w+', r'quite \w+',
        r'foarte \w+', r'extrem de \w+'
    ]
    for pattern in detail_patterns:
        if re.search(pattern, review_lower):
            score += 0.1
            break
    
    # Check for specific feature mentions beyond just keypoints
    feature_words = ['feature', 'quality', 'material', 'design', 'function', 'performance',
                     'caracteristica', 'calitate', 'material', 'design', 'functie', 'performanta']
    feature_mentions = sum(1 for word in feature_words if word in review_lower)
    if feature_mentions > 0:
        score += min(feature_mentions * 0.15, 0.4)
    
    return min(score, 1.0)


def calculate_weighted_product_rating(
    reviews_data: List[Dict],
    include_shadow: bool = True
) -> Dict[str, float]:
    """
    Calculate weighted average product rating based on all reviews.
    More detailed and specific reviews have more influence on the overall rating.
    
    Args:
        reviews_data: List of dicts with keys: rating, value_score, category, is_shadow, is_verified_purchase
        include_shadow: Whether to include shadow-banned reviews (with reduced weight)
    
    Returns:
        Dict with weighted_rating, total_reviews, positive_ratio, confidence_score
    """
    if not reviews_data:
        return {
            "weighted_rating": 0.0,
            "total_reviews": 0,
            "positive_ratio": 0.0,
            "confidence_score": 0.0
        }
    
    weighted_sum = 0.0
    total_weight = 0.0
    positive_count = 0
    total_count = 0
    
    for review in reviews_data:
        rating = review.get('rating', 0)
        value_score = review.get('value_score', 0)
        category = review.get('category', '')
        is_shadow = review.get('is_shadow', False)
        is_verified = review.get('is_verified_purchase', False)
        
        # Skip if filtering out shadow reviews
        if is_shadow and not include_shadow:
            continue
        
        # Calculate weight for this review
        weight = calculate_review_weight(value_score, category, is_shadow, is_verified)
        
        weighted_sum += rating * weight
        total_weight += weight
        total_count += 1
        
        if rating >= 4:
            positive_count += 1
    
    # Calculate final metrics
    weighted_rating = weighted_sum / total_weight if total_weight > 0 else 0.0
    positive_ratio = positive_count / total_count if total_count > 0 else 0.0
    
    # Confidence score based on number of high-value reviews
    high_value_reviews = sum(1 for r in reviews_data if r.get('value_score', 0) >= 60)
    confidence_score = min(high_value_reviews / 10, 1.0)  # Max confidence at 10+ high-value reviews
    
    return {
        "weighted_rating": round(weighted_rating, 2),
        "total_reviews": total_count,
        "positive_ratio": round(positive_ratio, 2),
        "confidence_score": round(confidence_score, 2)
    }


def calculate_review_weight(
    value_score: float,
    category: str,
    is_shadow: bool,
    is_verified_purchase: bool
) -> float:
    """
    Calculate the weight of a review for the overall product rating.
    
    Weights are based on:
    - Value score: Higher value = more weight
    - Category: Public reviews > Support > Shadow > Rejected
    - Verification status: Verified purchases get bonus weight
    """
    # Base weight from value score (normalized 0-1)
    base_weight = value_score / 100.0
    
    # Category multiplier
    category_multipliers = {
        'public_positive': 1.0,
        'public_negative': 1.0,
        'support': 0.8,  # Support issues still count but slightly less
        'shadow': 0.3,   # Shadow reviews have minimal influence
        'rejected': 0.0  # Rejected reviews don't count
    }
    category_mult = category_multipliers.get(category, 0.5)
    
    # Verification bonus
    verification_mult = 1.2 if is_verified_purchase else 1.0
    
    # Shadow penalty (additional to category)
    shadow_mult = 0.4 if is_shadow else 1.0
    
    final_weight = base_weight * category_mult * verification_mult * shadow_mult
    
    # Ensure minimum weight for any published review
    if category in ['public_positive', 'public_negative'] and not is_shadow:
        final_weight = max(final_weight, 0.1)
    
    return max(final_weight, 0.01)  # Minimum weight to avoid division by zero


def normalize_score(score: float, min_val: float = 0, max_val: float = 100) -> float:
    """Normalize a score to a 0-100 scale."""
    return max(min_val, min(score, max_val))
