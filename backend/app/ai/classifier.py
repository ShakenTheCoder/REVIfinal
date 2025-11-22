from transformers import AutoTokenizer, AutoModelForSequenceClassification, pipeline
import torch
import json
import re
from typing import Dict, List

class ReviewClassifier:
    def __init__(self):
        self.device = 0 if torch.cuda.is_available() else -1
        
        # Use XLM-RoBERTa for multilingual sentiment analysis
        model_name = "cardiffnlp/twitter-xlm-roberta-base-sentiment"
        self.sentiment_pipeline = pipeline(
            "sentiment-analysis",
            model=model_name,
            tokenizer=model_name,
            device=self.device
        )
        
        # Positive sentiment templates to detect generic reviews
        self.generic_positive_patterns = [
            r"^great\s*product\s*!*$",
            r"^excellent\s*!*$",
            r"^good\s*!*$",
            r"^amazing\s*!*$",
            r"^awesome\s*!*$",
            r"^love\s*it\s*!*$",
            r"^perfect\s*!*$",
            r"^produs\s*bun\s*!*$",
            r"^excelent\s*!*$",
        ]
        
        # Support keywords in English and Romanian
        self.support_keywords = [
            "broken", "defect", "not working", "doesn't work", "problem", "issue",
            "fault", "damaged", "malfunction", "error", "failed", "stopped working",
            "help", "support", "warranty", "refund", "return", "exchange",
            "stricat", "defect", "nu functioneaza", "nu merge", "problema", "issue",
            "deteriorat", "eroare", "garantie", "returnare"
        ]
        
    def classify_review(
        self,
        review_id: str,
        review_text: str,
        rating: int,
        product_description: str,
        product_keypoints: List[str],
        is_verified_purchase: bool = False
    ) -> Dict:
        # System prompt for classification logic
        system_prompt = """You are REVI, an AI system for automated review moderation.

Task:
Classify the given review into EXACTLY one of:
- public_positive
- public_negative
- support
- shadow
- rejected

Languages: English and Romanian as input. Responses must ALWAYS be in English.

Rules:
Positive relevant → public_positive
Negative relevant → public_negative
Technical complaint → support
5-star but generic or bot-like → shadow
Irrelevant or contradicts product facts → rejected

Always return strict JSON following this schema:
{review_id, category, confidence, reason, tags, severity,
matched_description_points, recommended_action, suggested_automatic_response}

DO NOT include markdown. DO NOT include natural language outside the JSON."""
        
        # Analyze sentiment
        sentiment_result = self.sentiment_pipeline(review_text[:512])[0]
        sentiment_label = sentiment_result['label'].lower()
        sentiment_score = sentiment_result['score']
        
        # Detect language
        language = self._detect_language(review_text)
        
        # Check for support keywords
        has_support_keywords = any(keyword in review_text.lower() for keyword in self.support_keywords)
        
        # Check if review is generic/bot-like
        is_generic = self._is_generic_review(review_text, rating)
        
        # Match product keypoints
        matched_points = self._match_keypoints(review_text, product_keypoints, product_description)
        
        # Extract tags
        tags = self._extract_tags(review_text, product_keypoints)
        
        # Classification logic
        category = self._determine_category(
            review_text=review_text,
            rating=rating,
            sentiment_label=sentiment_label,
            sentiment_score=sentiment_score,
            has_support_keywords=has_support_keywords,
            is_generic=is_generic,
            matched_points=matched_points,
            product_description=product_description
        )
        
        # Determine confidence
        confidence = self._calculate_confidence(
            sentiment_score=sentiment_score,
            matched_points_count=len(matched_points),
            is_generic=is_generic,
            has_support_keywords=has_support_keywords
        )
        
        # Generate reason
        reason = self._generate_reason(category, sentiment_label, matched_points, is_generic, has_support_keywords)
        
        # Determine severity
        severity = self._determine_severity(category, rating, has_support_keywords)
        
        # Recommended action
        recommended_action = self._get_recommended_action(category)
        
        # Generate automatic response
        automatic_response = self._generate_automatic_response(category, rating, is_verified_purchase)
        
        return {
            "review_id": review_id,
            "category": category,
            "confidence": round(confidence, 2),
            "reason": reason,
            "tags": tags,
            "severity": severity,
            "matched_description_points": matched_points,
            "recommended_action": recommended_action,
            "suggested_automatic_response": automatic_response
        }
    
    def _detect_language(self, text: str) -> str:
        romanian_chars = ['ă', 'â', 'î', 'ș', 'ț', 'Ă', 'Â', 'Î', 'Ș', 'Ț']
        romanian_words = ['produs', 'foarte', 'calitate', 'bun', 'excelent', 'recomand']
        
        if any(char in text for char in romanian_chars):
            return "ro"
        if any(word in text.lower() for word in romanian_words):
            return "ro"
        return "en"
    
    def _is_generic_review(self, text: str, rating: int) -> bool:
        if rating < 5:
            return False
        
        text_clean = text.lower().strip()
        
        # Very short reviews are more likely to be generic
        if len(text_clean) < 30:
            for pattern in self.generic_positive_patterns:
                if re.match(pattern, text_clean, re.IGNORECASE):
                    return True
            
            # Additional check: if it's just one or two words and 5 stars, likely generic
            word_count = len(text_clean.split())
            if word_count <= 3:
                return True
        
        return False
    
    def _match_keypoints(self, review_text: str, keypoints: List[str], description: str) -> List[str]:
        matched = []
        review_lower = review_text.lower()
        
        if keypoints:
            for keypoint in keypoints:
                keypoint_lower = keypoint.lower()
                keywords = keypoint_lower.split()
                if any(keyword in review_lower for keyword in keywords):
                    matched.append(keypoint)
        
        return matched
    
    def _extract_tags(self, review_text: str, keypoints: List[str]) -> List[str]:
        tags = []
        review_lower = review_text.lower()
        
        # Quality indicators
        if any(word in review_lower for word in ['quality', 'premium', 'excellent', 'great', 'perfect', 'calitate', 'excelent']):
            tags.append('quality')
        
        # Price indicators
        if any(word in review_lower for word in ['price', 'expensive', 'cheap', 'value', 'worth', 'pret', 'scump', 'ieftin']):
            tags.append('price')
        
        # Performance indicators
        if any(word in review_lower for word in ['performance', 'works', 'working', 'fast', 'slow', 'functioneaza', 'performanta']):
            tags.append('performance')
        
        # Design indicators
        if any(word in review_lower for word in ['design', 'look', 'appearance', 'beautiful', 'ugly', 'aspect', 'frumos']):
            tags.append('design')
        
        # Durability indicators
        if any(word in review_lower for word in ['durable', 'broke', 'broken', 'lasted', 'durabilitate', 'rezistent']):
            tags.append('durability')
        
        return tags
    
    def _determine_category(
        self,
        review_text: str,
        rating: int,
        sentiment_label: str,
        sentiment_score: float,
        has_support_keywords: bool,
        is_generic: bool,
        matched_points: List[str],
        product_description: str
    ) -> str:
        review_lower = review_text.lower()
        text_length = len(review_text)
        
        # CATEGORY 3: Support - highest priority
        if has_support_keywords and rating <= 3:
            return "support"
        
        # CATEGORY 5: Rejected - contradicts product or completely irrelevant
        if self._contradicts_description(review_text, product_description):
            return "rejected"
        
        # Improved relevance check: consider both length and matched points
        if len(matched_points) == 0 and text_length > 100:
            # Long review with no matched keypoints might be irrelevant
            # But only reject if it's also very negative
            if rating <= 2:
                return "rejected"
        
        # CATEGORY 4: Shadow - generic 5-star reviews ONLY if truly generic
        # Don't shadow-ban reviews that are detailed even if they're positive
        if is_generic and rating == 5:
            # Extra check: if review has matched keypoints, it's not truly generic
            if len(matched_points) == 0:
                return "shadow"
        
        # CATEGORY 1 & 2: Public positive or negative
        # Improved logic: use both rating and sentiment
        if rating >= 4:
            # High rating reviews
            if 'negative' in sentiment_label and sentiment_score > 0.7:
                # Mixed review: high rating but negative sentiment (confusion or sarcasm)
                # Treat carefully - publish as positive but could be reviewed
                return "public_positive"
            return "public_positive"
        elif rating <= 2:
            # Low rating reviews
            return "public_negative"
        else:
            # Rating = 3 (neutral)
            # Use sentiment to decide
            if 'positive' in sentiment_label:
                return "public_positive"
            else:
                return "public_negative"
    
    def _contradicts_description(self, review_text: str, product_description: str) -> bool:
        # Simple contradiction detection
        review_lower = review_text.lower()
        description_lower = product_description.lower()
        
        # Color contradictions
        colors = ['red', 'blue', 'green', 'black', 'white', 'yellow', 'pink', 'purple', 'rosu', 'albastru', 'verde', 'negru', 'alb']
        review_colors = [color for color in colors if color in review_lower]
        description_colors = [color for color in colors if color in description_lower]
        
        if review_colors and description_colors:
            if not any(color in description_colors for color in review_colors):
                return True
        
        return False
    
    def _calculate_confidence(
        self,
        sentiment_score: float,
        matched_points_count: int,
        is_generic: bool,
        has_support_keywords: bool
    ) -> float:
        base_confidence = sentiment_score
        
        # Adjust based on matched keypoints
        if matched_points_count > 0:
            base_confidence += 0.1 * min(matched_points_count, 3)
        
        # High confidence for generic detection
        if is_generic:
            base_confidence = max(base_confidence, 0.85)
        
        # High confidence for support keywords
        if has_support_keywords:
            base_confidence = max(base_confidence, 0.80)
        
        return min(base_confidence, 1.0)
    
    def _generate_reason(
        self,
        category: str,
        sentiment_label: str,
        matched_points: List[str],
        is_generic: bool,
        has_support_keywords: bool
    ) -> str:
        if category == "public_positive":
            reason = f"Positive review with {sentiment_label} sentiment."
            if matched_points:
                reason += f" Mentions product features: {', '.join(matched_points[:3])}."
            return reason
        
        elif category == "public_negative":
            reason = f"Negative review with {sentiment_label} sentiment."
            if matched_points:
                reason += f" References product features: {', '.join(matched_points[:3])}."
            return reason
        
        elif category == "support":
            return "Review contains technical issues or support requests that require attention."
        
        elif category == "shadow":
            return "Generic positive review without substantive content. Published but shadow-banned."
        
        elif category == "rejected":
            return "Review is irrelevant or contradicts product description."
        
        return "Review classified based on content analysis."
    
    def _determine_severity(self, category: str, rating: int, has_support_keywords: bool) -> str:
        if category == "support":
            return "high" if rating <= 2 else "medium"
        
        if category == "public_negative" and rating <= 2:
            return "high"
        
        if category == "rejected":
            return "low"
        
        return "low"
    
    def _get_recommended_action(self, category: str) -> str:
        actions = {
            "public_positive": "publish",
            "public_negative": "publish",
            "support": "create_ticket",
            "shadow": "publish_shadow",
            "rejected": "reject"
        }
        return actions.get(category, "review")
    
    def _generate_automatic_response(self, category: str, rating: int, is_verified_purchase: bool) -> str:
        if category == "public_positive":
            responses = [
                "Thank you so much for your wonderful review! We're thrilled that you're enjoying your purchase.",
                "We really appreciate you taking the time to share your experience with us. Thank you!",
                "Thank you for your kind words! We're so happy you're satisfied with your purchase.",
            ]
            return responses[rating % len(responses)]
        
        elif category == "public_negative":
            return "We're sorry to hear about your experience. We take all feedback seriously and will use this to improve."
        
        elif category == "support":
            return "Your issue has been recognized. A support agent will contact you shortly to resolve this matter."
        
        return ""

# Global classifier instance
_classifier = None

def get_classifier() -> ReviewClassifier:
    global _classifier
    if _classifier is None:
        _classifier = ReviewClassifier()
    return _classifier
