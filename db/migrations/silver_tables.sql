CREATE SCHEMA IF NOT EXISTS silver;
CREATE TABLE IF NOT EXISTS silver.products_fakestore (
    product_id INTEGER PRIMARY KEY,
    title TEXT,
    price NUMERIC(10, 2),
    description TEXT,
    category TEXT,
    image_url TEXT,
    rating_rate NUMERIC(3, 1),
    rating_count INTEGER,
    _source VARCHAR(100),
    _ingested_at TIMESTAMP WITH TIME ZONE,
    _pipeline_run VARCHAR(50),
    _silver_loaded_at TIMESTAMP WITH TIME ZONE DEFAULT now()
);
CREATE TABLE IF NOT EXISTS silver.products_dummyjson (
    product_id INTEGER PRIMARY KEY,
    title TEXT,
    description TEXT,
    category TEXT,
    price NUMERIC(10, 2),
    discount_percentage NUMERIC(5, 2),
    rating NUMERIC(3, 2),
    stock INTEGER,
    brand TEXT,
    sku TEXT,
    weight NUMERIC(8, 2),
    warranty_information TEXT,
    shipping_information TEXT,
    availability_status TEXT,
    return_policy TEXT,
    minimum_order_quantity INTEGER,
    thumbnail_url TEXT,
    _source VARCHAR(100),
    _ingested_at TIMESTAMP WITH TIME ZONE,
    _pipeline_run VARCHAR(50),
    _silver_loaded_at TIMESTAMP WITH TIME ZONE DEFAULT now()
);
CREATE TABLE IF NOT EXISTS silver.users (
    user_id INTEGER PRIMARY KEY,
    first_name TEXT,
    last_name TEXT,
    maiden_name TEXT,
    age INTEGER,
    gender TEXT,
    email TEXT,
    phone TEXT,
    username TEXT,
    birth_date DATE,
    blood_group TEXT,
    height NUMERIC(5, 2),
    weight NUMERIC(5, 2),
    eye_color TEXT,
    ip_address TEXT,
    mac_address TEXT,
    university TEXT,
    ein TEXT,
    ssn TEXT,
    role TEXT,
    _source VARCHAR(100),
    _ingested_at TIMESTAMP WITH TIME ZONE,
    _pipeline_run VARCHAR(50),
    _silver_loaded_at TIMESTAMP WITH TIME ZONE DEFAULT now()
);
CREATE TABLE IF NOT EXISTS silver.carts (
    cart_id INTEGER PRIMARY KEY,
    user_id INTEGER,
    total NUMERIC(10, 2),
    discounted_total NUMERIC(10, 2),
    total_quantity INTEGER,
    _source VARCHAR(100),
    _ingested_at TIMESTAMP WITH TIME ZONE,
    _pipeline_run VARCHAR(50),
    _silver_loaded_at TIMESTAMP WITH TIME ZONE DEFAULT now()
);
CREATE TABLE IF NOT EXISTS silver.posts (
    post_id INTEGER PRIMARY KEY,
    user_id INTEGER,
    title TEXT,
    body TEXT,
    _source VARCHAR(100),
    _ingested_at TIMESTAMP WITH TIME ZONE,
    _pipeline_run VARCHAR(50),
    _silver_loaded_at TIMESTAMP WITH TIME ZONE DEFAULT now()
);
CREATE TABLE IF NOT EXISTS silver.cart_user_summary (
    cart_id INTEGER,
    user_id INTEGER,
    first_name TEXT,
    last_name TEXT,
    email TEXT,
    total NUMERIC(10, 2),
    discounted_total NUMERIC(10, 2),
    total_quantity INTEGER,
    _pipeline_run VARCHAR(50),
    _silver_loaded_at TIMESTAMP WITH TIME ZONE DEFAULT now()
);