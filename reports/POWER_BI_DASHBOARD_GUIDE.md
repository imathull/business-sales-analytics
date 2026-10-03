# Power BI Dashboard Setup & Architecture Guide
## Business Sales & Performance Analytics System

This guide outlines the data model schema, DAX measure calculations, visual hierarchy, and layout specs for building the **3-Page Power BI Business Analytics Dashboard**.

---

## 1. Data Model & Relationships (Star Schema)

Import tables into Power BI from the cleaned CSV (`data/processed/cleaned_sales_data.csv`) or directly via PostgreSQL / SQLite connection:

- **Fact Table**: `sales`
- **Dimension Tables**: `branches`, `products`, `salespeople`, `DateTable`

### Relationships:
1. `branches` (`branch_id`) **1 ─── * ** `sales` (`branch_id`)
2. `products` (`product_id`) **1 ─── * ** `sales` (`product_id`)
3. `salespeople` (`salesperson_id`) **1 ─── * ** `sales` (`salesperson_id`)
4. `DateTable` (`Date`) **1 ─── * ** `sales` (`transaction_date`)

---

## 2. Key DAX Measures

Create a dedicated **`_Measures`** table in Power BI and paste the following DAX calculations:

```dax
// 1. Total Net Sales Revenue
Total Revenue = SUM(sales[net_sales])

// 2. Total Transactions Count
Total Transactions = COUNTROWS(sales)

// 3. Total Units Sold
Total Units Sold = SUM(sales[quantity])

// 4. Average Order Value (AOV)
Average Order Value = DIVIDE([Total Revenue], [Total Transactions], 0)

// 5. Average Discount Percentage
Average Discount % = AVERAGE(sales[discount])

// 6. Previous Month Revenue (Time Intelligence)
Prior Month Revenue = 
CALCULATE(
    [Total Revenue],
    DATEADD('DateTable'[Date], -1, MONTH)
)

// 7. Month-over-Month (MoM) Growth %
MoM Revenue Growth % = 
DIVIDE(
    [Total Revenue] - [Prior Month Revenue],
    [Prior Month Revenue],
    0
)

// 8. IQR High-Value Anomaly Flag Count
High Value Anomalies Count = 
CALCULATE(
    COUNTROWS(sales),
    sales[net_sales] > 1800  -- Based on IQR upper bound threshold
)
```

---

## 3. Dashboard Page Architecture

---

### Page 1: Executive Overview

**Objective**: Provide senior stakeholders with instant high-level performance indicators and macro trends.

| Visual Element | Visual Type | Source Fields / Measures | Description |
| :--- | :--- | :--- | :--- |
| **KPI Card 1** | Card | `[Total Revenue]` | Formatted as Currency (`$M` or `$K`) |
| **KPI Card 2** | Card | `[Total Transactions]` | Formatted as Whole Number |
| **KPI Card 3** | Card | `[Total Units Sold]` | Formatted as Whole Number |
| **KPI Card 4** | Card | `[Average Order Value]` | Formatted as Currency (`$`) |
| **Revenue Trend** | Line Chart | X-Axis: `DateTable[YearMonth]`, Y-Axis: `[Total Revenue]` | Shows monthly trajectory across 15 months |
| **Branch Revenue** | Clustered Bar Chart | Y-Axis: `branches[branch_name]`, X-Axis: `[Total Revenue]` | Ranked by net revenue |
| **Category Share** | Donut Chart | Legend: `products[category]`, Values: `[Total Revenue]` | Shows percentage contribution |
| **Date Slicer** | Slicer (Slider) | `DateTable[Date]` | Allows custom date filtering |

---

### Page 2: Sales Analysis

**Objective**: Enable interactive granular analysis across products, regions, and sales teams.

| Visual Element | Visual Type | Source Fields / Measures | Description |
| :--- | :--- | :--- | :--- |
| **Top 10 Products** | Horizontal Bar Chart | Y-Axis: `products[product_name]`, X-Axis: `[Total Revenue]` | Filtered by Top 10 visual filter |
| **Salesperson Matrix** | Matrix | Rows: `salespeople[salesperson_name]`, Values: `[Total Revenue]`, `[Total Transactions]`, `[Average Order Value]` | Sorted by revenue |
| **Regional Sales** | Stacked Column Chart | X-Axis: `branches[region]`, Y-Axis: `[Total Revenue]`, Legend: `products[category]` | Multi-category regional breakdown |
| **Payment Breakdown** | Treemap / Pie Chart | Category: `sales[payment_method]`, Values: `[Total Revenue]` | Payment preference breakdown |
| **Interactive Slicers** | Multi-select Slicers | `branches[region]`, `products[category]`, `sales[customer_type]` | Cross-filtering dashboard control |

---

### Page 3: Data Quality & Insights

**Objective**: Transparently demonstrate data audit findings, quality cleaning metrics, and transaction anomalies.

| Visual Element | Visual Type | Source Fields / Measures | Description |
| :--- | :--- | :--- | :--- |
| **Audit Card 1** | Card | `Raw Records: 7,625` | Total raw records imported |
| **Audit Card 2** | Card | `Clean Records: 7,240` | Valid records retained in warehouse |
| **Audit Card 3** | Card | `Flawed Records: 385` | Dropped duplicate/invalid records |
| **Data Quality Breakdown** | Clustered Column Chart | X-Axis: `Quality Issue Type`, Y-Axis: `Count` | Highlights missing values, bad dates, invalid numbers |
| **High Outlier Scatter** | Scatter Plot | X-Axis: `sales[quantity]`, Y-Axis: `sales[net_sales]`, Details: `sales[transaction_id]` | Identifies transactions > IQR limit |
| **Key Findings Box** | Text Box / Card | Custom Analytical Text | Highlights key observations for leadership |

---

## 4. How to Import and Build in Power BI Desktop

1. Launch **Power BI Desktop**.
2. Click **Get Data** ──> **Text/CSV** and select `data/processed/cleaned_sales_data.csv` (or choose **PostgreSQL database**).
3. In **Transform Data** (Power Query), verify column data types:
   - `transaction_date`: Date
   - `quantity`: Whole Number
   - `unit_price`, `discount`, `gross_amount`, `net_sales`: Decimal Number
4. Create relationships under the **Model View**.
5. Create a new measure table and paste the DAX measures from Section 2.
6. Build Visual Pages 1, 2, and 3 as specified above.
7. Save the dashboard as `reports/Business_Sales_Performance_Dashboard.pbix`.
