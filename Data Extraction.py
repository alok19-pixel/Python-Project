import yfinance as yf
import pandas as pd

TATACHEM = yf.download('TATACHEM.NS', start='2020-04-01', end='2025-03-31', interval='1d')
NIFTY = yf.download('^NSEI', start='2020-04-01', end='2025-03-31', interval='1d')

# Calculate daily returns
tatachem_ret = TATACHEM['Close'].pct_change()
nifty_ret = NIFTY['Close'].pct_change()

# Align the data (ensure both series have the same dates)
data = pd.concat([
    TATACHEM[['Open', 'High', 'Low', 'Close']],
    NIFTY[['Open', 'High', 'Low', 'Close']],
    tatachem_ret,
    nifty_ret
], axis=1).dropna()

data.columns = [
    'TATACHEM_Open', 'TATACHEM_High', 'TATACHEM_Low', 'TATACHEM_Close',
    'NIFTY_Open', 'NIFTY_High', 'NIFTY_Low', 'NIFTY_Close',
    'TATACHEM_ret', 'NIFTY_ret'
]

print(data.head())
data.to_csv("D:/Python/TataChem_NIFTY_2024.csv", index=True)