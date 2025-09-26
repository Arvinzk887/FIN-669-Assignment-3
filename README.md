# FIN 669 - Assignment 3

A small Python project for financial data analysis and visualization using Alpha Vantage market data and basic managerial accounting (break-even) analysis.

## Overview

This repository contains three scripts:

- `code1.py`: Download daily price data from Alpha Vantage for one or more symbols, compute daily returns, and plot a histogram of returns for a chosen symbol. Includes robust retry, throttle handling, and optional use of adjusted vs. unadjusted close.
- `code2.py`: Fetch and locally cache daily close prices for `INTC` and `NVDA`, compute average daily return and volatility, and plot 10-year price trends. Uses a simple CSV cache (e.g., `av_cache_INTC_daily.csv`).
- `code3.py`: Simple break-even analysis tool that asks for selling price, variable cost, and fixed cost, then computes the contribution margin, break-even in units and sales, and plots a break-even chart.

## Requirements

- Python 3.10+
- Alpha Vantage API key for `code1.py` and `code2.py`
- See `requirements.txt` for Python package dependencies

Install dependencies:

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\\Scripts\\activate
pip install -r requirements.txt
```

## Alpha Vantage API Key

- Obtain a free API key from `https://www.alphavantage.co/support/#api-key`.
- For `code1.py`, you can set the environment variable `ALPHAVANTAGE_API_KEY` or pass via the script variable.
- For `code2.py`, update the `API_KEY` constant near the top of the file.

Set an environment variable (Unix/macOS):

```bash
export ALPHAVANTAGE_API_KEY="YOUR_KEY_HERE"
```

On Windows (PowerShell):

```powershell
$Env:ALPHAVANTAGE_API_KEY = "YOUR_KEY_HERE"
```

## Data Caching

`code2.py` reads/writes CSV caches in the project root, named `av_cache_{SYMBOL}_daily.csv`. If the API is throttled or unavailable, the script falls back to cached data when found.

The repository already includes example caches:
- `av_cache_INTC_daily.csv`
- `av_cache_NVDA_daily.csv`

## Usage

### 1) `code1.py` — Returns histogram for a focus symbol

Edit the configuration at the bottom of the file if desired:
- `symbols`: list of tickers to fetch
- `start_date`, `end_date`: date range `YYYY-MM-DD`
- `focus_symbol`: symbol used for the histogram
- `api_key`: set to your Alpha Vantage key or leave `None` to use `ALPHAVANTAGE_API_KEY`

Run:

```bash
python code1.py
```

This will print sample price and return values and display a histogram of daily returns for the focus symbol.

### 2) `code2.py` — Ten-year stats and price trend for INTC vs NVDA

Confirm/update the `API_KEY` constant near the top of the script. Then run:

```bash
python code2.py
```

The script will:
- Download 10 years of data (or fall back to cache)
- Compute average daily return and volatility (stdev)
- Plot closing prices for both symbols

### 3) `code3.py` — Break-even analysis

Run the script and provide the three prompts when asked:

```bash
python code3.py
```

Inputs required:
- Selling price per unit
- Variable cost per unit
- Fixed cost per period (year)

The script will output:
- Contribution margin per unit
- Break-even point in units and in sales
- A break-even chart

## Notes and Tips

- If you receive API throttle messages, try again later or rely on cached data (`code2.py`).
- `code1.py` can use adjusted close (via the `adjusted` flag) when available.
- Matplotlib windows may need to be closed to return to the terminal.

## Troubleshooting

- Missing API key: ensure `ALPHAVANTAGE_API_KEY` is set for `code1.py` or `API_KEY` is edited in `code2.py`.
- No data downloaded: verify the symbol is valid and the date range covers trading days.
- Plot not showing: in some environments you may need to run with an interactive backend or use `%matplotlib inline` in notebooks.

## License

Educational use for FIN 669 coursework.
