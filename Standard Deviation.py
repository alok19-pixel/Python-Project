import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime

# ────────────────────────────────────────────────
#  USER CONFIGURATION – change these values
# ────────────────────────────────────────────────
ticker_symbol = "SBIN.NS"          # ← Change ticker here
start_date    = "2025-04-01"            # ← Start date (YYYY-MM-DD) or None
end_date      = None                    # ← End date (YYYY-MM-DD) or None for latest
interval      = "1d"                    # ← "1d", "5d", "1wk", "1mo", "3mo", etc.

risk_free_rate = 0.065
market_return  = 0.13
cost_of_debt   = 0.08
tax_rate       = 0.30
# ────────────────────────────────────────────────

ticker = yf.Ticker(ticker_symbol)
info = ticker.info

# Quick current WACC snapshot (using latest available data)
market_cap = info.get('marketCap', 0)
total_debt = info.get('totalDebt', 0)
cash       = info.get('totalCash', 0)
enterprise_value = market_cap + total_debt - cash

E = market_cap
D = total_debt
V = E + D if E + D > 0 else 1
weight_equity = E / V
weight_debt   = D / V

beta = info.get('beta', 1.0)
cost_of_equity = risk_free_rate + beta * (market_return - risk_free_rate)
wacc = (weight_equity * cost_of_equity) + (weight_debt * cost_of_debt * (1 - tax_rate))

print(f"Current snapshot for {ticker_symbol}")
print(f"  WACC (approx): {wacc:.2%}")
print(f"  Market Cap:    ₹{market_cap / 1e7:,.2f} Cr")
print(f"  Enterprise Val:₹{enterprise_value / 1e7:,.2f} Cr\n")

# ────────────────────────────────────────────────
#  Download historical data with custom dates & interval
# ────────────────────────────────────────────────
print(f"Downloading {interval} data for {ticker_symbol}...")
print(f"  From: {start_date if start_date else 'earliest available'}")
print(f"  To:   {end_date if end_date else 'latest available'}\n")

hist = ticker.history(
    start=start_date,
    end=end_date,
    interval=interval,
    auto_adjust=True,
    actions=False
)

if hist.empty:
    print("No data returned. Check ticker, dates or internet connection.")
else:
    actual_start = hist.index[0].strftime("%Y-%m-%d")
    actual_end   = hist.index[-1].strftime("%Y-%m-%d")
    
    closes = hist['Close']
    returns = closes.pct_change().dropna() * 100   # in percent

    mean_ret = returns.mean()
    std_ret  = returns.std()

    ann_factor = {'1d':252, '5d':252/5, '1wk':52, '1mo':12, '3mo':4}.get(interval, 252)
    ann_mean = mean_ret * ann_factor
    ann_std  = std_ret  * np.sqrt(ann_factor)

    print(f"Period actually used: {actual_start} → {actual_end}")
    print(f"Number of periods:    {len(returns):,}")
    print(f"Mean return per {interval}: {mean_ret:6.3f}%")
    print(f"Std dev per {interval}:     {std_ret:6.3f}%")
    print(f"Annualized mean (approx):   {ann_mean:6.2f}%")
    print(f"Annualized volatility:      {ann_std:6.2f}%\n")

    # ── Plot with ±1σ bands ───────────────────────────────────────
    plt.figure(figsize=(14, 7))

    # Shaded ±1σ region
    plt.fill_between(
        returns.index,
        mean_ret + std_ret,
        mean_ret - std_ret,
        color='gray', alpha=0.09, label=f'±1 Std Dev ({interval})'
    )

    # Mean line
    plt.axhline(mean_ret, color='black', linestyle='--', linewidth=1.4,
                label=f'Mean = {mean_ret:.3f}%')

    # ±1σ lines
    plt.axhline(mean_ret + std_ret, color='red', linestyle=':', linewidth=1.1, alpha=0.75,
                label=f'+1σ = {mean_ret + std_ret:.3f}%')
    plt.axhline(mean_ret - std_ret, color='limegreen', linestyle=':', linewidth=1.1, alpha=0.75,
                label=f'-1σ = {mean_ret - std_ret:.3f}%')

    # Scatter points
    above = returns > mean_ret
    plt.scatter(returns.index[above], returns[above],
                color='red', marker='o', s=28, alpha=0.55, label='Above Mean')
    plt.scatter(returns.index[~above], returns[~above],
                color='lightgreen', marker='o', s=28, alpha=0.55, label='≤ Mean')

    # Faint return line
    plt.plot(returns.index, returns, color='navy', linewidth=0.5, alpha=0.25)

    plt.title(f"{ticker_symbol} – Returns ({interval}) from {actual_start} to {actual_end}\n"
              f"with ±1 Std Dev Bands", fontsize=14, pad=12)
    plt.xlabel('Date')
    plt.ylabel(f'Return per {interval} (%)')
    plt.grid(True, alpha=0.25)
    plt.legend(loc='upper right', fontsize=9.5)
    plt.tight_layout()
    plt.show()

    # ... after calculating 'returns' and 'mean_ret'

above = returns > mean_ret
below_or_equal = returns <= mean_ret

print(f"Days above mean: {above.sum()} ({above.mean()*100:.2f}%)")
print(f"Days ≤ mean:     {below_or_equal.sum()} ({below_or_equal.mean()*100:.2f}%)")
print(f"Total days:      {len(returns)}")

