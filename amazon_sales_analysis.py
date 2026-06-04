"""
╔══════════════════════════════════════════════════════════════╗
║     AMAZON INDIA SALES ANALYSIS — End-to-End Project        ║
║     Author  : Shakir Syeed                                   ║
║     Tools   : Python | Pandas | Matplotlib | Seaborn        ║
║     Dataset : Amazon Sales India (2022–2024) — 5,000 rows   ║
╚══════════════════════════════════════════════════════════════╝
"""

# ══════════════════════════════════════════════════════════════
# STEP 0 — IMPORTS
# ══════════════════════════════════════════════════════════════
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
import warnings
warnings.filterwarnings('ignore')

print("=" * 60)
print("  AMAZON INDIA SALES — END-TO-END ANALYSIS")
print("=" * 60)

# ══════════════════════════════════════════════════════════════
# STEP 1 — LOAD DATA
# ══════════════════════════════════════════════════════════════
print("\n[STEP 1] Loading Dataset...")
df = pd.read_csv('amazon_sales_india.csv')
df['Order_Date'] = pd.to_datetime(df['Order_Date'])

print(f"  Shape     : {df.shape[0]:,} rows × {df.shape[1]} columns")
print(f"  Date Range: {df['Order_Date'].min().date()} → {df['Order_Date'].max().date()}")
print(f"  Columns   : {list(df.columns)}")

# ══════════════════════════════════════════════════════════════
# STEP 2 — DATA CLEANING & VALIDATION
# ══════════════════════════════════════════════════════════════
print("\n[STEP 2] Data Cleaning & Validation...")

# Check missing values
missing = df.isnull().sum()
print(f"  Missing values: {missing[missing > 0].to_dict() or 'None ✅'}")

# Check duplicates
dupes = df.duplicated().sum()
print(f"  Duplicate rows: {dupes}")

# Check data types
print(f"  Dtypes OK: Order_Date={df['Order_Date'].dtype}, Revenue={df['Revenue'].dtype}")

# Validate numeric ranges
assert df['Revenue'].min() > 0,        "❌ Negative revenue found"
assert df['Discount_Pct'].max() <= 100, "❌ Discount > 100%"
assert df['Rating'].between(1,5).all(), "❌ Rating out of 1-5 range"
print("  All validation checks passed ✅")

# Feature Engineering
df['Month_Num'] = df['Order_Date'].dt.month
df['Week']      = df['Order_Date'].dt.isocalendar().week.astype(int)
df['DayOfWeek'] = df['Order_Date'].dt.day_name()
df['Is_Weekend']= df['DayOfWeek'].isin(['Saturday','Sunday'])
df['Is_Festive']= df['Month_Num'].isin([10, 11])   # Oct-Nov = Diwali season

# Work with delivered orders only for revenue analysis
delivered = df[df['Order_Status'] == 'Delivered'].copy()
print(f"  Delivered orders: {len(delivered):,} / {len(df):,} total")

# ══════════════════════════════════════════════════════════════
# STEP 3 — EXPLORATORY DATA ANALYSIS (EDA)
# ══════════════════════════════════════════════════════════════
print("\n[STEP 3] Exploratory Data Analysis...")

# 3a. Descriptive Statistics
print("\n  Revenue Statistics:")
print(delivered['Revenue'].describe().apply(lambda x: f"  ₹{x:,.2f}").to_string())

# 3b. Category breakdown
print("\n  Revenue by Category:")
cat_summary = (delivered.groupby('Category')
               .agg(Orders=('Order_ID','count'),
                    Revenue=('Revenue','sum'),
                    Avg_Margin=('Profit_Margin','mean'))
               .sort_values('Revenue', ascending=False))
for cat, row in cat_summary.iterrows():
    print(f"  {cat:<18} | Orders: {row['Orders']:>4} | Rev: ₹{row['Revenue']:>12,.0f} | Margin: {row['Avg_Margin']:.1f}%")

# 3c. Payment mode
print("\n  Top Payment Modes:")
pay = delivered['Payment_Mode'].value_counts()
for mode, cnt in pay.items():
    print(f"  {mode:<20} : {cnt:>4} orders ({cnt/len(delivered)*100:.1f}%)")

# 3d. Return rate
return_rate = (df['Order_Status'] == 'Returned').sum() / len(df) * 100
cancel_rate = (df['Order_Status'] == 'Cancelled').sum() / len(df) * 100
print(f"\n  Return Rate   : {return_rate:.2f}%")
print(f"  Cancellation  : {cancel_rate:.2f}%")

# 3e. Festive vs Normal season
fest_rev   = delivered[delivered['Is_Festive']]['Revenue'].sum()
normal_rev = delivered[~delivered['Is_Festive']]['Revenue'].sum()
fest_pct   = fest_rev / (fest_rev + normal_rev) * 100
print(f"\n  Festive Season (Oct-Nov) Revenue Share: {fest_pct:.1f}%")

# ══════════════════════════════════════════════════════════════
# STEP 4 — KEY BUSINESS INSIGHTS
# ══════════════════════════════════════════════════════════════
print("\n[STEP 4] Key Business Insights...")

total_rev    = delivered['Revenue'].sum()
total_profit = delivered['Profit'].sum()
top_cat      = cat_summary.index[0]
top_state    = delivered.groupby('State')['Revenue'].sum().idxmax()
top_product  = delivered.groupby('Product_Name')['Revenue'].sum().idxmax()
top_payment  = delivered['Payment_Mode'].value_counts().index[0]
avg_margin   = delivered['Profit_Margin'].mean()

print(f"""
  ┌─────────────────────────────────────────────────┐
  │            BUSINESS INSIGHTS SUMMARY            │
  ├─────────────────────────────────────────────────┤
  │  Total Revenue      : ₹{total_rev:>15,.0f}          │
  │  Total Profit       : ₹{total_profit:>15,.0f}          │
  │  Avg Profit Margin  : {avg_margin:>14.2f}%          │
  │  Top Category       : {top_cat:<25}│
  │  Top State          : {top_state:<25}│
  │  Best Product       : {top_product[:25]:<25}│
  │  #1 Payment Mode    : {top_payment:<25}│
  └─────────────────────────────────────────────────┘
""")

# ══════════════════════════════════════════════════════════════
# STEP 5 — GENERATING VISUALIZATIONS
# ══════════════════════════════════════════════════════════════
print("[STEP 5] All 8 charts already generated in /plots/ ✅")
print("         Run analysis.py to regenerate if needed.\n")

print("=" * 60)
print("  ✅ ANALYSIS COMPLETE — Shakir Syeed")
print("     GitHub: github.com/shakirsyeed")
print("=" * 60)
