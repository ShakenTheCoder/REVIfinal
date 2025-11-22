from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import and_, desc
from typing import List
from uuid import UUID
import uuid

from ..database import get_db
from ..models import Product, BaseReview, ReviewAnalysis, PublishedReview, User, SupportTicket, RejectedReview
from ..schemas import ProductResponse, ReviewSubmission, PublicReviewResponse
from ..ai.classifier import get_classifier
from ..ai.embeddings import get_embedding_service
from ..utils.scoring import calculate_value_score

router = APIRouter()

@router.get("/products", response_model=List[ProductResponse])
async def get_products(db: Session = Depends(get_db)):
    products = db.query(Product).filter(Product.is_active == True).all()
    return products

@router.get("/products/{product_id}", response_model=ProductResponse)
async def get_product(product_id: str, db: Session = Depends(get_db)):
    try:
        product_uuid = UUID(product_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid product ID format")
    
    product = db.query(Product).filter(Product.id == product_uuid).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    return product

@router.get("/products/{product_id}/reviews/public")
async def get_public_reviews(
    product_id: str,
    tab: str = "positive",
    db: Session = Depends(get_db)
):
    try:
        product_uuid = UUID(product_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid product ID format")
    
    # Base query for published reviews
    query = db.query(
        PublishedReview,
        BaseReview,
        ReviewAnalysis
    ).join(
        BaseReview, PublishedReview.review_id == BaseReview.id
    ).join(
        ReviewAnalysis, PublishedReview.analysis_id == ReviewAnalysis.id
    ).filter(
        BaseReview.product_id == product_uuid
    )
    
    # Filter by tab
    if tab == "positive":
        query = query.filter(
            and_(
                ReviewAnalysis.category == "public_positive",
                PublishedReview.is_shadow == False
            )
        )
    elif tab == "negative":
        query = query.filter(
            and_(
                ReviewAnalysis.category == "public_negative",
                PublishedReview.is_shadow == False
            )
        )
    elif tab == "shadow":
        query = query.filter(PublishedReview.is_shadow == True)
    else:
        # All public reviews
        query = query.filter(PublishedReview.is_shadow == False)
    
    # Order by value score
    query = query.order_by(desc(ReviewAnalysis.value_score))
    
    results = query.all()
    
    reviews = []
    for pub_review, base_review, analysis in results:
        reviews.append({
            "id": str(base_review.id),
            "reviewer_name": base_review.reviewer_name or "Anonymous",
            "rating": base_review.rating,
            "review_text": base_review.review_text,
            "is_verified_purchase": base_review.is_verified_purchase,
            "submitted_at": base_review.submitted_at.isoformat(),
            "automatic_response": pub_review.automatic_response,
            "value_score": float(analysis.value_score) if analysis.value_score else 0,
            "helpful_count": pub_review.helpful_count,
            "category": analysis.category
        })
    
    # Generate summary for negative reviews
    summary = None
    if tab == "negative" and reviews:
        summary = {
            "title": "Common Issues",
            "count": len(reviews),
            "top_issues": _extract_top_issues(reviews)
        }
    
    return {
        "reviews": reviews,
        "summary": summary,
        "total": len(reviews)
    }

@router.post("/reviews")
async def submit_review(
    review: ReviewSubmission,
    db: Session = Depends(get_db)
):
    try:
        product_uuid = UUID(review.product_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid product ID format")
    
    # Get product
    product = db.query(Product).filter(Product.id == product_uuid).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    # Create or get user
    user = None
    if review.reviewer_email:
        user = db.query(User).filter(User.email == review.reviewer_email).first()
        if not user:
            user = User(
                name=review.reviewer_name,
                email=review.reviewer_email,
                is_verified_purchaser=review.is_verified_purchase
            )
            db.add(user)
            db.commit()
            db.refresh(user)
    
    # Create base review
    base_review = BaseReview(
        product_id=product_uuid,
        user_id=user.id if user else None,
        reviewer_name=review.reviewer_name,
        reviewer_email=review.reviewer_email,
        rating=review.rating,
        review_text=review.review_text,
        is_verified_purchase=review.is_verified_purchase
    )
    db.add(base_review)
    db.commit()
    db.refresh(base_review)
    
    # Classify review using AI
    classifier = get_classifier()
    embedding_service = get_embedding_service()
    
    classification_result = classifier.classify_review(
        review_id=str(base_review.id),
        review_text=review.review_text,
        rating=review.rating,
        product_description=product.long_description or product.description,
        product_keypoints=product.keypoints or [],
        is_verified_purchase=review.is_verified_purchase
    )
    
    # Calculate semantic similarity for scoring
    semantic_similarity = embedding_service.calculate_similarity_to_keypoints(
        review.review_text,
        product.keypoints or []
    )
    
    # Calculate value score
    matched_keypoints = classification_result["matched_description_points"]
    sentiment_score = classification_result["confidence"]
    
    value_score = calculate_value_score(
        review_text=review.review_text,
        product_description=product.long_description or product.description,
        keypoints=product.keypoints or [],
        matched_keypoints=matched_keypoints,
        is_verified_purchase=review.is_verified_purchase,
        sentiment_score=sentiment_score,
        semantic_similarity=semantic_similarity
    )
    
    # Create review analysis
    analysis = ReviewAnalysis(
        review_id=base_review.id,
        category=classification_result["category"],
        confidence=classification_result["confidence"],
        reason=classification_result["reason"],
        tags=classification_result["tags"],
        severity=classification_result["severity"],
        recommended_action=classification_result["recommended_action"],
        matched_description_points=classification_result["matched_description_points"],
        suggested_automatic_response=classification_result["suggested_automatic_response"],
        value_score=value_score
    )
    db.add(analysis)
    db.commit()
    db.refresh(analysis)
    
    # Process based on category
    category = classification_result["category"]
    
    if category in ["public_positive", "public_negative"]:
        # Publish review
        published = PublishedReview(
            review_id=base_review.id,
            analysis_id=analysis.id,
            is_shadow=False,
            automatic_response=classification_result["suggested_automatic_response"]
        )
        db.add(published)
        db.commit()
        
        return {
            "status": "published",
            "message": "Thank you for your review! It has been published.",
            "category": category,
            "review_id": str(base_review.id)
        }
    
    elif category == "shadow":
        # Publish but shadow-ban
        published = PublishedReview(
            review_id=base_review.id,
            analysis_id=analysis.id,
            is_shadow=True,
            automatic_response=classification_result["suggested_automatic_response"]
        )
        db.add(published)
        db.commit()
        
        return {
            "status": "published",
            "message": "Thank you for your review!",
            "category": category,
            "review_id": str(base_review.id)
        }
    
    elif category == "support":
        # Create support ticket
        priority = "high" if review.is_verified_purchase else "normal"
        
        ticket = SupportTicket(
            review_id=base_review.id,
            analysis_id=analysis.id,
            priority=priority,
            issue_description=review.review_text,
            customer_email=review.reviewer_email,
            automatic_response=classification_result["suggested_automatic_response"]
        )
        db.add(ticket)
        db.commit()
        
        response_message = classification_result["suggested_automatic_response"]
        if not review.reviewer_email:
            response_message += " Please provide your email so we can reach you."
        
        return {
            "status": "support_ticket_created",
            "message": response_message,
            "category": category,
            "ticket_id": str(ticket.id)
        }
    
    elif category == "rejected":
        # Reject review
        rejected = RejectedReview(
            review_id=base_review.id,
            analysis_id=analysis.id,
            rejection_reason=classification_result["reason"],
            user_notified=True,
            notification_message="Your review was not published because it was marked as irrelevant to the product."
        )
        db.add(rejected)
        db.commit()
        
        return {
            "status": "rejected",
            "message": "Your review was not published because it was marked as irrelevant to the product.",
            "reason": classification_result["reason"],
            "category": category
        }
    
    return {
        "status": "processed",
        "message": "Review has been processed.",
        "category": category
    }

def _extract_top_issues(reviews: List[dict]) -> List[str]:
    """Extract common issues from negative reviews."""
    issues = []
    for review in reviews[:3]:  # Top 3 negative reviews
        text = review["review_text"]
        if len(text) > 100:
            issues.append(text[:100] + "...")
        else:
            issues.append(text)
    return issues
