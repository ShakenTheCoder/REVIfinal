# REVI API Documentation

Complete API reference for the REVI review moderation system.

## Base URL

```
http://localhost:8000/api
```

## Authentication

Currently no authentication required (demo system). In production, implement JWT or OAuth2.

---

## Public Endpoints

### Get All Products

Retrieve list of all active products.

**Endpoint**: `GET /products`

**Response**:
```json
[
  {
    "id": "650e8400-e29b-41d4-a716-446655440001",
    "store_id": "550e8400-e29b-41d4-a716-446655440000",
    "title": "Premium Wireless Bluetooth Headphones",
    "description": "High-quality over-ear headphones with active noise cancellation",
    "long_description": "Full product description...",
    "price": 149.99,
    "currency": "USD",
    "image_url": "https://...",
    "category": "Electronics",
    "keypoints": [
      "Active Noise Cancellation",
      "Bluetooth 5.0",
      "30-hour battery life"
    ],
    "created_at": "2024-01-01T00:00:00"
  }
]
```

---

### Get Product by ID

Retrieve detailed information about a specific product.

**Endpoint**: `GET /products/{product_id}`

**Parameters**:
- `product_id` (path, required): UUID of the product

**Response**:
```json
{
  "id": "650e8400-e29b-41d4-a716-446655440001",
  "store_id": "550e8400-e29b-41d4-a716-446655440000",
  "title": "Premium Wireless Bluetooth Headphones",
  "description": "High-quality over-ear headphones...",
  "long_description": "Experience superior sound quality...",
  "price": 149.99,
  "currency": "USD",
  "image_url": "https://...",
  "category": "Electronics",
  "keypoints": ["Active Noise Cancellation", "Bluetooth 5.0"],
  "created_at": "2024-01-01T00:00:00"
}
```

**Errors**:
- `404`: Product not found
- `400`: Invalid product ID format

---

### Get Public Reviews

Retrieve public reviews for a product, filtered by tab.

**Endpoint**: `GET /products/{product_id}/reviews/public`

**Parameters**:
- `product_id` (path, required): UUID of the product
- `tab` (query, optional): Filter by category
  - `positive` (default): Public positive reviews
  - `negative`: Public negative reviews
  - `shadow`: Shadow-banned reviews
  - `all`: All public reviews

**Response**:
```json
{
  "reviews": [
    {
      "id": "750e8400-e29b-41d4-a716-446655440001",
      "reviewer_name": "John Doe",
      "rating": 5,
      "review_text": "These headphones are amazing! The noise cancellation...",
      "is_verified_purchase": true,
      "submitted_at": "2024-01-15T10:30:00",
      "automatic_response": "Thank you so much for your wonderful review!",
      "value_score": 87.5,
      "helpful_count": 5,
      "category": "public_positive"
    }
  ],
  "summary": {
    "title": "Common Issues",
    "count": 3,
    "top_issues": [
      "Battery life shorter than advertised...",
      "Uncomfortable for extended wear..."
    ]
  },
  "total": 15
}
```

**Note**: `summary` is only included for negative reviews tab.

---

### Submit Review

Submit a new customer review. The review will be automatically classified by AI.

**Endpoint**: `POST /reviews`

**Request Body**:
```json
{
  "product_id": "650e8400-e29b-41d4-a716-446655440001",
  "reviewer_name": "Jane Smith",
  "reviewer_email": "jane@example.com",
  "rating": 5,
  "review_text": "Excellent product! The sound quality is crystal clear...",
  "is_verified_purchase": true
}
```

**Fields**:
- `product_id` (required): UUID of the product
- `reviewer_name` (optional): Customer name
- `reviewer_email` (optional): Customer email (required for support tickets)
- `rating` (required): Integer 1-5
- `review_text` (required): Review content
- `is_verified_purchase` (optional): Boolean, default false

**Response - Published**:
```json
{
  "status": "published",
  "message": "Thank you for your review! It has been published.",
  "category": "public_positive",
  "review_id": "850e8400-e29b-41d4-a716-446655440001"
}
```

**Response - Support Ticket**:
```json
{
  "status": "support_ticket_created",
  "message": "Your issue has been recognized. A support agent will contact you shortly.",
  "category": "support",
  "ticket_id": "950e8400-e29b-41d4-a716-446655440001"
}
```

**Response - Rejected**:
```json
{
  "status": "rejected",
  "message": "Your review was not published because it was marked as irrelevant to the product.",
  "reason": "Review contradicts product description",
  "category": "rejected"
}
```

**Errors**:
- `404`: Product not found
- `400`: Invalid request data
- `422`: Validation error

---

## Admin Endpoints

### Get All Reviews

Retrieve all reviews with classification information.

**Endpoint**: `GET /admin/reviews/all`

**Parameters**:
- `skip` (query, optional): Number of records to skip (default: 0)
- `limit` (query, optional): Maximum records to return (default: 50)

**Response**:
```json
{
  "reviews": [
    {
      "id": "750e8400-e29b-41d4-a716-446655440001",
      "product_id": "650e8400-e29b-41d4-a716-446655440001",
      "reviewer_name": "John Doe",
      "reviewer_email": "john@example.com",
      "rating": 5,
      "review_text": "Excellent product!",
      "language": "en",
      "is_verified_purchase": true,
      "submitted_at": "2024-01-15T10:30:00",
      "category": "public_positive",
      "confidence": 0.95,
      "reason": "Positive review with positive sentiment. Mentions product features: Active Noise Cancellation.",
      "tags": ["quality", "performance"],
      "value_score": 87.5
    }
  ],
  "total": 150,
  "skip": 0,
  "limit": 50
}
```

---

### Get Shadow Reviews

Retrieve all shadow-banned reviews.

**Endpoint**: `GET /admin/reviews/shadow`

**Response**:
```json
{
  "reviews": [
    {
      "id": "760e8400-e29b-41d4-a716-446655440001",
      "product_id": "650e8400-e29b-41d4-a716-446655440001",
      "reviewer_name": "Anonymous",
      "reviewer_email": null,
      "rating": 5,
      "review_text": "Great product!",
      "submitted_at": "2024-01-16T12:00:00",
      "category": "shadow",
      "reason": "Generic positive review without substantive content.",
      "value_score": 45.0
    }
  ],
  "total": 8
}
```

---

### Get Rejected Reviews

Retrieve all rejected reviews with rejection reasons.

**Endpoint**: `GET /admin/reviews/rejected`

**Response**:
```json
{
  "reviews": [
    {
      "id": "770e8400-e29b-41d4-a716-446655440001",
      "product_id": "650e8400-e29b-41d4-a716-446655440001",
      "reviewer_name": "Angry Customer",
      "reviewer_email": "angry@example.com",
      "rating": 1,
      "review_text": "Received red headphones instead of blue!",
      "submitted_at": "2024-01-17T09:00:00",
      "category": "rejected",
      "reason": "Review contradicts product description (product is matte black).",
      "rejected_at": "2024-01-17T09:00:05",
      "user_notified": true
    }
  ],
  "total": 5
}
```

---

### Get Review Detail

Get comprehensive information about a specific review.

**Endpoint**: `GET /admin/reviews/{review_id}`

**Parameters**:
- `review_id` (path, required): UUID of the review

**Response**:
```json
{
  "review": {
    "id": "750e8400-e29b-41d4-a716-446655440001",
    "product_id": "650e8400-e29b-41d4-a716-446655440001",
    "product_title": "Premium Wireless Bluetooth Headphones",
    "reviewer_name": "John Doe",
    "reviewer_email": "john@example.com",
    "rating": 5,
    "review_text": "Excellent headphones...",
    "language": "en",
    "is_verified_purchase": true,
    "submitted_at": "2024-01-15T10:30:00"
  },
  "analysis": {
    "category": "public_positive",
    "confidence": 0.95,
    "reason": "Positive review with positive sentiment...",
    "tags": ["quality", "performance"],
    "severity": "low",
    "matched_points": ["Active Noise Cancellation", "Bluetooth 5.0"],
    "value_score": 87.5
  },
  "published": {
    "is_shadow": false,
    "automatic_response": "Thank you for your wonderful review!",
    "published_at": "2024-01-15T10:30:05"
  },
  "rejected": null,
  "ticket": null
}
```

---

### Get Support Tickets

Retrieve all support tickets.

**Endpoint**: `GET /admin/support`

**Parameters**:
- `status` (query, optional): Filter by status
  - `open`: Open tickets
  - `assigned`: Assigned tickets
  - `resolved`: Resolved tickets
  - `closed`: Closed tickets

**Response**:
```json
{
  "tickets": [
    {
      "id": "850e8400-e29b-41d4-a716-446655440001",
      "review_id": "750e8400-e29b-41d4-a716-446655440001",
      "priority": "high",
      "status": "open",
      "assigned_to": null,
      "issue_description": "Headphones stopped working after 2 days...",
      "customer_email": "customer@example.com",
      "automatic_response": "Your issue has been recognized...",
      "created_at": "2024-01-18T14:00:00",
      "updated_at": "2024-01-18T14:00:00"
    }
  ],
  "total": 12
}
```

---

### Assign Support Ticket

Assign a support ticket to an agent.

**Endpoint**: `POST /admin/tickets/{ticket_id}/assign`

**Parameters**:
- `ticket_id` (path, required): UUID of the ticket
- `admin_user` (query, optional): Admin username for audit trail

**Request Body**:
```json
{
  "assigned_to": "agent@example.com"
}
```

**Response**:
```json
{
  "status": "success",
  "message": "Ticket assigned to agent@example.com",
  "ticket_id": "850e8400-e29b-41d4-a716-446655440001"
}
```

---

### Override Review Category

Manually override the AI classification of a review.

**Endpoint**: `POST /admin/reviews/{review_id}/override`

**Parameters**:
- `review_id` (path, required): UUID of the review

**Request Body**:
```json
{
  "new_category": "public_positive",
  "reason": "Manual review shows this is a valid positive review",
  "admin_user": "admin@example.com"
}
```

**Fields**:
- `new_category` (required): One of: `public_positive`, `public_negative`, `support`, `shadow`, `rejected`
- `reason` (required): Explanation for the override
- `admin_user` (required): Admin username for audit trail

**Response**:
```json
{
  "status": "success",
  "message": "Review category changed from rejected to public_positive",
  "review_id": "750e8400-e29b-41d4-a716-446655440001"
}
```

---

## Error Responses

All endpoints may return the following error responses:

### 400 Bad Request
```json
{
  "detail": "Invalid product ID format"
}
```

### 404 Not Found
```json
{
  "detail": "Product not found"
}
```

### 422 Unprocessable Entity
```json
{
  "detail": [
    {
      "loc": ["body", "rating"],
      "msg": "ensure this value is less than or equal to 5",
      "type": "value_error.number.not_le"
    }
  ]
}
```

### 500 Internal Server Error
```json
{
  "detail": "Internal server error"
}
```

---

## Rate Limiting

Not implemented in demo version. For production, implement rate limiting:
- Public endpoints: 100 requests/minute per IP
- Admin endpoints: 500 requests/minute per user

---

## Pagination

Endpoints that return lists support pagination:

**Parameters**:
- `skip`: Number of records to skip (default: 0)
- `limit`: Maximum records to return (default: 50, max: 100)

---

## Testing with cURL

### Submit a review:
```bash
curl -X POST http://localhost:8000/api/reviews \
  -H "Content-Type: application/json" \
  -d '{
    "product_id": "650e8400-e29b-41d4-a716-446655440001",
    "reviewer_name": "Test User",
    "rating": 5,
    "review_text": "Great product with excellent noise cancellation!",
    "is_verified_purchase": true
  }'
```

### Get product reviews:
```bash
curl http://localhost:8000/api/products/650e8400-e29b-41d4-a716-446655440001/reviews/public?tab=positive
```

### Get all reviews (admin):
```bash
curl http://localhost:8000/api/admin/reviews/all
```

---

## Interactive API Documentation

FastAPI provides interactive API documentation:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

---

For support or questions, please refer to the main README.md file.
