# Finance Terminal

A Bloomberg-inspired personal market terminal built with **Python + Streamlit**.

Personal project to combine my finance studies (banking & financial markets) with
hands-on data/automation skills. Design benchmarked against the Bloomberg
Professional terminal (academic access at my university).

## Current modules

**MACRO — Eurozone Dashboard** (Bloomberg ECO inspired)
- ECB policy corridor (deposit facility, main refi, marginal lending) + €STR
- HICP inflation, headline vs core, against the 2% target
- BTP-Bund 10Y spread (basis points) and multi-country 10Y yields (IT/DE/FR/ES)
- KPI cards with as-of dates; range selector 1Y → MAX
- Data: ECB Data Portal REST API — free, no API key

**EQ — Company Overview** (Bloomberg DES/GIP inspired)
- Real-time quote header: last price, daily change, ranges, volume, market cap
- Interactive candlestick + volume chart (1M / 3M / 6M / YTD / 1Y / 5Y / MAX)
- Valuation ratios: P/E (TTM & FWD), P/B, P/S, EV/EBITDA, EV/Revenue, dividend yield
- Profitability & leverage: ROE, ROA, margins, Debt/Equity, current ratio, FCF
- Business profile and latest headlines

Works with any Yahoo Finance symbol, including Borsa Italiana listings
(`ISP.MI`, `ENI.MI`, `UCG.MI`, ...).

## Quickstart

Requires Python 3.10+.

```bash
git clone <this-repo>
cd finance-terminal
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```

The app opens at `http://localhost:8501`.

## Deploy (free)

1. Push this repo to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io), sign in with GitHub
3. New app → select the repo → main file `app.py` → Deploy

## Project structure

```
finance-terminal/
├── app.py                  # Entry point: config, styling, module routing
├── test_data.py            # Smoke test for the ECB data layer
├── modules/
│   ├── company.py          # EQ — Company Overview screen
│   └── macro.py            # MACRO — Eurozone Dashboard
├── utils/
│   ├── data.py             # Equity data layer (yfinance + caching)
│   ├── macro.py            # Macro data layer (ECB Data Portal)
│   └── format.py           # Number formatting helpers
├── .streamlit/config.toml  # Dark terminal theme
└── requirements.txt
```

Adding a module = one file in `modules/` exposing a `render()` function,
plus one line in the `MODULES` dict in `app.py`.

## Roadmap

- [x] MACRO — Eurozone dashboard (ECB Data Portal): rates, HICP, BTP-Bund spread
- [ ] MACRO — US side (FRED API, requires free API key): Fed funds, CPI, yield curve
- [ ] Daily BTP-Bund spread source (IRS convergence yields are monthly averages)
- [ ] WL — Watchlist with persistent storage
- [ ] SCR — Multi-criteria fundamental screener
- [ ] NEWS — Aggregated feed with AI-generated daily brief
- [ ] Peer comparison table on the company screen

## Data & limitations

Macro data from the [ECB Data Portal](https://data.ecb.europa.eu) REST API
(no key required). Run `python test_data.py` to verify all series.

Market data from Yahoo Finance via [`yfinance`](https://github.com/ranaroussi/yfinance)
(unofficial API): quotes are delayed and fundamentals may differ from primary
sources. Yahoo occasionally changes its endpoints — if data stops loading,
update the library (`pip install -U yfinance`).

**Educational project — not investment advice.**
