CREATE SCHEMA IF NOT EXISTS silver;
CREATE TABLE IF NOT EXISTS silver.silver_products (
    silver_id BIGSERIAL PRIMARY KEY,
    product_id INTEGER NOT NULL,
    source_system VARCHAR(50) NOT NULL,
    title VARCHAR(500) NOT NULL,
    description TEXT,
    category VARCHAR(200) NOT NULL,
    price DECIMAL(12, 2) NOT NULL CHECK (price >= 0),
    discount_percentage DECIMAL(5, 2) DEFAULT 0,
    rating DECIMAL(3, 2) CHECK (
        rating >= 0
        AND rating <= 5
    ),
    stock INTEGER DEFAULT 0,
    brand VARCHAR(200),
    sku VARCHAR(100),
    weight DECIMAL(10, 2),
    warranty_info VARCHAR(500),
    shipping_info VARCHAR(500),
    availability_status VARCHAR(50),
    return_policy VARCHAR(500),
    min_order_quantity INTEGER DEFAULT 1,
    image_url TEXT,
    thumbnail_url TEXT,
    is_valid BOOLEAN DEFAULT TRUE,
    validation_errors JSONB,
    quality_score DECIMAL(5, 2),
    bronze_batch_id INTEGER,
    silver_processed_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    silver_version INTEGER DEFAULT 1,
    UNIQUE(product_id, source_system)
);
CREATE INDEX idx_silver_products_product_id ON silver.silver_products(product_id);
CREATE INDEX idx_silver_products_category ON silver.silver_products(category);
CREATE INDEX idx_silver_products_price ON silver.silver_products(price);
CREATE INDEX idx_silver_products_rating ON silver.silver_products(rating);
CREATE INDEX idx_silver_products_valid ON silver.silver_products(is_valid);
CREATE TABLE IF NOT EXISTS silver.silver_users (
    silver_id BIGSERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL UNIQUE,
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    maiden_name VARCHAR(100),
    full_name VARCHAR(200) GENERATED ALWAYS AS (
        COALESCE(first_name || ' ', '') || COALESCE(last_name, '')
    ) STORED,
    email VARCHAR(255) NOT NULL UNIQUE,
    phone VARCHAR(50),
    age INTEGER CHECK (
        age >= 0
        AND age <= 150
    ),
    gender VARCHAR(20),
    blood_group VARCHAR(10),
    height DECIMAL(5, 2),
    weight DECIMAL(5, 2),
    eye_color VARCHAR(30),
    address_line1 VARCHAR(255),
    address_line2 VARCHAR(255),
    city VARCHAR(100),
    state VARCHAR(100),
    postal_code VARCHAR(20),
    country VARCHAR(100),
    university VARCHAR(255),
    company_name VARCHAR(255),
    company_title VARCHAR(255),
    role VARCHAR(100),
    is_valid BOOLEAN DEFAULT TRUE,
    validation_errors JSONB,
    quality_score DECIMAL(5, 2),
    bronze_batch_id INTEGER,
    silver_processed_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    silver_version INTEGER DEFAULT 1
);
CREATE INDEX idx_silver_users_email ON silver.silver_users(email);
CREATE INDEX idx_silver_users_age ON silver.silver_users(age);
CREATE INDEX idx_silver_users_city ON silver.silver_users(city);
CREATE TABLE IF NOT EXISTS silver.silver_carts (
    silver_id BIGSERIAL PRIMARY KEY,
    cart_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    total_amount DECIMAL(12, 2) NOT NULL CHECK (total_amount >= 0),
    discounted_total DECIMAL(12, 2),
    total_quantity INTEGER NOT NULL DEFAULT 0,
    is_valid BOOLEAN DEFAULT TRUE,
    validation_errors JSONB,
    bronze_batch_id INTEGER,
    silver_processed_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    CONSTRAINT fk_user FOREIGN KEY (user_id) REFERENCES silver.silver_users(user_id) ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS silver.silver_cart_items (
    item_id BIGSERIAL PRIMARY KEY,
    cart_id INTEGER NOT NULL,
    product_id INTEGER NOT NULL,
    quantity INTEGER NOT NULL CHECK (quantity > 0),
    silver_processed_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    CONSTRAINT fk_cart FOREIGN KEY (cart_id) REFERENCES silver.silver_carts(cart_id) ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS silver.silver_posts (
    silver_id BIGSERIAL PRIMARY KEY,
    post_id INTEGER NOT NULL UNIQUE,
    user_id INTEGER NOT NULL,
    title VARCHAR(500) NOT NULL,
    body TEXT,
    word_count INTEGER,
    has_content BOOLEAN GENERATED ALWAYS AS (
        body IS NOT NULL
        AND LENGTH(body) > 0
    ) STORED,
    is_valid BOOLEAN DEFAULT TRUE,
    validation_errors JSONB,
    bronze_batch_id INTEGER,
    silver_processed_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    CONSTRAINT fk_post_user FOREIGN KEY (user_id) REFERENCES silver.silver_users(user_id) ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS silver.silver_error_logs (
    error_id BIGSERIAL PRIMARY KEY,
    source_table VARCHAR(100) NOT NULL,
    source_system VARCHAR(50),
    raw_data JSONB,
    validation_errors JSONB,
    error_type VARCHAR(50),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    processed BOOLEAN DEFAULT FALSE
);
CREATE INDEX idx_error_logs_source ON silver.silver_error_logs(source_table);
CREATE INDEX idx_error_logs_created ON silver.silver_error_logs(created_at);
ALTER CREATE TABLE IF NOT EXISTS silver.silver_quality_metrics (
    metric_id BIGSERIAL PRIMARY KEY,
    table_name VARCHAR(100),
    metric_date DATE DEFAULT CURRENT_DATE,
    total_records INTEGER,
    valid_records INTEGER,
    invalid_records INTEGER,
    completeness_score DECIMAL(5, 2),
    duplicate_count INTEGER,
    null_rate JSONB,
    processed_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);