-- ====================================================================
-- Executive KPI Summary Queries
-- Used for high-level dashboard verification and automated reporting
-- ====================================================================

-- KPI 1: Overall Net Sales Revenue, Total Volume, Units, and AOV
SELECT 
    ROUND(SUM(net_sales), 2) AS total_revenue,
    COUNT(transaction_id) AS total_transactions,
    SUM(quantity) AS total_units_sold,
    ROUND(AVG(net_sales), 2) AS average_order_value,
    ROUND(AVG(discount), 2) AS avg_discount_percentage
FROM sales;

-- KPI 2: Top 5 Branches by Net Revenue
SELECT 
    b.branch_name,
    b.region,
    ROUND(SUM(s.net_sales), 2) AS total_revenue
FROM sales s
JOIN branches b ON s.branch_id = b.branch_id
GROUP BY b.branch_name, b.region
ORDER BY total_revenue DESC
LIMIT 5;

-- KPI 3: Top 5 Products by Revenue
SELECT 
    p.product_name,
    p.category,
    SUM(s.quantity) AS units_sold,
    ROUND(SUM(s.net_sales), 2) AS total_revenue
FROM sales s
JOIN products p ON s.product_id = p.product_id
GROUP BY p.product_name, p.category
ORDER BY total_revenue DESC
LIMIT 5;
