from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import and_, desc, or_
from typing import List, Optional
from uuid import UUID

from ..database import get_db
from ..models import (
    BaseReview, ReviewAnalysis, PublishedReview, RejectedReview,
    SupportTicket, AdminAction, Product
)
from ..schemas import AdminReviewResponse, SupportTicketResponse, TicketAssignment, ReviewOverride

router = APIRouter()

@router.get("/reviews/all")
async def get_all_reviews(
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db)
):
    query = db.query(
        BaseReview,
        ReviewAnalysis
    ).outerjoin(
        ReviewAnalysis, BaseReview.id == ReviewAnalysis.review_id
    ).order_by(
        desc(BaseReview.submitted_at)
    )
    
    total = query.count()
    results = query.offset(skip).limit(limit).all()
    
    reviews = []
    for base_review, analysis in results:
        reviews.append({
            "id": str(base_review.id),
            "product_id": str(base_review.product_id),
            "reviewer_name": base_review.reviewer_name or "Anonymous",
            "reviewer_email": base_review.reviewer_email,
            "rating": base_review.rating,
            "review_text": base_review.review_text,
            "language": base_review.language,
            "is_verified_purchase": base_review.is_verified_purchase,
            "submitted_at": base_review.submitted_at.isoformat(),
            "category": analysis.category if analysis else None,
            "confidence": float(analysis.confidence) if analysis and analysis.confidence else None,
            "reason": analysis.reason if analysis else None,
            "tags": analysis.tags if analysis else [],
            "value_score": float(analysis.value_score) if analysis and analysis.value_score else None
        })
    
    return {
        "reviews": reviews,
        "total": total,
        "skip": skip,
        "limit": limit
    }

@router.get("/reviews/shadow")
async def get_shadow_reviews(db: Session = Depends(get_db)):
    query = db.query(
        BaseReview,
        ReviewAnalysis,
        PublishedReview
    ).join(
        ReviewAnalysis, BaseReview.id == ReviewAnalysis.review_id
    ).join(
        PublishedReview, BaseReview.id == PublishedReview.review_id
    ).filter(
        PublishedReview.is_shadow == True
    ).order_by(
        desc(BaseReview.submitted_at)
    )
    
    results = query.all()
    
    reviews = []
    for base_review, analysis, pub_review in results:
        reviews.append({
            "id": str(base_review.id),
            "product_id": str(base_review.product_id),
            "reviewer_name": base_review.reviewer_name or "Anonymous",
            "reviewer_email": base_review.reviewer_email,
            "rating": base_review.rating,
            "review_text": base_review.review_text,
            "submitted_at": base_review.submitted_at.isoformat(),
            "category": analysis.category,
            "reason": analysis.reason,
            "value_score": float(analysis.value_score) if analysis.value_score else 0
        })
    
    return {
        "reviews": reviews,
        "total": len(reviews)
    }

@router.get("/reviews/rejected")
async def get_rejected_reviews(db: Session = Depends(get_db)):
    query = db.query(
        BaseReview,
        ReviewAnalysis,
        RejectedReview
    ).join(
        ReviewAnalysis, BaseReview.id == ReviewAnalysis.review_id
    ).join(
        RejectedReview, BaseReview.id == RejectedReview.review_id
    ).order_by(
        desc(RejectedReview.rejected_at)
    )
    
    results = query.all()
    
    reviews = []
    for base_review, analysis, rejected in results:
        reviews.append({
            "id": str(base_review.id),
            "product_id": str(base_review.product_id),
            "reviewer_name": base_review.reviewer_name or "Anonymous",
            "reviewer_email": base_review.reviewer_email,
            "rating": base_review.rating,
            "review_text": base_review.review_text,
            "submitted_at": base_review.submitted_at.isoformat(),
            "category": analysis.category,
            "reason": rejected.rejection_reason,
            "rejected_at": rejected.rejected_at.isoformat(),
            "user_notified": rejected.user_notified
        })
    
    return {
        "reviews": reviews,
        "total": len(reviews)
    }

@router.get("/support")
async def get_support_tickets(
    status: Optional[str] = None,
    db: Session = Depends(get_db)
):
    query = db.query(SupportTicket).order_by(
        desc(SupportTicket.priority),
        desc(SupportTicket.created_at)
    )
    
    if status:
        query = query.filter(SupportTicket.status == status)
    
    tickets = query.all()
    
    results = []
    for ticket in tickets:
        results.append({
            "id": str(ticket.id),
            "review_id": str(ticket.review_id),
            "priority": ticket.priority,
            "status": ticket.status,
            "assigned_to": ticket.assigned_to,
            "issue_description": ticket.issue_description,
            "customer_email": ticket.customer_email,
            "automatic_response": ticket.automatic_response,
            "created_at": ticket.created_at.isoformat(),
            "updated_at": ticket.updated_at.isoformat()
        })
    
    return {
        "tickets": results,
        "total": len(results)
    }

@router.post("/tickets/{ticket_id}/assign")
async def assign_ticket(
    ticket_id: str,
    assignment: TicketAssignment,
    admin_user: str = "admin",
    db: Session = Depends(get_db)
):
    try:
        ticket_uuid = UUID(ticket_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid ticket ID format")
    
    ticket = db.query(SupportTicket).filter(SupportTicket.id == ticket_uuid).first()
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    
    old_assigned = ticket.assigned_to
    ticket.assigned_to = assignment.assigned_to
    ticket.status = "assigned"
    
    # Log admin action
    admin_action = AdminAction(
        admin_user=admin_user,
        action_type="assign_ticket",
        target_id=ticket_uuid,
        target_type="ticket",
        old_value=old_assigned,
        new_value=assignment.assigned_to
    )
    db.add(admin_action)
    
    db.commit()
    db.refresh(ticket)
    
    return {
        "status": "success",
        "message": f"Ticket assigned to {assignment.assigned_to}",
        "ticket_id": str(ticket.id)
    }

@router.post("/reviews/{review_id}/override")
async def override_review_category(
    review_id: str,
    override: ReviewOverride,
    db: Session = Depends(get_db)
):
    try:
        review_uuid = UUID(review_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid review ID format")
    
    # Get review and analysis
    base_review = db.query(BaseReview).filter(BaseReview.id == review_uuid).first()
    if not base_review:
        raise HTTPException(status_code=404, detail="Review not found")
    
    analysis = db.query(ReviewAnalysis).filter(ReviewAnalysis.review_id == review_uuid).first()
    if not analysis:
        raise HTTPException(status_code=404, detail="Review analysis not found")
    
    old_category = analysis.category
    analysis.category = override.new_category
    
    # Update published/rejected status based on new category
    if override.new_category in ["public_positive", "public_negative"]:
        # Remove from rejected if exists
        rejected = db.query(RejectedReview).filter(RejectedReview.review_id == review_uuid).first()
        if rejected:
            db.delete(rejected)
        
        # Add to published if not exists
        published = db.query(PublishedReview).filter(PublishedReview.review_id == review_uuid).first()
        if not published:
            published = PublishedReview(
                review_id=review_uuid,
                analysis_id=analysis.id,
                is_shadow=False,
                automatic_response="Review manually approved by admin"
            )
            db.add(published)
    
    elif override.new_category == "rejected":
        # Remove from published if exists
        published = db.query(PublishedReview).filter(PublishedReview.review_id == review_uuid).first()
        if published:
            db.delete(published)
        
        # Add to rejected if not exists
        rejected = db.query(RejectedReview).filter(RejectedReview.review_id == review_uuid).first()
        if not rejected:
            rejected = RejectedReview(
                review_id=review_uuid,
                analysis_id=analysis.id,
                rejection_reason=override.reason,
                user_notified=False
            )
            db.add(rejected)
    
    # Log admin action
    admin_action = AdminAction(
        admin_user=override.admin_user,
        action_type="override_category",
        target_id=review_uuid,
        target_type="review",
        reason=override.reason,
        old_value=old_category,
        new_value=override.new_category
    )
    db.add(admin_action)
    
    db.commit()
    
    return {
        "status": "success",
        "message": f"Review category changed from {old_category} to {override.new_category}",
        "review_id": str(review_uuid)
    }

@router.get("/reviews/{review_id}")
async def get_review_detail(
    review_id: str,
    db: Session = Depends(get_db)
):
    try:
        review_uuid = UUID(review_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid review ID format")
    
    base_review = db.query(BaseReview).filter(BaseReview.id == review_uuid).first()
    if not base_review:
        raise HTTPException(status_code=404, detail="Review not found")
    
    analysis = db.query(ReviewAnalysis).filter(ReviewAnalysis.review_id == review_uuid).first()
    published = db.query(PublishedReview).filter(PublishedReview.review_id == review_uuid).first()
    rejected = db.query(RejectedReview).filter(RejectedReview.review_id == review_uuid).first()
    ticket = db.query(SupportTicket).filter(SupportTicket.review_id == review_uuid).first()
    product = db.query(Product).filter(Product.id == base_review.product_id).first()
    
    return {
        "review": {
            "id": str(base_review.id),
            "product_id": str(base_review.product_id),
            "product_title": product.title if product else None,
            "reviewer_name": base_review.reviewer_name,
            "reviewer_email": base_review.reviewer_email,
            "rating": base_review.rating,
            "review_text": base_review.review_text,
            "language": base_review.language,
            "is_verified_purchase": base_review.is_verified_purchase,
            "submitted_at": base_review.submitted_at.isoformat()
        },
        "analysis": {
            "category": analysis.category if analysis else None,
            "confidence": float(analysis.confidence) if analysis and analysis.confidence else None,
            "reason": analysis.reason if analysis else None,
            "tags": analysis.tags if analysis else [],
            "severity": analysis.severity if analysis else None,
            "matched_points": analysis.matched_description_points if analysis else [],
            "value_score": float(analysis.value_score) if analysis and analysis.value_score else None
        } if analysis else None,
        "published": {
            "is_shadow": published.is_shadow,
            "automatic_response": published.automatic_response,
            "published_at": published.published_at.isoformat()
        } if published else None,
        "rejected": {
            "reason": rejected.rejection_reason,
            "rejected_at": rejected.rejected_at.isoformat()
        } if rejected else None,
        "ticket": {
            "id": str(ticket.id),
            "priority": ticket.priority,
            "status": ticket.status,
            "assigned_to": ticket.assigned_to
        } if ticket else None
    }
