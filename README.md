# Stock Data Visualizer (Web)

A Flask web app that charts historical stock data from the Alpha Vantage API, running in Docker.

## Run with Docker
1. Create a `.env` file in this folder:
   ```
   ALPHA_VANTAGE_API_KEY=your_key_here
   ```
2. Build and start the container:
   ```bash
   docker compose up --build
   ```
3. Open http://localhost:5001

Stop it with Ctrl+C, or `docker compose down`.

## Run without Docker
```bash
python3 -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
flask --app app run --port 5001
```

## Files
| File | Purpose |
|------|---------|
| `app.py` | Flask routes (GET shows the form, POST validates input and builds the chart) |
| `symbols.py` | Loads stock symbols from `stocks.csv` into the dropdown |
| `api_client.py` | Queries Alpha Vantage and handles errors |
| `data_processor.py` | Filters data to the selected date range |
| `chart_generator.py` | Builds the pygal chart |
| `templates/index.html` | The web form and chart display |
| `Dockerfile`, `docker-compose.yml` | Container setup |
