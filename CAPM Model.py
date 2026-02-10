import yfinance as yf
import pandas as pd

# 1. Download daily adjusted close prices for Reliance and Nifty 50 for 2023
reliance = yf.download("RELIANCE.NS", start="2022-04-01", end="2025-03-31")['Close']
wipro = yf.download("WIPRO.NS", start="2022-04-01", end="2025-03-31")['Close']
canara_bank = yf.download("CANBK.NS", start="2022-04-01", end="2025-03-31")['Close']
nifty = yf.download("^NSEI", start="2022-04-01", end="2025-03-31")['Close']

# 2. Calculate daily returns
reliance_ret = reliance.pct_change().dropna()
nifty_ret = nifty.pct_change().dropna()

# 3. Align the data (ensure both series have the same dates)
data = pd.concat([reliance_ret, nifty_ret], axis=1, join='inner')
data.columns = ['Reliance', 'Nifty']
data = data.dropna()

# 4. Calculate beta (Covariance of Reliance & Nifty / Variance of Nifty)
cov_matrix = data.cov()
beta = cov_matrix.loc['Reliance', 'Nifty'] / cov_matrix.loc['Nifty', 'Nifty']

# 5. Calculate expected return using CAPM formula
# CAPM: E(R) = Rf + Beta * (Rm - Rf)
risk_free_rate = 0.0625  # Example: 6.25% annual risk-free rate
market_return = data['Nifty'].mean() * 252  # Annualized market return
expected_return = risk_free_rate + beta * (market_return - risk_free_rate)

# 6. Print results
print(f"Reliance Beta (2023): {beta:.4f}")
print(f"Expected Annual Market Return (Nifty): {market_return:.2%}")
print(f"Expected Annual Return for Reliance (CAPM): {expected_return:.2%}")