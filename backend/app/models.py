from sqlalchemy import Column, String, Integer, Numeric, Boolean, DateTime, ARRAY, Text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
from .database import Base

class Store(Base):
    __tablename__ = "stores"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    domain = Column(String(255), unique=True, nullable=False)
    logo_url = Column(Text)
    description = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    
    products = relationship("Product", back_populates="store")

class Product(Base):
    __tablename__ = "products"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    store_id = Column(UUID(as_uuid=True), ForeignKey("stores.id", ondelete="CASCADE"))
    title = Column(String(500), nullable=False)
    description = Column(Text, nullable=False)
    long_description = Column(Text)
    price = Column(Numeric(10, 2), nullable=False)
    currency = Column(String(3), default="USD")
    image_url = Column(Text)
    category = Column(String(100))
    keypoints = Column(ARRAY(Text))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    
    store = relationship("Store", back_populates="products")
    reviews = relationship("BaseReview", back_populates="product")

class User(Base):
    __tablename__ = "users"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255))
    email = Column(String(255), unique=True)
    is_verified_purchaser = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    total_reviews = Column(Integer, default=0)
    
    reviews = relationship("BaseReview", back_populates="user")

class BaseReview(Base):
    __tablename__ = "base_reviews"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    product_id = Column(UUID(as_uuid=True), ForeignKey("products.id", ondelete="CASCADE"))
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"))
    reviewer_name = Column(String(255))
    reviewer_email = Column(String(255))
    rating = Column(Integer, nullable=False)
    review_text = Column(Text, nullable=False)
    language = Column(String(10))
    is_verified_purchase = Column(Boolean, default=False)
    submitted_at = Column(DateTime, default=datetime.utcnow)
    ip_address = Column(String(45))
    
    product = relationship("Product", back_populates="reviews")
    user = relationship("User", back_populates="reviews")
    analysis = relationship("ReviewAnalysis", back_populates="review", uselist=False)
    published = relationship("PublishedReview", back_populates="review", uselist=False)
    rejected = relationship("RejectedReview", back_populates="review", uselist=False)
    ticket = relationship("SupportTicket", back_populates="review", uselist=False)

class ReviewAnalysis(Base):
    __tablename__ = "review_analysis"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    review_id = Column(UUID(as_uuid=True), ForeignKey("base_reviews.id", ondelete="CASCADE"), unique=True)
    category = Column(String(50), nullable=False)
    confidence = Column(Numeric(3, 2))
    reason = Column(Text)
    tags = Column(ARRAY(Text))
    severity = Column(String(20))
    recommended_action = Column(String(50))
    matched_description_points = Column(ARRAY(Text))
    suggested_automatic_response = Column(Text)
    value_score = Column(Numeric(5, 2), default=0)
    analyzed_at = Column(DateTime, default=datetime.utcnow)
    
    review = relationship("BaseReview", back_populates="analysis")
    published = relationship("PublishedReview", back_populates="analysis")
    rejected = relationship("RejectedReview", back_populates="analysis")
    ticket = relationship("SupportTicket", back_populates="analysis")

class PublishedReview(Base):
    __tablename__ = "published_reviews"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    review_id = Column(UUID(as_uuid=True), ForeignKey("base_reviews.id", ondelete="CASCADE"))
    analysis_id = Column(UUID(as_uuid=True), ForeignKey("review_analysis.id", ondelete="CASCADE"))
    is_shadow = Column(Boolean, default=False)
    automatic_response = Column(Text)
    response_language = Column(String(10), default="en")
    published_at = Column(DateTime, default=datetime.utcnow)
    views = Column(Integer, default=0)
    helpful_count = Column(Integer, default=0)
    
    review = relationship("BaseReview", back_populates="published")
    analysis = relationship("ReviewAnalysis", back_populates="published")

class RejectedReview(Base):
    __tablename__ = "rejected_reviews"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    review_id = Column(UUID(as_uuid=True), ForeignKey("base_reviews.id", ondelete="CASCADE"))
    analysis_id = Column(UUID(as_uuid=True), ForeignKey("review_analysis.id", ondelete="CASCADE"))
    rejection_reason = Column(Text, nullable=False)
    user_notified = Column(Boolean, default=False)
    notification_message = Column(Text)
    rejected_at = Column(DateTime, default=datetime.utcnow)
    
    review = relationship("BaseReview", back_populates="rejected")
    analysis = relationship("ReviewAnalysis", back_populates="rejected")

class SupportTicket(Base):
    __tablename__ = "support_tickets"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    review_id = Column(UUID(as_uuid=True), ForeignKey("base_reviews.id", ondelete="CASCADE"))
    analysis_id = Column(UUID(as_uuid=True), ForeignKey("review_analysis.id", ondelete="CASCADE"))
    priority = Column(String(20), default="normal")
    status = Column(String(20), default="open")
    assigned_to = Column(String(255))
    issue_description = Column(Text)
    customer_email = Column(String(255))
    automatic_response = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    resolved_at = Column(DateTime)
    
    review = relationship("BaseReview", back_populates="ticket")
    analysis = relationship("ReviewAnalysis", back_populates="ticket")

class AdminAction(Base):
    __tablename__ = "admin_actions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    admin_user = Column(String(255), nullable=False)
    action_type = Column(String(50), nullable=False)
    target_id = Column(UUID(as_uuid=True), nullable=False)
    target_type = Column(String(50), nullable=False)
    reason = Column(Text)
    old_value = Column(Text)
    new_value = Column(Text)
    performed_at = Column(DateTime, default=datetime.utcnow)
