"""Builds the pygal chart and returns it as SVG for the web page."""
import pygal


def generate_chart(symbol, chart_type, dates, series, start, end):
    chart_class = pygal.Bar if chart_type == "Bar" else pygal.Line
    chart = chart_class(
        x_label_rotation=45,
        show_minor_x_labels=False,
        x_labels_major_count=min(len(dates), 15),
        width=1100,
        height=550,
    )
    chart.title = f"Stock Data for {symbol}: {start} to {end}"
    chart.x_labels = dates
    for name, values in series.items():
        chart.add(name, values)
    return chart.render_data_uri()
