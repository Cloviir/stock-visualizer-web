"""Requests stock data from the Alpha Vantage API."""
import os
import time

import requests

BASE_URL = "https://www.alphavantage.co/query"


class StockAPIError(Exception):
    pass


def get_api_key():
    key = os.getenv("ALPHA_VANTAGE_API_KEY")
    if not key:
        try:
            from dotenv import load_dotenv
            load_dotenv(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env"))
            key = os.getenv("ALPHA_VANTAGE_API_KEY")
        except ImportError:
            pass
    if not key:
        raise StockAPIError("No API key found. Set ALPHA_VANTAGE_API_KEY in your .env file.")
    return key


def _request(params):
    try:
        response = requests.get(BASE_URL, params=params, timeout=15)
        response.raise_for_status()
        return response.json()
    except (requests.RequestException, ValueError) as e:
        raise StockAPIError(f"Could not reach Alpha Vantage: {e}")


def _has_series(data):
    return any(k != "Meta Data" and isinstance(v, dict) for k, v in data.items())


def fetch_stock_data(symbol, function):
    params = {"function": function, "symbol": symbol, "apikey": get_api_key()}
    if function == "TIME_SERIES_INTRADAY":
        params["interval"] = "60min"

    data = _request(params)

    # Free keys can't use outputsize=full on some endpoints; wait, then retry with compact.
    info = data.get("Information", "")
    if "outputsize" in params and ("outputsize" in info.lower() or "premium" in info.lower()) and not _has_series(data):
        time.sleep(1.5)
        params["outputsize"] = "compact"
        data = _request(params)

    if "Error Message" in data:
        raise StockAPIError(f"Alpha Vantage has no data for symbol {symbol}.")
    if "Note" in data or ("Information" in data and not _has_series(data)):
        raise StockAPIError("API limit reached or request not allowed: "
                            + data.get("Note", data.get("Information", "")))
    if not _has_series(data):
        raise StockAPIError("Unexpected response from Alpha Vantage.")
    return data
