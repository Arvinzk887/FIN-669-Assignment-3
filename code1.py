#Importing the required libraries
import pandas as pd
import matplotlib.pyplot as plt
import sys
import os
import time
from datetime import datetime
import requests


def download_historical_prices(symbols, start_date, end_date, api_key=None, adjusted=True, max_retries=3):
    """
    Download historical daily prices for the given symbols from Alpha Vantage.

    Parameters
    ----------
    symbols : list[str]
        List of ticker symbols.
    start_date : str (YYYY-MM-DD)
        Start date (inclusive).
    end_date : str (YYYY-MM-DD)
        End date (inclusive).
    api_key : str | None
        Alpha Vantage API key. If None, uses environment variable 'ALPHAVANTAGE_API_KEY'.
    adjusted : bool
        If True, uses adjusted close; otherwise uses raw close.
    max_retries : int
        Number of retries on rate limit or transient errors per symbol.
    """

    if not symbols:
        raise ValueError("No symbols provided")

    if api_key is None:
        api_key = os.getenv("ALPHAVANTAGE_API_KEY")
    if not api_key:
        raise ValueError("Alpha Vantage API key not provided. Pass api_key or set ALPHAVANTAGE_API_KEY.")

    start_dt = datetime.strptime(start_date, "%Y-%m-%d").date()
    end_dt = datetime.strptime(end_date, "%Y-%m-%d").date()

    # Return a dict mapping symbol -> list of (datetime, price) sorted ascending by date
    symbol_to_prices = {}
    for symbol in symbols:
        price_points = []
        # Prefer compact to avoid premium/full constraints; fallback from adjusted to non-adjusted,
        # and finally try non-adjusted full if still empty within the date range.
        variants = []
        if adjusted:
            variants.append(("TIME_SERIES_DAILY_ADJUSTED", "compact"))
        variants.append(("TIME_SERIES_DAILY", "compact"))
        variants.append(("TIME_SERIES_DAILY", "full"))

        for function_name, outputsize in variants:
            attempt = 0
            wait_seconds = 12
            while attempt <= max_retries:
                params = {
                    "function": function_name,
                    "symbol": symbol,
                    "outputsize": outputsize,
                    "datatype": "json",
                    "apikey": api_key,
                }
                try:
                    response = requests.get("https://www.alphavantage.co/query", params=params, timeout=30)
                except requests.RequestException as req_err:
                    attempt += 1
                    if attempt > max_retries:
                        raise RuntimeError(f"Network error for {symbol}: {req_err}")
                    time.sleep(wait_seconds)
                    wait_seconds *= 2
                    continue

                if response.status_code != 200:
                    attempt += 1
                    if attempt > max_retries:
                        raise RuntimeError(f"HTTP {response.status_code} from Alpha Vantage for {symbol}")
                    time.sleep(wait_seconds)
                    wait_seconds *= 2
                    continue

                payload = response.json()

                # Explicit premium gating: switch variant if premium endpoint message encountered
                premium_msg = None
                if isinstance(payload, dict):
                    premium_msg = payload.get("Information") or payload.get("Note")
                if premium_msg and "premium" in premium_msg.lower():
                    # Try next variant without counting as a failed attempt
                    break

                # Handle rate limit note (non-premium)
                if isinstance(payload, dict) and ("Note" in payload or "Information" in payload):
                    attempt += 1
                    if attempt > max_retries:
                        raise RuntimeError(
                            f"Rate limited or unavailable for {symbol}. {payload.get('Note') or payload.get('Information')}"
                        )
                    time.sleep(wait_seconds)
                    wait_seconds *= 2
                    continue

                # Handle error message
                if isinstance(payload, dict) and "Error Message" in payload:
                    # Try next variant
                    break

                ts = payload.get("Time Series (Daily)")
                if not ts:
                    # Try next variant
                    break

                rows = []
                price_key = "5. adjusted close" if function_name.endswith("ADJUSTED") else "4. close"
                for date_str, fields in ts.items():
                    d = datetime.strptime(date_str, "%Y-%m-%d").date()
                    if start_dt <= d <= end_dt:
                        price_val = fields.get(price_key)
                        if price_val is not None:
                            rows.append((d, float(price_val)))

                if rows:
                    rows.sort(key=lambda x: x[0])
                    price_points = [(datetime.fromordinal(d.toordinal()), v) for d, v in rows]
                else:
                    price_points = []
                # Completed with this variant
                break

            # If we obtained any points, stop trying more variants
            if price_points:
                break

        symbol_to_prices[symbol] = price_points

    return symbol_to_prices

def compute_daily_returns(price_series):
    """
    Percent change for daily returns from a price series or a list of prices.
    """
    # Accept either pandas Series (of prices) or a plain list/sequence of floats
    try:
        import pandas as _pd  # local import to avoid global dependency at runtime
        if isinstance(price_series, _pd.Series):
            if price_series.empty:
                raise ValueError("'price_series' is empty.")
            returns = price_series.pct_change().dropna()
            if returns.empty:
                raise RuntimeError("Computed returns are empty after pct_change().")
            return returns
    except Exception:
        # If pandas is not usable, fall back to sequence handling below
        pass

    seq = list(price_series)
    if len(seq) < 2:
        raise ValueError("Not enough price points to compute returns.")
    returns_list = []
    prev = seq[0]
    for current in seq[1:]:
        if prev == 0:
            raise ZeroDivisionError("Encountered zero price while computing returns.")
        returns_list.append((current / prev) - 1.0)
        prev = current
    return returns_list

def plot_histogram(returns, title:str, bins:int=20)->None:
    """
    Plot a histogram of returns (accepts pandas Series or a sequence of floats).
    """
    # Determine emptiness and prepare data
    data = None
    try:
        import pandas as _pd
        if isinstance(returns, _pd.Series):
            if returns.empty:
                raise ValueError("'returns' is empty; nothing to plot.")
            data = returns.values.tolist()
    except Exception:
        pass
    if data is None:
        data = list(returns)
        if len(data) == 0:
            raise ValueError("'returns' is empty; nothing to plot.")

    plt.figure()
    plt.hist(data, bins=bins)
    plt.title(title)
    plt.xlabel("Daily Return")
    plt.ylabel("Frequency")
    plt.tight_layout()
    plt.show()

def main()->None:
    #===Config---
    symbols=['INTC', 'NVDA']
    start_date='2024-01-01'
    end_date='2024-12-31'
    focus_symbol='INTC' #Which symbol to focus on
    api_key='Enter_Your_API_Key_Here' # Alpha Vantage API key

    #===Download Data---
    prices = download_historical_prices(symbols, start_date, end_date, api_key=api_key, adjusted=True)
    print("Sample of downloaded prices:")
    for sym in symbols:
        pts = prices.get(sym, [])[:5]
        preview = ", ".join([f"{dt.date()}={val:.2f}" for dt, val in pts]) if pts else "<no data>"
        print(f"  {sym}: {preview}")
    if not any(prices.get(sym) for sym in symbols):
        print("No price data fetched within the specified date range.", file=sys.stderr)
        sys.exit(1)

    #===Compute Daily Returns for the focus symbol---
    if focus_symbol not in prices or len(prices[focus_symbol]) == 0:
        raise KeyError(
            f"No data available for '{focus_symbol}'. Available with data: {[s for s in symbols if prices.get(s)]}"
        )

    #===Compute Daily Returns for the focus symbol---
    focus_prices = [p for _, p in prices[focus_symbol]]
    if len(focus_prices) == 0:
        print(f"No price data available for {focus_symbol} in the specified date range.", file=sys.stderr)
        sys.exit(1)
    daily_returns = compute_daily_returns(focus_prices)
    print("Sample of daily returns:")
    try:
        import pandas as _pd
        if isinstance(daily_returns, _pd.Series):
            print(daily_returns.head().to_string())
        else:
            preview = ", ".join([f"{r:.4f}" for r in list(daily_returns)[:5]])
            print(preview)
    except Exception:
        preview = ", ".join([f"{r:.4f}" for r in list(daily_returns)[:5]])
        print(preview)
    plot_histogram(
        daily_returns,
        title=f"{focus_symbol} Daily Returns Histogram",
        bins=20,
    )

if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        #Fail loudly with a helpful message.
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)