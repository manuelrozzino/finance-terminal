"""
Finance Terminal — MVP
A Bloomberg-inspired personal market terminal built with Streamlit.

Entry point: page configuration, global terminal styling, module routing.
New modules are added to the MODULES dict below.
"""

import streamlit as st

from modules import company, macro

# ------------------------------------------------------------------ page setup
st.set_page_config(
    page_title="Finance Terminal",
    page_icon="▮",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ------------------------------------------------------------- global styling
# Terminal look: IBM Plex Mono everywhere, dense key/value grids,
# amber section rules. Colors match .streamlit/config.toml.
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500;600;700&display=swap');

    html, body, [class*="st-"], [data-testid="stSidebar"] {
        font-family: 'IBM Plex Mono', Consolas, Menlo, monospace !important;
    }

    /* tighter vertical rhythm than Streamlit defaults */
    .block-container { padding-top: 1.2rem; padding-bottom: 2rem; }

    /* dense key/value row used across modules */
    .kv {
        display: flex;
        justify-content: space-between;
        align-items: baseline;
        gap: 12px;
        border-bottom: 1px solid #1E242E;
        padding: 3px 0;
        font-size: 0.83rem;
    }
    .kv-label {
        color: #FF9900;
        text-transform: uppercase;
        letter-spacing: .04em;
        font-size: 0.68rem;
        white-space: nowrap;
    }
    .kv-value {
        color: #E6EDF3;
        font-weight: 600;
        text-align: right;
    }

    /* amber section headers */
    .section-title {
        color: #FF9900;
        font-size: 0.78rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: .08em;
        border-bottom: 2px solid #FF9900;
        padding-bottom: 2px;
        margin: 16px 0 8px 0;
    }

    /* big price header */
    .px-last { font-size: 2.4rem; font-weight: 700; line-height: 1.05; }
    .px-chg  { font-size: 1.05rem; font-weight: 600; }
    .muted   { color: #8B949E; font-size: 0.75rem; }

    /* news list */
    .news-item { padding: 6px 0; border-bottom: 1px solid #1E242E; font-size: 0.85rem; }
    .news-meta { color: #8B949E; font-size: 0.70rem; }
    a { color: #58A6FF !important; text-decoration: none; }
    a:hover { text-decoration: underline; }
    </style>
    """,
    unsafe_allow_html=True,
)

# ------------------------------------------------------------------ navigation
# Register modules here. Each entry maps a sidebar label to a render function.
MODULES = {
    "EQ — Company Overview": company.render,
    "MACRO — Eurozone Dashboard": macro.render,
    # Roadmap — future modules plug in here:
    # "WL — Watchlist": watchlist.render,
    # "SCR — Screener": screener.render,
}

with st.sidebar:
    st.markdown("## ▮ TERMINAL")
    st.caption("personal market terminal — MVP v0.1")
    choice = st.radio("MODULES", list(MODULES.keys()))
    st.divider()
    st.markdown(
        '<span class="muted">Data: Yahoo Finance (delayed).<br>'
        "Educational project — not investment advice.</span>",
        unsafe_allow_html=True,
    )

# Render the selected module
MODULES[choice]()
