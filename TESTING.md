# REVI Testing Guide

Complete guide for testing the REVI AI review moderation system.

## 🧪 Test Categories

This guide covers testing all 5 review classification categories with specific examples.

## Prerequisites

Ensure REVI is running:
```bash
docker-compose up -d
```

Access the frontend at http://localhost:3000

## Test Product Selection

For all tests, we'll use the **Premium Wireless Bluetooth Headphones** product.

Product Details:
- Price: $149.99
- Key Features: Active Noise Cancellation, Bluetooth 5.0, 30-hour battery life
- Color: Matte black finish

---

## Category 1: Public Positive ✅

These reviews should be **published on the Positive Reviews tab** with an automatic thank you response.

### Test Case 1.1: Detailed Positive Review

**Input:**
```
Name: Sarah Mitchell
Email: sarah.m@email.com
Rating: ⭐⭐⭐⭐⭐ (5 stars)
Review: "These headphones exceeded my expectations! The active noise cancellation is phenomenal - I can work in a busy coffee shop without any distractions. The Bluetooth 5.0 connection is rock solid, and the 30-hour battery life is accurate. The memory foam cushions are incredibly comfortable even after 8 hours of use."
☑ Verified Purchase
```

**Expected Result:**
- Status: `published`
- Category: `public_positive`
- Automatic Response: Thank you message in English
- Value Score: ~85-90 (high score due to keypoint matches)
- Published on: Positive Reviews tab

**Verification:**
1. Submit the review
2. Check response message
3. Go to Positive Reviews tab
4. Verify review appears with high value score
5. Check Admin Panel → All Reviews for classification details

### Test Case 1.2: Short Positive Review

**Input:**
```
Name: Mike Johnson
Rating: ⭐⭐⭐⭐ (4 stars)
Review: "Good headphones, sound quality is great and battery lasts long."
```

**Expected Result:**
- Status: `published`
- Category: `public_positive`
- Value Score: ~55-65 (lower due to length)
- Published on: Positive Reviews tab

---

## Category 2: Public Negative 🔴

These reviews should be **published on the Negative Reviews tab** and included in the summary.

### Test Case 2.1: Legitimate Complaint

**Input:**
```
Name: David Chen
Email: david.c@email.com
Rating: ⭐⭐ (2 stars)
Review: "Very disappointed with these headphones. The build quality feels cheap and flimsy. The battery life is nowhere near 30 hours - I'm getting maybe 15 hours at best. The noise cancellation is mediocre compared to competitors. Not worth $149.99."
☑ Verified Purchase
```

**Expected Result:**
- Status: `published`
- Category: `public_negative`
- Automatic Response: Apology message
- Published on: Negative Reviews tab
- Included in: Negative summary at top
- Value Score: ~60-70 (detailed feedback)

**Verification:**
1. Submit the review
2. Go to Negative Reviews tab
3. Check if review appears in summary box
4. Verify automatic apology response

### Test Case 2.2: Constructive Criticism

**Input:**
```
Name: Emily Roberts
Rating: ⭐⭐⭐ (3 stars)
Review: "The sound quality is decent, but the headphones are uncomfortable for long wear. The ear cushions get hot after an hour. The aluminum construction is nice but adds unnecessary weight. Good product overall but needs improvements."
```

**Expected Result:**
- Status: `published`
- Category: `public_negative`
- Published on: Negative Reviews tab

---

## Category 3: Support Ticket 🎫

These reviews should **create a support ticket** and NOT be published.

### Test Case 3.1: Product Defect (High Priority)

**Input:**
```
Name: John Williams
Email: john.w@email.com
Rating: ⭐ (1 star)
Review: "BROKEN! The left ear stopped working completely after just 2 days of use. This is unacceptable for a $150 product. I need a replacement immediately or a full refund. The right ear is crackling too."
☑ Verified Purchase
```

**Expected Result:**
- Status: `support_ticket_created`
- Category: `support`
- Message: "Your issue has been recognized. A support agent will contact you shortly."
- Ticket Priority: `high` (verified purchase)
- Not published on any tab

**Verification:**
1. Submit the review
2. Check response mentions support contact
3. Go to Admin Panel → Support Tickets
4. Verify ticket exists with high priority
5. Check ticket contains customer email

### Test Case 3.2: Technical Issue (Normal Priority)

**Input:**
```
Name: Lisa Anderson
Email: lisa.a@email.com
Rating: ⭐⭐ (2 stars)
Review: "The Bluetooth keeps disconnecting every 10 minutes. I've tried resetting them multiple times but the problem persists. Please help me fix this issue."
```

**Expected Result:**
- Status: `support_ticket_created`
- Category: `support`
- Ticket Priority: `normal` (not verified purchase)

### Test Case 3.3: Missing Email (Should request email)

**Input:**
```
Name: Anonymous User
Rating: ⭐ (1 star)
Review: "Headphones are defective and not working properly. Need warranty service."
(No email provided)
```

**Expected Result:**
- Status: `support_ticket_created`
- Message: Includes "Please provide your email so we can reach you."
- Ticket created but marked as needing contact info

---

## Category 4: Shadow 👻

These reviews should be **published but hidden** from default view (shadow-banned).

### Test Case 4.1: Generic 5-Star Review

**Input:**
```
Name: Bot User
Rating: ⭐⭐⭐⭐⭐ (5 stars)
Review: "Great product!"
```

**Expected Result:**
- Status: `published`
- Category: `shadow`
- Published on: Shadow Reviews tab only
- NOT visible in: Positive Reviews tab
- Value Score: ~40-50 (low due to no content)

**Verification:**
1. Submit the review
2. Check Positive Reviews tab - should NOT appear
3. Go to Shadow Reviews tab - should appear
4. Admin Panel → Shadow Reviews - should be listed

### Test Case 4.2: Bot-Like Pattern

**Input:**
```
Rating: ⭐⭐⭐⭐⭐ (5 stars)
Review: "Excellent!!!"
```

**Expected Result:**
- Category: `shadow`
- Reason: Generic positive without substantive content

### Test Case 4.3: Single Word Review

**Input:**
```
Rating: ⭐⭐⭐⭐⭐ (5 stars)
Review: "Perfect"
```

**Expected Result:**
- Category: `shadow`

---

## Category 5: Rejected ❌

These reviews should be **rejected and NOT published** anywhere.

### Test Case 5.1: Color Contradiction

**Input:**
```
Name: Confused Buyer
Rating: ⭐ (1 star)
Review: "I ordered the black headphones but received red ones! This is false advertising. The product page clearly showed red color but I got something completely different."
```

**Expected Result:**
- Status: `rejected`
- Category: `rejected`
- Message: "Your review was not published because it was marked as irrelevant to the product."
- Reason: Contradicts product description (product is matte black)
- Not visible on any public tab

**Verification:**
1. Submit the review
2. Check rejection message
3. Verify NOT in Positive/Negative/Shadow tabs
4. Admin Panel → Rejected Reviews - should be listed with reason

### Test Case 5.2: Completely Irrelevant

**Input:**
```
Name: Wrong Product
Rating: ⭐ (1 star)
Review: "The screen resolution is terrible and the keyboard is too small. The laptop overheats constantly."
```

**Expected Result:**
- Status: `rejected`
- Category: `rejected`
- Reason: Review is about a laptop, not headphones

### Test Case 5.3: Spam/Unrelated

**Input:**
```
Rating: ⭐⭐⭐⭐⭐ (5 stars)
Review: "Check out my website for amazing deals! www.example.com"
```

**Expected Result:**
- Status: `rejected`
- Reason: Spam/promotional content

---

## Romanian Language Testing 🇷🇴

The system supports Romanian reviews with the same classification logic.

### Test Case 6.1: Romanian Positive Review

**Input:**
```
Name: Ion Popescu
Rating: ⭐⭐⭐⭐⭐ (5 stars)
Review: "Căști excelente! Calitatea sunetului este extraordinară și anularea zgomotului funcționează perfect. Bateria durează exact cât este specificat în descriere. Foarte confortabile pentru utilizare îndelungată. Recomand cu încredere!"
☑ Verified Purchase
```

**Expected Result:**
- Status: `published`
- Category: `public_positive`
- Language: `ro` (detected)
- Automatic Response: English (as per spec)
- Published on: Positive Reviews tab

### Test Case 6.2: Romanian Support Request

**Input:**
```
Name: Maria Ionescu
Email: maria.i@email.ro
Rating: ⭐ (1 star)
Review: "Căștile sunt stricate! Sunetul nu funcționează deloc la urechea stângă. Am nevoie urgentă de înlocuire sau rambursare. Produsul este defect."
☑ Verified Purchase
```

**Expected Result:**
- Status: `support_ticket_created`
- Category: `support`
- Automatic Response: English
- Priority: `high`

### Test Case 6.3: Romanian Generic Review

**Input:**
```
Rating: ⭐⭐⭐⭐⭐ (5 stars)
Review: "Produs bun!"
```

**Expected Result:**
- Category: `shadow`
- Reason: Generic positive (Romanian equivalent of "Good product!")

---

## Value Score Testing

### Test High-Value Review

**Input:**
```
Name: Expert Reviewer
Email: expert@audio.com
Rating: ⭐⭐⭐⭐⭐ (5 stars)
Review: "As an audio professional, I'm impressed with these headphones. The active noise cancellation uses advanced algorithms to eliminate ambient noise effectively. The Bluetooth 5.0 chipset provides stable connectivity up to 10 meters. Battery life consistently delivers 28-30 hours per charge. The memory foam ear cushions with protein leather distribute pressure evenly. The aluminum construction is both durable and lightweight. The foldable design makes them travel-friendly. Sound profile is balanced with clear highs, detailed mids, and punchy bass. The matte black finish resists fingerprints."
☑ Verified Purchase
```

**Expected Result:**
- Value Score: ~95-100 (maximum score)
- Reasons:
  - Long, detailed review (L: high)
  - Multiple keypoint matches (D: high)
  - High semantic similarity (K: high)
  - Verified purchase (P: 1.0)
  - Strong positive sentiment (S: high)

**Verification:**
1. Submit review
2. Check Admin Panel for value_score
3. Verify it appears first in review list (highest score)

### Test Low-Value Review

**Input:**
```
Rating: ⭐⭐⭐⭐⭐ (5 stars)
Review: "Good"
```

**Expected Result:**
- Value Score: ~20-30 (very low)
- Published but shadow-banned
- Appears last in any listing

---

## Admin Panel Testing

### Test Admin Override

1. Submit a review that gets classified as `rejected`
2. Go to Admin Panel → Rejected Reviews
3. Click on the review
4. Override to `public_positive`
5. Verify it now appears in Positive Reviews tab

### Test Ticket Assignment

1. Submit a support-category review with email
2. Go to Admin Panel → Support Tickets
3. Find the ticket
4. Assign to "Agent Smith"
5. Verify ticket status changes to "assigned"

---

## API Testing with cURL

### Test Review Submission

```bash
curl -X POST http://localhost:8000/api/reviews \
  -H "Content-Type: application/json" \
  -d '{
    "product_id": "650e8400-e29b-41d4-a716-446655440001",
    "reviewer_name": "API Test User",
    "reviewer_email": "test@example.com",
    "rating": 5,
    "review_text": "Testing the API with a positive review about the noise cancellation and Bluetooth features.",
    "is_verified_purchase": true
  }'
```

### Test Get Reviews

```bash
# Positive reviews
curl http://localhost:8000/api/products/650e8400-e29b-41d4-a716-446655440001/reviews/public?tab=positive

# Negative reviews
curl http://localhost:8000/api/products/650e8400-e29b-41d4-a716-446655440001/reviews/public?tab=negative

# Shadow reviews
curl http://localhost:8000/api/products/650e8400-e29b-41d4-a716-446655440001/reviews/public?tab=shadow
```

---

## Expected Metrics

After running all test cases, you should see:

**Admin Panel → All Reviews:**
- Total: ~15+ reviews
- Public Positive: ~3-4 reviews
- Public Negative: ~2-3 reviews
- Support: ~3-4 tickets
- Shadow: ~3-4 reviews
- Rejected: ~2-3 reviews

**Support Tickets:**
- High Priority: 2+
- Normal Priority: 1-2

**Value Scores:**
- Range: 20-100
- Distribution: Bell curve with most in 50-70 range

---

## Troubleshooting

### Review Not Classified Correctly?

Check Admin Panel → All Reviews to see:
- AI confidence score
- Classification reason
- Matched keypoints

### Support Ticket Not Created?

Verify:
- Review contains support keywords
- Rating is low (1-3 stars)
- Check Admin Panel → Support Tickets

### Shadow Review Visible in Positive Tab?

Check:
- Admin Panel → Shadow Reviews
- Verify `is_shadow` flag is true

---

## Automated Testing (Future)

For production, implement:

```python
# pytest example
def test_positive_review_classification():
    review = {
        "product_id": "...",
        "rating": 5,
        "review_text": "Excellent noise cancellation and battery life!",
        "is_verified_purchase": True
    }
    response = client.post("/api/reviews", json=review)
    assert response.json()["category"] == "public_positive"
```

---

## Performance Testing

Test with multiple simultaneous submissions:

```bash
# Submit 100 reviews concurrently
for i in {1..100}; do
  curl -X POST http://localhost:8000/api/reviews \
    -H "Content-Type: application/json" \
    -d "{...}" &
done
wait
```

Expected: All reviews processed within 30 seconds

---

## Success Criteria

✅ All 5 categories correctly classified
✅ Romanian language properly detected and handled
✅ Value scores calculated accurately
✅ Support tickets created with correct priority
✅ Automatic responses generated in English
✅ Admin overrides work correctly
✅ No reviews lost or duplicated

---

For issues or questions, refer to README.md or open an issue in the repository.
