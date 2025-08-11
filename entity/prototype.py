from dataclasses import dataclass
import asyncio
import logging
from datetime import datetime
from typing import List, Dict, Any

import httpx
from quart import Quart, request, jsonify, Response
from quart_schema import QuartSchema, validate_request, validate_querystring

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

app = Quart(__name__)
QuartSchema(app)

# In-memory caches
latest_rates_cache: Dict[str, Any] = {}

@dataclass
class DisplayTableBody:
    # TODO: define fields for table rows; using placeholder for dynamic structure
    dummy: Dict[str, Any]

@dataclass
class FetchRatesBody:
    base_currency: str
    target_currencies: List[str]

@dataclass
class ConvertCurrencyBody:
    from_currency: str
    to_currency: str
    amount: float

@dataclass
class GetLatestQuery:
    base_currency: str = "USD"

def build_html_table(data: List[Dict[str, Any]]) -> str:
    if not data:
        return "<table><tr><td>No data</td></tr></table>"
    columns = list(data[0].keys())
    header_html = "".join(f"<th>{col}</th>" for col in columns)
    rows_html = ""
    for row in data:
        row_html = "".join(f"<td>{row.get(col, '')}</td>" for col in columns)
        rows_html += f"<tr>{row_html}</tr>"
    return (
        '<table border="1" cellspacing="0" cellpadding="5">'
        f"<thead><tr>{header_html}</tr></thead>"
        f"<tbody>{rows_html}</tbody>"
        "</table>"
    )

@app.route("/api/currency-rates/display-table", methods=["POST"])
@validate_request(DisplayTableBody)  # validation last for POST (workaround for library issue)
async def display_table(data: DisplayTableBody):
    raw = await request.get_json()  # use raw JSON array directly
    if not isinstance(raw, list):
        return jsonify({"error": "Expected a JSON array"}), 400
    html_table = build_html_table(raw)
    return Response(html_table, content_type="text/html")

@app.route("/api/currency-rates/fetch", methods=["POST"])
@validate_request(FetchRatesBody)  # validation last for POST
async def fetch_currency_rates(data: FetchRatesBody):
    try:
        base = data.base_currency.upper()
        targets = data.target_currencies
        url = f"https://open.er-api.com/v6/latest/{base}"
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.get(url)
            resp.raise_for_status()
            api_data = resp.json()
        if api_data.get("result") != "success":
            return jsonify({"error": "External API error"}), 502
        rates = api_data.get("rates", {})
        filtered = {c: rates[c] for c in targets if c in rates}
        latest_rates_cache[base] = {
            "base_currency": base,
            "rates": filtered,
            "timestamp": api_data.get("time_last_update_utc"),
        }
        table_data = [{"Currency": k, "Rate": v} for k, v in filtered.items()]
        html_table = build_html_table(table_data)
        return Response(html_table, content_type="text/html")
    except httpx.RequestError as e:
        logger.exception(e)
        return jsonify({"error": "Failed to contact external API"}), 502
    except Exception as e:
        logger.exception(e)
        return jsonify({"error": "Internal server error"}), 500

@validate_querystring(GetLatestQuery)  # validation first for GET (workaround for library issue)
@app.route("/api/currency-rates/latest", methods=["GET"])
async def get_latest_rates():
    base = request.args.get("base_currency", "USD").upper()
    cached = latest_rates_cache.get(base)
    if not cached:
        return jsonify({"error": "No cached rates found"}), 404
    table = build_html_table([{"Currency": k, "Rate": v} for k, v in cached["rates"].items()])
    return Response(table, content_type="text/html")

@app.route("/api/currency-rates/convert", methods=["POST"])
@validate_request(ConvertCurrencyBody)  # validation last for POST
async def convert_currency(data: ConvertCurrencyBody):
    try:
        frm = data.from_currency.upper()
        to = data.to_currency.upper()
        amt = data.amount
        cached = latest_rates_cache.get(frm)
        if not cached:
            return jsonify({"error": f"No cached rates for {frm}"}), 404
        rate = cached["rates"].get(to)
        if rate is None:
            return jsonify({"error": f"Rate for {to} not found"}), 404
        converted = round(amt * rate, 6)
        return jsonify({
            "from_currency": frm,
            "to_currency": to,
            "original_amount": amt,
            "converted_amount": converted,
            "rate": rate,
            "timestamp": cached.get("timestamp"),
        })
    except Exception as e:
        logger.exception(e)
        return jsonify({"error": "Internal server error"}), 500

if __name__ == "__main__":
    app.run(use_reloader=False, debug=True, host="0.0.0.0", port=8000, threaded=True)