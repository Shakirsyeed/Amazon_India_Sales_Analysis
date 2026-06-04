import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import seaborn as sns
import warnings, os
warnings.filterwarnings('ignore')

os.makedirs('/home/claude/plots', exist_ok=True)

df = pd.read_csv('/home/claude/amazon_sales_india.csv')
df['Order_Date'] = pd.to_datetime(df['Order_Date'])

# ── Colour Palette ───────────────────────────────────────────
AMAZON_ORANGE = '#FF9900'
AMAZON_DARK   = '#232F3E'
AMAZON_BLUE   = '#146EB4'
ACCENT        = '#E31837'
GREENS        = ['#1a9641','#a6d96a','#fdae61','#d7191c','#2c7bb6','#7b2d8b']
PALETTE       = [AMAZON_ORANGE, AMAZON_BLUE, ACCENT, '#2ecc71', '#9b59b6', '#1abc9c']

plt.rcParams.update({
    'font.family':       'DejaVu Sans',
    'axes.facecolor':    '#F9F9F9',
    'figure.facecolor':  'white',
    'axes.spines.top':   False,
    'axes.spines.right': False,
    'axes.grid':         True,
    'grid.alpha':        0.3,
    'axes.titlesize':    13,
    'axes.labelsize':    11,
})

# ════════════════════════════════════════════════════════════
# PLOT 1 — KPI Summary Dashboard
# ════════════════════════════════════════════════════════════
delivered = df[df['Order_Status'] == 'Delivered']
total_rev    = delivered['Revenue'].sum()
total_profit = delivered['Profit'].sum()
total_orders = len(delivered)
avg_margin   = delivered['Profit_Margin'].mean()
avg_order    = delivered['Revenue'].mean()
total_units  = delivered['Quantity'].sum()

fig, axes = plt.subplots(2, 3, figsize=(16, 7))
fig.suptitle('📦 Amazon India Sales — KPI Overview (2022–2024)',
             fontsize=17, fontweight='bold', color=AMAZON_DARK, y=1.01)

kpis = [
    ('💰 Total Revenue',     f'₹{total_rev/1e6:.2f}M',   AMAZON_ORANGE),
    ('📈 Total Profit',      f'₹{total_profit/1e6:.2f}M', '#2ecc71'),
    ('🛒 Total Orders',      f'{total_orders:,}',          AMAZON_BLUE),
    ('📊 Avg Profit Margin', f'{avg_margin:.1f}%',         '#9b59b6'),
    ('🧾 Avg Order Value',   f'₹{avg_order:,.0f}',        ACCENT),
    ('📦 Units Sold',        f'{total_units:,}',           '#1abc9c'),
]

for ax, (label, value, color) in zip(axes.flatten(), kpis):
    ax.set_facecolor(color + '18')
    ax.text(0.5, 0.6, value, ha='center', va='center',
            fontsize=28, fontweight='bold', color=color, transform=ax.transAxes)
    ax.text(0.5, 0.25, label, ha='center', va='center',
            fontsize=12, color=AMAZON_DARK, transform=ax.transAxes)
    for sp in ax.spines.values(): sp.set_visible(False)
    ax.set_xticks([]); ax.set_yticks([])
    ax.spines['bottom'].set_color(color)
    ax.spines['bottom'].set_visible(True)
    ax.spines['bottom'].set_linewidth(3)

plt.tight_layout()
plt.savefig('/home/claude/plots/01_kpi_dashboard.png', dpi=150, bbox_inches='tight')
plt.close()
print("✅ Plot 1 done")

# ════════════════════════════════════════════════════════════
# PLOT 2 — Monthly Revenue Trend (line)
# ════════════════════════════════════════════════════════════
monthly = (delivered.groupby(['Year','Month', delivered['Order_Date'].dt.month])
           .agg(Revenue=('Revenue','sum'), Profit=('Profit','sum'))
           .reset_index())
monthly.columns = ['Year','Month_Name','Month_Num','Revenue','Profit']
monthly = monthly.sort_values(['Year','Month_Num'])
monthly['YearMonth'] = monthly['Year'].astype(str) + '-' + monthly['Month_Num'].astype(str).str.zfill(2)

fig, ax = plt.subplots(figsize=(16, 5))
for yr, grp in monthly.groupby('Year'):
    ax.plot(range(len(grp)), grp['Revenue']/1000,
            marker='o', linewidth=2.5, markersize=6, label=str(yr))
    # annotate peak
    peak_idx = grp['Revenue'].idxmax()
    peak_row  = grp.loc[peak_idx]
    pos = list(grp.index).index(peak_idx)
    ax.annotate(f'₹{peak_row["Revenue"]/1000:.0f}K',
                xy=(pos, peak_row['Revenue']/1000),
                xytext=(0, 12), textcoords='offset points',
                ha='center', fontsize=8, color='gray')

months_labels = monthly[monthly['Year']==2022]['Month_Name'].tolist()
ax.set_xticks(range(len(months_labels)))
ax.set_xticklabels(months_labels, rotation=35, ha='right')
ax.set_title('📅 Monthly Revenue Trend by Year', fontweight='bold')
ax.set_ylabel('Revenue (₹ Thousands)')
ax.legend(title='Year')
ax.fill_between(range(len(monthly[monthly['Year']==2023])),
                monthly[monthly['Year']==2023]['Revenue'].values/1000,
                alpha=0.07, color=AMAZON_ORANGE)
plt.tight_layout()
plt.savefig('/home/claude/plots/02_monthly_trend.png', dpi=150, bbox_inches='tight')
plt.close()
print("✅ Plot 2 done")

# ════════════════════════════════════════════════════════════
# PLOT 3 — Category Performance (Revenue + Profit Margin)
# ════════════════════════════════════════════════════════════
cat_perf = (delivered.groupby('Category')
            .agg(Revenue=('Revenue','sum'),
                 Profit=('Profit','sum'),
                 Orders=('Order_ID','count'),
                 Avg_Margin=('Profit_Margin','mean'))
            .reset_index()
            .sort_values('Revenue', ascending=True))

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))

# Horizontal bar — Revenue
bars = ax1.barh(cat_perf['Category'], cat_perf['Revenue']/1000,
                color=PALETTE[:len(cat_perf)], edgecolor='white', height=0.6)
for bar, val in zip(bars, cat_perf['Revenue']/1000):
    ax1.text(val + 50, bar.get_y() + bar.get_height()/2,
             f'₹{val:.0f}K', va='center', fontsize=9)
ax1.set_title('Revenue by Category (₹ Thousands)', fontweight='bold')
ax1.set_xlabel('Revenue (₹K)')

# Bubble — Margin vs Orders
sc = ax2.scatter(cat_perf['Orders'], cat_perf['Avg_Margin'],
                 s=cat_perf['Revenue']/500, c=PALETTE[:len(cat_perf)],
                 alpha=0.85, edgecolors='white', linewidth=1.5)
for _, row in cat_perf.iterrows():
    ax2.annotate(row['Category'], (row['Orders'], row['Avg_Margin']),
                 textcoords='offset points', xytext=(6,4), fontsize=9)
ax2.set_title('Profit Margin % vs Order Volume\n(Bubble size = Revenue)', fontweight='bold')
ax2.set_xlabel('Number of Orders')
ax2.set_ylabel('Avg Profit Margin (%)')

plt.tight_layout()
plt.savefig('/home/claude/plots/03_category_performance.png', dpi=150, bbox_inches='tight')
plt.close()
print("✅ Plot 3 done")

# ════════════════════════════════════════════════════════════
# PLOT 4 — State & City Tier Analysis
# ════════════════════════════════════════════════════════════
state_rev = (delivered.groupby('State')['Revenue'].sum()
             .sort_values(ascending=False).head(10).reset_index())
tier_rev  = (delivered.groupby('City_Tier')
             .agg(Revenue=('Revenue','sum'), Orders=('Order_ID','count'))
             .reset_index())

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))

# Top 10 states
colors_state = [AMAZON_ORANGE if i == 0 else AMAZON_BLUE + '99' for i in range(len(state_rev))]
bars = ax1.bar(state_rev['State'], state_rev['Revenue']/1000,
               color=colors_state, edgecolor='white')
for bar, val in zip(bars, state_rev['Revenue']/1000):
    ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 30,
             f'₹{val:.0f}K', ha='center', fontsize=8, rotation=45)
ax1.set_title('🗺️ Top 10 States by Revenue', fontweight='bold')
ax1.set_ylabel('Revenue (₹K)')
ax1.set_xticklabels(state_rev['State'], rotation=40, ha='right', fontsize=9)

# City Tier donut
wedge_colors = [AMAZON_ORANGE, AMAZON_BLUE, '#2ecc71']
wedges, texts, autotexts = ax2.pie(
    tier_rev['Revenue'], labels=tier_rev['City_Tier'],
    autopct='%1.1f%%', colors=wedge_colors,
    pctdistance=0.75, startangle=90,
    wedgeprops=dict(width=0.55, edgecolor='white', linewidth=2))
for at in autotexts: at.set_fontsize(11); at.set_fontweight('bold')
ax2.set_title('🏙️ Revenue Share by City Tier', fontweight='bold')

plt.tight_layout()
plt.savefig('/home/claude/plots/04_geo_analysis.png', dpi=150, bbox_inches='tight')
plt.close()
print("✅ Plot 4 done")

# ════════════════════════════════════════════════════════════
# PLOT 5 — Payment Mode & Channel + Order Status
# ════════════════════════════════════════════════════════════
pay_rev = (delivered.groupby('Payment_Mode')['Revenue'].sum()
           .sort_values(ascending=False).reset_index())
chan_rev = (df.groupby(['Channel','Order_Status'])['Order_ID'].count()
            .reset_index().rename(columns={'Order_ID':'Count'}))
status_counts = df['Order_Status'].value_counts()

fig, axes = plt.subplots(1, 3, figsize=(18, 6))

# Payment mode bar
axes[0].barh(pay_rev['Payment_Mode'], pay_rev['Revenue']/1000,
             color=[AMAZON_ORANGE, AMAZON_BLUE, '#2ecc71', '#9b59b6', ACCENT, '#1abc9c'],
             edgecolor='white', height=0.6)
for i, (_, row) in enumerate(pay_rev.iterrows()):
    axes[0].text(row['Revenue']/1000 + 10, i,
                 f'₹{row["Revenue"]/1000:.0f}K', va='center', fontsize=9)
axes[0].set_title('💳 Revenue by Payment Mode', fontweight='bold')
axes[0].set_xlabel('Revenue (₹K)')

# Order status pie
axes[1].pie(status_counts, labels=status_counts.index,
            autopct='%1.1f%%',
            colors=[AMAZON_ORANGE, ACCENT, '#2ecc71'],
            startangle=90,
            wedgeprops=dict(edgecolor='white', linewidth=2))
axes[1].set_title('📦 Order Status Distribution', fontweight='bold')

# Channel stacked bar
chan_pivot = chan_rev.pivot(index='Channel', columns='Order_Status', values='Count').fillna(0)
chan_pivot.plot(kind='bar', ax=axes[2], color=[AMAZON_ORANGE, '#2ecc71', ACCENT],
               edgecolor='white', rot=0)
axes[2].set_title('📱 Orders by Channel & Status', fontweight='bold')
axes[2].set_ylabel('Number of Orders')
axes[2].legend(title='Status', fontsize=9)

plt.tight_layout()
plt.savefig('/home/claude/plots/05_payment_channel.png', dpi=150, bbox_inches='tight')
plt.close()
print("✅ Plot 5 done")

# ════════════════════════════════════════════════════════════
# PLOT 6 — Top 10 Products + Discount vs Profit Margin
# ════════════════════════════════════════════════════════════
top_products = (delivered.groupby('Product_Name')['Revenue'].sum()
                .sort_values(ascending=False).head(10).reset_index())
disc_margin  = (delivered.groupby('Category')
                .agg(Avg_Discount=('Discount_Pct','mean'),
                     Avg_Margin=('Profit_Margin','mean'))
                .reset_index())

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(17, 6))

# Top 10 products
colors_p = [AMAZON_ORANGE if i < 3 else AMAZON_BLUE + 'BB' for i in range(10)]
ax1.barh(top_products['Product_Name'], top_products['Revenue']/1000,
         color=colors_p, edgecolor='white', height=0.65)
for i, (_, row) in enumerate(top_products.iterrows()):
    ax1.text(row['Revenue']/1000 + 5, i,
             f'₹{row["Revenue"]/1000:.0f}K', va='center', fontsize=9)
ax1.set_title('🏆 Top 10 Products by Revenue', fontweight='bold')
ax1.set_xlabel('Revenue (₹K)')
ax1.invert_yaxis()

# Discount vs Margin scatter
for i, row in disc_margin.iterrows():
    ax2.scatter(row['Avg_Discount'], row['Avg_Margin'],
                s=200, color=PALETTE[i], zorder=5)
    ax2.annotate(row['Category'], (row['Avg_Discount'], row['Avg_Margin']),
                 xytext=(5, 4), textcoords='offset points', fontsize=10)
m, b = np.polyfit(disc_margin['Avg_Discount'], disc_margin['Avg_Margin'], 1)
xline = np.linspace(disc_margin['Avg_Discount'].min(), disc_margin['Avg_Discount'].max(), 100)
ax2.plot(xline, m*xline+b, '--', color='gray', linewidth=1.5, label='Trend')
ax2.set_title('🎯 Avg Discount % vs Avg Profit Margin\nby Category', fontweight='bold')
ax2.set_xlabel('Avg Discount (%)')
ax2.set_ylabel('Avg Profit Margin (%)')
ax2.legend()

plt.tight_layout()
plt.savefig('/home/claude/plots/06_products_discount.png', dpi=150, bbox_inches='tight')
plt.close()
print("✅ Plot 6 done")

# ════════════════════════════════════════════════════════════
# PLOT 7 — Quarterly YoY Growth
# ════════════════════════════════════════════════════════════
qtr = (delivered.groupby(['Year','Quarter'])
       .agg(Revenue=('Revenue','sum'), Profit=('Profit','sum'), Orders=('Order_ID','count'))
       .reset_index())
qtr['Label'] = qtr['Year'].astype(str) + ' ' + qtr['Quarter']

fig, axes = plt.subplots(1, 2, figsize=(16, 6))
x = np.arange(len(qtr))
width = 0.35

axes[0].bar(x - width/2, qtr['Revenue']/1000, width,
            label='Revenue', color=AMAZON_ORANGE, edgecolor='white')
axes[0].bar(x + width/2, qtr['Profit']/1000, width,
            label='Profit', color=AMAZON_BLUE, edgecolor='white')
axes[0].set_xticks(x)
axes[0].set_xticklabels(qtr['Label'], rotation=40, ha='right', fontsize=8)
axes[0].set_title('📊 Quarterly Revenue vs Profit', fontweight='bold')
axes[0].set_ylabel('₹ Thousands')
axes[0].legend()

# YoY growth rate
yr_rev = delivered.groupby('Year')['Revenue'].sum()
yoy_growth = yr_rev.pct_change() * 100
colors_g = [AMAZON_ORANGE if v >= 0 else ACCENT for v in yoy_growth.dropna()]
axes[1].bar(yoy_growth.dropna().index, yoy_growth.dropna().values,
            color=colors_g, edgecolor='white', width=0.5)
for i, (yr, val) in enumerate(yoy_growth.dropna().items()):
    axes[1].text(yr, val + 0.5, f'{val:.1f}%', ha='center', fontsize=12, fontweight='bold')
axes[1].axhline(0, color='black', linewidth=0.8, linestyle='--')
axes[1].set_title('📈 Year-over-Year Revenue Growth', fontweight='bold')
axes[1].set_ylabel('Growth (%)')
axes[1].set_xlabel('Year')

plt.tight_layout()
plt.savefig('/home/claude/plots/07_quarterly_yoy.png', dpi=150, bbox_inches='tight')
plt.close()
print("✅ Plot 7 done")

# ════════════════════════════════════════════════════════════
# PLOT 8 — Heatmap: Category × Month Revenue
# ════════════════════════════════════════════════════════════
month_order = ['January','February','March','April','May','June',
               'July','August','September','October','November','December']
heat_data = (delivered.groupby(['Category','Month'])['Revenue']
             .sum().reset_index()
             .pivot(index='Category', columns='Month', values='Revenue')
             .reindex(columns=[m for m in month_order if m in delivered['Month'].unique()])
             .fillna(0))

fig, ax = plt.subplots(figsize=(16, 5))
sns.heatmap(heat_data/1000, annot=True, fmt='.0f', cmap='YlOrRd',
            linewidths=0.5, linecolor='white', ax=ax,
            cbar_kws={'label': 'Revenue (₹K)'})
ax.set_title('🗓️ Revenue Heatmap — Category × Month (₹ Thousands)', fontweight='bold', fontsize=14)
ax.set_xlabel('')
ax.set_ylabel('')
plt.xticks(rotation=35, ha='right')
plt.tight_layout()
plt.savefig('/home/claude/plots/08_heatmap.png', dpi=150, bbox_inches='tight')
plt.close()
print("✅ Plot 8 done")

print("\n🎉 All 8 plots saved to /home/claude/plots/")

# ── Print Summary Stats ───────────────────────────────────
print("\n" + "="*55)
print("       AMAZON INDIA SALES — KEY INSIGHTS SUMMARY")
print("="*55)
print(f"  Total Revenue      : ₹{total_rev:,.0f}")
print(f"  Total Profit       : ₹{total_profit:,.0f}")
print(f"  Total Orders       : {total_orders:,}")
print(f"  Avg Profit Margin  : {avg_margin:.2f}%")
print(f"  Avg Order Value    : ₹{avg_order:,.2f}")
print(f"  Top Category       : {cat_perf.sort_values('Revenue',ascending=False).iloc[0]['Category']}")
print(f"  Top State          : {state_rev.iloc[0]['State']}")
print(f"  Top Payment Mode   : {pay_rev.iloc[0]['Payment_Mode']}")
print("="*55)
