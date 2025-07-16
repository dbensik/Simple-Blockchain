import requests
import json
from simple_blockchain.wallet import Wallet

# --- Configuration ---
NODE_URL = "http://127.0.0.1:5001"


def main():
    """Runs a full demonstration of the blockchain client."""
    print("--- 🏦 Creating Wallets for Alice and Bob ---")
    alice_wallet = Wallet()
    bob_wallet = Wallet()
    print(f"Alice's Address: {alice_wallet.address[:25]}...")
    print(f"Bob's Address: {bob_wallet.address[:25]}...")

    print("\n--- ⛏️ Mining a block to reward the node (miner) ---")
    try:
        mine_response = requests.get(f"{NODE_URL}/mine")
        if mine_response.status_code != 200:
            print("Error: Could not connect to the node. Is it running?")
            return
        mined_block = mine_response.json()
        print("Success! Node mined a block and received a reward.")
    except requests.exceptions.ConnectionError:
        print(
            "Fatal: Could not connect to the node. Please start the blockchain first."
        )
        # --- FIX: Corrected the run command ---
        print("Run: python -m simple_blockchain.blockchain -p 5001")
        return

    print("\n--- 💸 Alice is sending 5 coins to Bob ---")
    # 1. Define the transaction data
    transaction_data = {
        "sender": alice_wallet.address,
        "recipient": bob_wallet.address,
        "amount": 5.0,
        "fee": 0.01,
    }
    # The string must be identical to the one the server will verify
    transaction_string = json.dumps(transaction_data, sort_keys=True)

    # 2. Alice signs the transaction with her private key
    signature = alice_wallet.sign(transaction_string)
    print("Transaction signed successfully.")

    # 3. Broadcast the transaction to the network
    payload = {**transaction_data, "signature": signature}
    headers = {"Content-Type": "application/json"}
    response = requests.post(
        f"{NODE_URL}/transactions/new", json=payload, headers=headers
    )

    if response.status_code == 201:
        print("Transaction submitted successfully and is pending.")
    else:
        print(f"Error submitting transaction: {response.text}")
        return

    print("\n--- ⛏️ Mining a new block to confirm the transaction ---")
    requests.get(f"{NODE_URL}/mine")
    print("New block mined!")

    print("\n--- 🔗 Verifying the final chain state ---")
    chain_response = requests.get(f"{NODE_URL}/chain")
    chain = chain_response.json()["chain"]
    last_transaction = chain[-1]["transactions"][
        -1
    ]  # The last transaction in the last block

    print(f"Last transaction sender: {last_transaction['sender'][:25]}...")
    print(f"Last transaction recipient: {last_transaction['recipient'][:25]}...")
    print(f"Last transaction amount: {last_transaction['amount']}")
    assert last_transaction["sender"] == alice_wallet.address
    assert last_transaction["recipient"] == bob_wallet.address
    assert last_transaction["amount"] == 5.0
    print(
        "\n✅ Verification successful! The transaction is confirmed on the blockchain."
    )


if __name__ == "__main__":
    main()
