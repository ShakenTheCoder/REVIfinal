from typing import List, Dict
from collections import Counter
import re
from ..ai.embeddings import get_embedding_service

class ReviewInsightsGenerator:
    """
    Generates AI-powered insights for review sections.
    Extracts key themes, common praises, and complaints from reviews.
    """
    
    def __init__(self):
        self.embedding_service = get_embedding_service()
        
        # Common positive indicators
        self.positive_indicators = [
            'quality', 'excellent', 'great', 'perfect', 'love', 'amazing', 'recommend',
            'fantastic', 'wonderful', 'best', 'awesome', 'superb', 'brilliant',
            'calitate', 'excelent', 'perfect', 'recomandat', 'minunat', 'fantastic'
        ]
        
        # Common negative indicators
        self.negative_indicators = [
            'broken', 'defect', 'poor', 'bad', 'terrible', 'worst', 'disappointed',
            'problem', 'issue', 'waste', 'cheap', 'useless', 'failed', 'horrible',
            'stricat', 'prost', 'problema', 'dezamagit', 'ieftin', 'groaznic'
        ]
        
        # Feature categories
        self.feature_categories = {
            'quality': ['quality', 'durability', 'build', 'material', 'sturdy', 'solid', 'calitate', 'durabilitate'],
            'performance': ['performance', 'works', 'working', 'fast', 'speed', 'efficient', 'performanta', 'functioneaza'],
            'design': ['design', 'look', 'appearance', 'style', 'beautiful', 'aesthetic', 'aspect', 'frumos'],
            'value': ['price', 'value', 'worth', 'affordable', 'expensive', 'cheap', 'pret', 'valoare'],
            'usability': ['easy', 'simple', 'comfortable', 'convenient', 'user-friendly', 'usor', 'simplu', 'confortabil']
        }
    
    def generate_insights(
        self,
        reviews: List[Dict],
        category: str = 'positive'
    ) -> Dict:
        """
        Generate AI insights for a collection of reviews.
        
        Args:
            reviews: List of review dicts with keys: rating, review_text, value_score
            category: 'positive' or 'negative'
        
        Returns:
            Dict with summary, key_themes, common_phrases, sentiment_breakdown
        """
        if not reviews:
            return {
                "summary": f"No {category} reviews yet.",
                "key_themes": [],
                "common_points": [],
                "review_count": 0,
                "average_value_score": 0.0
            }
        
        # Extract high-value reviews (they matter most)
        high_value_reviews = [r for r in reviews if r.get('value_score', 0) >= 50]
        if not high_value_reviews:
            high_value_reviews = reviews[:5]  # At least use top 5
        
        # Extract themes and features mentioned
        themes = self._extract_themes(high_value_reviews, category)
        
        # Extract common points (specific praise or complaints)
        common_points = self._extract_common_points(high_value_reviews, category)
        
        # Calculate statistics
        avg_value_score = sum(r.get('value_score', 0) for r in reviews) / len(reviews)
        
        # Generate summary text
        summary = self._generate_summary_text(themes, common_points, category, len(reviews))
        
        return {
            "summary": summary,
            "key_themes": themes[:5],  # Top 5 themes
            "common_points": common_points[:3],  # Top 3 specific points
            "review_count": len(reviews),
            "average_value_score": round(avg_value_score, 1)
        }
    
    def _extract_themes(self, reviews: List[Dict], category: str) -> List[Dict]:
        """Extract key themes from reviews based on feature categories."""
        theme_scores = {}
        
        for review in reviews:
            text = review.get('review_text', '').lower()
            value_score = review.get('value_score', 50)
            weight = value_score / 100.0  # Higher value reviews influence more
            
            for theme, keywords in self.feature_categories.items():
                matches = sum(1 for keyword in keywords if keyword in text)
                if matches > 0:
                    if theme not in theme_scores:
                        theme_scores[theme] = {'count': 0, 'weight': 0.0}
                    theme_scores[theme]['count'] += matches
                    theme_scores[theme]['weight'] += weight * matches
        
        # Sort by weighted score
        sorted_themes = sorted(
            theme_scores.items(),
            key=lambda x: x[1]['weight'],
            reverse=True
        )
        
        return [
            {
                "name": theme,
                "mentions": data['count'],
                "weight": round(data['weight'], 2)
            }
            for theme, data in sorted_themes
        ]
    
    def _extract_common_points(self, reviews: List[Dict], category: str) -> List[str]:
        """Extract common specific points from reviews."""
        # Use sentiment indicators to find key phrases
        indicators = self.positive_indicators if category == 'positive' else self.negative_indicators
        
        phrases = []
        for review in reviews[:10]:  # Analyze top 10 high-value reviews
            text = review.get('review_text', '')
            sentences = re.split(r'[.!?]+', text)
            
            for sentence in sentences:
                sentence = sentence.strip()
                if len(sentence) < 15 or len(sentence) > 150:
                    continue
                
                sentence_lower = sentence.lower()
                # Check if sentence contains relevant indicators
                if any(indicator in sentence_lower for indicator in indicators):
                    phrases.append(sentence)
        
        # Return most common or representative phrases
        if not phrases:
            return []
        
        # Simple frequency-based selection
        phrase_counts = Counter(phrases)
        common_phrases = [phrase for phrase, count in phrase_counts.most_common(5)]
        
        # If we have duplicates or too few, take unique first sentences
        if len(common_phrases) < 3:
            for review in reviews[:5]:
                text = review.get('review_text', '')
                first_sentence = re.split(r'[.!?]+', text)[0].strip()
                if first_sentence and first_sentence not in common_phrases:
                    common_phrases.append(first_sentence)
                if len(common_phrases) >= 3:
                    break
        
        return common_phrases[:3]
    
    def _generate_summary_text(
        self,
        themes: List[Dict],
        common_points: List[str],
        category: str,
        count: int
    ) -> str:
        """Generate a natural language summary of the insights."""
        if not themes:
            return f"Based on {count} {category} reviews, customers have mixed feedback."
        
        top_theme = themes[0]['name'] if themes else 'overall experience'
        
        if category == 'positive':
            summary = f"Based on {count} positive reviews, customers particularly appreciate the {top_theme}. "
            
            if len(themes) > 1:
                other_themes = ', '.join([t['name'] for t in themes[1:3]])
                summary += f"Other frequently praised aspects include {other_themes}. "
            
            summary += "These reviews tend to be detailed and specific, providing valuable insights."
        
        else:  # negative
            summary = f"Based on {count} negative reviews, the main concerns relate to {top_theme}. "
            
            if len(themes) > 1:
                other_themes = ', '.join([t['name'] for t in themes[1:3]])
                summary += f"Customers also mention issues with {other_themes}. "
            
            summary += "These reviews highlight areas that may need attention."
        
        return summary


# Global insights generator instance
_insights_generator = None

def get_insights_generator() -> ReviewInsightsGenerator:
    global _insights_generator
    if _insights_generator is None:
        _insights_generator = ReviewInsightsGenerator()
    return _insights_generator
