# Finance Terminal

A Bloomberg-inspired personal market terminal built with **Python + Streamlit**.

Personal project to combine my finance studies (banking & financial markets) with
hands-on data/automation skills. Design benchmarked against the Bloomberg
Professional terminal (academic access at my university).

## Current modules

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
├── modules/
│   └── company.py          # EQ — Company Overview screen
├── utils/
│   ├── data.py             # Data layer (yfinance + caching)
│   └── format.py           # Number formatting helpers
├── .streamlit/config.toml  # Dark terminal theme
└── requirements.txt
```

Adding a module = one file in `modules/` exposing a `render()` function,
plus one line in the `MODULES` dict in `app.py`.

## Roadmap

- [ ] MACRO — Eurozone/US dashboard (ECB SDW + FRED APIs): rates, HICP, BTP-Bund spread
- [ ] WL — Watchlist with persistent storage
- [ ] SCR — Multi-criteria fundamental screener
- [ ] NEWS — Aggregated feed with AI-generated daily brief
- [ ] Peer comparison table on the company screen

## Data & limitations

Market data from Yahoo Finance via [`yfinance`](https://github.com/ranaroussi/yfinance)
(unofficial API): quotes are delayed and fundamentals may differ from primary
sources. Yahoo occasionally changes its endpoints — if data stops loading,
update the library (`pip install -U yfinance`).

**Educational project — not investment advice.**
