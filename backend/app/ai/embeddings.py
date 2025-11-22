from sentence_transformers import SentenceTransformer
import numpy as np
from typing import List
import torch

class EmbeddingService:
    def __init__(self):
        # Use multilingual sentence transformer for English and Romanian
        self.model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
        
    def get_embedding(self, text: str) -> np.ndarray:
        return self.model.encode(text, convert_to_numpy=True)
    
    def calculate_similarity(self, text1: str, text2: str) -> float:
        embeddings = self.model.encode([text1, text2], convert_to_numpy=True)
        
        # Cosine similarity
        similarity = np.dot(embeddings[0], embeddings[1]) / (
            np.linalg.norm(embeddings[0]) * np.linalg.norm(embeddings[1])
        )
        
        return float(similarity)
    
    def calculate_similarity_to_keypoints(self, review_text: str, keypoints: List[str]) -> float:
        if not keypoints:
            return 0.0
        
        review_embedding = self.get_embedding(review_text)
        keypoints_text = " ".join(keypoints)
        keypoints_embedding = self.get_embedding(keypoints_text)
        
        similarity = np.dot(review_embedding, keypoints_embedding) / (
            np.linalg.norm(review_embedding) * np.linalg.norm(keypoints_embedding)
        )
        
        return float(similarity)

# Global embedding service instance
_embedding_service = None

def get_embedding_service() -> EmbeddingService:
    global _embedding_service
    if _embedding_service is None:
        _embedding_service = EmbeddingService()
    return _embedding_service
