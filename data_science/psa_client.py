"""
Reusable client for the PSA OpenSTAT API (Philippine Statistics Authority).

Free, public, no API key. Any PSA table can be queried by human-readable
labels instead of numeric codes, and results come back as tidy rows:
    {"geo": ..., "item": ..., "period": "2026-10", "value": 138.6}

Standard library only, so it runs anywhere Python 3.9+ is installed.

Usage examples:
    python psa_client.py browse 2M/PI/CPI/2018NEW          # list tables in a folder
    python psa_client.py meta   2M/PI/CPI/2018NEW/0012M4ACP22.px   # show dimensions
"""
from __future__ import annotations

import json
import os
import ssl
import sys
import urllib.request


def _ssl_context() -> ssl.SSLContext:
    """Verified TLS context. python.org builds on macOS ship without root
    certificates, so fall back to certifi or the OS bundle when needed."""
    ctx = ssl.create_default_context()
    if ctx.get_ca_certs():
        return ctx
    try:
        import certifi
        return ssl.create_default_context(cafile=certifi.where())
    except ImportError:
        for path in ("/etc/ssl/cert.pem", "/etc/ssl/certs/ca-certificates.crt"):
            if os.path.exists(path):
                return ssl.create_default_context(cafile=path)
    return ctx


_CTX = _ssl_context()

BASE = "https://openstat.psa.gov.ph/PXWeb/api/v1/en/DB"

# Table paths used by the Casama project (kept here so they are easy to swap).
CPI_TABLE = "2M/PI/CPI/2018NEW/0012M4ACP22.px"   # CPI by commodity, monthly, 2018-present
FIES_TABLE = "1E/IE/0071E3ATME0.px"              # 2023 family expenditure by group

MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
          "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]


def _request(path: str, body: dict | None = None) -> object:
    url = f"{BASE}/{path}"
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(
        url, data=data,
        headers={"Content-Type": "application/json", "User-Agent": "psa-client/1.0"},
    )
    with urllib.request.urlopen(req, timeout=60, context=_CTX) as resp:
        return json.loads(resp.read().decode("utf-8-sig"))


def browse(folder: str = "") -> list[dict]:
    """List sub-folders ('l') and tables ('t') inside a folder."""
    return _request(folder)


def metadata(table: str) -> dict:
    """Return the table's title and its dimensions (code -> {value code: label})."""
    meta = _request(table)
    dims = {}
    for v in meta["variables"]:
        dims[v["code"]] = dict(zip(v["values"], v["valueTexts"]))
    return {"title": meta["title"], "dims": dims}


def _match(labels: dict[str, str], wanted: list[str]) -> list[str]:
    """Map wanted labels to value codes. Matches on exact label, label prefix
    (e.g. '04.5.1' matches '04.5.1 - Electricity (ND)'), or stripped label."""
    out = []
    for w in wanted:
        hit = [c for c, t in labels.items()
               if t == w or t.strip(". ").startswith(w) or c == w]
        if not hit:
            raise KeyError(f"No value matching {w!r}. Options start with: "
                           f"{list(labels.values())[:10]}")
        out.append(hit[0])
    return out


def query(table: str, selections: dict[str, list[str]]) -> list[dict]:
    """Query a table using labels. Dimensions not listed return all values.

    Returns tidy rows: one dict per cell, with every dimension label plus 'value'.
    """
    meta = metadata(table)
    body = {"query": [], "response": {"format": "json"}}
    for dim, wanted in selections.items():
        codes = _match(meta["dims"][dim], wanted)
        body["query"].append({"code": dim, "selection": {"filter": "item", "values": codes}})
    js = _request(table, body)
    return _px_json_to_rows(js, meta["dims"])


def _px_json_to_rows(js: dict, dims: dict) -> list[dict]:
    """PX-Web native JSON -> tidy rows. (PSA's json-stat2 output is unreliable:
    it returns a single placeholder value, so we use the native format.)"""
    keys = [c["code"] for c in js["columns"] if c["type"] in ("d", "t")]
    rows = []
    for cell in js["data"]:
        row = {k: dims[k][code] for k, code in zip(keys, cell["key"])}
        raw = cell["values"][0]
        try:
            row["value"] = float(raw)
        except ValueError:   # '..', '-', '' = not available
            row["value"] = None
        rows.append(row)
    return rows


def cpi_series(geos: list[str], items: list[str]) -> list[dict]:
    """Monthly CPI as tidy rows: geo, item, period (YYYY-MM), value."""
    raw = query(CPI_TABLE, {
        "Geolocation": geos,
        "Commodity Description": items,
        "Period": MONTHS,               # excludes the annual 'Ave' column
    })
    rows = []
    for r in raw:
        if r["value"] is None:
            continue  # months not yet published
        m = MONTHS.index(r["Period"]) + 1
        rows.append({
            "geo": r["Geolocation"].strip(". "),
            "item": r["Commodity Description"],
            "period": f"{r['Year']}-{m:02d}",
            "value": float(r["value"]),
        })
    rows.sort(key=lambda r: (r["geo"], r["item"], r["period"]))
    return rows


if __name__ == "__main__":
    if len(sys.argv) >= 2 and sys.argv[1] == "browse":
        for x in browse(sys.argv[2] if len(sys.argv) > 2 else ""):
            print(f"[{x['type']}] {x['id']:<20} {x['text']}")
    elif len(sys.argv) >= 3 and sys.argv[1] == "meta":
        m = metadata(sys.argv[2])
        print(m["title"])
        for dim, vals in m["dims"].items():
            print(f"\n## {dim} ({len(vals)} values)")
            for c, t in list(vals.items())[:25]:
                print(f"  {c:>4}  {t}")
    else:
        print(__doc__)
