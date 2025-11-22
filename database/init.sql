-- REVI Database Schema
-- Complete PostgreSQL schema for AI-powered review moderation system

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Stores table
CREATE TABLE stores (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    domain VARCHAR(255) UNIQUE NOT NULL,
    logo_url TEXT,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE
);

-- Products table
CREATE TABLE products (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    store_id UUID REFERENCES stores(id) ON DELETE CASCADE,
    title VARCHAR(500) NOT NULL,
    description TEXT NOT NULL,
    long_description TEXT,
    price DECIMAL(10, 2) NOT NULL,
    currency VARCHAR(3) DEFAULT 'USD',
    image_url TEXT,
    category VARCHAR(100),
    keypoints TEXT[], -- Array of key product features
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE
);

-- Users table
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255),
    email VARCHAR(255) UNIQUE,
    is_verified_purchaser BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    total_reviews INTEGER DEFAULT 0
);

-- Base reviews table (all submitted reviews, raw)
CREATE TABLE base_reviews (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    product_id UUID REFERENCES products(id) ON DELETE CASCADE,
    user_id UUID REFERENCES users(id) ON DELETE SET NULL,
    reviewer_name VARCHAR(255),
    reviewer_email VARCHAR(255),
    rating INTEGER CHECK (rating >= 1 AND rating <= 5),
    review_text TEXT NOT NULL,
    language VARCHAR(10), -- 'en' or 'ro'
    is_verified_purchase BOOLEAN DEFAULT FALSE,
    submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ip_address VARCHAR(45)
);

-- Review analysis table (AI classification results)
CREATE TABLE review_analysis (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    review_id UUID REFERENCES base_reviews(id) ON DELETE CASCADE UNIQUE,
    category VARCHAR(50) NOT NULL, -- 'public_positive', 'public_negative', 'support', 'shadow', 'rejected'
    confidence DECIMAL(3, 2) CHECK (confidence >= 0 AND confidence <= 1),
    reason TEXT,
    tags TEXT[],
    severity VARCHAR(20), -- 'low', 'medium', 'high'
    recommended_action VARCHAR(50),
    matched_description_points TEXT[],
    suggested_automatic_response TEXT,
    value_score DECIMAL(5, 2) DEFAULT 0, -- Calculated ranking score
    analyzed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Published reviews table (public-facing reviews)
CREATE TABLE published_reviews (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    review_id UUID REFERENCES base_reviews(id) ON DELETE CASCADE,
    analysis_id UUID REFERENCES review_analysis(id) ON DELETE CASCADE,
    is_shadow BOOLEAN DEFAULT FALSE, -- Shadow-banned reviews
    automatic_response TEXT,
    response_language VARCHAR(10) DEFAULT 'en',
    published_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    views INTEGER DEFAULT 0,
    helpful_count INTEGER DEFAULT 0
);

-- Rejected reviews table (not published)
CREATE TABLE rejected_reviews (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    review_id UUID REFERENCES base_reviews(id) ON DELETE CASCADE,
    analysis_id UUID REFERENCES review_analysis(id) ON DELETE CASCADE,
    rejection_reason TEXT NOT NULL,
    user_notified BOOLEAN DEFAULT FALSE,
    notification_message TEXT,
    rejected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Support tickets table
CREATE TABLE support_tickets (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    review_id UUID REFERENCES base_reviews(id) ON DELETE CASCADE,
    analysis_id UUID REFERENCES review_analysis(id) ON DELETE CASCADE,
    priority VARCHAR(20) DEFAULT 'normal', -- 'high', 'normal', 'low'
    status VARCHAR(20) DEFAULT 'open', -- 'open', 'assigned', 'resolved', 'closed'
    assigned_to VARCHAR(255),
    issue_description TEXT,
    customer_email VARCHAR(255),
    automatic_response TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    resolved_at TIMESTAMP
);

-- Admin actions table (audit trail)
CREATE TABLE admin_actions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    admin_user VARCHAR(255) NOT NULL,
    action_type VARCHAR(50) NOT NULL, -- 'override', 'publish', 'reject', 'assign_ticket', etc.
    target_id UUID NOT NULL, -- ID of the affected entity
    target_type VARCHAR(50) NOT NULL, -- 'review', 'ticket', etc.
    reason TEXT,
    old_value TEXT,
    new_value TEXT,
    performed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for performance
CREATE INDEX idx_products_store ON products(store_id);
CREATE INDEX idx_base_reviews_product ON base_reviews(product_id);
CREATE INDEX idx_base_reviews_submitted ON base_reviews(submitted_at DESC);
CREATE INDEX idx_review_analysis_review ON review_analysis(review_id);
CREATE INDEX idx_review_analysis_category ON review_analysis(category);
CREATE INDEX idx_published_reviews_review ON published_reviews(review_id);
CREATE INDEX idx_support_tickets_status ON support_tickets(status);
CREATE INDEX idx_support_tickets_priority ON support_tickets(priority);

-- Insert mock store data
INSERT INTO stores (id, name, domain, description) VALUES 
('550e8400-e29b-41d4-a716-446655440000', 'REVI Demo Store', 'demo.revi.ai', 'AI-powered e-commerce demo store');

-- Insert mock products
INSERT INTO products (id, store_id, title, description, long_description, price, image_url, category, keypoints) VALUES 
(
    '650e8400-e29b-41d4-a716-446655440001',
    '550e8400-e29b-41d4-a716-446655440000',
    'Premium Wireless Bluetooth Headphones',
    'High-quality over-ear headphones with active noise cancellation',
    'Experience superior sound quality with our Premium Wireless Bluetooth Headphones. Featuring advanced active noise cancellation technology, these headphones deliver crystal-clear audio in any environment. The soft memory foam ear cushions provide all-day comfort, while the 30-hour battery life ensures uninterrupted listening. Bluetooth 5.0 connectivity offers stable wireless connection up to 10 meters. The foldable design makes them perfect for travel. Available in matte black finish with premium aluminum construction.',
    149.99,
    'https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=800',
    'Electronics',
    ARRAY['Active Noise Cancellation', 'Bluetooth 5.0', '30-hour battery life', 'Memory foam cushions', 'Foldable design', 'Matte black finish', 'Aluminum construction']
),
(
    '650e8400-e29b-41d4-a716-446655440002',
    '550e8400-e29b-41d4-a716-446655440000',
    'Smart Fitness Tracker Watch',
    'Advanced fitness tracker with heart rate monitoring and GPS',
    'Track your fitness journey with our Smart Fitness Tracker Watch. This advanced wearable monitors your heart rate 24/7, tracks multiple workout modes including running, cycling, and swimming. Built-in GPS accurately maps your outdoor activities. The vibrant AMOLED touchscreen display shows real-time stats and notifications from your phone. Water-resistant up to 50 meters, making it perfect for swimming. Battery lasts up to 7 days on a single charge. Includes sleep tracking, stress monitoring, and guided breathing exercises. Compatible with iOS and Android.',
    89.99,
    'https://images.unsplash.com/photo-1575311373937-040b8e1fd5b6?w=800',
    'Fitness',
    ARRAY['Heart rate monitoring', 'Built-in GPS', 'AMOLED display', '50m water resistant', '7-day battery', 'Multiple workout modes', 'Sleep tracking', 'iOS and Android compatible']
),
(
    '650e8400-e29b-41d4-a716-446655440003',
    '550e8400-e29b-41d4-a716-446655440000',
    'Organic Green Tea Collection - 100 Bags',
    'Premium organic green tea from sustainable farms',
    'Discover the perfect cup with our Organic Green Tea Collection. Sourced from certified organic tea gardens in the mountains, each tea bag contains carefully selected green tea leaves that deliver a smooth, refreshing taste with natural antioxidants. This collection includes 100 individually wrapped tea bags to preserve freshness. No artificial flavors or additives - just pure, natural green tea. Rich in EGCG and antioxidants for health benefits. Each cup provides a calming ritual with delicate floral notes and a clean finish. Perfect for daily wellness routine.',
    24.99,
    'https://images.unsplash.com/photo-1564890369478-c89ca6d9cde9?w=800',
    'Food & Beverage',
    ARRAY['100% organic certified', '100 tea bags', 'Natural antioxidants', 'No artificial additives', 'Mountain-sourced', 'Individually wrapped', 'Rich in EGCG', 'Smooth taste']
);

-- Create function to update timestamps
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create triggers for updated_at
CREATE TRIGGER update_stores_updated_at BEFORE UPDATE ON stores FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_products_updated_at BEFORE UPDATE ON products FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_support_tickets_updated_at BEFORE UPDATE ON support_tickets FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
