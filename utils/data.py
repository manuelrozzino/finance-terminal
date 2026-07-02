"""Data access layer.

All external calls (Yahoo Finance via yfinance) live here, wrapped in
Streamlit's cache so repeated lookups don't hammer the API.

Every function fails soft: on any error it returns an empty dict /
DataFrame / list, and the UI layer decides what to show.
"""

from datetime import datetime

import pandas as pd
import streamlit as st
import yfinance as yf


@st.cache_data(ttl=300, show_spinner=False)
def get_info(ticker: str) -> dict:
    """Company profile + fundamentals. Returns {} when the ticker is unknown."""
    try:
        info = yf.Ticker(ticker).info or {}
    except Exception:
        return {}
    # Yahoo returns a near-empty dict for invalid symbols: validate on name.
    if not (info.get("shortName") or info.get("longName")):
        return {}
    return info


@st.cache_data(ttl=300, show_spinner=False)
def get_history(ticker: str, period: str, interval: str) -> pd.DataFrame:
    """OHLCV price history for the chart."""
    try:
        df = yf.Ticker(ticker).history(period=period, interval=interval)
    except Exception:
        return pd.DataFrame()
    return df if df is not None else pd.DataFrame()


@st.cache_data(ttl=600, show_spinner=False)
def get_news(ticker: str, limit: int = 8) -> list:
    """Latest headlines, normalised across old/new yfinance formats.

    yfinance >= 0.2.50 nests fields under entry["content"] with an ISO
    "pubDate"; older versions are flat with a unix "providerPublishTime".
    We handle both so a library update doesn't break the module.
    """
    try:
        raw = yf.Ticker(ticker).news or []
    except Exception:
        return []

    items = []
    for entry in raw[:limit]:
        content = entry.get("content", entry)
        title = content.get("title")
        if not title:
            continue

        # URL: new format uses canonicalUrl.url, old format uses link
        url = content.get("link")
        canonical = content.get("canonicalUrl")
        if isinstance(canonical, dict):
            url = canonical.get("url") or url

        # Publisher: new format nests under provider.displayName
        provider = content.get("publisher")
        if isinstance(content.get("provider"), dict):
            provider = content["provider"].get("displayName") or provider

        # Timestamp: ISO string (new) or unix epoch (old)
        published = None
        pub_date = content.get("pubDate")
        if pub_date:
            try:
                published = datetime.fromisoformat(pub_date.replace("Z", "+00:00"))
            except (ValueError, AttributeError):
                pass
        elif entry.get("providerPublishTime"):
            try:
                published = datetime.fromtimestamp(entry["providerPublishTime"])
            except (TypeError, ValueError, OSError):
                pass

        items.append(
            {
                "title": title,
                "url": url,
                "provider": provider or "—",
                "published": published,
            }
        )
    return items
