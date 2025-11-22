# REVI System Architecture

Comprehensive architecture documentation for the REVI AI-powered review moderation system.

## 🏛️ System Overview

REVI is a full-stack application that automatically moderates customer reviews using AI classification. The system consists of three main layers:

1. **Presentation Layer** (React Frontend)
2. **Application Layer** (FastAPI Backend)
3. **Data Layer** (PostgreSQL Database)

```
┌─────────────────────────────────────────────────────────────┐
│                         Frontend                             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │  Store Pages │  │ Review Form  │  │ Admin Panel  │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└────────────────────────┬────────────────────────────────────┘
                         │ HTTP/REST
┌────────────────────────┴────────────────────────────────────┐
│                      Backend (FastAPI)                       │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │ Public API   │  │  Admin API   │  │   AI Core    │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
│  ┌──────────────────────────────────────────────────┐      │
│  │           AI Classification Pipeline              │      │
│  │  ┌────────────┐  ┌────────────┐  ┌────────────┐ │      │
│  │  │ Classifier │  │ Embeddings │  │  Scoring   │ │      │
│  │  └────────────┘  └────────────┘  └────────────┘ │      │
│  └──────────────────────────────────────────────────┘      │
└────────────────────────┬────────────────────────────────────┘
                         │ SQL/ORM
┌────────────────────────┴────────────────────────────────────┐
│                   Database (PostgreSQL)                      │
│  ┌──────────────────────────────────────────────────┐      │
│  │  base_reviews │ review_analysis │ published_reviews │   │
│  │  support_tickets │ rejected_reviews │ products    │    │
│  └──────────────────────────────────────────────────┘      │
└─────────────────────────────────────────────────────────────┘
```

## 📦 Component Architecture

### Frontend Components

#### Pages
- **HomePage**: Product listing with grid layout
- **ProductPage**: Product details + review submission + review tabs
- **AdminPage**: Multi-tab admin interface

#### Components
- **ReviewForm**: Form for submitting new reviews
- **ReviewTabs**: Tabbed interface for viewing reviews by category
- **Navigation**: Global navigation bar

#### Services
- **api.js**: Centralized API client using Axios
  - Product API methods
  - Review API methods
  - Admin API methods

### Backend Structure

#### API Layer (`/app/api/`)

**public.py**: Public-facing endpoints
- Product retrieval
- Review submission
- Public review display

**admin.py**: Administrative endpoints
- Review management
- Ticket management
- Override capabilities

#### AI Layer (`/app/ai/`)

**classifier.py**: Core AI classification engine
```python
ReviewClassifier
├── classify_review()
├── _detect_language()
├── _is_generic_review()
├── _match_keypoints()
├── _extract_tags()
├── _determine_category()
├── _calculate_confidence()
└── _generate_automatic_response()
```

**embeddings.py**: Semantic similarity calculations
```python
EmbeddingService
├── get_embedding()
├── calculate_similarity()
└── calculate_similarity_to_keypoints()
```

#### Utils Layer (`/app/utils/`)

**scoring.py**: Value score calculation
- Implements V = 0.30*K + 0.25*D + 0.15*L + 0.10*P + 0.10*S + 0.10*U

#### Core Layer (`/app/`)

- **database.py**: Database connection and session management
- **models.py**: SQLAlchemy ORM models
- **schemas.py**: Pydantic request/response schemas
- **main.py**: FastAPI application initialization

### Database Schema

#### Entity Relationship Diagram

```
┌─────────────┐
│   stores    │
└──────┬──────┘
       │
       │ 1:N
       │
┌──────┴──────────┐
│    products     │
└──────┬──────────┘
       │
       │ 1:N
       │
┌──────┴──────────────┐
│   base_reviews      │◄─────────┐
└──────┬──────────────┘          │
       │                          │
       │ 1:1                      │
       │                          │
┌──────┴──────────────┐          │
│  review_analysis    │          │ 1:1
└──────┬──────────────┘          │
       │                          │
       ├──────────────────────────┤
       │ 1:1          1:1         │ 1:1
       │              │           │
┌──────┴─────────┐  ┌─┴───────┐ ┌─┴────────────┐
│ published_     │  │rejected_│ │  support_    │
│ reviews        │  │reviews  │ │  tickets     │
└────────────────┘  └─────────┘ └──────────────┘
```

#### Key Tables

**base_reviews**: All submitted reviews (immutable)
- Source of truth for all review data
- Never deleted, maintains complete audit trail

**review_analysis**: AI classification results
- One-to-one with base_reviews
- Contains category, confidence, reasoning

**published_reviews**: Public-facing reviews
- Includes automatic responses
- Shadow flag for soft-banning

**rejected_reviews**: Reviews not suitable for publication
- Includes rejection reason
- User notification status

**support_tickets**: Auto-generated tickets
- Created from support-category reviews
- Priority and assignment tracking

## 🔄 Data Flow

### Review Submission Flow

```
1. User submits review
   │
   ▼
2. Create BaseReview
   │
   ▼
3. AI Classification Pipeline
   ├─► Sentiment Analysis (XLM-RoBERTa)
   ├─► Language Detection
   ├─► Keypoint Matching
   ├─► Generic/Bot Detection
   └─► Category Determination
   │
   ▼
4. Calculate Value Score
   ├─► Semantic Similarity (Sentence Transformers)
   ├─► Keypoint Matches
   ├─► Length Score
   ├─► Verified Purchase Bonus
   └─► Sentiment Confidence
   │
   ▼
5. Create ReviewAnalysis
   │
   ▼
6. Route based on Category
   ├─► public_positive    → PublishedReview
   ├─► public_negative    → PublishedReview
   ├─► support            → SupportTicket
   ├─► shadow             → PublishedReview (shadow=true)
   └─► rejected           → RejectedReview
   │
   ▼
7. Generate Response
   └─► Return status + message to user
```

### Review Display Flow

```
1. User navigates to product page
   │
   ▼
2. Request reviews by tab (positive/negative/shadow)
   │
   ▼
3. Backend Query
   ├─► JOIN base_reviews
   ├─► JOIN review_analysis
   ├─► JOIN published_reviews
   ├─► FILTER by category and shadow flag
   └─► ORDER BY value_score DESC
   │
   ▼
4. Return enriched review data
   │
   ▼
5. Frontend renders reviews
   └─► Show automatic responses
```

### Admin Override Flow

```
1. Admin selects review
   │
   ▼
2. Choose new category + reason
   │
   ▼
3. Backend updates ReviewAnalysis.category
   │
   ▼
4. Route to appropriate table
   ├─► Remove from old table
   └─► Add to new table
   │
   ▼
5. Log AdminAction (audit trail)
   │
   ▼
6. Return success response
```

## 🤖 AI Classification Logic

### Decision Tree

```
Start
│
├─► Has support keywords? (broken, defect, help)
│   └─► YES → SUPPORT
│
├─► Contradicts product description?
│   └─► YES → REJECTED
│
├─► No keypoint matches + long review + low rating?
│   └─► YES → REJECTED
│
├─► Generic 5-star review? ("Great!", "Good")
│   └─► YES → SHADOW
│
└─► Rating >= 4 OR Positive sentiment?
    ├─► YES → PUBLIC_POSITIVE
    └─► NO → PUBLIC_NEGATIVE
```

### Classification Criteria

#### Category 1: Public Positive
- **Sentiment**: Positive or neutral
- **Rating**: 4-5 stars
- **Content**: Relevant to product
- **Action**: Publish + Thank you response
- **Value Score**: High priority for display

#### Category 2: Public Negative
- **Sentiment**: Negative
- **Rating**: 1-3 stars
- **Content**: Relevant to product
- **Action**: Publish + Sorry response
- **Special**: Included in negative summary

#### Category 3: Support
- **Keywords**: broken, defect, problem, not working
- **Rating**: Usually 1-2 stars
- **Action**: Create support ticket
- **Priority**: High if verified purchase
- **Response**: Contact promise

#### Category 4: Shadow
- **Pattern**: Generic praise
- **Examples**: "Great!", "Good product!", "Amazing"
- **Rating**: Usually 5 stars
- **Length**: Very short (<20 chars)
- **Action**: Publish but hide from default view

#### Category 5: Rejected
- **Issue**: Contradicts product facts
- **Example**: Claims wrong color when description is clear
- **Issue**: Completely irrelevant
- **Action**: Don't publish + Explain to user

## 🔢 Value Score Algorithm

### Formula Components

```python
V = 0.30*K + 0.25*D + 0.15*L + 0.10*P + 0.10*S + 0.10*U

where:
K = Semantic Similarity (0-1)
    - Cosine similarity between review and product description
    - Uses multilingual sentence embeddings

D = Keypoint Match Score (0-1)
    - matched_keypoints / total_keypoints
    - Rewards mentioning specific product features

L = Length Score (0-1)
    - Optimal range: 100-500 characters
    - Penalties for too short or too long

P = Verified Purchase (0 or 1)
    - Binary bonus for confirmed buyers

S = Sentiment Confidence (0-1)
    - From XLM-RoBERTa sentiment model
    - Higher confidence = higher score

U = Usefulness (0-1)
    - Based on user "helpful" votes
    - Defaults to 0.5 for new reviews
```

### Score Ranges

- **80-100**: Excellent review
  - Detailed, verified, matches product features
- **60-79**: Good review
  - Helpful content, some product mentions
- **40-59**: Average review
  - Basic feedback, minimal detail
- **20-39**: Low-value review
  - Generic, short, or off-topic
- **0-19**: Poor review
  - No useful information

## 🔐 Security Architecture

### Current State (Demo)
- ✅ Input validation via Pydantic
- ✅ SQL injection prevention via SQLAlchemy ORM
- ✅ CORS configured
- ❌ No authentication
- ❌ No rate limiting
- ❌ No encryption

### Production Requirements
- 🔒 JWT authentication for admin endpoints
- 🔒 Rate limiting per IP/user
- 🔒 HTTPS/TLS encryption
- 🔒 Password hashing (bcrypt)
- 🔒 API key for review submission
- 🔒 CSRF protection
- 🔒 Input sanitization
- 🔒 Database encryption at rest

## 📊 Performance Considerations

### Backend Optimization
- **AI Model Caching**: Models loaded once at startup
- **Connection Pooling**: SQLAlchemy pool for database
- **Async Operations**: FastAPI async/await for I/O
- **Batch Processing**: Could batch review classifications

### Database Optimization
- **Indexes**: All foreign keys indexed
- **Pagination**: Limit query results
- **Efficient Joins**: Minimize join depth
- **Query Optimization**: Use EXPLAIN for slow queries

### Frontend Optimization
- **Code Splitting**: Vite builds separate chunks
- **Lazy Loading**: React.lazy for routes
- **Caching**: Browser caching for static assets
- **Compression**: Nginx gzip compression

### Scaling Strategy

**Horizontal Scaling**:
```
Load Balancer
    │
    ├─► Backend Instance 1
    ├─► Backend Instance 2
    └─► Backend Instance 3
         │
         └─► Shared PostgreSQL
              └─► Redis Cache (optional)
```

**AI Model Optimization**:
- Use quantized models (INT8)
- GPU acceleration for high volume
- Separate AI service with queue
- Cache common classifications

## 🔍 Monitoring & Observability

### Health Checks
- `GET /health`: Backend health endpoint
- Database connection checks
- AI model availability checks

### Logging
- Request/response logging
- Error tracking
- Classification decision logging
- Admin action audit trail

### Metrics (Future)
- Review submission rate
- Classification accuracy
- Response times
- User satisfaction scores
- Support ticket resolution time

## 🧪 Testing Strategy

### Unit Tests
- AI classifier logic
- Value score calculations
- Input validation
- Database models

### Integration Tests
- API endpoint testing
- Database operations
- End-to-end review flow

### AI Model Testing
- Classification accuracy
- Language detection accuracy
- Embedding quality
- Edge case handling

## 🚀 Deployment Architecture

### Docker Compose (Development)
```
┌──────────────┐
│   Frontend   │ :3000
└──────┬───────┘
       │
┌──────┴───────┐
│   Backend    │ :8000
└──────┬───────┘
       │
┌──────┴───────┐
│  PostgreSQL  │ :5432
└──────────────┘
```

### Production (Kubernetes)
```
┌─────────────────────────────────┐
│      Ingress Controller         │
└────────────┬────────────────────┘
             │
    ┌────────┴────────┐
    │                 │
┌───┴─────┐     ┌────┴─────┐
│Frontend │     │ Backend  │
│  Pods   │     │  Pods    │
└─────────┘     └────┬─────┘
                     │
              ┌──────┴──────┐
              │  PostgreSQL │
              │   Service   │
              └─────────────┘
```

## 📋 API Design Principles

1. **RESTful**: Standard HTTP methods (GET, POST)
2. **JSON**: All request/response in JSON
3. **Versioned**: `/api` prefix for future versioning
4. **Documented**: OpenAPI/Swagger docs
5. **Consistent**: Standard error responses
6. **Idempotent**: Safe retry mechanisms

## 🔄 State Management

### Frontend State
- **Local State**: Component-level with useState
- **Route State**: React Router for navigation
- **API State**: Direct API calls, no global state
- **Future**: Consider Redux for complex admin state

### Backend State
- **Stateless**: Each request independent
- **Database**: All state in PostgreSQL
- **Session**: No sessions (demo)
- **Cache**: No caching layer (add Redis for production)

## 🎯 Design Decisions

### Why FastAPI?
- Fast, modern Python framework
- Automatic API documentation
- Pydantic validation
- Async support
- Type hints

### Why React?
- Component-based architecture
- Large ecosystem
- Excellent developer experience
- Vite for fast builds

### Why PostgreSQL?
- Robust relational database
- UUID support
- Array columns
- JSON support
- ACID compliance

### Why Local AI Models?
- Privacy (no data sent to external APIs)
- Cost (no per-request charges)
- Control (customizable)
- Speed (local inference)
- Offline capability

## 📚 References

- FastAPI: https://fastapi.tiangolo.com/
- React: https://react.dev/
- XLM-RoBERTa: https://huggingface.co/cardiffnlp/twitter-xlm-roberta-base-sentiment
- Sentence Transformers: https://www.sbert.net/
- PostgreSQL: https://www.postgresql.org/

---

This architecture is designed for demonstration purposes. Production deployments should include additional security, monitoring, and scaling considerations.
