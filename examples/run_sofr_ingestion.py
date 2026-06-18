"""Demonstrate SOFR ingestion and quote normalization."""

from pathlib import Path

from swaption_pricing.market import latest_sofr_observation, write_sofr_market_quote_csv


def main():
    project_root = Path(__file__).resolve().parent.parent
    source_csv = project_root / "data/common/market/sofr/sofr_history.sample.csv"
    quote_csv = project_root / "data/processed/sofr_latest_quote.csv"

    observation = latest_sofr_observation(source_csv)
    write_sofr_market_quote_csv(source_csv, quote_csv)

    print("SOFR Ingestion Example")
    print(f"Source: {source_csv}")
    print(f"Latest date: {observation.date}")
    print(f"Latest SOFR (%): {observation.rate_percent:.4f}")
    print(f"Normalized quote CSV: {quote_csv}")


if __name__ == "__main__":
    main()
