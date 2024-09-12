def create_html_string(report_data: dict) -> None:

    data = report_data

    html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Daily Transaction Report</title>
    <style>
        body {{ font-family: Arial, sans-serif; }}
        table {{ width: 50%; border-collapse: collapse; margin-bottom: 20px; }}
        table, th, td {{ border: 1px solid black; }}
        th, td {{ padding: 8px; text-align: left; }}
        th {{ background-color: #f2f2f2; }}
        h1, h2 {{ color: #29335C; }}
    </style>
</head>
<body>
    <h1>Daily Transaction Report</h1>

    <h2>Total Daily Transactions</h2>
    <p>{data['total daily transactions']}</p>

    <h2>Daily Transactions per Truck</h2>
    <table>
        <tr>
            <th>Truck ID</th>
            <th>Total Transactions</th>
        </tr>
        {''.join([f"<tr><td>{item['truck_id']}</td><td>{item['total']}</td></tr>" for item in data['daily transactions per truck']])}
    </table>

    <h2>Total Earnings per Truck</h2>
    <table>
        <tr>
            <th>Truck ID</th>
            <th>Total Earnings</th>
        </tr>
        {''.join([f"<tr><td>{item['truck_id']}</td><td>{item['total']}</td></tr>" for item in data['total earnings per truck']])}
    </table>

    <h2>Payment Method Proportions</h2>
    <table>
        <tr>
            <th>Payment Type</th>
            <th>Count</th>
            <th>Proportion</th>
        </tr>
        {''.join([f"<tr><td>{item['payment_type']}</td><td>{item['count']}</td><td>{
                 item['proportion']}</td></tr>" for item in data['pay method proportions']])}
    </table>
</body>
</html>
"""

    return html_content
