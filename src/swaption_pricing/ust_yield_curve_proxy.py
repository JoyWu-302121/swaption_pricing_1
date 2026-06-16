"""Fetch and normalize U.S. Treasury yield-curve snapshots from ustreasuryyieldcurve.com."""

from __future__ import annotations

import csv
import json
import ssl
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from .types import CurvePoint

USTYC_SNAPSHOT_URL = "https://www.ustreasuryyieldcurve.com/api/v1/yield_curve_snapshot"

YIELD_FIELD_TO_MATURITY = {
    "yield_1m": 1.0 / 12.0,
    "yield_2m": 2.0 / 12.0,
    "yield_3m": 3.0 / 12.0,
    "yield_4m": 4.0 / 12.0,
    "yield_6m": 6.0 / 12.0,
    "yield_1y": 1.0,
    "yield_2y": 2.0,
    "yield_3y": 3.0,
    "yield_5y": 5.0,
    "yield_7y": 7.0,
    "yield_10y": 10.0,
    "yield_20y": 20.0,
    "yield_30y": 30.0,
}


def build_ust_snapshot_url(*, date: str, offset: int = 0) -> str:
    """Return the site API URL for one U.S. Treasury yield-curve snapshot."""
    return f"{USTYC_SNAPSHOT_URL}?{urlencode({'date': date, 'offset': offset})}"


def fetch_ust_yield_curve_snapshot(*, date: str, offset: int = 0) -> dict:
    """Fetch one U.S. Treasury yield-curve snapshot from the public API.

    The site currently requires an SSL workaround in this environment, so the request
    uses an unverified SSL context for this public read-only endpoint.
    """
    url = build_ust_snapshot_url(date=date, offset=offset)
    request = Request(url, headers={"User-Agent": "swaption-pricing-ust-proxy-fetcher/0.1"})
    ssl_context = ssl._create_unverified_context()
    with urlopen(request, context=ssl_context, timeout=20) as response:  # noqa: S310
        payload = json.loads(response.read().decode("utf-8"))
    if not payload:
        raise ValueError("empty yield-curve snapshot response")
    return payload[0]


def snapshot_to_curve_points(snapshot: dict) -> list[CurvePoint]:
    """Convert one API snapshot into normalized curve points."""
    points: list[CurvePoint] = []
    for field, maturity in YIELD_FIELD_TO_MATURITY.items():
        value = snapshot.get(field)
        if value is None:
            continue
        points.append(CurvePoint(maturity=maturity, zero_rate=float(value) / 100.0))
    return points


def write_curve_points_csv(points: list[CurvePoint], output_csv: str | Path) -> Path:
    """Write normalized curve points to the project's curve_points CSV format."""
    output = Path(output_csv)
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=["maturity", "zero_rate"])
        writer.writeheader()
        for point in points:
            writer.writerow({"maturity": point.maturity, "zero_rate": point.zero_rate})
    return output


def write_snapshot_metadata(snapshot: dict, output_json: str | Path) -> Path:
    """Write a small metadata file for the fetched Treasury snapshot."""
    output = Path(output_json)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(snapshot, indent=2), encoding="utf-8")
    return output


def prepare_ust_yield_curve_proxy_bundle(
    *,
    date: str,
    output_dir: str | Path,
    offset: int = 0,
) -> dict[str, Path]:
    """Fetch and normalize one Treasury yield-curve snapshot into project files."""
    output_root = Path(output_dir)
    output_root.mkdir(parents=True, exist_ok=True)
    snapshot = fetch_ust_yield_curve_snapshot(date=date, offset=offset)
    points = snapshot_to_curve_points(snapshot)

    curve_csv = write_curve_points_csv(points, output_root / "curve_points.csv")
    metadata_json = write_snapshot_metadata(snapshot, output_root / "ust_yield_curve_snapshot.json")

    return {
        "curve_csv": curve_csv,
        "metadata_json": metadata_json,
    }
