import yfinance as yf
import pandas as pd
import numpy as np

# List of securities (tickers as per Yahoo Finance)
securities = {
    'ADANIPORTS': 'ADANIPORTS.NS', 'APOLLOHOSP': 'APOLLOHOSP.NS', 'ASIANPAINT': 'ASIANPAINT.NS', 'AXISBANK': 'AXISBANK.NS', 'BAJAJ-AUTO': 'BAJAJ-AUTO.NS',
    'BAJFINANCE': 'BAJFINANCE.NS', 'BAJAJFINSV': 'BAJAJFINSV.NS', 'BPCL': 'BPCL.NS', 'BHARTIARTL': 'BHARTIARTL.NS', 'BRITANNIA': 'BRITANNIA.NS',
    'CIPLA': 'CIPLA.NS', 'COALINDIA': 'COALINDIA.NS', 'DIVISLAB': 'DIVISLAB.NS', 'DRREDDY': 'DRREDDY.NS', 'EICHERMOT': 'EICHERMOT.NS',
    'GRASIM': 'GRASIM.NS', 'HCLTECH': 'HCLTECH.NS', 'HDFCBANK': 'HDFCBANK.NS', 'HDFCLIFE': 'HDFCLIFE.NS', 'HEROMOTOCO': 'HEROMOTOCO.NS',
    'HINDALCO': 'HINDALCO.NS', 'HINDUNILVR': 'HINDUNILVR.NS', 'ICICIBANK': 'ICICIBANK.NS', 'ITC': 'ITC.NS', 'INDUSINDBK': 'INDUSINDBK.NS',
    'INFY': 'INFY.NS', 'JSWSTEEL': 'JSWSTEEL.NS', 'KOTAKBANK': 'KOTAKBANK.NS', 'LTIM': 'LTIM.NS', 'LT': 'LT.NS',
    'M&M': 'M&M.NS', 'MARUTI': 'MARUTI.NS', 'NTPC': 'NTPC.NS', 'NESTLEIND': 'NESTLEIND.NS', 'ONGC': 'ONGC.NS',
    'POWERGRID': 'POWERGRID.NS', 'RELIANCE': 'RELIANCE.NS', 'SBILIFE': 'SBILIFE.NS', 'SBIN': 'SBIN.NS', 'SUNPHARMA': 'SUNPHARMA.NS',
    'TCS': 'TCS.NS', 'TATACONSUM': 'TATACONSUM.NS', 'TATAMOTORS': 'TATAMOTORS.NS', 'TATASTEEL': 'TATASTEEL.NS', 'TECHM': 'TECHM.NS',
    'TITAN': 'TITAN.NS', 'UPL': 'UPL.NS', 'ULTRACEMCO': 'ULTRACEMCO.NS', 'WIPRO': 'WIPRO.NS', 'HDFCAMC': 'HDFCAMC.NS'
}

start_date = "2021-04-01"
end_date = "2025-03-31"

# Download adjusted close prices for all securities
data = yf.download(list(securities.values()), start=start_date, end=end_date)['Close']
data.columns = list(securities.keys())

# Calculate daily returns
returns = data.pct_change().dropna()

# Assume annual risk-free rate (e.g., 6%)
risk_free_rate = 0.06
daily_rf = risk_free_rate / 252

# Calculate Sharpe ratio for each security
# Calculate Sharpe ratio for each security
sharpes = {}
for sec in securities:
    sec_ret = returns[sec].dropna()
    if sec_ret.empty:
        print(f"No return data for {sec}, skipping.")
        continue
    ann_vol = sec_ret.std() * np.sqrt(252)
    if ann_vol == 0 or np.isnan(ann_vol):
        print(f"Zero or NaN volatility for {sec}, skipping.")
        continue
    excess_ret = sec_ret - daily_rf
    ann_excess_ret = excess_ret.mean() * 252
    sharpe = ann_excess_ret / ann_vol
    sharpes[sec] = sharpe

# Print Sharpe ratios
for sec, sharpe in sharpes.items():
    print(f"Sharpe Ratio of {sec}: {sharpe:.4f}")

# Save Sharpe ratios to a CSV file
sharpe_df = pd.DataFrame.from_dict(sharpes, orient='index', columns=['Sharpe Ratio'])
sharpe_df.to_csv('Sharpe_Ratios.csv')
# Save Sharpe ratios to a CSV file  