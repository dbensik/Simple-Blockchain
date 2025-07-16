from flask import Flask, render_template_string
import requests
import datetime
from argparse import ArgumentParser

app = Flask(__name__)

# This will be set dynamically from command-line arguments
NODE_URL = ""

# A simple HTML template using Jinja2
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Blockchain Explorer</title>
    <style>
        body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif; margin: 2em; background-color: #f8f9fa; }
        h1 { color: #343a40; }
        .block { border: 1px solid #dee2e6; margin-bottom: 1em; padding: 1em; border-radius: 0.5em; background-color: #fff; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
        .block h3 { margin-top: 0; color: #007bff; }
        .tx { border-top: 1px solid #e9ecef; padding-top: 0.5em; margin-top: 0.5em; font-size: 0.9em; }
        .hash { font-family: "SF Mono", "Fira Code", "Consolas", monospace; word-break: break-all; color: #6c757d; }
        .meta-info { display: flex; justify-content: space-between; align-items: center; font-size: 0.85em; color: #6c757d; margin-bottom: 1em;}
        a { color: #007bff; text-decoration: none; }
        a:hover { text-decoration: underline; }
    </style>
</head>
<body>
    <h1>Blockchain Explorer</h1>
    <p>Viewing node: <a href="{{ node_url }}" target="_blank">{{ node_url }}</a> | <a href="/">Refresh</a></p>

    {% for block in chain|reverse %}
    <div class="block">
        <h3>Block {{ block.index }}</h3>
        <div class="meta-info">
            <span><strong>Timestamp:</strong> {{ block.timestamp|fromtimestamp }}</span>
            <span><strong>Proof:</strong> {{ block.proof }}</span>
        </div>
        <div><strong>Previous Hash:</strong> <span class="hash">{{ block.previous_hash }}</span></div>

        <h4>Transactions ({{ block.transactions|length }})</h4>
        {% for tx in block.transactions %}
            <div class="tx">
                 {% if tx.sender == '0' %}
                     <strong><span style="color: #28a745;">MINING REWARD (COINBASE)</span></strong><br>
                     <strong>To:</strong> <span class="hash">{{ tx.recipient[:45] }}{% if tx.recipient|length > 45 %}...{% endif %}</span><br>
                     <strong>Amount Rewarded:</strong> {{ tx.amount }}
                 {% else %}
                     <strong>From:</strong> <span class="hash">{{ tx.sender[:45] }}{% if tx.sender|length > 45 %}...{% endif %}</span><br>
                     <strong>To:</strong> <span class="hash">{{ tx.recipient[:45] }}{% if tx.recipient|length > 45 %}...{% endif %}</span><br>
                     <strong>Amount:</strong> {{ tx.amount }} (+ {{ tx.fee|default(0) }} fee)
                {% endif %}
            </div>
        {% else %}
            <div style="color: #6c757d;">No transactions in this block.</div>
        {% endfor %}
    </div>
    {% endfor %}
</body>
</html>
"""


@app.template_filter("fromtimestamp")
def fromtimestamp_filter(s):
    """Jinja2 filter to convert a Unix timestamp to a readable string."""
    return datetime.datetime.fromtimestamp(s).strftime("%Y-%m-%d %H:%M:%S UTC")


@app.route("/")
def view_chain():
    global NODE_URL
    try:
        response = requests.get(f"{NODE_URL}/chain")
        response.raise_for_status()
        chain_data = response.json()
        return render_template_string(
            HTML_TEMPLATE, chain=chain_data["chain"], node_url=NODE_URL
        )
    except requests.exceptions.RequestException as e:
        return (
            f"<h1>Error</h1><p>Could not connect to the blockchain node at {NODE_URL}.</p>"
            f"<p>Please ensure the node is running and the URL is correct.</p>"
            f"<hr><p><i>Error details: {e}</i></p>",
            500,
        )


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument(
        "--node-url",
        default="http://127.0.0.1:5001",
        type=str,
        help="The URL of the blockchain node to explore.",
    )
    parser.add_argument(
        "-p", "--port", default=8080, type=int, help="Port to run the explorer on."
    )
    args = parser.parse_args()

    # Set the global NODE_URL from the arguments
    NODE_URL = args.node_url
    port = args.port

    print(f"🔍 Explorer connecting to node at: {NODE_URL}")
    print(f"🚀 Explorer web interface running on: http://127.0.0.1:{port}")

    app.run(host="0.0.0.0", port=port)
