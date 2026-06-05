CREATE SCHEMA IF NOT EXISTS bronze;
-- ── Fakestore Products ───────────────────────────────────
CREATE TABLE IF NOT EXISTS bronze.fakestore_products (
    -- Raw API fields
    id INTEGER,
    title TEXT,
    price TEXT,
    -- keep as TEXT in bronze (don't cast)
    description TEXT,
    category TEXT,
    image TEXT,
    rating JSONB,
    -- store nested dict as JSONB
    -- Pipeline metadata
    _source VARCHAR(100),
    _ingested_at TIMESTAMP WITH TIME ZONE,
    _pipeline_run VARCHAR(50),
    _batch_id SERIAL -- auto increment per insert
);
-- ── DummyJSON Products ───────────────────────────────────
CREATE TABLE IF NOT EXISTS bronze.dummyjson_products (
    id INTEGER,
    title TEXT,
    description TEXT,
    category TEXT,
    price TEXT,
    "discountPercentage" TEXT,
    rating TEXT,
    stock TEXT,
    tags JSONB,
    brand TEXT,
    sku TEXT,
    weight TEXT,
    dimensions JSONB,
    "warrantyInformation" TEXT,
    "shippingInformation" TEXT,
    "availabilityStatus" TEXT,
    reviews JSONB,
    "returnPolicy" TEXT,
    "minimumOrderQuantity" TEXT,
    meta JSONB,
    images JSONB,
    thumbnail TEXT,
    _source VARCHAR(100),
    _ingested_at TIMESTAMP WITH TIME ZONE,
    _pipeline_run VARCHAR(50),
    _batch_id SERIAL
);
-- ── DummyJSON Users ──────────────────────────────────────
CREATE TABLE IF NOT EXISTS bronze.dummyjson_users (
    id INTEGER,
    "firstName" TEXT,
    "lastName" TEXT,
    "maidenName" TEXT,
    age TEXT,
    gender TEXT,
    email TEXT,
    phone TEXT,
    username TEXT,
    password TEXT,
    "birthDate" TEXT,
    image TEXT,
    "bloodGroup" TEXT,
    height TEXT,
    weight TEXT,
    "eyeColor" TEXT,
    hair JSONB,
    ip TEXT,
    address JSONB,
    "macAddress" TEXT,
    university TEXT,
    bank JSONB,
    company JSONB,
    ein TEXT,
    ssn TEXT,
    "userAgent" TEXT,
    crypto JSONB,
    role TEXT,
    _source VARCHAR(100),
    _ingested_at TIMESTAMP WITH TIME ZONE,
    _pipeline_run VARCHAR(50),
    _batch_id SERIAL
);
-- ── DummyJSON Carts ──────────────────────────────────────
CREATE TABLE IF NOT EXISTS bronze.dummyjson_carts (
    id INTEGER,
    "userId" TEXT,
    products JSONB,
    -- list of products kept as JSONB
    total TEXT,
    "discountedTotal" TEXT,
    "totalQuantity" TEXT,
    _source VARCHAR(100),
    _ingested_at TIMESTAMP WITH TIME ZONE,
    _pipeline_run VARCHAR(50),
    _batch_id SERIAL
);
-- ── JSONPlaceholder Posts ────────────────────────────────
CREATE TABLE IF NOT EXISTS bronze.jsonplaceholder_posts (
    id INTEGER,
    "userId" TEXT,
    title TEXT,
    body TEXT,
    _source VARCHAR(100),
    _ingested_at TIMESTAMP WITH TIME ZONE,
    _pipeline_run VARCHAR(50),
    _batch_id SERIAL
);
-- ── Pipeline Run Log ─────────────────────────────────────
-- Tracks every pipeline run — how many rows, success/fail
CREATE TABLE IF NOT EXISTS bronze.pipeline_run_log (
    run_id VARCHAR(50),
    source_name VARCHAR(100),
    status VARCHAR(20),
    -- success | failed
    rows_inserted INTEGER,
    error_message TEXT,
    started_at TIMESTAMP WITH TIME ZONE,
    finished_at TIMESTAMP WITH TIME ZONE
);