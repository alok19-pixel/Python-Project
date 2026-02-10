import yfinance as yf

# Example: Reliance Industries
ticker = yf.Ticker("HINDPETRO.NS")
info = ticker.info

# 1. Get Market Cap (Equity Value)
market_cap = info['marketCap']

# 2. Estimate Debt (Total Debt)
# yfinance may not always provide totalDebt; you may need to get it from financials or manually
total_debt = info.get('totalDebt', 0)

# 3. Get Cash (for Net Debt calculation)
cash = info.get('totalCash', 0)

# 4. Calculate Enterprise Value (EV)
enterprise_value = market_cap + total_debt - cash

# 5. Calculate Weights
E = market_cap
D = total_debt
V = E + D
weight_equity = E / V if V > 0 else 0
weight_debt = D / V if V > 0 else 0

# 6. Cost of Equity (using CAPM)
risk_free_rate = 0.065  # 6.5% (example, use Indian 10Y bond yield)
market_return = 0.13    # 13% (example, long-term Nifty return)
beta = 2.0472             # Use your calculated beta for the company

cost_of_equity = risk_free_rate + beta * (market_return - risk_free_rate)

# 7. Cost of Debt (use interest expense / total debt, or estimate)
cost_of_debt = 0.08  # 8% (example, use actual if available)

# 8. Corporate Tax Rate (India example)
tax_rate = 0.25  # 25%

# 9. WACC Calculation
wacc = (weight_equity * cost_of_equity) + (weight_debt * cost_of_debt * (1 - tax_rate))

# Print Results in Crores
print(f"Market Cap (Equity): {E/1e7:,.2f} Cr")
print(f"Total Debt: {D/1e7:,.2f} Cr")
print(f"Cash: {cash/1e7:,.2f} Cr")
print(f"Enterprise Value: {enterprise_value/1e7:,.2f} Cr")
print(f"Weight Equity: {weight_equity:.2%}")
print(f"Weight Debt: {weight_debt:.2%}")
print(f"Cost of Equity: {cost_of_equity:.2%}")
print(f"Cost of Debt (after tax): {cost_of_debt * (1-tax_rate):.2%}")
print(f"WACC: {wacc:.2%}")