"""EQ — Company Overview.

Single-security screen (Bloomberg DES/GIP inspired):
price header -> candlestick + volume chart -> valuation and
profitability ratios -> business profile -> latest headlines.
"""

import plotly.graph_objects as go
import streamlit as st
from plotly.subplots import make_subplots

from utils import data
from utils.format import DOWN, UP, chg_color, fmt_big, fmt_num, fmt_pct

# period label -> (yfinance period, bar interval)
PERIODS = {
    "1M": ("1mo", "1d"),
    "3M": ("3mo", "1d"),
    "6M": ("6mo", "1d"),
    "YTD": ("ytd", "1d"),
    "1Y": ("1y", "1d"),
    "5Y": ("5y", "1wk"),
    "MAX": ("max", "1mo"),
}

GRID = "#1E242E"


# ------------------------------------------------------------------ UI helpers
def kv(label: str, value: str) -> None:
    """Dense key/value row (styled via global CSS in app.py)."""
    st.markdown(
        f'<div class="kv"><span class="kv-label">{label}</span>'
        f'<span class="kv-value">{value}</span></div>',
        unsafe_allow_html=True,
    )


def section(title: str) -> None:
    st.markdown(f'<div class="section-title">{title}</div>', unsafe_allow_html=True)


# ---------------------------------------------------------------------- render
def render() -> None:
    # ------------------------------------------------------------ ticker input
    left, right = st.columns([2, 5])
    with left:
        ticker = (
            st.text_input(
                "TICKER",
                value="AAPL",
                help="Yahoo Finance symbols — e.g. AAPL, ISP.MI, ENI.MI, ASML.AS",
            )
            .strip()
            .upper()
        )

    if not ticker:
        st.info("Enter a ticker to load the company screen.")
        return

    info = data.get_info(ticker)
    if not info:
        st.error(
            f'No data found for "{ticker}". Check the symbol '
            "(Milan listings need the .MI suffix, e.g. ISP.MI, ENI.MI)."
        )
        return

    currency = info.get("currency", "")

    # ------------------------------------------------------------------ header
    name = info.get("longName") or info.get("shortName")
    exchange = info.get("fullExchangeName") or info.get("exchange", "")
    with right:
        st.markdown(
            f"### {name} <span class='muted'>{ticker} · {exchange}</span>",
            unsafe_allow_html=True,
        )
        st.markdown(
            f"<span class='muted'>{info.get('sector', '—')} · "
            f"{info.get('industry', '—')}</span>",
            unsafe_allow_html=True,
        )

    # ------------------------------------------------------------- price block
    last = info.get("currentPrice") or info.get("regularMarketPrice")
    prev = info.get("previousClose") or info.get("regularMarketPreviousClose")

    chg = chg_pct = None
    if last is not None and prev:
        chg = last - prev
        chg_pct = chg / prev * 100

    c1, c2, c3, c4, c5 = st.columns(5)
    with c1:
        color = chg_color(chg if chg is not None else 0)
        arrow = "" if chg is None else ("▲" if chg >= 0 else "▼")
        st.markdown(
            f"<div class='px-last' style='color:{color}'>{fmt_num(last)} "
            f"<span class='muted'>{currency}</span></div>"
            f"<div class='px-chg' style='color:{color}'>{arrow} {fmt_num(chg)} "
            f"({fmt_num(chg_pct)}%)</div>",
            unsafe_allow_html=True,
        )
    with c2:
        kv("OPEN", fmt_num(info.get("open") or info.get("regularMarketOpen")))
        kv("PREV CLOSE", fmt_num(prev))
    with c3:
        kv(
            "DAY RANGE",
            f"{fmt_num(info.get('dayLow'))} – {fmt_num(info.get('dayHigh'))}",
        )
        kv(
            "52W RANGE",
            f"{fmt_num(info.get('fiftyTwoWeekLow'))} – "
            f"{fmt_num(info.get('fiftyTwoWeekHigh'))}",
        )
    with c4:
        kv("VOLUME", fmt_big(info.get("volume") or info.get("regularMarketVolume")))
        kv("AVG VOL 3M", fmt_big(info.get("averageVolume")))
    with c5:
        kv("MKT CAP", fmt_big(info.get("marketCap")))
        kv("BETA", fmt_num(info.get("beta")))

    # ------------------------------------------------------------- price chart
    section("PRICE CHART")
    sel = st.segmented_control(
        "Period", list(PERIODS), default="6M", label_visibility="collapsed"
    )
    period, interval = PERIODS[sel or "6M"]

    hist = data.get_history(ticker, period, interval)
    if hist.empty:
        st.warning("No price history available for this period.")
    else:
        fig = make_subplots(
            rows=2,
            cols=1,
            shared_xaxes=True,
            row_heights=[0.78, 0.22],
            vertical_spacing=0.03,
        )
        fig.add_trace(
            go.Candlestick(
                x=hist.index,
                open=hist["Open"],
                high=hist["High"],
                low=hist["Low"],
                close=hist["Close"],
                increasing_line_color=UP,
                decreasing_line_color=DOWN,
                increasing_fillcolor=UP,
                decreasing_fillcolor=DOWN,
                name="OHLC",
            ),
            row=1,
            col=1,
        )
        vol_colors = [
            UP if c >= o else DOWN for o, c in zip(hist["Open"], hist["Close"])
        ]
        fig.add_trace(
            go.Bar(
                x=hist.index,
                y=hist["Volume"],
                marker_color=vol_colors,
                opacity=0.55,
                name="Volume",
            ),
            row=2,
            col=1,
        )
        fig.update_layout(
            template="plotly_dark",
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            margin=dict(l=0, r=0, t=10, b=0),
            height=460,
            showlegend=False,
            xaxis_rangeslider_visible=False,
            font=dict(family="IBM Plex Mono, monospace", size=11),
            hovermode="x unified",
        )
        fig.update_xaxes(gridcolor=GRID)
        fig.update_yaxes(gridcolor=GRID)
        st.plotly_chart(fig, use_container_width=True)

    # ------------------------------------------------------------------ ratios
    col_val, col_prof = st.columns(2)
    with col_val:
        section("VALUATION")
        kv("P/E (TTM)", fmt_num(info.get("trailingPE")))
        kv("P/E (FWD)", fmt_num(info.get("forwardPE")))
        kv("P/B", fmt_num(info.get("priceToBook")))
        kv("P/S (TTM)", fmt_num(info.get("priceToSalesTrailing12Months")))
        kv("EV/EBITDA", fmt_num(info.get("enterpriseToEbitda")))
        kv("EV/REVENUE", fmt_num(info.get("enterpriseToRevenue")))
        # NB: recent yfinance versions return dividendYield already in percent
        kv("DIV YIELD", fmt_pct(info.get("dividendYield"), is_fraction=False))
        kv("PAYOUT RATIO", fmt_pct(info.get("payoutRatio")))
    with col_prof:
        section("PROFITABILITY & LEVERAGE")
        kv("ROE", fmt_pct(info.get("returnOnEquity")))
        kv("ROA", fmt_pct(info.get("returnOnAssets")))
        kv("GROSS MARGIN", fmt_pct(info.get("grossMargins")))
        kv("OPERATING MARGIN", fmt_pct(info.get("operatingMargins")))
        kv("NET MARGIN", fmt_pct(info.get("profitMargins")))
        # yfinance returns debtToEquity in percent (e.g. 154.3) -> convert to x
        dte = info.get("debtToEquity")
        kv("DEBT/EQUITY", fmt_num(dte / 100, suffix="x") if dte is not None else "—")
        kv("CURRENT RATIO", fmt_num(info.get("currentRatio")))
        kv("FCF (TTM)", fmt_big(info.get("freeCashflow")))

    # ----------------------------------------------------------------- profile
    if info.get("longBusinessSummary"):
        with st.expander("COMPANY PROFILE"):
            st.write(info["longBusinessSummary"])
            m1, m2, m3 = st.columns(3)
            with m1:
                kv("EMPLOYEES", fmt_big(info.get("fullTimeEmployees")))
            with m2:
                kv("COUNTRY", info.get("country") or "—")
            with m3:
                kv("WEBSITE", info.get("website") or "—")

    # -------------------------------------------------------------------- news
    section("LATEST NEWS")
    news = data.get_news(ticker)
    if not news:
        st.markdown(
            '<span class="muted">No recent headlines.</span>', unsafe_allow_html=True
        )
    for n in news:
        title = n["title"]
        url = n["url"]
        provider = n["provider"]
        when = n["published"].strftime("%Y-%m-%d %H:%M") if n["published"] else ""
        title_html = f'<a href="{url}" target="_blank">{title}</a>' if url else title
        st.markdown(
            f'<div class="news-item">{title_html}<br>'
            f'<span class="news-meta">{provider} · {when}</span></div>',
            unsafe_allow_html=True,
        )
