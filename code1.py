#Importing the required libraries
import pandas as pd
import matplotlib.pyplot as plt
import sys
import yfinance as yf

symbols=['INTC', 'NVDA']
start_date='2024-01-01'
end_date='2024-12-31'

def download_historical_prices(symbols, start_date, end_date, auto_adjust=True):
    """
    Download historical prices for the given symbols
    """

    if not symbols:
        raise ValueError("No symbols provided")

    #Download the historical prices
    data = yf.download(symbols, start=start_date, end=end_date, auto_adjust=auto_adjust)

    #Process the data based on whether it's a single symbol or multiple symbols
    if len(symbols) == 1:
        #For a single symbol, yfinance returns a different format
        close = data['Close'].copy()
        close.name = f"{symbols[0]}_Close"
    else:
        #For multiple symbols
        close = pd.DataFrame()
        for symbol in symbols:
            close[f"{symbol}_Close"] = data['Close'][symbol]
        #Sort index just in case
        close = close.sort_index()
    return close

def compute_daily_returns(price_series:pd.Series) -> pd.Series:
    """
    Percent change for daily returns from a price series.
    """
    if price_series.empty:
        raise ValueError("'price_series' is empty.")
    returns = price_series.pct_change().dropna()
    if returns.empty:
        raise RuntimeError("Computed returns are empty after pct_change().")
    return returns

def plot_histogram(returns:pd.Series, title:str, bins:int=20)->None:
    """
    Plot a histogram of returns.
    """
    