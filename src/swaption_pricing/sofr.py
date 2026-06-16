"""SOFR ingestion helpers for public market-data workflows."""

from __future__ import annotations

import csv
import json
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import Request, urlopen

import pandas as pd

from .types import MarketQuote, SofrObservation

FRED_SOFR_CSV_URL = "https://fred.stlouisfed.org/graph/fredgraph.csv"


def build_fred_sofr_csv_url(*, cosd: str | None = None, coed: str | None = None) -> str:
    """Return the public FRED CSV URL for the SOFR series."""
    query = {"id": "SOFR"}
    if cosd:
        query["cosd"] = cosd
    if coed:
        query["coed"] = coed
    return f"{FRED_SOFR_CSV_URL}?{urlencode(query)}"


def download_sofr_history_csv(
    output_path: str | Path,
    *,
    cosd: str | None = None,
    coed: str | None = None,
) -> Path:
    """Download SOFR history from FRED into a local CSV file."""
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    url = build_fred_sofr_csv_url(cosd=cosd, coed=coed)
    request = Request(url, headers={"User-Agent": "swaption-pricing-sofr-downloader/0.1"})
    with urlopen(request) as response:  # noqa: S310 - official public data source
        output.write_bytes(response.read())
    return output


def load_sofr_history_csv(path: str | Path) -> list[SofrObservation]:
    """Load a FRED-style SOFR CSV with DATE,SOFR columns."""
    rows: list[SofrObservation] = []
    with Path(path).open(newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            raw_value = row["SOFR"].strip()
            if raw_value == ".":
                continue
            rows.append(SofrObservation(date=row["DATE"], rate_percent=float(raw_value)))
    return rows


def load_sofr_history_excel(path: str | Path, *, sheet_name: str = "Results") -> list[SofrObservation]:
    """Load a New York Fed-style SOFR Excel export."""
    df = pd.read_excel(path, sheet_name=sheet_name)
    required_columns = {"Effective Date", "Rate Type", "Rate (%)"}
    missing = required_columns.difference(df.columns)
    if missing:
        raise ValueError(f"missing required SOFR Excel columns: {sorted(missing)}")

    sofr_df = df[df["Rate Type"].astype(str).str.upper() == "SOFR"].copy()
    if sofr_df.empty:
        raise ValueError("no SOFR rows found in Excel file")

    observations: list[SofrObservation] = []
    for _, row in sofr_df.iterrows():
        observations.append(
            SofrObservation(
                date=pd.to_datetime(row["Effective Date"]).strftime("%Y-%m-%d"),
                rate_percent=float(row["Rate (%)"]),
            )
        )
    observations.sort(key=lambda item: item.date)
    return observations


def write_sofr_history_csv_from_observations(
    observations: list[SofrObservation],
    output_csv: str | Path,
) -> Path:
    """Write normalized SOFR observations to a FRED-style DATE,SOFR CSV."""
    output = Path(output_csv)
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=["DATE", "SOFR"])
        writer.writeheader()
        for obs in observations:
            writer.writerow({"DATE": obs.date, "SOFR": obs.rate_percent})
    return output


def latest_sofr_observation(path: str | Path) -> SofrObservation:
    """Return the most recent valid SOFR observation in a local CSV file."""
    observations = load_sofr_history_csv(path)
    if not observations:
        raise ValueError("no valid SOFR observations found")
    return observations[-1]


def latest_sofr_observation_from_excel(path: str | Path, *, sheet_name: str = "Results") -> SofrObservation:
    """Return the most recent valid SOFR observation from a New York Fed Excel export."""
    observations = load_sofr_history_excel(path, sheet_name=sheet_name)
    return observations[-1]


def sofr_to_market_quote(
    observation: SofrObservation,
    *,
    maturity_years: float = 1.0 / 360.0,
    pay_frequency: int = 1,
) -> MarketQuote:
    """Map one SOFR fixing into a short-end deposit-style market quote."""
    return MarketQuote(
        instrument_type="deposit",
        maturity=maturity_years,
        rate=observation.rate_percent / 100.0,
        pay_frequency=pay_frequency,
    )


def write_sofr_market_quote_csv(
    source_csv: str | Path,
    output_csv: str | Path,
    *,
    maturity_years: float = 1.0 / 360.0,
    pay_frequency: int = 1,
) -> Path:
    """Write the latest SOFR fixing as a normalized market quote CSV."""
    observation = latest_sofr_observation(source_csv)
    quote = sofr_to_market_quote(
        observation,
        maturity_years=maturity_years,
        pay_frequency=pay_frequency,
    )
    output = Path(output_csv)
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=["instrument_type", "maturity", "rate", "pay_frequency"])
        writer.writeheader()
        writer.writerow(
            {
                "instrument_type": quote.instrument_type,
                "maturity": quote.maturity,
                "rate": quote.rate,
                "pay_frequency": quote.pay_frequency,
            }
        )
    return output


def write_sofr_metadata_json(
    source_csv: str | Path,
    output_json: str | Path,
    *,
    source_name: str = "FRED_SOFR",
) -> Path:
    """Write a small metadata file for the downloaded SOFR snapshot."""
    observation = latest_sofr_observation(source_csv)
    output = Path(output_json)
    output.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "source": source_name,
        "latest_date": observation.date,
        "latest_rate_percent": observation.rate_percent,
        "source_csv": str(Path(source_csv)),
    }
    output.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return output


def prepare_sofr_data_bundle(
    output_dir: str | Path,
    *,
    cosd: str | None = None,
    coed: str | None = None,
    maturity_years: float = 1.0 / 360.0,
    pay_frequency: int = 1,
) -> dict[str, Path]:
    """Download SOFR history and prepare normalized outputs in one directory."""
    output_root = Path(output_dir)
    output_root.mkdir(parents=True, exist_ok=True)
    history_csv = output_root / "sofr_history.csv"
    quote_csv = output_root / "sofr_latest_quote.csv"
    metadata_json = output_root / "sofr_metadata.json"

    download_sofr_history_csv(history_csv, cosd=cosd, coed=coed)
    write_sofr_market_quote_csv(
        history_csv,
        quote_csv,
        maturity_years=maturity_years,
        pay_frequency=pay_frequency,
    )
    write_sofr_metadata_json(history_csv, metadata_json)

    return {
        "history_csv": history_csv,
        "quote_csv": quote_csv,
        "metadata_json": metadata_json,
    }


def prepare_sofr_data_bundle_from_local_csv(
    source_csv: str | Path,
    output_dir: str | Path,
    *,
    maturity_years: float = 1.0 / 360.0,
    pay_frequency: int = 1,
) -> dict[str, Path]:
    """Prepare normalized SOFR outputs from an existing local history CSV."""
    output_root = Path(output_dir)
    output_root.mkdir(parents=True, exist_ok=True)
    source = Path(source_csv)
    history_csv = output_root / "sofr_history.csv"
    quote_csv = output_root / "sofr_latest_quote.csv"
    metadata_json = output_root / "sofr_metadata.json"

    history_csv.write_bytes(source.read_bytes())
    write_sofr_market_quote_csv(
        history_csv,
        quote_csv,
        maturity_years=maturity_years,
        pay_frequency=pay_frequency,
    )
    write_sofr_metadata_json(history_csv, metadata_json)
    return {
        "history_csv": history_csv,
        "quote_csv": quote_csv,
        "metadata_json": metadata_json,
    }


def prepare_sofr_data_bundle_from_excel(
    source_excel: str | Path,
    output_dir: str | Path,
    *,
    sheet_name: str = "Results",
    maturity_years: float = 1.0 / 360.0,
    pay_frequency: int = 1,
) -> dict[str, Path]:
    """Prepare normalized SOFR outputs from a New York Fed Excel export."""
    output_root = Path(output_dir)
    output_root.mkdir(parents=True, exist_ok=True)
    history_csv = output_root / "sofr_history.csv"
    quote_csv = output_root / "sofr_latest_quote.csv"
    metadata_json = output_root / "sofr_metadata.json"

    observations = load_sofr_history_excel(source_excel, sheet_name=sheet_name)
    write_sofr_history_csv_from_observations(observations, history_csv)
    write_sofr_market_quote_csv(
        history_csv,
        quote_csv,
        maturity_years=maturity_years,
        pay_frequency=pay_frequency,
    )
    write_sofr_metadata_json(history_csv, metadata_json, source_name="NYFED_SOFR_XLSX")
    return {
        "history_csv": history_csv,
        "quote_csv": quote_csv,
        "metadata_json": metadata_json,
    }
