CREATE SCHEMA IF NOT EXISTS gold;
CREATE TABLE IF NOT EXISTS gold.sales_by_category (
    category TEXT,
    total_products INTEGER,
    avg_price NUMERIC(10, 2),
    avg_discount_pct NUMERIC(5, 2),
    avg_rating NUMERIC(4, 2),
    total_stock INTEGER,
    price_band TEXT,
    _pipeline_run VARCHAR(50),
    _gold_loaded_at TIMESTAMP WITH TIME ZONE DEFAULT now()
);
CREATE TABLE IF NOT EXISTS gold.top_spenders (
    user_id INTEGER,
    first_name TEXT,
    last_name TEXT,
    email TEXT,
    total_carts INTEGER,
    total_spent NUMERIC(10, 2),
    total_discounted NUMERIC(10, 2),
    total_savings NUMERIC(10, 2),
    total_items INTEGER,
    avg_cart_value NUMERIC(10, 2),
    _pipeline_run VARCHAR(50),
    _gold_loaded_at TIMESTAMP WITH TIME ZONE DEFAULT now()
);
CREATE TABLE IF NOT EXISTS gold.product_performance (
    source TEXT,
    product_id INTEGER,
    title TEXT,
    category TEXT,
    price NUMERIC(10, 2),
    rating NUMERIC(4, 2),
    stock INTEGER,
    rating_tier TEXT,
    stock_status TEXT,
    _pipeline_run VARCHAR(50),
    _gold_loaded_at TIMESTAMP WITH TIME ZONE DEFAULT now()
);
CREATE TABLE IF NOT EXISTS gold.discount_impact (
    category TEXT,
    total_products INTEGER,
    avg_full_price NUMERIC(10, 2),
    avg_discount_pct NUMERIC(5, 2),
    avg_discounted_price NUMERIC(10, 2),
    total_savings_per_unit NUMERIC(10, 2),
    _pipeline_run VARCHAR(50),
    _gold_loaded_at TIMESTAMP WITH TIME ZONE DEFAULT now()
);
CREATE TABLE IF NOT EXISTS gold.user_demographics (
    age_group TEXT,
    gender TEXT,
    user_count INTEGER,
    avg_age NUMERIC(4, 1),
    _pipeline_run VARCHAR(50),
    _gold_loaded_at TIMESTAMP WITH TIME ZONE DEFAULT now()
);
CREATE TABLE IF NOT EXISTS gold.post_activity (
    user_id INTEGER,
    first_name TEXT,
    last_name TEXT,
    email TEXT,
    post_count INTEGER,
    _pipeline_run VARCHAR(50),
    _gold_loaded_at TIMESTAMP WITH TIME ZONE DEFAULT now()
);
CREATE TABLE IF NOT EXISTS gold.pipeline_health (
    run_id VARCHAR(50),
    total_sources INTEGER,
    successful_sources INTEGER,
    failed_sources INTEGER,
    total_rows_inserted INTEGER,
    started_at TIMESTAMP WITH TIME ZONE,
    finished_at TIMESTAMP WITH TIME ZONE,
    duration_seconds NUMERIC(10, 2),
    _gold_loaded_at TIMESTAMP WITH TIME ZONE DEFAULT now()
);