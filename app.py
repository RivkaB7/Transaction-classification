from flask import Flask, request, jsonify, render_template_string
import requests
import os

app = Flask(__name__)

RPC_URL = "https://ethereum.publicnode.com"
ZERO_ADDRESS = "0x0000000000000000000000000000000000000000"
UNISWAP_POSITION_MANAGER = "0xc36442b4a4522e871399cd717abdd847ab11fe88"

KNOWN_METHOD_SELECTORS = {
    "0xa9059cbb": "Transfer",
    "0x095ea7b3": "Approval",
    "0x23b872dd": "Transfer",
    "0xd0e30db0": "Deposit",
    "0x2e1a7d4d": "Withdraw",
    "0x7ff36ab5": "Swap",
    "0x38ed1739": "Swap",
    "0x18cbafe5": "Swap",
    "0x414bf389": "Swap",
    "0xa415bcad": "Borrow",
    "0x573ade81": "Repay",
    "0x617ba037": "Deposit",
    "0xe8eda9df": "Deposit",
    "0x69328dec": "Withdraw",
    "0xc7c7f5b3": "Bridge"
}

KNOWN_CONTRACTS = {
    "0x888888888889758f76e7103c6cbf23abbf58f946": "Swap",
    "0x87870bca3f3fd6335c3f4ce8392d69350b4fa4e2": "Lending",
    "0x6c96de32cea08842dcc4058c14d3aaad7fa41dee": "Bridge"
}

UNI_MINT_SELECTOR = "0x88316456"
UNI_INCREASE_SELECTOR = "0x219f5d17"
UNI_DECREASE_SELECTOR = "0x0c49ccbe"
UNI_COLLECT_SELECTOR = "0xfc6f7865"
UNI_BURN_SELECTOR = "0x42966c68"

UNI_COLLECT_EVENT = "0x40d0efd1"
UNI_DECREASE_EVENT = "0x26f6a048"
UNI_INCREASE_EVENT = "0x3067048b"
TOPIC_TRANSFER = "0xddf252ad"

HTML_PAGE = """
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Transaction Classification</title>
  <style>
    body {
      margin: 0;
      font-family: Arial, sans-serif;
      background: radial-gradient(circle at top, #0d1630 0%, #050814 70%);
      color: white;
      display: flex;
      justify-content: center;
      align-items: center;
      min-height: 100vh;
    }
    .container {
      width: 760px;
      max-width: 90%;
      background: rgba(14, 24, 52, 0.95);
      border-radius: 26px;
      padding: 48px 36px;
      box-shadow: 0 0 40px rgba(0, 0, 0, 0.35);
      text-align: center;
    }
    .logo {
      color: #6f7cff;
      font-size: 20px;
      font-weight: 700;
      letter-spacing: 3px;
      margin-bottom: 26px;
    }
    h1 {
      font-size: 58px;
      margin: 0 0 26px;
      font-weight: 700;
    }
    .subtitle {
      color: #c8cfdd;
      font-size: 20px;
      margin-bottom: 34px;
    }
    input {
      width: 100%;
      box-sizing: border-box;
      padding: 18px 16px;
      border: none;
      border-radius: 16px;
      background: #18264c;
      color: white;
      font-size: 16px;
      outline: none;
      margin-bottom: 24px;
    }
    input::placeholder {
      color: #94a0bf;
    }
    button {
      width: 100%;
      border: none;
      border-radius: 16px;
      padding: 18px;
      font-size: 18px;
      font-weight: 700;
      color: white;
      cursor: pointer;
      background: linear-gradient(90deg, #5546ff, #5a4df2);
      transition: transform 0.15s ease, opacity 0.15s ease;
    }
    button:hover {
      transform: translateY(-1px);
      opacity: 0.96;
    }
    .result {
      margin-top: 30px;
      color: #00ffb2;
      font-size: 20px;
      font-weight: 600;
      min-height: 28px;
    }
    .details {
      margin-top: 18px;
      text-align: left;
      background: #121d3b;
      border-radius: 16px;
      padding: 18px;
      color: #d8deea;
      word-break: break-word;
      display: none;
    }
    .details strong {
      color: white;
    }
    .error {
      color: #ff7a7a;
    }
  </style>
</head>
<body>
  <div class="container">
    <div class="logo">FORDEFI</div>
    <h1>Transaction Classification</h1>
    <div class="subtitle">Enter a transaction hash to analyze</div>

    <input type="text" id="hashInput" placeholder="0x..." />
    <button onclick="classifyTransaction()">Analyze Transaction</button>

    <div class="result" id="result"></div>

    <div class="details" id="details">
      <div><strong>Hash:</strong> <span id="hashText"></span></div>
      <div><strong>From:</strong> <span id="fromText"></span></div>
      <div><strong>To:</strong> <span id="toText"></span></div>
    </div>
  </div>

  <script>
    async function classifyTransaction() {
      const hash = document.getElementById("hashInput").value.trim();
      const resultDiv = document.getElementById("result");
      const detailsDiv = document.getElementById("details");

      if (!hash) {
        resultDiv.className = "result error";
        resultDiv.innerText = "Please enter a transaction hash";
        detailsDiv.style.display = "none";
        return;
      }

      resultDiv.className = "result";
      resultDiv.innerText = "Analyzing...";
      detailsDiv.style.display = "none";

      try {
        const response = await fetch("/classify", {
          method: "POST",
          headers: {
            "Content-Type": "application/json"
          },
          body: JSON.stringify({ tx_hash: hash })
        });

        const data = await response.json();

        if (!response.ok) {
          throw new Error(data.error || "Server error");
        }

        resultDiv.className = "result";
        resultDiv.innerText = "Result: " + data.result;

        document.getElementById("hashText").innerText = data.hash || "";
        document.getElementById("fromText").innerText = data.from || "";
        document.getElementById("toText").innerText = data.to || "";
        detailsDiv.style.display = "block";

      } catch (error) {
        resultDiv.className = "result error";
        resultDiv.innerText = "Error: " + error.message;
        detailsDiv.style.display = "none";
      }
    }
  </script>
</body>
</html>
"""

def rpc_call(method, params):
    payload = {
        "jsonrpc": "2.0",
        "method": method,
        "params": params,
        "id": 1
    }
    response = requests.post(RPC_URL, json=payload, timeout=30)
    response.raise_for_status()
    data = response.json()

    if "error" in data:
        raise ValueError(str(data["error"]))

    return data.get("result")

def get_transaction_by_hash(tx_hash):
    tx = rpc_call("eth_getTransactionByHash", [tx_hash])
    if tx is None:
        raise ValueError("Transaction not found")
    return tx

def get_transaction_receipt(tx_hash):
    receipt = rpc_call("eth_getTransactionReceipt", [tx_hash])
    if receipt is None:
        raise ValueError("Transaction receipt not found")
    return receipt

def topic_to_address(topic_value):
    if not topic_value:
        return None
    topic_value = topic_value.lower().replace("0x", "")
    return "0x" + topic_value[-40:]

def is_zero_address(address):
    return bool(address) and address.lower() == ZERO_ADDRESS

def contains_selector_anywhere(input_data, selector):
    return selector.replace("0x", "") in input_data.replace("0x", "")

def classify_uniswap_position(tx, receipt):
    input_data = (tx.get("input") or "").lower()
    logs = receipt.get("logs", [])

    create_score = 0
    close_score = 0

    if contains_selector_anywhere(input_data, UNI_MINT_SELECTOR):
        create_score += 4
    if contains_selector_anywhere(input_data, UNI_INCREASE_SELECTOR):
        create_score += 2
    if contains_selector_anywhere(input_data, UNI_DECREASE_SELECTOR):
        close_score += 4
    if contains_selector_anywhere(input_data, UNI_COLLECT_SELECTOR):
        close_score += 2
    if contains_selector_anywhere(input_data, UNI_BURN_SELECTOR):
        close_score += 3

    for log in logs:
        if (log.get("address") or "").lower() != UNISWAP_POSITION_MANAGER:
            continue

        topics = log.get("topics", [])
        if not topics:
            continue

        topic0 = (topics[0] or "").lower()

        if topic0.startswith(UNI_INCREASE_EVENT):
            create_score += 3
        elif topic0.startswith(UNI_DECREASE_EVENT):
            close_score += 3
        elif topic0.startswith(UNI_COLLECT_EVENT):
            close_score += 2
        elif topic0.startswith(TOPIC_TRANSFER) and len(topics) >= 3:
            from_addr = topic_to_address(topics[1])
            to_addr = topic_to_address(topics[2])

            if is_zero_address(from_addr):
                create_score += 4
            if is_zero_address(to_addr):
                close_score += 4

    if create_score > close_score:
        return "Create Position"
    if close_score > create_score:
        return "Close Position"

    return "Create Position"

def classify_transaction(tx, receipt):
    input_data = (tx.get("input") or "").lower()
    to_address = (tx.get("to") or "").lower()
    value = tx.get("value") or "0x0"

    if to_address == "":
        return "Contract Creation"

    if input_data == "0x":
        try:
            if int(value, 16) > 0:
                return "ETH Transfer"
        except Exception:
            pass
        return "Simple Transaction"

    if to_address == UNISWAP_POSITION_MANAGER:
        return classify_uniswap_position(tx, receipt)

    selector = input_data[:10]

    if selector in KNOWN_METHOD_SELECTORS:
        return KNOWN_METHOD_SELECTORS[selector]

    if to_address in KNOWN_CONTRACTS:
        return KNOWN_CONTRACTS[to_address]

    return "Smart Contract Interaction"

@app.route("/")
def home():
    return render_template_string(HTML_PAGE)

@app.route("/classify", methods=["POST"])
def classify_api():
    try:
        data = request.get_json()
        tx_hash = data.get("tx_hash", "").strip()

        if not tx_hash:
            return jsonify({"error": "Missing transaction hash"}), 400

        tx = get_transaction_by_hash(tx_hash)
        receipt = get_transaction_receipt(tx_hash)
        result = classify_transaction(tx, receipt)

        return jsonify({
            "result": result,
            "hash": tx.get("hash"),
            "from": tx.get("from"),
            "to": tx.get("to")
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
