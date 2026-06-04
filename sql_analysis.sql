-- ================================================================
-- AMAZON INDIA SALES — SQL ANALYSIS QUERIES
-- Tool: PostgreSQL / MySQL / SQLite compatible
-- Author: Shakir Syeed
-- ================================================================

-- ── TABLE SETUP (if importing CSV) ──────────────────────────────
/*
CREATE TABLE amazon_sales (
    Order_ID       VARCHAR(20),
    Order_Date     DATE,
    Month          VARCHAR(15),
    Quarter        VARCHAR(5),
    Year           INT,
    Customer_ID    VARCHAR(20),
    Customer_Name  VARCHAR(100),
    State          VARCHAR(50),
    City_Tier      VARCHAR(10),
    Category       VARCHAR(30),
    Product_Name   VARCHAR(100),
    MRP            DECIMAL(10,2),
    Discount_Pct   INT,
    Sale_Price     DECIMAL(10,2),
    Quantity       INT,
    Revenue        DECIMAL(10,2),
    COGS           DECIMAL(10,2),
    Profit         DECIMAL(10,2),
    Profit_Margin  DECIMAL(5,2),
    Payment_Mode   VARCHAR(30),
    Order_Status   VARCHAR(20),
    Channel        VARCHAR(20),
    Rating         DECIMAL(3,1)
);
*/

-- ================================================================
-- SECTION 1: OVERALL BUSINESS SUMMARY
-- ================================================================

-- Q1. Total Revenue, Profit, Orders, Avg Order Value
SELECT
    COUNT(Order_ID)                         AS Total_Orders,
    ROUND(SUM(Revenue), 2)                  AS Total_Revenue,
    ROUND(SUM(Profit), 2)                   AS Total_Profit,
    ROUND(AVG(Revenue), 2)                  AS Avg_Order_Value,
    ROUND(AVG(Profit_Margin), 2)            AS Avg_Profit_Margin_Pct,
    ROUND(SUM(Profit) / SUM(Revenue) * 100, 2) AS Overall_Margin_Pct
FROM amazon_sales
WHERE Order_Status = 'Delivered';


-- Q2. Year-wise Revenue & Growth
WITH yearly AS (
    SELECT
        Year,
        ROUND(SUM(Revenue), 2) AS Revenue,
        COUNT(Order_ID)        AS Orders
    FROM amazon_sales
    WHERE Order_Status = 'Delivered'
    GROUP BY Year
)
SELECT
    Year,
    Revenue,
    Orders,
    LAG(Revenue) OVER (ORDER BY Year)   AS Prev_Year_Revenue,
    ROUND(
        (Revenue - LAG(Revenue) OVER (ORDER BY Year))
        / LAG(Revenue) OVER (ORDER BY Year) * 100, 2
    ) AS YoY_Growth_Pct
FROM yearly
ORDER BY Year;


-- ================================================================
-- SECTION 2: CATEGORY ANALYSIS
-- ================================================================

-- Q3. Revenue, Profit, Margin by Category (Ranked)
SELECT
    Category,
    COUNT(Order_ID)                     AS Orders,
    ROUND(SUM(Revenue), 2)              AS Total_Revenue,
    ROUND(SUM(Profit), 2)               AS Total_Profit,
    ROUND(AVG(Profit_Margin), 2)        AS Avg_Margin_Pct,
    ROUND(AVG(Discount_Pct), 1)         AS Avg_Discount_Pct,
    RANK() OVER (ORDER BY SUM(Revenue) DESC) AS Revenue_Rank
FROM amazon_sales
WHERE Order_Status = 'Delivered'
GROUP BY Category
ORDER BY Total_Revenue DESC;


-- Q4. Top 5 Products per Category by Revenue
WITH ranked_products AS (
    SELECT
        Category,
        Product_Name,
        ROUND(SUM(Revenue), 2) AS Total_Revenue,
        COUNT(Order_ID)        AS Orders,
        RANK() OVER (PARTITION BY Category ORDER BY SUM(Revenue) DESC) AS Rank_In_Category
    FROM amazon_sales
    WHERE Order_Status = 'Delivered'
    GROUP BY Category, Product_Name
)
SELECT * FROM ranked_products
WHERE Rank_In_Category <= 5
ORDER BY Category, Rank_In_Category;


-- ================================================================
-- SECTION 3: TIME-BASED ANALYSIS
-- ================================================================

-- Q5. Monthly Revenue Trend with MoM Growth
WITH monthly AS (
    SELECT
        Year,
        Month,
        EXTRACT(MONTH FROM Order_Date) AS Month_Num,
        ROUND(SUM(Revenue), 2)         AS Revenue,
        COUNT(Order_ID)                AS Orders
    FROM amazon_sales
    WHERE Order_Status = 'Delivered'
    GROUP BY Year, Month, EXTRACT(MONTH FROM Order_Date)
)
SELECT
    Year,
    Month,
    Revenue,
    Orders,
    LAG(Revenue) OVER (PARTITION BY Year ORDER BY Month_Num) AS Prev_Month_Rev,
    ROUND(
        (Revenue - LAG(Revenue) OVER (PARTITION BY Year ORDER BY Month_Num))
        / NULLIF(LAG(Revenue) OVER (PARTITION BY Year ORDER BY Month_Num), 0) * 100, 2
    ) AS MoM_Growth_Pct
FROM monthly
ORDER BY Year, Month_Num;


-- Q6. Best and Worst performing Month per Year
WITH monthly_rev AS (
    SELECT
        Year,
        Month,
        ROUND(SUM(Revenue), 2) AS Revenue,
        RANK() OVER (PARTITION BY Year ORDER BY SUM(Revenue) DESC) AS Best_Rank,
        RANK() OVER (PARTITION BY Year ORDER BY SUM(Revenue) ASC)  AS Worst_Rank
    FROM amazon_sales
    WHERE Order_Status = 'Delivered'
    GROUP BY Year, Month
)
SELECT Year, Month, Revenue,
       CASE WHEN Best_Rank = 1 THEN '🏆 Best Month'
            WHEN Worst_Rank = 1 THEN '⚠️ Worst Month' END AS Flag
FROM monthly_rev
WHERE Best_Rank = 1 OR Worst_Rank = 1
ORDER BY Year;


-- ================================================================
-- SECTION 4: GEOGRAPHIC ANALYSIS
-- ================================================================

-- Q7. Revenue & Profit by State (Top 10)
SELECT
    State,
    City_Tier,
    COUNT(Order_ID)             AS Orders,
    ROUND(SUM(Revenue), 2)      AS Total_Revenue,
    ROUND(SUM(Profit), 2)       AS Total_Profit,
    ROUND(AVG(Profit_Margin),2) AS Avg_Margin
FROM amazon_sales
WHERE Order_Status = 'Delivered'
GROUP BY State, City_Tier
ORDER BY Total_Revenue DESC
LIMIT 10;


-- Q8. City Tier Revenue Comparison
SELECT
    City_Tier,
    COUNT(DISTINCT Customer_ID)     AS Unique_Customers,
    COUNT(Order_ID)                 AS Total_Orders,
    ROUND(SUM(Revenue), 2)          AS Total_Revenue,
    ROUND(AVG(Revenue), 2)          AS Avg_Order_Value,
    ROUND(AVG(Profit_Margin), 2)    AS Avg_Margin_Pct
FROM amazon_sales
WHERE Order_Status = 'Delivered'
GROUP BY City_Tier
ORDER BY Total_Revenue DESC;


-- ================================================================
-- SECTION 5: CUSTOMER ANALYSIS
-- ================================================================

-- Q9. Repeat vs One-time Customers
WITH customer_orders AS (
    SELECT
        Customer_ID,
        COUNT(Order_ID) AS Order_Count,
        ROUND(SUM(Revenue), 2) AS Lifetime_Value
    FROM amazon_sales
    WHERE Order_Status = 'Delivered'
    GROUP BY Customer_ID
)
SELECT
    CASE WHEN Order_Count = 1 THEN 'One-Time Customer'
         WHEN Order_Count BETWEEN 2 AND 3 THEN 'Returning Customer'
         ELSE 'Loyal Customer (4+)' END     AS Customer_Type,
    COUNT(Customer_ID)                      AS Customer_Count,
    ROUND(AVG(Lifetime_Value), 2)           AS Avg_Lifetime_Value,
    ROUND(SUM(Lifetime_Value), 2)           AS Total_Revenue_Contribution
FROM customer_orders
GROUP BY Customer_Type
ORDER BY Total_Revenue_Contribution DESC;


-- Q10. Top 10 Customers by Revenue
SELECT
    Customer_ID,
    Customer_Name,
    COUNT(Order_ID)            AS Orders,
    ROUND(SUM(Revenue), 2)     AS Total_Revenue,
    ROUND(AVG(Rating), 1)      AS Avg_Rating
FROM amazon_sales
WHERE Order_Status = 'Delivered'
GROUP BY Customer_ID, Customer_Name
ORDER BY Total_Revenue DESC
LIMIT 10;


-- ================================================================
-- SECTION 6: PAYMENT & CHANNEL ANALYSIS
-- ================================================================

-- Q11. Revenue by Payment Mode
SELECT
    Payment_Mode,
    COUNT(Order_ID)                                          AS Orders,
    ROUND(SUM(Revenue), 2)                                   AS Total_Revenue,
    ROUND(SUM(Revenue) / SUM(SUM(Revenue)) OVER () * 100, 2) AS Revenue_Share_Pct
FROM amazon_sales
WHERE Order_Status = 'Delivered'
GROUP BY Payment_Mode
ORDER BY Total_Revenue DESC;


-- Q12. Channel Performance + Return Rate
SELECT
    Channel,
    COUNT(Order_ID)                                              AS Total_Orders,
    SUM(CASE WHEN Order_Status = 'Delivered'  THEN 1 ELSE 0 END) AS Delivered,
    SUM(CASE WHEN Order_Status = 'Returned'   THEN 1 ELSE 0 END) AS Returned,
    SUM(CASE WHEN Order_Status = 'Cancelled'  THEN 1 ELSE 0 END) AS Cancelled,
    ROUND(SUM(CASE WHEN Order_Status = 'Returned' THEN 1 ELSE 0 END)
          / COUNT(Order_ID) * 100, 2)                            AS Return_Rate_Pct
FROM amazon_sales
GROUP BY Channel
ORDER BY Total_Orders DESC;


-- ================================================================
-- SECTION 7: DISCOUNT & PRICING ANALYSIS
-- ================================================================

-- Q13. Impact of Discount on Profit Margin
SELECT
    CASE
        WHEN Discount_Pct < 10  THEN '0-9% Discount'
        WHEN Discount_Pct < 20  THEN '10-19% Discount'
        WHEN Discount_Pct < 30  THEN '20-29% Discount'
        WHEN Discount_Pct < 40  THEN '30-39% Discount'
        ELSE '40%+ Discount'
    END                              AS Discount_Band,
    COUNT(Order_ID)                  AS Orders,
    ROUND(AVG(Profit_Margin), 2)     AS Avg_Profit_Margin,
    ROUND(SUM(Revenue), 2)           AS Total_Revenue
FROM amazon_sales
WHERE Order_Status = 'Delivered'
GROUP BY Discount_Band
ORDER BY Discount_Band;


-- ================================================================
-- SECTION 8: ADVANCED — ROLLING & WINDOW ANALYTICS
-- ================================================================

-- Q14. 3-Month Rolling Avg Revenue per Category
WITH monthly_cat AS (
    SELECT
        Category,
        DATE_TRUNC('month', Order_Date) AS Month_Start,
        ROUND(SUM(Revenue), 2)          AS Monthly_Revenue
    FROM amazon_sales
    WHERE Order_Status = 'Delivered'
    GROUP BY Category, DATE_TRUNC('month', Order_Date)
)
SELECT
    Category,
    Month_Start,
    Monthly_Revenue,
    ROUND(AVG(Monthly_Revenue) OVER (
        PARTITION BY Category
        ORDER BY Month_Start
        ROWS BETWEEN 2 PRECEDING AND CURRENT ROW
    ), 2) AS Rolling_3M_Avg
FROM monthly_cat
ORDER BY Category, Month_Start;


-- Q15. Cumulative Revenue by Category over time
SELECT
    Category,
    Order_Date,
    ROUND(SUM(Revenue), 2) AS Daily_Revenue,
    ROUND(SUM(SUM(Revenue)) OVER (
        PARTITION BY Category ORDER BY Order_Date
    ), 2) AS Cumulative_Revenue
FROM amazon_sales
WHERE Order_Status = 'Delivered'
GROUP BY Category, Order_Date
ORDER BY Category, Order_Date;

-- ================================================================
-- END OF SQL ANALYSIS — amazon_sales_india
-- ================================================================
