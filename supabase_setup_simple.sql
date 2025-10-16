-- Paper-CMS Database Setup for Supabase PostgreSQL (Simplified Version)
-- Run this SQL in your Supabase SQL Editor
-- This version does not use Row Level Security for easier setup

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create enum types
CREATE TYPE user_role AS ENUM ('AUTHOR', 'REVIEWER', 'ADMIN');
CREATE TYPE paper_status AS ENUM ('SUBMITTED', 'UNDER_REVIEW', 'REVIEWED', 'ACCEPTED', 'REJECTED', 'REVISION_REQUIRED');
CREATE TYPE review_recommendation AS ENUM ('ACCEPT', 'MINOR_REVISION', 'MAJOR_REVISION', 'REJECT');
CREATE TYPE conference_status AS ENUM ('ACTIVE', 'CLOSED', 'UPCOMING');

-- Users table
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(120) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role user_role NOT NULL DEFAULT 'AUTHOR',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE
);

-- Categories table
CREATE TABLE IF NOT EXISTS categories (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL,
    description TEXT,
    color VARCHAR(7) DEFAULT '#007bff'
);

-- Conferences table
CREATE TABLE IF NOT EXISTS conferences (
    id SERIAL PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    year INTEGER NOT NULL,
    submission_deadline TIMESTAMP NOT NULL,
    review_deadline TIMESTAMP,
    notification_date TIMESTAMP,
    status conference_status NOT NULL DEFAULT 'UPCOMING',
    description TEXT,
    website VARCHAR(500),
    reviews_per_paper INTEGER DEFAULT 3
);

-- Papers table
CREATE TABLE IF NOT EXISTS papers (
    id SERIAL PRIMARY KEY,
    title VARCHAR(500) NOT NULL,
    abstract TEXT NOT NULL,
    status paper_status NOT NULL DEFAULT 'SUBMITTED',
    submission_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    file_path VARCHAR(500),
    conference_name VARCHAR(200) NOT NULL,
    keywords VARCHAR(500),
    submitted_by INTEGER NOT NULL REFERENCES users(id),
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Reviews table
CREATE TABLE IF NOT EXISTS reviews (
    id SERIAL PRIMARY KEY,
    paper_id INTEGER NOT NULL REFERENCES papers(id) ON DELETE CASCADE,
    reviewer_id INTEGER NOT NULL REFERENCES users(id),
    score INTEGER,
    comments TEXT,
    recommendation review_recommendation,
    review_date TIMESTAMP,
    assigned_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    deadline TIMESTAMP,
    is_completed BOOLEAN DEFAULT FALSE,
    technical_quality INTEGER,
    novelty INTEGER,
    clarity INTEGER,
    significance INTEGER
);

-- Affiliations table
CREATE TABLE IF NOT EXISTS affiliations (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    institution_name VARCHAR(200) NOT NULL,
    department VARCHAR(200),
    position VARCHAR(100),
    is_primary BOOLEAN DEFAULT FALSE
);

-- Paper-Authors junction table
CREATE TABLE IF NOT EXISTS paper_authors (
    paper_id INTEGER REFERENCES papers(id) ON DELETE CASCADE,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    PRIMARY KEY (paper_id, user_id)
);

-- Paper-Categories junction table
CREATE TABLE IF NOT EXISTS paper_categories (
    paper_id INTEGER REFERENCES papers(id) ON DELETE CASCADE,
    category_id INTEGER REFERENCES categories(id) ON DELETE CASCADE,
    PRIMARY KEY (paper_id, category_id)
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_users_role ON users(role);
CREATE INDEX IF NOT EXISTS idx_papers_status ON papers(status);
CREATE INDEX IF NOT EXISTS idx_papers_conference ON papers(conference_name);
CREATE INDEX IF NOT EXISTS idx_papers_submitted_by ON papers(submitted_by);
CREATE INDEX IF NOT EXISTS idx_reviews_paper ON reviews(paper_id);
CREATE INDEX IF NOT EXISTS idx_reviews_reviewer ON reviews(reviewer_id);
CREATE INDEX IF NOT EXISTS idx_reviews_completed ON reviews(is_completed);

-- Create trigger to update last_updated on papers
CREATE OR REPLACE FUNCTION update_last_updated()
RETURNS TRIGGER AS $$
BEGIN
    NEW.last_updated = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_papers_last_updated
    BEFORE UPDATE ON papers
    FOR EACH ROW
    EXECUTE FUNCTION update_last_updated();

-- Insert default admin user (password: admin123)
-- You should change this password after first login
INSERT INTO users (name, email, password_hash, role) 
VALUES (
    'Administrator', 
    'admin@paper-cms.com', 
    'scrypt:32768:8:1$qJ8VWq8IjXlE1O0P$ae6c9f8b5c4d3e2f1a0b9c8d7e6f5a4b3c2d1e0f9a8b7c6d5e4f3a2b1c0d9e8f7a6b5c4d3e2f1a0b9c8d7e6f', 
    'ADMIN'
) ON CONFLICT (email) DO NOTHING;

-- Insert default categories
INSERT INTO categories (name, description, color) VALUES
    ('Computer Science', 'General computer science research', '#007bff'),
    ('Machine Learning', 'AI and ML research papers', '#28a745'),
    ('Data Science', 'Data analysis and statistics', '#ffc107'),
    ('Software Engineering', 'Software development research', '#dc3545'),
    ('Cybersecurity', 'Security and privacy research', '#6f42c1')
ON CONFLICT (name) DO NOTHING;

-- Create a sample conference
INSERT INTO conferences (name, year, submission_deadline, status, description, reviews_per_paper) VALUES
    ('International Conference on Academic Research', 2025, '2025-06-01 23:59:59', 'ACTIVE', 'Premier academic research conference', 3)
ON CONFLICT DO NOTHING;

COMMIT;

-- IMPORTANT NOTES:
-- 1. This setup does NOT enable Row Level Security (RLS) for easier initial setup
-- 2. Create a storage bucket named 'papers' in Supabase Storage dashboard
-- 3. Set the bucket to private and configure appropriate policies
-- 4. Change the default admin password after first login
-- 5. If you need RLS, run the policies from the main supabase_setup.sql file separately