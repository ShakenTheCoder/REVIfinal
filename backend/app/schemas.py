from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from uuid import UUID

class ReviewSubmission(BaseModel):
    product_id: str
    reviewer_name: Optional[str] = None
    reviewer_email: Optional[str] = None
    rating: int = Field(..., ge=1, le=5)
    review_text: str
    is_verified_purchase: bool = False

class ReviewAnalysisResult(BaseModel):
    review_id: str
    category: str
    confidence: float
    reason: str
    tags: List[str]
    severity: str
    matched_description_points: List[str]
    recommended_action: str
    suggested_automatic_response: str

class ProductResponse(BaseModel):
    id: UUID
    store_id: UUID
    title: str
    description: str
    long_description: Optional[str]
    price: float
    currency: str
    image_url: Optional[str]
    category: Optional[str]
    keypoints: Optional[List[str]]
    created_at: datetime
    
    class Config:
        from_attributes = True

class PublicReviewResponse(BaseModel):
    id: str
    reviewer_name: Optional[str]
    rating: int
    review_text: str
    is_verified_purchase: bool
    submitted_at: datetime
    automatic_response: Optional[str]
    value_score: float
    helpful_count: int
    
    class Config:
        from_attributes = True

class AdminReviewResponse(BaseModel):
    id: str
    product_id: str
    reviewer_name: Optional[str]
    reviewer_email: Optional[str]
    rating: int
    review_text: str
    language: Optional[str]
    is_verified_purchase: bool
    submitted_at: datetime
    category: Optional[str]
    confidence: Optional[float]
    reason: Optional[str]
    tags: Optional[List[str]]
    value_score: Optional[float]
    
    class Config:
        from_attributes = True

class SupportTicketResponse(BaseModel):
    id: str
    review_id: str
    priority: str
    status: str
    assigned_to: Optional[str]
    issue_description: Optional[str]
    customer_email: Optional[str]
    automatic_response: Optional[str]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class TicketAssignment(BaseModel):
    assigned_to: str

class ReviewOverride(BaseModel):
    new_category: str
    reason: str
    admin_user: str
