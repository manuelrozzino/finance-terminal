"""Macro data layer — ECB Data Portal (https://data.ecb.europa.eu).

Free REST API, no key required. Endpoint pattern:
  https://data-api.ecb.europa.eu/service/data/{FLOW}/{KEY}?format=csvdata

Every fetch fails soft (returns an empty Series) so the UI degrades
gracefully when a single series is unavailable.
"""

import io

import pandas as pd
import requests
import streamlit as st

BASE = "https://data-api.ecb.europa.eu/service/data/{flow}/{key}"
HEADERS = {"User-Agent": "finance-terminal/0.2 (personal study project)"}

# Central registry: fixing or adding a series = one line here.
# alias: (dataflow, series key)
SERIES = {
    # --- ECB policy corridor (daily levels) ---
    "DFR":     ("FM", "B.U2.EUR.4F.KR.DFR.LEV"),      # deposit facility
    "MRO":     ("FM", "B.U2.EUR.4F.KR.MRR_FR.LEV"),   # main refi, fixed rate
    "MRO_MBR": ("FM", "B.U2.EUR.4F.KR.MRR_MBR.LEV"),  # main refi, min bid (2000-2008)
    "MLF":     ("FM", "B.U2.EUR.4F.KR.MLFR.LEV"),     # marginal lending
    "ESTR":    ("EST", "B.EU000A2X2A25.WT"),          # euro short-term rate (from 10/2019)
    # --- Inflation (monthly, values are already YoY %) ---
    "HICP":      ("ICP", "M.U2.N.000000.4.ANR"),      # headline
    "HICP_CORE": ("ICP", "M.U2.N.XEF000.4.ANR"),      # excl. energy & food
    # --- 10Y govt yields, monthly (EU convergence criterion series) ---
    "IT10": ("IRS", "M.IT.L.L40.CI.0000.EUR.N.Z"),
    "DE10": ("IRS", "M.DE.L.L40.CI.0000.EUR.N.Z"),
    "FR10": ("IRS", "M.FR.L.L40.CI.0000.EUR.N.Z"),
    "ES10": ("IRS", "M.ES.L.L40.CI.0000.EUR.N.Z"),
}


@st.cache_data(ttl=3600, show_spinner=False)
def ecb(flow: str, key: str, start: str = "1999-01") -> pd.Series:
    """Fetch one ECB series as a date-indexed float Series (empty on failure)."""
    try:
        r = requests.get(
            BASE.format(flow=flow, key=key),
            params={"format": "csvdata", "startPeriod": start},
            headers=HEADERS,
            timeout=30,
        )
        r.raise_for_status()
        df = pd.read_csv(io.StringIO(r.text))
    except Exception:
        return pd.Series(dtype=float)

    if df.empty or "TIME_PERIOD" not in df.columns or "OBS_VALUE" not in df.columns:
        return pd.Series(dtype=float)

    s = pd.Series(
        pd.to_numeric(df["OBS_VALUE"], errors="coerce").values,
        index=pd.to_datetime(df["TIME_PERIOD"], errors="coerce"),
        name=f"{flow}.{key}",
    )
    return s.dropna().sort_index()


def get(alias: str, start: str = "1999-01") -> pd.Series:
    """Fetch a series by registry alias (see SERIES)."""
    flow, key = SERIES[alias]
    return ecb(flow, key, start)


def mro_combined() -> pd.Series:
    """MRO rate continuous since 1999.

    The fixed-rate series (MRR_FR) has a hole in 2000-2008, when the ECB
    ran variable-rate tenders: patch it with the minimum bid rate series.
    """
    fr = get("MRO")
    mbr = get("MRO_MBR")
    if fr.empty:
        return mbr
    return fr.combine_first(mbr).sort_index()
