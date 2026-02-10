
import os
import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# Settings
securities = {
    'BankNifty': '^NSEBANK',
    'CanaraBank': 'CANBK.NS',
    'SBIN': 'SBIN.NS',
    'AdaniPower': 'ADANIPOWER.NS'
}
# include benchmark separately
benchmark_key = 'BankNifty'
start_date = "2020-01-01"
end_date = "2025-01-01"
out_dir = r'D:\Python'
os.makedirs(out_dir, exist_ok=True)

# Download close prices
tickers = [securities[k] for k in securities]
data = yf.download(tickers + [securities[benchmark_key]], start=start_date, end=end_date, progress=False)['Close'] \
         if isinstance(tickers, list) else yf.download(list(securities.values()), start=start_date, end=end_date, progress=False)['Close']

# map columns -> keys (yfinance order may vary)
col_map = {}
all_keys = list(securities.keys())
for key, tk in securities.items():
    # find matching column name in data by ticker string 
    matches = [c for c in data.columns if tk.split('.')[0].upper() in str(c).upper() or tk.upper() in str(c).upper()]
    col_map[key] = matches[0] if matches else None

# If direct mapping failed, assume order corresponds
if any(v is None for v in col_map.values()):
    data.columns = all_keys

# rename to friendly keys if needed
rename_map = {}
for key, tk in securities.items():
    # try to find column by ticker
    for col in data.columns:
        if tk in str(col) or key in str(col):
            rename_map[col] = key
data = data.rename(columns=rename_map)

# Ensure benchmark present
if benchmark_key not in data.columns:
    raise SystemExit("Benchmark column not found in downloaded data.")

# Calculate daily returns WITHOUT auto-filling NaNs (preserve trading gaps)
returns = data.pct_change(fill_method=None)

# helper: compute beta two ways with aligned data and optional excess returns
def compute_betas(stock_returns, market_returns, rf=0.0, use_excess=False):
    # align pairwise and drop NaNs
    pair = pd.concat([stock_returns, market_returns], axis=1).dropna()
    if pair.shape[0] < 2:
        return {'covvar': np.nan, 'ols': np.nan}
    s = pair.iloc[:,0].astype(float)
    m = pair.iloc[:,1].astype(float)
    if use_excess:
        s = s - rf
        m = m - rf
    # cov/var method (pandas uses ddof=1 sample variance/covariance)
    cov = s.cov(m)            # sample covariance (ddof=1)
    var_m = m.var()           # sample variance (ddof=1)
    beta_covvar = cov / var_m if var_m != 0 else np.nan
    # OLS slope (np.polyfit uses least-squares) => same slope as regression with intercept
    slope, intercept = np.polyfit(m.values, s.values, 1)
    return {'covvar': beta_covvar, 'ols': slope}

# compute YOY betas and overall
years = sorted(returns.dropna(how='all').index.year.unique())
seclist = [k for k in securities.keys() if k != benchmark_key]
beta_table = []

for sec in seclist:
    # overall
    overall = compute_betas(returns[sec], returns[benchmark_key], rf=0.0, use_excess=False)
    # per-year
    per_year = {}
    for y in years:
        yearly = returns[returns.index.year == y]
        res = compute_betas(yearly[sec], yearly[benchmark_key])
        per_year[y] = res
    beta_table.append({'security': sec, 'overall_covvar': overall['covvar'], 'overall_ols': overall['ols'], 'per_year': per_year})

# Build DataFrame for output (covvar method)
beta_df_cov = pd.DataFrame(index=seclist, columns=years, dtype=float)
beta_df_ols = pd.DataFrame(index=seclist, columns=years, dtype=float)
for row in beta_table:
    sec = row['security']
    for y, vals in row['per_year'].items():
        beta_df_cov.at[sec, y] = vals['covvar']
        beta_df_ols.at[sec, y] = vals['ols']

# Add benchmark row = 1 for all years
beta_df_cov.loc[benchmark_key] = 1.0
beta_df_ols.loc[benchmark_key] = 1.0

# Save CSVs
beta_df_cov.to_csv(os.path.join(out_dir, 'beta_yoy_covvar.csv'))
beta_df_ols.to_csv(os.path.join(out_dir, 'beta_yoy_ols.csv'))

# Compare methods: report securities/years where methods differ > tolerance
tol = 0.05  # 5% absolute difference tolerance
diffs = (beta_df_cov - beta_df_ols).abs()
mismatches = diffs.stack()[diffs.stack() > tol]
if not mismatches.empty:
    print("Method differences > tol (covvar vs OLS):")
    print(mismatches)
else:
    print("No large differences between cov/var and OLS methods (within tol).")

# Plot line chart with Years on X-axis and one line per security (covvar)
years_plot = list(beta_df_cov.columns)
fig, ax = plt.subplots(figsize=(10,6))
cmap = plt.cm.Blues
n = len(beta_df_cov.index)
colors = [cmap(0.2 + 0.6*i/max(1,n-1)) for i in range(n)]
for i, sec in enumerate(beta_df_cov.index):
    yvals = beta_df_cov.loc[sec, years_plot].astype(float).values
    ax.plot(years_plot, yvals, marker='o', color=colors[i], label=sec)
ax.set_xlabel('Year')
ax.set_ylabel('Beta (vs BankNifty)')
ax.set_title('YOY Beta (cov/var) — Years on X-axis')
ax.legend()
ax.grid(axis='y', linestyle='--', alpha=0.6)
plt.tight_layout()
plt.savefig(os.path.join(out_dir, 'beta_yoy_line_covvar.png'), dpi=300)
plt.show()

# Print summary (overall values)
print("Overall betas (covvar / ols):")
for row in beta_table:
    print(f"{row['security']}: covvar={row['overall_covvar']:.4f}, ols={row['overall_ols']:.4f}")
# ...existing code...
