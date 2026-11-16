"""Stock Data Visualizer - Flask web app."""
from datetime import datetime

from flask import Flask, render_template, request

import api_client
import data_processor
import chart_generator
from symbols import load_symbols

app = Flask(__name__)

CHART_TYPES = {"1": "Bar", "2": "Line"}
TIME_SERIES = {
    "1": ("TIME_SERIES_INTRADAY", "Intraday"),
    "2": ("TIME_SERIES_DAILY", "Daily"),
    "3": ("TIME_SERIES_WEEKLY", "Weekly"),
    "4": ("TIME_SERIES_MONTHLY", "Monthly"),
}

SYMBOLS = load_symbols()


def _parse_date(value):
    try:
        return datetime.strptime(value, "%Y-%m-%d").date()
    except (TypeError, ValueError):
        return None


def validate(form):
    """Checks every field. Returns (cleaned values, list of error messages)."""
    errors = []

    symbol = form.get("symbol", "").strip().upper()
    if not symbol:
        errors.append("Please select a stock symbol.")
    elif symbol not in SYMBOLS:
        errors.append(f"'{symbol}' is not a valid stock symbol.")

    chart_type = form.get("chart_type", "")
    if chart_type not in CHART_TYPES:
        errors.append("Please select a chart type.")

    time_series = form.get("time_series", "")
    if time_series not in TIME_SERIES:
        errors.append("Please select a time series.")

    start_raw = form.get("start_date", "").strip()
    start = _parse_date(start_raw)
    if not start_raw:
        errors.append("Please enter a start date.")
    elif start is None:
        errors.append("Start date must be a valid date in YYYY-MM-DD format.")

    end_raw = form.get("end_date", "").strip()
    end = _parse_date(end_raw)
    if not end_raw:
        errors.append("Please enter an end date.")
    elif end is None:
        errors.append("End date must be a valid date in YYYY-MM-DD format.")

    if start and end and end < start:
        errors.append("End date cannot be before the start date.")

    values = {
        "symbol": symbol,
        "chart_type": chart_type,
        "time_series": time_series,
        "start_date": start_raw,
        "end_date": end_raw,
    }
    return values, errors, start, end


@app.route("/", methods=["GET", "POST"])
def index():
    context = {
        "symbols": SYMBOLS,
        "chart_types": CHART_TYPES,
        "time_series": {k: label for k, (_, label) in TIME_SERIES.items()},
        "values": {},
        "errors": [],
        "chart": None,
    }

    if request.method == "POST":
        values, errors, start, end = validate(request.form)
        context["values"] = values
        context["errors"] = errors

        if not errors:
            function = TIME_SERIES[values["time_series"]][0]
            try:
                data = api_client.fetch_stock_data(values["symbol"], function)
                series = data_processor.extract_series(data)
                filtered = data_processor.filter_by_date(series, start, end)
                if not filtered:
                    context["errors"].append(
                        "No data found for that date range. Try a different range or time series."
                    )
                else:
                    dates, chart_series = data_processor.to_chart_data(filtered)
                    context["chart"] = chart_generator.generate_chart(
                        values["symbol"], CHART_TYPES[values["chart_type"]],
                        dates, chart_series, start, end,
                    )
            except api_client.StockAPIError as e:
                context["errors"].append(str(e))
            except Exception:
                app.logger.exception("Unexpected error while building chart")
                context["errors"].append("Something went wrong. Please try again.")

    return render_template("index.html", **context)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
