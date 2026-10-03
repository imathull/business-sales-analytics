-- ====================================================================
-- Database Schema: Business Sales & Performance Analytics System
-- Target Dialect: PostgreSQL / SQLite Compatible DDL
-- Schema Design: 3NF Star Schema (Dimensions + Fact Table)
-- ====================================================================

-- 1. Drop existing tables if re-initializing (Order: Fact table first, then Dimensions)
DROP TABLE IF EXISTS sales;
DROP TABLE IF EXISTS products;
DROP TABLE IF EXISTS salespeople;
DROP TABLE IF EXISTS branches;

-- 2. Dimension: Branches
CREATE TABLE branches (
    branch_id VARCHAR(20) PRIMARY KEY,
    branch_name VARCHAR(100) NOT NULL,
    region VARCHAR(50) NOT NULL
);

-- 3. Dimension: Salespeople
CREATE TABLE salespeople (
    salesperson_id VARCHAR(20) PRIMARY KEY,
    salesperson_name VARCHAR(100) NOT NULL
);

-- 4. Dimension: Products
CREATE TABLE products (
    product_id VARCHAR(20) PRIMARY KEY,
    product_name VARCHAR(150) NOT NULL,
    category VARCHAR(100) NOT NULL,
    unit_price DECIMAL(10, 2) NOT NULL CHECK (unit_price > 0)
);

-- 5. Fact Table: Sales
CREATE TABLE sales (
    transaction_id VARCHAR(30) PRIMARY KEY,
    transaction_date DATE NOT NULL,
    branch_id VARCHAR(20) NOT NULL,
    salesperson_id VARCHAR(20) NOT NULL,
    product_id VARCHAR(20) NOT NULL,
    quantity INT NOT NULL CHECK (quantity > 0),
    unit_price DECIMAL(10, 2) NOT NULL CHECK (unit_price > 0),
    discount DECIMAL(5, 2) DEFAULT 0.00 CHECK (discount >= 0 AND discount <= 100),
    gross_amount DECIMAL(12, 2) NOT NULL,
    discount_amount DECIMAL(12, 2) NOT NULL,
    net_sales DECIMAL(12, 2) NOT NULL,
    payment_method VARCHAR(50) NOT NULL,
    customer_type VARCHAR(50) NOT NULL,
    FOREIGN KEY (branch_id) REFERENCES branches(branch_id) ON DELETE RESTRICT,
    FOREIGN KEY (salesperson_id) REFERENCES salespeople(salesperson_id) ON DELETE RESTRICT,
    FOREIGN KEY (product_id) REFERENCES products(product_id) ON DELETE RESTRICT
);

-- 6. Indexes for Optimized Query Performance
CREATE INDEX idx_sales_date ON sales(transaction_date);
CREATE INDEX idx_sales_branch ON sales(branch_id);
CREATE INDEX idx_sales_product ON sales(product_id);
CREATE INDEX idx_sales_salesperson ON sales(salesperson_id);
