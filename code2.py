#Importing the required libraries
import time
import os
import requests
import pandas as pd
import matplotlib.pyplot as plt

# Alpha Vantage configuration
API_KEY = "9HYX0X3DN1Q1ZOXQ"
BASE_URL = "https://www.alphavantage.co/query"

def get_cache_path(symbol: str) -> str:
    return f"av_cache_{symbol}_daily.csv"


def load_cached_close_prices(symbol: str) -> pd.DataFrame | None:
    path = get_cache_path(symbol)
    if os.path.exists(path):
        try:
            df = pd.read_csv(path, index_col=0, parse_dates=True)
            if "Close" in df.columns:
                df.index = pd.to_datetime(df.index)
                df = df.sort_index()
                return df[["Close"]]
        except Exception:
            return None
    return None


def save_cache(symbol: str, df: pd.DataFrame) -> None:
    path = get_cache_path(symbol)
    try:
        df.to_csv(path)
    except Exception:
        pass


def fetch_alpha_vantage_daily(symbol: str) -> pd.DataFrame:
    # Try free-friendly endpoint sequence, preferring unadjusted full first
    endpoint_options = [
        {"function": "TIME_SERIES_DAILY", "outputsize": "full"},
        {"function": "TIME_SERIES_DAILY", "outputsize": "compact"},
        {"function": "TIME_SERIES_DAILY_ADJUSTED", "outputsize": "compact"},
        {"function": "TIME_SERIES_DAILY_ADJUSTED", "outputsize": "full"},
    ]

    quick_attempts = 3
    delays = [1, 2]

    for option in endpoint_options:
        params = {
            "function": option["function"],
            "symbol": symbol,
            "outputsize": option["outputsize"],
            "apikey": API_KEY,
        }
        for attempt in range(1, quick_attempts + 1):
            try:
                response = requests.get(BASE_URL, params=params, timeout=30)
                response.raise_for_status()
                data = response.json()
            except requests.RequestException as exc:
                if attempt == quick_attempts:
                    # On final network failure, try cache
                    cached = load_cached_close_prices(symbol)
                    if cached is not None:
                        return cached
                    raise RuntimeError(f"Network error fetching {symbol}: {exc}")
                time.sleep(delays[min(attempt - 1, len(delays) - 1)])
                continue

            # Handle various Alpha Vantage non-data responses
            if "Error Message" in data:
                # Symbol or function-level error; try next endpoint option
                break

            if "Note" in data or "Information" in data:
                premium_or_throttle_msg = (data.get("Note") or data.get("Information") or "").lower()
                is_premium_block = "premium" in premium_or_throttle_msg
                if is_premium_block:
                    # Immediately try next endpoint option
                    break
                # Throttle: only quick retry; on last attempt, try cache
                if attempt == quick_attempts:
                    cached = load_cached_close_prices(symbol)
                    if cached is not None:
                        return cached
                    # Move to next endpoint option
                    break
                time.sleep(delays[min(attempt - 1, len(delays) - 1)])
                continue

            time_series = data.get("Time Series (Daily)")
            if not time_series:
                if attempt == quick_attempts:
                    # Try cache, else move to next option
                    cached = load_cached_close_prices(symbol)
                    if cached is not None:
                        return cached
                    break
                time.sleep(delays[min(attempt - 1, len(delays) - 1)])
                continue

            df = pd.DataFrame.from_dict(time_series, orient="index")
            df.index = pd.to_datetime(df.index)
            df = df.sort_index()
            df = df.rename(columns={"4. close": "Close"})
            df["Close"] = df["Close"].astype(float)
            save_cache(symbol, df[["Close"]])
            return df[["Close"]]

    # If all endpoints failed, last resort is cache
    cached = load_cached_close_prices(symbol)
    if cached is not None:
        return cached
    raise RuntimeError("Failed to retrieve data from Alpha Vantage and no cache available.")

# Retrieve last 10 years of data for both INTC and NVDA
start_date = pd.Timestamp.today().normalize() - pd.DateOffset(years=10)
intc_data = fetch_alpha_vantage_daily("INTC")
nvda_data = fetch_alpha_vantage_daily("NVDA")
intc_data = intc_data[intc_data.index >= start_date]
nvda_data = nvda_data[nvda_data.index >= start_date]

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