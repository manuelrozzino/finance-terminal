"""MACRO — Eurozone Dashboard.

ECB policy corridor + €STR, HICP inflation vs the 2% target, the
BTP-Bund spread and multi-country 10Y sovereign yields.
Data: ECB Data Portal (free, no API key). See utils/macro.py.
"""

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from utils import macro

# chart palette
AMBER = "#FF9900"
WHITE = "#E6EDF3"
BLUE = "#58A6FF"
GREEN = "#00E676"
RED = "#FF5252"
VIOLET = "#C792EA"
GREY = "#8B949E"
GRID = "#1E242E"

PERIODS = {"1Y": 1, "3Y": 3, "5Y": 5, "10Y": 10, "MAX": None}

# module-scoped styling (KPI cards)
CSS = """
<style>
.kpi { border: 1px solid #1E242E; border-left: 3px solid #FF9900;
       background: #10151D; padding: 8px 12px; margin-bottom: 10px; }
.kpi-label { color: #FF9900; font-size: 0.63rem; text-transform: uppercase;
             letter-spacing: .06em; white-space: nowrap; }
.kpi-value { color: #E6EDF3; font-size: 1.3rem; font-weight: 700; line-height: 1.25; }
.kpi-sub   { color: #8B949E; font-size: 0.63rem; }
</style>
"""


# ------------------------------------------------------------------ UI helpers
def kpi(label: str, value: str, sub: str = "") -> None:
    st.markdown(
        f'<div class="kpi"><div class="kpi-label">{label}</div>'
        f'<div class="kpi-value">{value}</div>'
        f'<div class="kpi-sub">{sub}</div></div>',
        unsafe_allow_html=True,
    )


def section(title: str) -> None:
    st.markdown(f'<div class="section-title">{title}</div>', unsafe_allow_html=True)


def last_of(s: pd.Series, decimals: int = 2, suffix: str = "%"):
    """(formatted last value, as-of label) — ('—', 'no data') when empty."""
    if s.empty:
        return "—", "no data"
    date = s.index[-1]
    monthly = len(s) > 1 and (s.index[-1] - s.index[-2]).days > 20
    asof = date.strftime("%b %Y") if monthly else date.strftime("%d %b %Y")
    return f"{s.iloc[-1]:.{decimals}f}{suffix}", f"as of {asof}"


def trim(s: pd.Series, years) -> pd.Series:
    """Keep only the last N years (None = full history)."""
    if years is None or s.empty:
        return s
    return s[s.index >= s.index.max() - pd.DateOffset(years=years)]


def line_fig(lines, height=310, hline=None, hline_text="", ysuffix="%"):
    """Terminal-styled multi-line chart. lines: [(label, Series, color), ...]"""
    fig = go.Figure()
    for label, s, color in lines:
        if s.empty:
            continue
        fig.add_trace(
            go.Scatter(
                x=s.index, y=s.values, name=label, mode="lines",
                line=dict(color=color, width=1.6),
            )
        )
    if hline is not None:
        fig.add_hline(
            y=hline, line_dash="dash", line_color=GREY, opacity=0.7,
            annotation_text=hline_text,
            annotation_font=dict(color=GREY, size=10),
        )
    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        height=height,
        margin=dict(l=0, r=0, t=8, b=0),
        legend=dict(orientation="h", y=1.12, x=0, font=dict(size=10)),
        font=dict(family="IBM Plex Mono, monospace", size=11),
        hovermode="x unified",
    )
    fig.update_xaxes(gridcolor=GRID)
    fig.update_yaxes(gridcolor=GRID, ticksuffix=ysuffix)
    return fig


# ---------------------------------------------------------------------- render
def render() -> None:
    st.markdown(CSS, unsafe_allow_html=True)
    st.markdown(
        "### Eurozone Macro <span class='muted'>· ECB Data Portal</span>",
        unsafe_allow_html=True,
    )

    with st.spinner("Loading ECB data (first load ~10s, then cached for 1h)..."):
        dfr = macro.get("DFR")
        mro = macro.mro_combined()
        mlf = macro.get("MLF")
        estr = macro.get("ESTR", start="2019-10")
        hicp = macro.get("HICP")
        core = macro.get("HICP_CORE")
        it10 = macro.get("IT10")
        de10 = macro.get("DE10")
        fr10 = macro.get("FR10")
        es10 = macro.get("ES10")

    # BTP-Bund spread in basis points (monthly, IT minus DE)
    spread = ((it10 - de10) * 100).dropna()

    failed = [
        name
        for name, s in [
            ("DFR", dfr), ("MRO", mro), ("MLF", mlf), ("ESTR", estr),
            ("HICP", hicp), ("HICP_CORE", core),
            ("IT10", it10), ("DE10", de10), ("FR10", fr10), ("ES10", es10),
        ]
        if s.empty
    ]
    if failed:
        st.warning(
            "Series unavailable: " + ", ".join(failed)
            + " — run `python test_data.py` for diagnostics."
        )

    # ------------------------------------------------------------- KPI cards
    r1 = st.columns(4)
    with r1[0]:
        v, a = last_of(dfr)
        kpi("ECB DEPOSIT FACILITY", v, a)
    with r1[1]:
        v, a = last_of(mro)
        kpi("ECB MAIN REFI", v, a)
    with r1[2]:
        v, a = last_of(mlf)
        kpi("ECB MARGINAL LENDING", v, a)
    with r1[3]:
        v, a = last_of(estr, decimals=3)
        kpi("€STR", v, a)

    r2 = st.columns(4)
    with r2[0]:
        v, a = last_of(hicp)
        kpi("HICP YOY", v, a)
    with r2[1]:
        v, a = last_of(core)
        kpi("HICP CORE YOY", v, a)
    with r2[2]:
        v, a = last_of(spread, decimals=0, suffix=" bp")
        kpi("BTP-BUND 10Y", v, a)
    with r2[3]:
        v, a = last_of(it10)
        kpi("BTP 10Y YIELD", v, a)

    # -------------------------------------------------------- period selector
    sel = st.segmented_control(
        "Range", list(PERIODS), default="10Y", label_visibility="collapsed"
    )
    yrs = PERIODS[sel or "10Y"]

    # ------------------------------------------------------------ charts 2x2
    a1, a2 = st.columns(2)
    with a1:
        section("ECB POLICY CORRIDOR & €STR")
        st.plotly_chart(
            line_fig([
                ("Marginal lending", trim(mlf, yrs), WHITE),
                ("Main refi", trim(mro, yrs), AMBER),
                ("Deposit facility", trim(dfr, yrs), BLUE),
                ("€STR", trim(estr, yrs), GREEN),
            ]),
            use_container_width=True,
        )
    with a2:
        section("HICP INFLATION (YOY)")
        st.plotly_chart(
            line_fig(
                [
                    ("Headline", trim(hicp, yrs), AMBER),
                    ("Core (ex energy & food)", trim(core, yrs), BLUE),
                ],
                hline=2.0,
                hline_text="ECB target 2%",
            ),
            use_container_width=True,
        )

    b1, b2 = st.columns(2)
    with b1:
        section("BTP-BUND 10Y SPREAD")
        sp = trim(spread, yrs)
        fig = line_fig([("IT - DE spread", sp, RED)], ysuffix=" bp")
        if not sp.empty:
            fig.update_traces(fill="tozeroy", fillcolor="rgba(255,82,82,0.08)")
        st.plotly_chart(fig, use_container_width=True)
    with b2:
        section("GOVT 10Y YIELDS")
        st.plotly_chart(
            line_fig([
                ("Italy", trim(it10, yrs), GREEN),
                ("Germany", trim(de10, yrs), WHITE),
                ("France", trim(fr10, yrs), BLUE),
                ("Spain", trim(es10, yrs), VIOLET),
            ]),
            use_container_width=True,
        )

    st.markdown(
        "<span class='muted'>Sources: ECB Data Portal — policy rates (FM), "
        "€STR (EST), HICP (ICP), 10Y convergence yields (IRS, monthly averages). "
        "Spread computed as IT minus DE, in basis points.</span>",
        unsafe_allow_html=True,
    )
