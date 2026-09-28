import csv
import json
import os
import webbrowser
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse, parse_qs

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


def read_csv(filename):
    with open(os.path.join(BASE_DIR, filename), "r", encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))


def read_json(filename):
    with open(os.path.join(BASE_DIR, filename), "r", encoding="utf-8") as f:
        return json.load(f)


farmers = read_csv("farmers.csv")
production = read_csv("crop_production.csv")
prices = read_csv("market_prices.csv")
feedback = read_json("farmer_feedback.json")


def dashboard_html(selected_crop="All"):

    prod = production
    price_data = prices

    if selected_crop != "All":
        prod = [x for x in production if x["Crop"] == selected_crop]
        price_data = [x for x in prices if x["Crop"] == selected_crop]

    # -----------------------------
    # KPI calculations
    # -----------------------------

    total_prod = sum(float(x["Production_Tons"]) for x in prod)

    price_values = [float(x["Modal_Price"]) for x in price_data]

    avg_price = (
        sum(price_values) / len(price_values)
        if price_values else 0
    )

    # -----------------------------
    # Crop production
    # -----------------------------

    crop_prod = {}

    for row in prod:
        crop = row["Crop"]
        crop_prod[crop] = crop_prod.get(crop, 0) + float(
            row["Production_Tons"]
        )

    # -----------------------------
    # Year production
    # -----------------------------

    year_prod = {}

    for row in prod:
        year = row["Year"]
        year_prod[year] = year_prod.get(year, 0) + float(
            row["Production_Tons"]
        )

    # -----------------------------
    # Crop price
    # -----------------------------

    crop_price_total = {}
    crop_price_count = {}

    for row in price_data:

        crop = row["Crop"]
        price = float(row["Modal_Price"])

        crop_price_total[crop] = (
            crop_price_total.get(crop, 0) + price
        )

        crop_price_count[crop] = (
            crop_price_count.get(crop, 0) + 1
        )

    crop_price = {}

    for crop in crop_price_total:
        crop_price[crop] = (
            crop_price_total[crop]
            / crop_price_count[crop]
        )

    # -----------------------------
    # Crop options
    # -----------------------------

    crops = sorted(set(x["Crop"] for x in production))

    crop_options = '<option value="All">All Crops</option>'

    for crop in crops:

        selected = (
            "selected"
            if crop == selected_crop
            else ""
        )

        crop_options += (
            f'<option value="{crop}" {selected}>{crop}</option>'
        )

    # -----------------------------
    # Bar chart
    # -----------------------------

    crop_bars = ""

    max_crop = max(crop_prod.values()) if crop_prod else 1

    for crop, value in sorted(
        crop_prod.items(),
        key=lambda x: x[1],
        reverse=True
    ):

        width = (value / max_crop) * 100

        crop_bars += f"""
        <div class="bar-row">

            <div class="bar-label">
                {crop}
            </div>

            <div class="bar-container">

                <div class="bar"
                     style="width:{width:.1f}%">
                </div>

            </div>

            <div class="bar-value">
                {value:,.1f}
            </div>

        </div>
        """

    # -----------------------------
    # Year chart
    # -----------------------------

    year_chart = ""

    years = sorted(year_prod.keys())

    max_year = max(year_prod.values()) if year_prod else 1

    for year in years:

        value = year_prod[year]

        height = (value / max_year) * 180

        year_chart += f"""
        <div class="year-column">

            <div class="year-value">
                {value:,.0f}
            </div>

            <div class="year-bar"
                 style="height:{height:.1f}px">
            </div>

            <div class="year-label">
                {year}
            </div>

        </div>
        """

    # -----------------------------
    # Price table
    # -----------------------------

    price_rows = ""

    for crop, value in sorted(crop_price.items()):

        price_rows += f"""
        <tr>
            <td>{crop}</td>
            <td>₹{value:,.2f}</td>
        </tr>
        """

    # -----------------------------
    # Production table
    # -----------------------------

    production_rows = ""

    for row in prod[:100]:

        production_rows += f"""
        <tr>
            <td>{row["Production_ID"]}</td>
            <td>{row["Farmer_ID"]}</td>
            <td>{row["Crop"]}</td>
            <td>{row["Year"]}</td>
            <td>{row["Season"]}</td>
            <td>{row["Production_Tons"]}</td>
            <td>{row["Yield_Per_Acre"]}</td>
        </tr>
        """

    # -----------------------------
    # Feedback
    # -----------------------------

    feedback_rows = ""

    for row in feedback[:100]:

        feedback_rows += f"""
        <tr>
            <td>{row.get("Farmer_ID", "")}</td>
            <td>{row.get("Crop", "")}</td>
            <td>{row.get("District", "")}</td>
            <td>{row.get("Quality", "")}</td>
            <td>{row.get("Feedback", "")}</td>
        </tr>
        """

    # -----------------------------
    # HTML
    # -----------------------------

    return f"""
<!DOCTYPE html>

<html>

<head>

<meta charset="UTF-8">

<title>
Smart Agriculture Analytics Dashboard
</title>

<style>

* {{
    box-sizing: border-box;
}}

body {{

    margin: 0;

    font-family:
        Arial,
        Helvetica,
        sans-serif;

    background:
        #f1f5f3;

    color:
        #1f2937;

}}

.header {{

    background:
        linear-gradient(
            135deg,
            #14532d,
            #166534,
            #15803d
        );

    color: white;

    padding: 32px 45px;

}}

.header h1 {{

    margin: 0;

    font-size: 32px;

}}

.header p {{

    margin-top: 8px;

    opacity: .9;

}}

.container {{

    padding: 30px 45px;

}}

.filter-box {{

    background: white;

    padding: 18px 22px;

    border-radius: 14px;

    margin-bottom: 25px;

    box-shadow:
        0 3px 12px
        rgba(0,0,0,.07);

}}

select {{

    padding: 10px 18px;

    border-radius: 8px;

    border: 1px solid #cbd5e1;

    font-size: 15px;

}}

.cards {{

    display: grid;

    grid-template-columns:
        repeat(4, 1fr);

    gap: 20px;

    margin-bottom: 28px;

}}

.card {{

    background: white;

    padding: 24px;

    border-radius: 16px;

    box-shadow:
        0 4px 14px
        rgba(0,0,0,.07);

}}

.card-title {{

    color: #64748b;

    font-size: 14px;

    margin-bottom: 10px;

}}

.card-value {{

    font-size: 28px;

    font-weight: bold;

    color: #166534;

}}

.grid {{

    display: grid;

    grid-template-columns:
        1fr 1fr;

    gap: 24px;

    margin-bottom: 25px;

}}

.panel {{

    background: white;

    padding: 24px;

    border-radius: 16px;

    box-shadow:
        0 4px 14px
        rgba(0,0,0,.07);

}}

.panel h2 {{

    margin-top: 0;

    color: #14532d;

}}

.bar-row {{

    display: grid;

    grid-template-columns:
        90px 1fr 90px;

    align-items: center;

    gap: 10px;

    margin: 13px 0;

}}

.bar-label {{

    font-weight: 600;

}}

.bar-container {{

    background:
        #e2e8f0;

    height: 22px;

    border-radius: 20px;

    overflow: hidden;

}}

.bar {{

    height: 100%;

    background:
        linear-gradient(
            90deg,
            #166534,
            #4ade80
        );

    border-radius: 20px;

}}

.bar-value {{

    text-align: right;

    font-weight: bold;

}}

.year-chart {{

    height: 250px;

    display: flex;

    align-items: end;

    justify-content: space-around;

    border-bottom:
        2px solid #cbd5e1;

    padding-top: 25px;

}}

.year-column {{

    height: 100%;

    display: flex;

    flex-direction: column;

    justify-content: end;

    align-items: center;

}}

.year-bar {{

    width: 42px;

    background:
        linear-gradient(
            to top,
            #166534,
            #4ade80
        );

    border-radius:
        7px 7px 0 0;

}}

.year-value {{

    font-size: 11px;

    margin-bottom: 5px;

}}

.year-label {{

    margin-top: 8px;

    font-weight: bold;

}}

table {{

    width: 100%;

    border-collapse:
        collapse;

}}

th {{

    background:
        #166534;

    color: white;

    padding: 11px;

    text-align: left;

}}

td {{

    padding: 10px;

    border-bottom:
        1px solid #e5e7eb;

}}

tr:hover {{

    background:
        #f0fdf4;

}}

.table-wrap {{

    overflow-x: auto;

    max-height: 450px;

    overflow-y: auto;

}}

.footer {{

    text-align: center;

    padding: 30px;

    color: #64748b;

}}

@media(max-width:900px) {{

    .cards {{

        grid-template-columns:
            repeat(2,1fr);

    }}

    .grid {{

        grid-template-columns: 1fr;

    }}

}}

@media(max-width:600px) {{

    .container {{

        padding: 20px;

    }}

    .cards {{

        grid-template-columns: 1fr;

    }}

}}

</style>

</head>

<body>

<div class="header">

<h1>
🌾 Smart Agriculture Analytics Dashboard
</h1>

<p>
Crop Production & Market Price Analytics System
</p>

</div>


<div class="container">


<div class="filter-box">

<form>

<b>🔎 Select Crop:</b>

<select
name="crop"
onchange="this.form.submit()">

{crop_options}

</select>

</form>

</div>


<div class="cards">


<div class="card">

<div class="card-title">
👨‍🌾 Total Farmers
</div>

<div class="card-value">
{len(farmers):,}
</div>

</div>


<div class="card">

<div class="card-title">
🌾 Total Production
</div>

<div class="card-value">
{total_prod:,.2f} Tons
</div>

</div>


<div class="card">

<div class="card-title">
💰 Average Market Price
</div>

<div class="card-value">
₹{avg_price:,.2f}
</div>

</div>


<div class="card">

<div class="card-title">
💬 Farmer Feedback
</div>

<div class="card-value">
{len(feedback):,}
</div>

</div>


</div>


<div class="grid">


<div class="panel">

<h2>
🌾 Crop-wise Production
</h2>

{crop_bars}

</div>


<div class="panel">

<h2>
📈 Year-wise Production
</h2>

<div class="year-chart">

{year_chart}

</div>

</div>


</div>


<div class="grid">


<div class="panel">

<h2>
💰 Crop-wise Average Market Price
</h2>

<table>

<tr>

<th>Crop</th>

<th>Average Price</th>

</tr>

{price_rows}

</table>

</div>


<div class="panel">

<h2>
📊 Analytics Summary
</h2>

<p>
<strong>Total Farmers:</strong>
{len(farmers):,}
</p>

<p>
<strong>Production Records:</strong>
{len(production):,}
</p>

<p>
<strong>Market Price Records:</strong>
{len(prices):,}
</p>

<p>
<strong>Feedback Records:</strong>
{len(feedback):,}
</p>

<p>
<strong>Selected Crop:</strong>
{selected_crop}
</p>

</div>


</div>


<div class="panel">

<h2>
🌾 Crop Production Details
</h2>

<div class="table-wrap">

<table>

<tr>

<th>Production ID</th>
<th>Farmer ID</th>
<th>Crop</th>
<th>Year</th>
<th>Season</th>
<th>Production Tons</th>
<th>Yield/Acre</th>

</tr>

{production_rows}

</table>

</div>

</div>


<br>


<div class="panel">

<h2>
💬 Farmer Feedback
</h2>

<div class="table-wrap">

<table>

<tr>

<th>Farmer ID</th>
<th>Crop</th>
<th>District</th>
<th>Quality</th>
<th>Feedback</th>

</tr>

{feedback_rows}

</table>

</div>

</div>


</div>


<div class="footer">

Smart Agriculture Analytics Project
<br>
Python • MySQL • MongoDB

</div>


</body>

</html>
"""


class DashboardHandler(BaseHTTPRequestHandler):

    def do_GET(self):

        query = parse_qs(
            urlparse(self.path).query
        )

        selected_crop = query.get(
            "crop",
            ["All"]
        )[0]

        html = dashboard_html(
            selected_crop
        )

        self.send_response(200)

        self.send_header(
            "Content-Type",
            "text/html; charset=utf-8"
        )

        self.end_headers()

        self.wfile.write(
            html.encode("utf-8")
        )

    def log_message(self, format, *args):
        pass


server = HTTPServer(
    ("localhost", 8000),
    DashboardHandler
)

print()
print("=" * 60)
print("🌾 SMART AGRICULTURE ANALYTICS DASHBOARD")
print("=" * 60)
print()
print("Dashboard URL:")
print("http://localhost:8000")
print()
print("Press CTRL+C to stop")
print("=" * 60)

webbrowser.open(
    "http://localhost:8000"
)

server.serve_forever()