-- ====================================================================
-- Business Sales & Performance Analytics - SQL Analysis Queries
-- Demonstrates SQL proficiency for interview defense:
-- SELECT, WHERE, GROUP BY, HAVING, JOINs, CASE, Subqueries, CTEs, Window Functions
-- ====================================================================

-- --------------------------------------------------------------------
-- QUERY 1: Monthly Revenue Trend & Month-over-Month (MoM) Growth Rate
-- Technique: CTE, Substr/Date Truncation, Window Function (LAG)
-- --------------------------------------------------------------------
WITH MonthlySales AS (
    SELECT 
        SUBSTR(transaction_date, 1, 7) AS sales_month,
        COUNT(transaction_id) AS total_orders,
        SUM(quantity) AS total_units_sold,
        SUM(net_sales) AS current_month_revenue
    FROM sales
    GROUP BY SUBSTR(transaction_date, 1, 7)
)
SELECT 
    sales_month,
    total_orders,
    total_units_sold,
    ROUND(current_month_revenue, 2) AS current_month_revenue,
    ROUND(LAG(current_month_revenue, 1) OVER (ORDER BY sales_month), 2) AS prior_month_revenue,
    ROUND(
        (current_month_revenue - LAG(current_month_revenue, 1) OVER (ORDER BY sales_month)) 
        / NULLIF(LAG(current_month_revenue, 1) OVER (ORDER BY sales_month), 0) * 100, 2
    ) AS mom_growth_pct
FROM MonthlySales
ORDER BY sales_month;

-- --------------------------------------------------------------------
-- QUERY 2: Branch & Regional Revenue Breakdown with Average Order Value
-- Technique: Multi-table INNER JOIN, GROUP BY, HAVING, Aggregate Functions
-- --------------------------------------------------------------------
SELECT 
    b.region,
    b.branch_id,
    b.branch_name,
    COUNT(s.transaction_id) AS total_transactions,
    SUM(s.quantity) AS total_units_sold,
    ROUND(SUM(s.net_sales), 2) AS total_revenue,
    ROUND(AVG(s.net_sales), 2) AS avg_order_value,
    ROUND(AVG(s.discount), 2) AS avg_discount_pct
FROM sales s
INNER JOIN branches b ON s.branch_id = b.branch_id
GROUP BY b.region, b.branch_id, b.branch_name
HAVING SUM(s.net_sales) > 50000
ORDER BY total_revenue DESC;

-- --------------------------------------------------------------------
-- QUERY 3: Product Rank Within Category (Top Products per Category)
-- Technique: Window Function RANK() OVER (PARTITION BY ... ORDER BY ...)
-- --------------------------------------------------------------------
WITH ProductPerformance AS (
    SELECT 
        p.category,
        p.product_id,
        p.product_name,
        SUM(s.quantity) AS total_units_sold,
        SUM(s.net_sales) AS total_revenue,
        AVG(s.unit_price) AS avg_unit_price
    FROM sales s
    INNER JOIN products p ON s.product_id = p.product_id
    GROUP BY p.category, p.product_id, p.product_name
)
SELECT 
    category,
    product_id,
    product_name,
    total_units_sold,
    ROUND(total_revenue, 2) AS total_revenue,
    RANK() OVER (PARTITION BY category ORDER BY total_revenue DESC) AS rank_in_category
FROM ProductPerformance
ORDER BY category, rank_in_category;

-- --------------------------------------------------------------------
-- QUERY 4: Top Salesperson per Branch
-- Technique: CTE, Multi-Table JOIN, DENSE_RANK()
-- --------------------------------------------------------------------
WITH SalespersonTotals AS (
    SELECT 
        b.branch_name,
        sp.salesperson_id,
        sp.salesperson_name,
        COUNT(s.transaction_id) AS closed_deals,
        SUM(s.net_sales) AS total_revenue,
        DENSE_RANK() OVER (PARTITION BY b.branch_name ORDER BY SUM(s.net_sales) DESC) AS rank_in_branch
    FROM sales s
    INNER JOIN salespeople sp ON s.salesperson_id = sp.salesperson_id
    INNER JOIN branches b ON s.branch_id = b.branch_id
    GROUP BY b.branch_name, sp.salesperson_id, sp.salesperson_name
)
SELECT 
    branch_name,
    salesperson_name,
    closed_deals,
    ROUND(total_revenue, 2) AS total_revenue
FROM SalespersonTotals
WHERE rank_in_branch = 1
ORDER BY total_revenue DESC;

-- --------------------------------------------------------------------
-- QUERY 5: Category Percentage Share of Total Revenue
-- Technique: Window Function SUM() OVER() (Total Aggregation)
-- --------------------------------------------------------------------
SELECT 
    p.category,
    SUM(s.quantity) AS total_units_sold,
    ROUND(SUM(s.net_sales), 2) AS category_revenue,
    ROUND(
        (SUM(s.net_sales) / SUM(SUM(s.net_sales)) OVER ()) * 100, 2
    ) AS revenue_share_pct
FROM sales s
INNER JOIN products p ON s.product_id = p.product_id
GROUP BY p.category
ORDER BY category_revenue DESC;

-- --------------------------------------------------------------------
-- QUERY 6: Transaction Size Segmentation using CASE Statement
-- Technique: CASE expression, Grouping by Derived Tiers
-- --------------------------------------------------------------------
SELECT 
    CASE 
        WHEN net_sales >= 2000 THEN '1. Enterprise Tier (>= $2,000)'
        WHEN net_sales >= 1000 THEN '2. Major Tier ($1,000 - $1,999)'
        WHEN net_sales >= 500  THEN '3. Standard Tier ($500 - $999)'
        ELSE '4. Small Tier (< $500)'
    END AS order_tier,
    COUNT(transaction_id) AS order_count,
    SUM(quantity) AS total_units,
    ROUND(SUM(net_sales), 2) AS total_tier_revenue,
    ROUND(AVG(net_sales), 2) AS avg_tier_value
FROM sales
GROUP BY 
    CASE 
        WHEN net_sales >= 2000 THEN '1. Enterprise Tier (>= $2,000)'
        WHEN net_sales >= 1000 THEN '2. Major Tier ($1,000 - $1,999)'
        WHEN net_sales >= 500  THEN '3. Standard Tier ($500 - $999)'
        ELSE '4. Small Tier (< $500)'
    END
ORDER BY order_tier;

-- --------------------------------------------------------------------
-- QUERY 7: Products Sold Above Average Overall Unit Price
-- Technique: Subquery in WHERE clause
-- --------------------------------------------------------------------
SELECT 
    p.product_id,
    p.product_name,
    p.category,
    p.unit_price
FROM products p
WHERE p.unit_price > (SELECT AVG(unit_price) FROM sales)
ORDER BY p.unit_price DESC;

-- --------------------------------------------------------------------
-- QUERY 8: Payment Method Preferences by Customer Type
-- Technique: Pivot-style Conditional Aggregation (CASE + SUM)
-- --------------------------------------------------------------------
SELECT 
    customer_type,
    COUNT(transaction_id) AS total_orders,
    ROUND(SUM(CASE WHEN payment_method = 'Credit Card' THEN net_sales ELSE 0 END), 2) AS credit_card_sales,
    ROUND(SUM(CASE WHEN payment_method = 'Wire Transfer' THEN net_sales ELSE 0 END), 2) AS wire_transfer_sales,
    ROUND(SUM(CASE WHEN payment_method = 'PayPal' THEN net_sales ELSE 0 END), 2) AS paypal_sales,
    ROUND(SUM(CASE WHEN payment_method = 'Cash' THEN net_sales ELSE 0 END), 2) AS cash_sales
FROM sales
GROUP BY customer_type
ORDER BY total_orders DESC;
