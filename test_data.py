"""Smoke test for the ECB data layer.

Run it before launching the app (with the venv active):

    python test_data.py

Prints PASS/FAIL for every series in the registry, so a wrong series
key or a network problem is obvious in seconds. No Streamlit needed.
"""

import io
import sys

import pandas as pd
import requests

from utils.macro import BASE, HEADERS, SERIES

# some series need a specific start (MRO_MBR ended in 2008, ESTR began 10/2019)
START = {"MRO_MBR": "2000-01", "ESTR": "2019-10"}
DEFAULT_START = "2015-01"


def fetch(flow: str, key: str, start: str):
    r = requests.get(
        BASE.format(flow=flow, key=key),
        params={"format": "csvdata", "startPeriod": start},
        headers=HEADERS,
        timeout=30,
    )
    r.raise_for_status()
    df = pd.read_csv(io.StringIO(r.text))
    d = df[["TIME_PERIOD", "OBS_VALUE"]].dropna()
    if d.empty:
        raise ValueError("empty result")
    return d.iloc[-1, 0], d.iloc[-1, 1], len(d)


def main() -> None:
    print("Testing ECB Data Portal series...\n")
    failures = 0
    for alias, (flow, key) in SERIES.items():
        try:
            date, value, n = fetch(flow, key, START.get(alias, DEFAULT_START))
            print(f"  PASS  {alias:10s} last={date} -> {value}  ({n} obs)")
        except Exception as e:
            failures += 1
            print(f"  FAIL  {alias:10s} {type(e).__name__}: {str(e)[:70]}")

    print()
    if failures:
        print(f"{failures} series failed — paste this whole output to Claude to fix.")
        sys.exit(1)
    print("All series OK — you're good to go: streamlit run app.py")


if __name__ == "__main__":
    main()
