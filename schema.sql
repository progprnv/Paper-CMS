-- PaperFlow CMS Database Schema
-- MySQL Database Schema for Research Paper Management System

SET FOREIGN_KEY_CHECKS = 0;

-- Create database
CREATE DATABASE IF NOT EXISTS paperflow_cms CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE paperflow_cms;

-- Users table
CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(120) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role ENUM('AUTHOR', 'REVIEWER', 'ADMIN') NOT NULL DEFAULT 'AUTHOR',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP NULL,
    is_active BOOLEAN DEFAULT TRUE,
    INDEX idx_users_email (email),
    INDEX idx_users_role (role)
);

-- Conferences table
CREATE TABLE conferences (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    year INT NOT NULL,
    submission_deadline DATETIME NOT NULL,
    review_deadline DATETIME,
    notification_date DATETIME,
    status ENUM('ACTIVE', 'CLOSED', 'UPCOMING') NOT NULL DEFAULT 'UPCOMING',
    description TEXT,
    website VARCHAR(500),
    reviews_per_paper INT DEFAULT 3,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_conferences_year (year),
    INDEX idx_conferences_status (status)
);

-- Categories table
CREATE TABLE categories (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL,
    description TEXT,
    color VARCHAR(7) DEFAULT '#007bff',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Papers table
CREATE TABLE papers (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(500) NOT NULL,
    abstract TEXT NOT NULL,
    status ENUM('SUBMITTED', 'UNDER_REVIEW', 'REVIEWED', 'ACCEPTED', 'REJECTED', 'REVISION_REQUIRED') 
           NOT NULL DEFAULT 'SUBMITTED',
    submission_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    file_path VARCHAR(500),
    conference_id INT NOT NULL,
    keywords VARCHAR(500),
    submitted_by INT NOT NULL,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    FOREIGN KEY (conference_id) REFERENCES conferences(id) ON DELETE CASCADE,
    FOREIGN KEY (submitted_by) REFERENCES users(id) ON DELETE CASCADE,
    
    INDEX idx_papers_status (status),
    INDEX idx_papers_conference (conference_id),
    INDEX idx_papers_submission_date (submission_date),
    FULLTEXT idx_papers_search (title, abstract, keywords)
);

-- Paper-Authors many-to-many relationship
CREATE TABLE paper_authors (
    paper_id INT,
    user_id INT,
    PRIMARY KEY (paper_id, user_id),
    FOREIGN KEY (paper_id) REFERENCES papers(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Paper-Categories many-to-many relationship
CREATE TABLE paper_categories (
    paper_id INT,
    category_id INT,
    PRIMARY KEY (paper_id, category_id),
    FOREIGN KEY (paper_id) REFERENCES papers(id) ON DELETE CASCADE,
    FOREIGN KEY (category_id) REFERENCES categories(id) ON DELETE CASCADE
);

-- Reviews table
CREATE TABLE reviews (
    id INT AUTO_INCREMENT PRIMARY KEY,
    paper_id INT NOT NULL,
    reviewer_id INT NOT NULL,
    score INT CHECK (score >= 1 AND score <= 10),
    comments TEXT,
    recommendation ENUM('ACCEPT', 'MINOR_REVISION', 'MAJOR_REVISION', 'REJECT'),
    review_date TIMESTAMP NULL,
    assigned_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    deadline DATETIME,
    is_completed BOOLEAN DEFAULT FALSE,
    
    -- Detailed scoring
    technical_quality INT CHECK (technical_quality >= 1 AND technical_quality <= 5),
    novelty INT CHECK (novelty >= 1 AND novelty <= 5),
    clarity INT CHECK (clarity >= 1 AND clarity <= 5),
    significance INT CHECK (significance >= 1 AND significance <= 5),
    confidential_comments TEXT,
    
    FOREIGN KEY (paper_id) REFERENCES papers(id) ON DELETE CASCADE,
    FOREIGN KEY (reviewer_id) REFERENCES users(id) ON DELETE CASCADE,
    
    UNIQUE KEY unique_paper_reviewer (paper_id, reviewer_id),
    INDEX idx_reviews_paper (paper_id),
    INDEX idx_reviews_reviewer (reviewer_id),
    INDEX idx_reviews_completed (is_completed),
    INDEX idx_reviews_deadline (deadline)
);

-- Affiliations table
CREATE TABLE affiliations (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    institution_name VARCHAR(200) NOT NULL,
    department VARCHAR(200),
    position VARCHAR(100),
    is_primary BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_affiliations_user (user_id)
);

-- Notifications table (for future use)
CREATE TABLE notifications (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    title VARCHAR(200) NOT NULL,
    message TEXT NOT NULL,
    type ENUM('INFO', 'SUCCESS', 'WARNING', 'ERROR') DEFAULT 'INFO',
    is_read BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_notifications_user (user_id),
    INDEX idx_notifications_read (is_read)
);

-- Comments table (for review discussions)
CREATE TABLE comments (
    id INT AUTO_INCREMENT PRIMARY KEY,
    paper_id INT NOT NULL,
    user_id INT NOT NULL,
    parent_id INT NULL,
    content TEXT NOT NULL,
    is_public BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    FOREIGN KEY (paper_id) REFERENCES papers(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (parent_id) REFERENCES comments(id) ON DELETE CASCADE,
    
    INDEX idx_comments_paper (paper_id),
    INDEX idx_comments_user (user_id),
    INDEX idx_comments_parent (parent_id)
);

-- File tracking table
CREATE TABLE files (
    id INT AUTO_INCREMENT PRIMARY KEY,
    paper_id INT NOT NULL,
    filename VARCHAR(255) NOT NULL,
    original_filename VARCHAR(255) NOT NULL,
    file_path VARCHAR(500) NOT NULL,
    file_size BIGINT NOT NULL,
    mime_type VARCHAR(100) NOT NULL,
    version INT DEFAULT 1,
    uploaded_by INT NOT NULL,
    uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (paper_id) REFERENCES papers(id) ON DELETE CASCADE,
    FOREIGN KEY (uploaded_by) REFERENCES users(id) ON DELETE CASCADE,
    
    INDEX idx_files_paper (paper_id),
    INDEX idx_files_version (paper_id, version)
);

-- Activity log table
CREATE TABLE activity_logs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    action VARCHAR(100) NOT NULL,
    entity_type VARCHAR(50) NOT NULL,
    entity_id INT,
    details JSON,
    ip_address VARCHAR(45),
    user_agent TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL,
    INDEX idx_activity_user (user_id),
    INDEX idx_activity_entity (entity_type, entity_id),
    INDEX idx_activity_date (created_at)
);

-- System settings table
CREATE TABLE settings (
    id INT AUTO_INCREMENT PRIMARY KEY,
    key_name VARCHAR(100) UNIQUE NOT NULL,
    value TEXT,
    description TEXT,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

SET FOREIGN_KEY_CHECKS = 1;

-- Insert default categories
INSERT INTO categories (name, description, color) VALUES
('Computer Science', 'Research in computer science and technology', '#007bff'),
('Artificial Intelligence', 'AI and machine learning research', '#28a745'),
('Data Science', 'Data analysis and big data research', '#17a2b8'),
('Software Engineering', 'Software development methodologies', '#ffc107'),
('Cybersecurity', 'Information security and privacy', '#dc3545'),
('Human-Computer Interaction', 'User experience and interface design', '#6f42c1'),
('Distributed Systems', 'Distributed computing and systems', '#fd7e14'),
('Computer Networks', 'Network protocols and communication', '#20c997'),
('Database Systems', 'Database design and management', '#6c757d'),
('Computer Graphics', 'Graphics and visualization', '#e83e8c');

-- Insert default conferences
INSERT INTO conferences (name, year, submission_deadline, review_deadline, notification_date, status, description) VALUES
('International Conference on Software Engineering', 2024, '2024-12-15 23:59:59', '2025-02-15 23:59:59', '2025-03-15 23:59:59', 'ACTIVE', 'Premier conference for software engineering research'),
('ACM SIGCHI Conference on Human Factors', 2024, '2024-11-30 23:59:59', '2025-01-30 23:59:59', '2025-02-28 23:59:59', 'ACTIVE', 'Leading conference in human-computer interaction'),
('IEEE International Conference on Data Engineering', 2025, '2025-01-31 23:59:59', '2025-03-31 23:59:59', '2025-04-30 23:59:59', 'UPCOMING', 'Top venue for database and data engineering research');

-- Insert default admin user (password: admin123)
INSERT INTO users (name, email, password_hash, role) VALUES
('System Administrator', 'admin@paperflow.com', 'scrypt:32768:8:1$3mGVMPbz$2f8b80c8e6f3b7c9a0a3c5d4b7e8f9a2b3c4d5e6f7a8b9c0d1e2f3a4b5c6d7e8f9a0b1c2d3e4f5a6b7c8d9e0f1a2b3c4d5e6f7a8b9c0d1e2f3a4', 'ADMIN');

-- Insert sample reviewer users
INSERT INTO users (name, email, password_hash, role) VALUES
('Dr. Jane Smith', 'jane.smith@university.edu', 'scrypt:32768:8:1$reviewer1$1a2b3c4d5e6f7a8b9c0d1e2f3a4b5c6d7e8f9a0b1c2d3e4f5a6b7c8d9e0f1a2b3c4d5e6f7a8b9c0d1e2f3a4b5c6d7e8f9a0b1c2d3e4f5a6b7c8d9e0f1a2', 'REVIEWER'),
('Prof. John Doe', 'john.doe@institute.org', 'scrypt:32768:8:1$reviewer2$2b3c4d5e6f7a8b9c0d1e2f3a4b5c6d7e8f9a0b1c2d3e4f5a6b7c8d9e0f1a2b3c4d5e6f7a8b9c0d1e2f3a4b5c6d7e8f9a0b1c2d3e4f5a6b7c8d9e0f1a2b3', 'REVIEWER'),
('Dr. Alice Johnson', 'alice.johnson@research.com', 'scrypt:32768:8:1$reviewer3$3c4d5e6f7a8b9c0d1e2f3a4b5c6d7e8f9a0b1c2d3e4f5a6b7c8d9e0f1a2b3c4d5e6f7a8b9c0d1e2f3a4b5c6d7e8f9a0b1c2d3e4f5a6b7c8d9e0f1a2b3c4', 'REVIEWER');

-- Insert system settings
INSERT INTO settings (key_name, value, description) VALUES
('max_file_size', '16777216', 'Maximum file upload size in bytes (16MB)'),
('allowed_file_types', 'pdf,doc,docx', 'Allowed file extensions for paper uploads'),
('reviews_per_paper', '3', 'Default number of reviews required per paper'),
('review_deadline_days', '30', 'Default review deadline in days'),
('email_notifications', 'true', 'Enable email notifications'),
('system_maintenance_mode', 'false', 'System maintenance mode flag');

-- Create views for common queries
CREATE VIEW paper_stats AS
SELECT 
    p.id,
    p.title,
    p.status,
    COUNT(r.id) as review_count,
    AVG(r.score) as average_score,
    c.name as conference_name,
    c.year as conference_year
FROM papers p
LEFT JOIN reviews r ON p.id = r.paper_id AND r.is_completed = TRUE
JOIN conferences c ON p.conference_id = c.id
GROUP BY p.id, p.title, p.status, c.name, c.year;

CREATE VIEW user_stats AS
SELECT 
    u.id,
    u.name,
    u.email,
    u.role,
    COUNT(DISTINCT pa.paper_id) as authored_papers,
    COUNT(DISTINCT r.id) as completed_reviews
FROM users u
LEFT JOIN paper_authors pa ON u.id = pa.user_id
LEFT JOIN reviews r ON u.id = r.reviewer_id AND r.is_completed = TRUE
GROUP BY u.id, u.name, u.email, u.role;

-- Create triggers for activity logging
DELIMITER //

CREATE TRIGGER paper_status_change_log
AFTER UPDATE ON papers
FOR EACH ROW
BEGIN
    IF OLD.status != NEW.status THEN
        INSERT INTO activity_logs (action, entity_type, entity_id, details)
        VALUES ('status_change', 'paper', NEW.id, 
                JSON_OBJECT('old_status', OLD.status, 'new_status', NEW.status));
    END IF;
END //

CREATE TRIGGER review_completion_log
AFTER UPDATE ON reviews
FOR EACH ROW
BEGIN
    IF OLD.is_completed = FALSE AND NEW.is_completed = TRUE THEN
        INSERT INTO activity_logs (user_id, action, entity_type, entity_id, details)
        VALUES (NEW.reviewer_id, 'review_completed', 'review', NEW.id, 
                JSON_OBJECT('paper_id', NEW.paper_id, 'score', NEW.score, 'recommendation', NEW.recommendation));
    END IF;
END //

DELIMITER ;

-- Create indexes for better performance
CREATE INDEX idx_papers_full_search ON papers (title, abstract, keywords);
CREATE INDEX idx_reviews_score ON reviews (score);
CREATE INDEX idx_reviews_recommendation ON reviews (recommendation);
CREATE INDEX idx_activity_logs_date ON activity_logs (created_at);

-- Create stored procedures for common operations
DELIMITER //

CREATE PROCEDURE GetPaperWithReviews(IN paper_id INT)
BEGIN
    SELECT 
        p.*,
        c.name as conference_name,
        c.year as conference_year,
        GROUP_CONCAT(cat.name) as categories,
        COUNT(r.id) as review_count,
        AVG(r.score) as average_score
    FROM papers p
    JOIN conferences c ON p.conference_id = c.id
    LEFT JOIN paper_categories pc ON p.id = pc.paper_id
    LEFT JOIN categories cat ON pc.category_id = cat.id
    LEFT JOIN reviews r ON p.id = r.paper_id AND r.is_completed = TRUE
    WHERE p.id = paper_id
    GROUP BY p.id;
    
    SELECT 
        r.*,
        u.name as reviewer_name
    FROM reviews r
    JOIN users u ON r.reviewer_id = u.id
    WHERE r.paper_id = paper_id;
END //

CREATE PROCEDURE GetUserDashboardStats(IN user_id INT)
BEGIN
    DECLARE user_role VARCHAR(20);
    
    SELECT role INTO user_role FROM users WHERE id = user_id;
    
    IF user_role = 'AUTHOR' THEN
        SELECT 
            COUNT(*) as total_papers,
            SUM(CASE WHEN p.status = 'ACCEPTED' THEN 1 ELSE 0 END) as accepted_papers,
            SUM(CASE WHEN p.status = 'UNDER_REVIEW' THEN 1 ELSE 0 END) as under_review_papers,
            SUM(CASE WHEN p.status = 'REJECTED' THEN 1 ELSE 0 END) as rejected_papers
        FROM papers p
        JOIN paper_authors pa ON p.id = pa.paper_id
        WHERE pa.user_id = user_id;
        
    ELSEIF user_role = 'REVIEWER' THEN
        SELECT 
            COUNT(CASE WHEN r.is_completed = FALSE THEN 1 END) as pending_reviews,
            COUNT(CASE WHEN r.is_completed = TRUE THEN 1 END) as completed_reviews,
            COUNT(CASE WHEN r.deadline < NOW() AND r.is_completed = FALSE THEN 1 END) as overdue_reviews
        FROM reviews r
        WHERE r.reviewer_id = user_id;
        
    ELSEIF user_role = 'ADMIN' THEN
        SELECT 
            (SELECT COUNT(*) FROM papers) as total_papers,
            (SELECT COUNT(*) FROM users WHERE is_active = TRUE) as active_users,
            (SELECT COUNT(*) FROM conferences WHERE status = 'ACTIVE') as active_conferences,
            (SELECT COUNT(*) FROM reviews WHERE is_completed = FALSE) as pending_reviews;
    END IF;
END //

DELIMITER ;