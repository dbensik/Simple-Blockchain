# simulation.py
import requests
import json
import time
import random
from argparse import ArgumentParser
from typing import List

# Assuming wallet is in the simple_blockchain package
from simple_blockchain.wallet import Wallet


def create_wallets(count: int) -> List[Wallet]:
    """Creates a specified number of wallets."""
    print(f"Creating {count} wallets for the simulation...")
    return [Wallet() for _ in range(count)]


def create_transaction_payload(
    sender: Wallet, recipient: Wallet, amount: float, fee: float
) -> dict:
    """Signs and prepares a transaction payload for the API."""
    transaction_data = {
        "sender": sender.address,
        "recipient": recipient.address,
        "amount": amount,
        "fee": fee,
    }
    # The string must be identical to the one the server will verify
    transaction_string = json.dumps(transaction_data, sort_keys=True)
    signature = sender.sign(transaction_string)
    return {**transaction_data, "signature": signature}


def main(node_url: str, num_wallets: int, tps: float):
    """
    Runs a continuous simulation of random transactions.

    :param node_url: The URL of the blockchain node to send transactions to.
    :param num_wallets: The number of wallets to simulate.
    :param tps: The target number of transactions per second.
    """
    print("--- 🎬 Starting Blockchain Transaction Simulator ---")
    print(f"Node URL: {node_url}")
    print(f"Simulating with {num_wallets} wallets.")
    print(f"Targeting ~{tps} transactions per second.")

    wallets = create_wallets(num_wallets)
    headers = {"Content-Type": "application/json"}
    delay = 1.0 / tps

    print("\n--- 🚀 Simulation running. Press CTRL+C to stop. ---")
    try:
        while True:
            # 1. Select a random sender and recipient
            sender, recipient = random.sample(wallets, 2)

            # 2. Generate a random amount and fee
            amount = round(random.uniform(0.1, 10.0), 4)
            fee = round(random.uniform(0.001, 0.1), 4)

            # 3. Create and sign the transaction
            payload = create_transaction_payload(sender, recipient, amount, fee)

            # 4. Broadcast the transaction
            try:
                response = requests.post(
                    f"{node_url}/transactions/new", json=payload, headers=headers
                )
                if response.status_code == 201:
                    print(
                        f"✅ Success: {amount} coins from {sender.address[:10]}... to {recipient.address[:10]}..."
                    )
                else:
                    print(f"🔥 Error: {response.status_code} - {response.text}")
            except requests.exceptions.ConnectionError:
                print(
                    f"🔌 Connection Error: Could not connect to node at {node_url}. Is it running?"
                )

            # 5. Wait to maintain the target TPS
            time.sleep(delay)

    except KeyboardInterrupt:
        print("\n--- 🛑 Simulation stopped by user. ---")


if __name__ == "__main__":
    parser = ArgumentParser(
        description="Run an automated transaction simulation against a blockchain node."
    )
    parser.add_argument(
        "--node-url",
        default="http://127.0.0.1:5001",
        type=str,
        help="The URL of the blockchain node.",
    )
    parser.add_argument(
        "-w", "--wallets", default=10, type=int, help="Number of wallets to create."
    )
    parser.add_argument(
        "-t", "--tps", default=0.5, type=float, help="Target transactions per second."
    )
    args = parser.parse_args()

    main(args.node_url, args.wallets, args.tps)
