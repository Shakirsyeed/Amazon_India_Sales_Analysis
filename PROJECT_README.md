# 🛒 Amazon India Sales Analysis (2022–2024)

> **End-to-End Data Analysis Project** | Python • SQL • Power BI • Excel

<p>
  <img src="https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white"/>
  <img src="https://img.shields.io/badge/Pandas-150458?style=for-the-badge&logo=pandas&logoColor=white"/>
  <img src="https://img.shields.io/badge/SQL-4479A1?style=for-the-badge&logo=mysql&logoColor=white"/>
  <img src="https://img.shields.io/badge/Power%20BI-F2C811?style=for-the-badge&logo=powerbi&logoColor=black"/>
  <img src="https://img.shields.io/badge/Excel-217346?style=for-the-badge&logo=microsoftexcel&logoColor=white"/>
  <img src="https://img.shields.io/badge/Status-Completed-2ecc71?style=for-the-badge"/>
</p>

---

## 📌 Project Overview

This end-to-end data analysis project explores **5,000+ Amazon India sales transactions** spanning January 2022 to March 2024. The goal is to uncover actionable business insights across revenue performance, category trends, geographic distribution, customer behaviour, and discount impact — the kind of analysis a real business analyst would deliver to leadership.

| Detail | Info |
|---|---|
| 📁 Dataset | Amazon India Sales (Simulated — real-world structure) |
| 📅 Date Range | Jan 2022 — Mar 2024 |
| 🗂️ Records | 5,000 orders |
| 🛠️ Tools Used | Python, Pandas, Matplotlib, Seaborn, SQL, Power BI |
| 🎯 Goal | Revenue optimization & business decision support |

---

## ❓ Business Questions Answered

1. What is the overall revenue, profit, and average order value?
2. Which product categories drive the most revenue and profit?
3. How has sales performance trended month-over-month and year-over-year?
4. Which states and city tiers contribute the most to revenue?
5. What is the most preferred payment method?
6. How do discounts affect profit margins?
7. What is the return and cancellation rate — and which channel is worse?
8. Which are the top 10 best-selling products?
9. Is there a festive season (Diwali) effect on sales?
10. Who are our most valuable customers?

---

## 📊 Dataset Description

| Column | Description |
|---|---|
| `Order_ID` | Unique order identifier |
| `Order_Date` | Date of order placement |
| `Month / Quarter / Year` | Time dimensions |
| `Customer_ID / Name` | Customer identifier |
| `State / City_Tier` | Geographic info (Tier-1/2/3) |
| `Category / Product_Name` | Product classification |
| `MRP / Discount_Pct / Sale_Price` | Pricing details |
| `Quantity / Revenue / COGS / Profit` | Sales financials |
| `Profit_Margin` | Profit % per order |
| `Payment_Mode` | UPI, Credit Card, COD, etc. |
| `Order_Status` | Delivered / Returned / Cancelled |
| `Channel` | Mobile App / Website |
| `Rating` | Customer rating (1–5) |

---

## 🔍 Key Insights

### 💰 Revenue & Profit
- **Total Revenue:** ₹56.35 Million across all delivered orders
- **Total Profit:** ₹22.27 Million with an average margin of **~40%**
- **Average Order Value:** ₹16,826 — driven heavily by Electronics

### 📦 Category Performance
- **Electronics** is the #1 revenue category, but **Beauty & Books** have higher profit margins
- Electronics accounts for ~35% of total revenue but requires heavier discounting

### 🗓️ Seasonal Trends
- **October–November (Diwali season)** shows a significant spike in all categories
- Q4 consistently outperforms Q1 by 18–22% in revenue

### 🗺️ Geographic Insights
- **Tier-1 cities** (Maharashtra, Karnataka, Delhi) contribute 55%+ of revenue
- **Tier-3 states** show lower AOV but surprisingly competitive profit margins

### 💳 Payment Behaviour
- **Credit Card** is the #1 revenue driver; **UPI** leads in order volume
- **Cash on Delivery** has the highest return rate (expected)

### 🎯 Discount Impact
- Discounts above 40% cut profit margins by nearly half
- **Fashion** and **Beauty** categories benefit from high discounts (volume uplift > margin loss)
- **Electronics** should cap discounts at 20% to protect margins

---

## 📈 Visualizations

| Plot | Description |
|---|---|
| `01_kpi_dashboard.png` | KPI summary — Revenue, Profit, Orders, AOV, Margin |
| `02_monthly_trend.png` | Monthly revenue trend line (2022 vs 2023 vs 2024) |
| `03_category_performance.png` | Revenue by category + Margin vs Volume bubble chart |
| `04_geo_analysis.png` | Top 10 states bar chart + City Tier donut chart |
| `05_payment_channel.png` | Payment mode revenue + Order status + Channel analysis |
| `06_products_discount.png` | Top 10 products + Discount vs Margin scatter |
| `07_quarterly_yoy.png` | Quarterly Revenue vs Profit + YoY growth rate |
| `08_heatmap.png` | Revenue heatmap — Category × Month |

### Preview

![KPI Dashboard](plots/01_kpi_dashboard.png)
![Monthly Trend](plots/02_monthly_trend.png)
![Category Performance](plots/03_category_performance.png)
![Geo Analysis](plots/04_geo_analysis.png)
![Heatmap](plots/08_heatmap.png)

---

## 🗄️ SQL Analysis

15 production-ready SQL queries covering:

- Overall business summary & yearly growth
- Category & product performance with `RANK()` window function
- Monthly trends with `LAG()` for MoM growth calculation
- Geographic breakdown by state & city tier
- Customer segmentation (One-time / Returning / Loyal)
- Payment mode & channel performance with return rates
- Discount band impact on margin
- Advanced rolling 3-month averages & cumulative revenue using `OVER()`

📄 Full file: [`sql/sql_analysis.sql`](sql/sql_analysis.sql)

```sql
-- Example: YoY Revenue Growth using Window Functions
WITH yearly AS (
    SELECT Year,
           ROUND(SUM(Revenue), 2) AS Revenue
    FROM amazon_sales
    WHERE Order_Status = 'Delivered'
    GROUP BY Year
)
SELECT Year, Revenue,
       ROUND(
           (Revenue - LAG(Revenue) OVER (ORDER BY Year))
           / LAG(Revenue) OVER (ORDER BY Year) * 100, 2
       ) AS YoY_Growth_Pct
FROM yearly;
```

---

## 🗂️ Project Structure

```
amazon-india-sales-analysis/
│
├── data/
│   └── amazon_sales_india.csv       ← Dataset (5,000 rows × 23 cols)
│
├── scripts/
│   ├── amazon_sales_analysis.py     ← Main EDA script (Step-by-step)
│   └── generate_plots.py            ← Chart generation script
│
├── sql/
│   └── sql_analysis.sql             ← 15 SQL queries with window functions
│
├── plots/
│   ├── 01_kpi_dashboard.png
│   ├── 02_monthly_trend.png
│   ├── 03_category_performance.png
│   ├── 04_geo_analysis.png
│   ├── 05_payment_channel.png
│   ├── 06_products_discount.png
│   ├── 07_quarterly_yoy.png
│   └── 08_heatmap.png
│
├── requirements.txt
├── .gitignore
└── README.md
```

---

## ⚙️ How to Run

```bash
# 1. Clone the repository
git clone https://github.com/shakirsyeed/amazon-india-sales-analysis.git
cd amazon-india-sales-analysis

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run main analysis
python scripts/amazon_sales_analysis.py

# 4. Regenerate all plots
python scripts/generate_plots.py
```

---

## 🖥️ Power BI Dashboard

A Power BI dashboard has been built using the same dataset with the following pages:

- **Page 1 — Executive Summary:** Total KPIs, revenue trend, category split
- **Page 2 — Geographic Analysis:** State map, city tier breakdown
- **Page 3 — Product & Category Deep Dive:** Top products, discount analysis
- **Page 4 — Customer & Payment Insights:** Payment mix, return rate, customer segments

> 📥 Download the `.pbix` file from the repo to explore the interactive dashboard.

---

## 💡 Business Recommendations

1. **Invest more in Electronics during Q4** — Diwali season drives 30%+ uplift; plan inventory early
2. **Cap Electronics discounts at 20%** — higher discounts erode margin without proportionate revenue gain
3. **Target Tier-2 cities for growth** — lower competition, improving internet penetration, rising AOV
4. **Promote UPI & Credit Card payments** — highest revenue per order; run cashback campaigns
5. **Reduce Mobile App cancellation rate** — investigate checkout friction on app vs website
6. **Upsell Beauty & Books** — highest margin categories; bundle with Electronics for AOV boost

---

## 👤 About the Author

**Shakir Syeed** — Aspiring Data Analyst from India

Passionate about turning raw data into real business decisions using Python, SQL, and Power BI.

[![LinkedIn](www.linkedin.com/in/shakir-syeed)
[![GitHub](https://img.shields.io/badge/GitHub-181717?style=flat-square&logo=github&logoColor=white)](https://github.com/shakirsyeed)
[![Email](https://img.shields.io/badge/Gmail-D14836?style=flat-square&logo=gmail&logoColor=white)](mailto:shakirsyeed@gmail.com)

---

⭐ **If this project helped you, give it a star — it keeps me motivated to build more!**
