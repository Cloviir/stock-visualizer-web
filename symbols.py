"""Loads stock symbols from stocks.csv to populate the form's dropdown."""
import csv
import os

CSV_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "stocks.csv")


def load_symbols(path=CSV_PATH):
    """Returns a sorted list of symbols from the CSV's 'Symbol' column
    (or the first column if no header named Symbol exists)."""
    if not os.path.exists(path):
        print(f"Warning: {path} not found. The symbol dropdown will be empty.")
        return []

    with open(path, newline="", encoding="utf-8-sig") as f:
        rows = list(csv.reader(f))
    if not rows:
        return []

    header = [h.strip().lower() for h in rows[0]]
    if "symbol" in header:
        col, data = header.index("symbol"), rows[1:]
    elif "ticker" in header:
        col, data = header.index("ticker"), rows[1:]
    else:
        col, data = 0, rows

    symbols = {row[col].strip().upper() for row in data if len(row) > col and row[col].strip()}
    return sorted(symbols)
