#Importing the required libraries
import yfinance as yf
import matplotlib.pyplot as plt

# Retrieving historical data for both AAPL and MSFT
intc_data = yf.Ticker("INTC").history(period="10y")
nvda_data = yf.Ticker("NVDA").history(period="10y")
# Calculating daily returns for each stock
intc_returns = intc_data['Close'].pct_change().dropna()
nvda_returns = nvda_data['Close'].pct_change().dropna()
# Calculating average return and volatility (standard deviation)
intc_avg_return = intc_returns.mean()
nvda_avg_return = nvda_returns.mean()
intc_volatility = intc_returns.std()
nvda_volatility = nvda_returns.std()
# Displaying calculated statistics
print(f"INTC - Average Daily Return: {intc_avg_return:.4f}, Volatility: {intc_volatility:.4f}")
print(f"NVDA - Average Daily Return: {nvda_avg_return:.4f}, Volatility: {nvda_volatility:.4f}")
# Plotting stock price trends
plt.figure(figsize=(12, 6))
plt.plot(intc_data['Close'], label='INTC')
plt.plot(nvda_data['Close'], label='NVDA')
plt.title('INTC vs NVDA - 10 Year Closing Prices')
plt.xlabel('Date')
plt.ylabel('Closing Price (USD)')
plt.legend()
plt.show()