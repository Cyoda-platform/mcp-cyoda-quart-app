```python
import asyncio
import logging
from datetime import datetime
from typing import List, Dict, Any

import httpx
from quart import Quart, request, jsonify, Response
from quart_schema import QuartSchema

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

app = Quart(__name__)
QuartSchema(app)

# In-memory cache for latest fetched data keyed by job_id (simulate entity_job pattern)
entity_job: Dict[str, Dict[str, Any]] = {}
latest_rates_cache: Dict[str, Any] = {}  # store latest fetched rates keyed by base_currency


# Helper: build HTML table from a list of dicts (dynamic columns)
def build_html_table(data: List[Dict[str, Any]]) -> str:
    if not data:
        return "<table><tr><td>No data</td></tr></table>"

    columns = list(data[0].keys())
    # Build table header
    header_html = "".join(f"<th>{col}</th>" for col in columns)

    # Build table rows
    rows_html = ""
    for row in data:
        row_html = "".join(f"<td>{row.get(col, '')}</td>" for col in columns)
        rows_html += f"<tr>{row_html}</tr>"

    table_html = (
        f'<table border="1" cellspacing="0" cellpadding="5">'
        f"<thead><tr>{header_html}</tr></thead>"
        f"<tbody>{rows_html}</tbody>"
        f"</table>"
    )
    return table_html


# POST endpoint: Accept arbitrary JSON array and return full data as HTML table
@app.route("/api/currency-rates/display-table", methods=["POST"])
async def display_table():
    try:
        data = await request.get_json()
        if not isinstance(data, list):
            return jsonify({"error": "Expected a JSON array"}), 400

        html_table = build_html_table(data)
        return Response(html_table, content_type="text/html")
    except Exception as e:
        logger.exception(e)
        return jsonify({"error": "Failed to process request"}), 500


# POST endpoint: fetch live currency rates from external API and return HTML table
@app.route("/api/currency-rates/fetch", methods=["POST"])
async def fetch_currency_rates():
    try:
        req_data = await request.get_json()
        base_currency = req_data.get("base_currency", "USD")
        target_currencies = req_data.get("target_currencies", [])

        if not isinstance(target_currencies, list) or not base_currency:
            return jsonify({"error": "Invalid request parameters"}), 400

        # Use real external API: ExchangeRate-API (https://www.exchangerate-api.com/)
        # Free tier allows https://open.er-api.com/v6/latest/USD without key
        url = f"https://open.er-api.com/v6/latest/{base_currency.upper()}"

        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.get(url)
            resp.raise_for_status()
            data = resp.json()

        # Check API result status
        if data.get("result") != "success":
            return jsonify({"error": "External API error"}), 502

        rates = data.get("rates", {})
        filtered_rates = {
            cur: rates[cur]
            for cur in target_currencies
            if cur in rates
        }

        # Cache latest rates keyed by base_currency
        latest_rates_cache[base_currency.upper()] = {
            "base_currency": base_currency.upper(),
            "rates": filtered_rates,
            "timestamp": data.get("time_last_update_utc"),
        }

        # Build HTML table for response
        table_data = [{"Currency": k, "Rate": v} for k, v in filtered_rates.items()]
        html_table = build_html_table(table_data)

        return Response(html_table, content_type="text/html")

    except httpx.RequestError as e:
        logger.exception(e)
        return jsonify({"error": "Failed to contact external API"}), 502
    except Exception as e:
        logger.exception(e)
        return jsonify({"error": "Internal server error"}), 500


# GET endpoint: return cached latest rates as HTML table
@app.route("/api/currency-rates/latest", methods=["GET"])
async def get_latest_rates():
    try:
        base_currency = request.args.get("base_currency", "USD").upper()
        cached = latest_rates_cache.get(base_currency)
        if not cached:
            return jsonify({"error": "No cached rates found for base currency"}), 404

        table_data = [{"Currency": k, "Rate": v} for k, v in cached["rates"].items()]
        html_table = build_html_table(table_data)
        return Response(html_table, content_type="text/html")
    except Exception as e:
        logger.exception(e)
        return jsonify({"error": "Internal server error"}), 500


# POST endpoint: convert amount using cached latest rates, return JSON
@app.route("/api/currency-rates/convert", methods=["POST"])
async def convert_currency():
    try:
        req_data = await request.get_json()
        from_currency = req_data.get("from_currency", "").upper()
        to_currency = req_data.get("to_currency", "").upper()
        amount = req_data.get("amount")

        if not from_currency or not to_currency or amount is None:
            return jsonify({"error": "Missing required fields"}), 400

        # Find rates for from_currency base
        cached = latest_rates_cache.get(from_currency)
        if not cached:
            return jsonify({"error": f"No cached rates found for base currency {from_currency}"}), 404

        rate = cached["rates"].get(to_currency)
        if rate is None:
            return jsonify({"error": f"Rate for {to_currency} not found"}), 404

        converted_amount = round(amount * rate, 6)
        response = {
            "from_currency": from_currency,
            "to_currency": to_currency,
            "original_amount": amount,
            "converted_amount": converted_amount,
            "rate": rate,
            "timestamp": cached.get("timestamp"),
        }
        return jsonify(response)
    except Exception as e:
        logger.exception(e)
        return jsonify({"error": "Internal server error"}), 500


if __name__ == "__main__":
    app.run(use_reloader=False, debug=True, host="0.0.0.0", port=8000, threaded=True)
```
