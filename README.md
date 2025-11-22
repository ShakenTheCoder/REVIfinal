# REVI - AI-Powered Review Moderation System

REVI is a complete full-stack system that integrates into any business website and automatically moderates customer reviews using AI. It uses local open-source models for multilingual (English + Romanian) review classification and moderation.

## 🏗️ Architecture

- **Frontend**: React 18 + Vite + TailwindCSS
- **Backend**: Python FastAPI
- **Database**: PostgreSQL 15
- **AI Models**: 
  - XLM-RoBERTa for sentiment analysis
  - Multilingual Sentence Transformers for embeddings
  - Local classification pipeline

## 📋 Features

### Core Functionality

1. **Mock E-Commerce Store**
   - Product listing page
   - Detailed product pages with images, descriptions, and key features
   - Review submission forms

2. **AI-Powered Review Classification**
   - **Category 1 - Public Positive**: Positive, relevant reviews published on Positive tab with automatic thank you responses
   - **Category 2 - Public Negative**: Negative, relevant reviews published on Negative tab with summary
   - **Category 3 - Support**: Technical issues automatically create support tickets
   - **Category 4 - Shadow**: Generic/bot-like reviews published but shadow-banned
   - **Category 5 - Rejected**: Irrelevant or contradictory reviews are rejected with explanation

3. **Review Value Scoring Algorithm**
   ```
   V = 0.30*K + 0.25*D + 0.15*L + 0.10*P + 0.10*S + 0.10*U
   ```
   Where:
   - K: Semantic similarity to product description
   - D: Matched product keypoints
   - L: Review length score
   - P: Verified purchase bonus
   - S: Sentiment confidence
   - U: Usefulness factor (can be updated by user votes)

4. **Admin Panel**
   - View all reviews with classifications
   - Manage shadow reviews
   - Review rejected reviews
   - Support ticket management with priority assignment
   - Manual category override capability
   - Complete audit trail

5. **Public Review Tabs**
   - Positive Reviews (sorted by value score)
   - Negative Reviews (with pinned issue summary)
   - Shadow Reviews (hidden from public by default)

## 🗄️ Database Schema

### Tables

- **stores**: Store information
- **products**: Product catalog with keypoints
- **users**: Customer information
- **base_reviews**: All submitted reviews (raw data)
- **review_analysis**: AI classification results
- **published_reviews**: Public-facing reviews
- **rejected_reviews**: Rejected reviews with reasons
- **support_tickets**: Auto-generated support tickets
- **admin_actions**: Audit trail for admin actions

See `database/init.sql` for complete schema.

## 🤖 AI Classification Pipeline

### System Prompt

```
You are REVI, an AI system for automated review moderation.

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
```

### Classification Output

```json
{
  "review_id": "...",
  "category": "public_positive | public_negative | support | shadow | rejected",
  "confidence": 0.0-1.0,
  "reason": "...",
  "tags": ["keyword1","keyword2"],
  "severity": "low|medium|high",
  "recommended_action": "publish | publish_shadow | create_ticket | reject",
  "matched_description_points": ["...","..."],
  "suggested_automatic_response": "English only"
}
```

### Models Used

1. **Sentiment Analysis**: `cardiffnlp/twitter-xlm-roberta-base-sentiment`
   - Multilingual sentiment classification
   - Supports English and Romanian

2. **Semantic Embeddings**: `paraphrase-multilingual-MiniLM-L12-v2`
   - Sentence embeddings for similarity calculation
   - Used for value score computation

## 🚀 Quick Start

### Prerequisites

- Docker & Docker Compose
- 8GB+ RAM (for AI models)
- 10GB+ disk space

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd revi
   ```

2. **Start all services with Docker Compose**
   ```bash
   docker-compose up --build
   ```

   This will:
   - Build and start PostgreSQL database
   - Initialize database schema with mock data
   - Build and start FastAPI backend
   - Download AI models (first run takes 5-10 minutes)
   - Build and start React frontend

3. **Access the application**
   - **Frontend**: http://localhost:3000
   - **Backend API**: http://localhost:8000
   - **API Docs**: http://localhost:8000/docs

### First Run Notes

- First startup will download ~1GB of AI models
- Models are cached in the Docker image after first build
- Database is initialized with 3 mock products

## 📡 API Endpoints

### Public Endpoints

- `GET /api/products` - List all products
- `GET /api/products/{id}` - Get product details
- `GET /api/products/{id}/reviews/public?tab={positive|negative|shadow}` - Get public reviews
- `POST /api/reviews` - Submit a review

### Admin Endpoints

- `GET /api/admin/reviews/all` - Get all reviews
- `GET /api/admin/reviews/shadow` - Get shadow reviews
- `GET /api/admin/reviews/rejected` - Get rejected reviews
- `GET /api/admin/reviews/{id}` - Get detailed review info
- `GET /api/admin/support` - Get support tickets
- `POST /api/admin/tickets/{id}/assign` - Assign ticket to agent
- `POST /api/admin/reviews/{id}/override` - Override review category

## 🧪 Testing the System

### Test Review Categories

1. **Public Positive** (will be published)
   ```
   Rating: 5 stars
   Text: "These headphones are amazing! The noise cancellation works perfectly and the battery life is exactly as advertised. Very comfortable for long listening sessions."
   ```

2. **Public Negative** (will be published)
   ```
   Rating: 2 stars
   Text: "Disappointed with the build quality. The headphones feel cheap and the battery doesn't last as long as advertised. Not worth the price."
   ```

3. **Support Ticket** (will create ticket)
   ```
   Rating: 1 star
   Text: "The headphones stopped working after 2 days. The left ear is completely broken. I need a replacement immediately!"
   Email: customer@example.com
   ```

4. **Shadow** (published but hidden)
   ```
   Rating: 5 stars
   Text: "Great product!"
   ```

5. **Rejected** (not published)
   ```
   Rating: 1 star
   Text: "I ordered red headphones but received blue ones!"
   Note: Product description says "matte black finish"
   ```

### Romanian Language Support

```
Rating: 5 stars
Text: "Produs excelent! Calitate foarte bună și funcționează perfect. Recomand!"
```

## 📁 Project Structure

```
revi/
├── backend/
│   ├── app/
│   │   ├── ai/
│   │   │   ├── classifier.py      # AI classification logic
│   │   │   ├── embeddings.py      # Semantic similarity
│   │   │   └── responses.py       # Auto-response generation
│   │   ├── api/
│   │   │   ├── public.py          # Public API endpoints
│   │   │   └── admin.py           # Admin API endpoints
│   │   ├── utils/
│   │   │   └── scoring.py         # Value score calculation
│   │   ├── database.py            # Database connection
│   │   ├── models.py              # SQLAlchemy models
│   │   ├── schemas.py             # Pydantic schemas
│   │   └── main.py                # FastAPI app
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── ReviewForm.jsx     # Review submission form
│   │   │   └── ReviewTabs.jsx     # Review display tabs
│   │   ├── pages/
│   │   │   ├── HomePage.jsx       # Product listing
│   │   │   ├── ProductPage.jsx    # Product details
│   │   │   └── AdminPage.jsx      # Admin panel
│   │   ├── services/
│   │   │   └── api.js             # API client
│   │   ├── App.jsx
│   │   └── main.jsx
│   ├── package.json
│   ├── vite.config.js
│   ├── tailwind.config.js
│   └── Dockerfile
├── database/
│   └── init.sql                   # Database schema + mock data
├── docker-compose.yml
└── README.md
```

## 🔧 Development

### Backend Development

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Frontend Development

```bash
cd frontend
npm install
npm run dev
```

### Database Access

```bash
docker exec -it revi-postgres psql -U revi_user -d revi_db
```

## 🎯 Key Business Logic

### Review Processing Workflow

1. User submits review via form
2. Review saved to `base_reviews` table
3. AI classifier analyzes review:
   - Sentiment analysis
   - Keypoint matching
   - Language detection
   - Category determination
4. Analysis saved to `review_analysis` table
5. Value score calculated
6. Action taken based on category:
   - **Public**: Add to `published_reviews`
   - **Support**: Create `support_ticket`
   - **Rejected**: Add to `rejected_reviews`
7. User receives appropriate response
8. Admin can override any classification

### Value Score Factors

- **Semantic Similarity (30%)**: How well review matches product description
- **Keypoint Matches (25%)**: Number of product features mentioned
- **Length (15%)**: Optimal 100-500 characters
- **Verified Purchase (10%)**: Bonus for verified buyers
- **Sentiment (10%)**: Confidence of sentiment analysis
- **Usefulness (10%)**: Based on user helpful votes

## 🔒 Security Considerations

- No authentication implemented (demo system)
- Input validation on all endpoints
- SQL injection prevention via SQLAlchemy ORM
- CORS configured for development
- Admin endpoints should be protected in production

## 🚀 Production Deployment

1. Add authentication/authorization
2. Use environment variables for secrets
3. Configure proper CORS origins
4. Set up SSL/TLS certificates
5. Use production-grade WSGI server (Gunicorn)
6. Configure nginx reverse proxy
7. Set up monitoring and logging
8. Regular database backups

## 📊 Monitoring

- Backend health check: `GET /health`
- API documentation: http://localhost:8000/docs
- Database monitoring via pgAdmin or similar tools

## 🤝 Contributing

This is a demonstration system. For production use, consider:
- Adding user authentication
- Implementing rate limiting
- Adding email notifications
- Implementing real-time updates (WebSockets)
- Adding more sophisticated AI models
- Implementing A/B testing for classification rules

## 📝 License

MIT License - See LICENSE file for details

## 🙏 Acknowledgments

- XLM-RoBERTa by Cardiff NLP
- Sentence Transformers by UKPLab
- FastAPI by Sebastián Ramírez
- React by Meta

## 📞 Support

For issues and questions, please open an issue in the repository.

---

**REVI** - Intelligent Review Moderation, Powered by AI
