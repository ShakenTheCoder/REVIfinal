# REVI Quick Start Guide

Get REVI up and running in 5 minutes!

## Prerequisites

- Docker & Docker Compose installed
- 8GB+ available RAM
- 10GB+ disk space

## Installation

### Option 1: Automated Setup (Recommended)

```bash
# Clone the repository
git clone <repository-url>
cd revi

# Run the setup script
chmod +x setup.sh
./setup.sh
```

### Option 2: Manual Setup

```bash
# Clone the repository
git clone <repository-url>
cd revi

# Start all services
docker-compose up -d --build
```

**Note**: First build will take 5-10 minutes to download AI models (~1GB).

## Access the Application

Once all containers are running:

- **Frontend (Store)**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs

## Quick Demo

### 1. Browse Products

1. Open http://localhost:3000
2. You'll see 3 demo products:
   - Premium Wireless Bluetooth Headphones
   - Smart Fitness Tracker Watch
   - Organic Green Tea Collection

### 2. View a Product

Click on any product to see:
- Product details
- Key features
- Existing reviews (initially empty)

### 3. Submit Test Reviews

Try submitting these different types of reviews:

#### ✅ Positive Review (Will be published)
```
Name: John Smith
Rating: ⭐⭐⭐⭐⭐
Review: "These headphones are amazing! The active noise cancellation works perfectly and the battery really does last 30 hours. Very comfortable for long listening sessions. Highly recommend!"
☑ Verified Purchase
```

#### 🔴 Negative Review (Will be published)
```
Name: Sarah Johnson
Rating: ⭐⭐
Review: "Disappointed with the build quality. The headphones feel cheap and flimsy. The battery life is nowhere near the advertised 30 hours - I'm getting maybe 15 hours at best."
☑ Verified Purchase
```

#### 🎫 Support Ticket (Creates ticket)
```
Name: Mike Wilson
Email: mike@example.com
Rating: ⭐
Review: "BROKEN! The left ear stopped working after just 2 days. This is completely unacceptable. I need a replacement immediately or a full refund!"
☑ Verified Purchase
```

#### 👻 Shadow Review (Published but hidden)
```
Name: Anonymous
Rating: ⭐⭐⭐⭐⭐
Review: "Great product!"
```

#### ❌ Rejected Review (Not published)
```
Name: Confused Buyer
Rating: ⭐
Review: "I ordered the red headphones but received blue ones! This is false advertising!"
Note: Product description says "matte black finish" - review will be rejected
```

#### 🇷🇴 Romanian Review (Will be classified)
```
Name: Ion Popescu
Rating: ⭐⭐⭐⭐⭐
Review: "Produs excelent! Calitatea sunetului este extraordinară și reducerea zgomotului funcționează perfect. Bateria durează exact cât este specificat. Recomand cu încredere!"
☑ Verified Purchase
```

### 4. View Reviews

After submitting reviews:

1. Go back to the product page
2. Scroll to "Customer Reviews"
3. Switch between tabs:
   - **Positive Reviews**: See published positive reviews
   - **Negative Reviews**: See negative reviews with issue summary
   - **Shadow Reviews**: See shadow-banned reviews

### 5. Access Admin Panel

1. Click "Admin Panel" in the navigation
2. Explore:
   - **All Reviews**: See all submitted reviews with AI classifications
   - **Shadow Reviews**: Reviews that were shadow-banned
   - **Rejected Reviews**: Reviews that were not published
   - **Support Tickets**: Auto-generated tickets from problematic reviews

## Understanding the AI Classification

Each review is automatically classified:

| Category | Criteria | Action |
|----------|----------|--------|
| **Public Positive** | Positive sentiment + relevant content | Published ✅ + Thank you response |
| **Public Negative** | Negative sentiment + relevant content | Published ⚠️ + Sorry response |
| **Support** | Technical issues + complaints | Creates ticket 🎫 |
| **Shadow** | Generic/bot-like (e.g., "Great!") | Published but hidden 👻 |
| **Rejected** | Irrelevant or contradictory | Not published ❌ |

## View the Classification Details

1. Submit any review
2. Check the response message
3. Go to Admin Panel → All Reviews
4. See the AI classification details:
   - Category
   - Confidence score
   - Reason
   - Tags
   - Value score

## Value Score Explained

Each review gets a value score (0-100) based on:

- **30%** - Semantic similarity to product description
- **25%** - Number of product features mentioned
- **15%** - Review length (optimal: 100-500 chars)
- **10%** - Verified purchase status
- **10%** - Sentiment confidence
- **10%** - User helpfulness votes

Higher scores appear first in the review list.

## Troubleshooting

### Containers not starting?

```bash
# Check container status
docker-compose ps

# View logs
docker-compose logs backend
docker-compose logs frontend
docker-compose logs postgres
```

### Can't access frontend?

```bash
# Restart frontend
docker-compose restart frontend

# Check if port 3000 is available
lsof -i :3000
```

### Backend errors?

```bash
# Check backend logs
docker-compose logs -f backend

# Restart backend
docker-compose restart backend
```

### Database issues?

```bash
# Check database
docker exec -it revi-postgres psql -U revi_user -d revi_db

# Verify tables
\dt

# Check products
SELECT * FROM products;
```

## Stop the Application

```bash
# Stop all services
docker-compose down

# Stop and remove volumes (cleans database)
docker-compose down -v
```

## Next Steps

- Read [README.md](README.md) for complete documentation
- Check [API.md](API.md) for API reference
- See [DEPLOYMENT.md](DEPLOYMENT.md) for production deployment

## Support

Having issues? Check:
1. Docker is running: `docker ps`
2. Ports 3000 and 8000 are free
3. You have enough disk space: `df -h`
4. You have enough RAM: `free -h`

For more help, open an issue in the repository.

---

**Enjoy exploring REVI!** 🚀
