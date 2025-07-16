import hashlib
import json
from time import time
from urllib.parse import urlparse
from uuid import uuid4
from .wallet import Wallet
import requests
from flask import Flask, jsonify, request
from pyvis.network import Network


class Blockchain:
    """
    Manages the chain, storage, and new block creation for the blockchain.
    """

    def __init__(self):
        self.chain = []
        self.current_transactions = []
        self.nodes = set()

        # Create the genesis block
        self.new_block(proof=100, previous_hash="1", transactions=[])

    def register_node(self, address: str) -> None:
        """
        Add a new node to the list of nodes.

        :param address: Address of node. Eg. 'http://192.168.0.5:5000'
        """
        parsed_url = urlparse(address)
        if parsed_url.netloc:
            self.nodes.add(parsed_url.netloc)
        elif parsed_url.path:
            # Accepts an URL without scheme like '192.168.0.5:5000'.
            self.nodes.add(parsed_url.path)
        else:
            raise ValueError("Invalid URL")

    def validate_chain(self, chain: list) -> bool:
        """
        Determine if a given blockchain is valid.

        :param chain: A blockchain
        :return: True if valid, False if not
        """
        last_block = chain[0]
        current_index = 1

        while current_index < len(chain):
            block = chain[current_index]
            # Uncomment the print statements below for debugging consensus
            # print(f'{last_block}')
            # print(f'{block}')
            # print("\n-----------\n")

            # Check that the hash of the block is correct
            if block["previous_hash"] != self.hash(last_block):
                return False

            # Check that the Proof of Work is correct
            if not self.validate_proof(
                last_block["proof"], block["proof"], block["previous_hash"]
            ):
                return False

            last_block = block
            current_index += 1

        return True

    def resolve_conflicts(self) -> bool:
        """
        This is our consensus algorithm. It resolves conflicts by replacing
        our chain with the longest one in the network.

        :return: True if our chain was replaced, False if not
        """
        neighbors = self.nodes
        new_chain = None

        # We're only looking for chains longer than ours
        max_length = len(self.chain)

        # Grab and verify the chains from all the nodes in our network
        for node in neighbors:
            try:
                response = requests.get(f"http://{node}/chain")

                if response.status_code == 200:
                    length = response.json()["length"]
                    chain = response.json()["chain"]

                    # Check if the length is longer and the chain is valid
                    if length > max_length and self.validate_chain(chain):
                        max_length = length
                        new_chain = chain
            except requests.exceptions.ConnectionError:
                print(f"Could not connect to node {node}. Skipping.")
                continue

        # Replace our chain if we discovered a new, valid chain longer than ours
        if new_chain:
            self.chain = new_chain
            return True

        return False

    def new_block(
        self, proof: int, transactions: list, previous_hash: str = None
    ) -> dict:
        """
        Create a new Block in the Blockchain.

        :param proof: The proof given by the Proof of Work algorithm
        :param transactions: A list of transactions to include in the block.
        :param previous_hash: Hash of previous Block
        :return: New Block
        """
        block = {
            "index": len(self.chain) + 1,
            "timestamp": time(),
            "transactions": transactions,
            "proof": proof,
            "previous_hash": previous_hash or self.hash(self.chain[-1]),
        }

        # The mempool is now cleared by the caller (e.g., the /mine endpoint)
        self.chain.append(block)
        return block

        # In the Blockchain class

    def new_transaction(
        self, sender: str, recipient: str, amount: float, fee: float, signature: str
    ) -> int:
        """
        Creates a new transaction to go into the next mined Block.
        Now includes signature verification.

        :param sender: Address of the Sender (public key)
        :param recipient: Address of the Recipient
        :param amount: Amount
        :param fee: Transaction fee to reward the miner
        :param signature: The digital signature of the transaction
        :return: The index of the Block that will hold this transaction
        """
        transaction_data = {
            "sender": sender,
            "recipient": recipient,
            "amount": amount,
            "fee": fee,
        }

        # The data that was signed is the transaction itself, excluding the signature
        # We sort the keys to ensure the hash is consistent
        transaction_string = json.dumps(transaction_data, sort_keys=True)

        # Verify the signature
        if sender != "0" and not Wallet.verify_signature(
            sender, signature, transaction_string
        ):
            # The sender address is the public key
            print(f"Invalid signature from sender {sender}")
            return -1  # Indicate failure

        self.current_transactions.append({**transaction_data, "signature": signature})

        if not self.chain:  # Handle case where chain is empty at startup
            return 1
        return self.last_block["index"] + 1

    @property
    def last_block(self) -> dict:
        """Returns the last block in the chain."""
        return self.chain[-1]

    @staticmethod
    def hash(block: dict) -> str:
        """
        Creates a SHA-256 hash of a Block.

        :param block: Block
        :return: The hash string
        """
        # We must make sure that the Dictionary is Ordered, or we'll have inconsistent hashes
        block_string = json.dumps(block, sort_keys=True).encode()
        return hashlib.sha256(block_string).hexdigest()

    def proof_of_work(self, last_block: dict) -> int:
        """
        Simple Proof of Work Algorithm:
         - Find a number 'p' such that hash(last_proof, p, last_hash) contains 4 leading zeroes.

        :param last_block: The last Block dictionary
        :return: The new proof
        """
        last_proof = last_block["proof"]
        last_hash = self.hash(last_block)
        proof = 0
        while self.validate_proof(last_proof, proof, last_hash) is False:
            proof += 1

        return proof

    @staticmethod
    def validate_proof(last_proof: int, proof: int, last_hash: str) -> bool:
        """
        Validates the proof: Does hash(last_proof, proof, last_hash) contain 4 leading zeroes?

        :param last_proof: Previous Proof
        :param proof: Current Proof
        :param last_hash: Hash of the previous block
        :return: True if correct, False if not.
        """
        guess = f"{last_proof}{proof}{last_hash}".encode()
        guess_hash = hashlib.sha256(guess).hexdigest()
        return guess_hash[:4] == "0000"


# --- API Section ---

# Instantiate the Node
app = Flask(__name__)

# Generate a globally unique address for this node
node_identifier = str(uuid4()).replace("-", "")

# Instantiate the Blockchain
blockchain = Blockchain()


@app.route("/mine", methods=["GET"])
def mine():
    # We run the proof of work algorithm to get the next proof...
    last_block = blockchain.last_block
    proof = blockchain.proof_of_work(last_block)

    # Take a snapshot of the current pending transactions and clear the mempool
    transactions_for_block = list(blockchain.current_transactions)
    blockchain.current_transactions = []

    # Calculate the total fees from the transactions being mined
    total_fees = sum(tx.get("fee", 0) for tx in transactions_for_block)
    mining_reward = 1 + total_fees

    # We must receive a reward for finding the proof.
    # The sender is "0" to signify that this node has mined a new coin.
    # By convention, the reward is the first transaction in the block.
    reward_transaction = {
        "sender": "0",
        "recipient": node_identifier,
        "amount": mining_reward,
        "signature": "0",  # Coinbase transactions don't need a real signature
        "fee": 0,  # The reward transaction itself has no fee
    }
    transactions_for_block.insert(0, reward_transaction)

    # Forge the new Block by adding it to the chain
    previous_hash = blockchain.hash(last_block)
    block = blockchain.new_block(proof, transactions_for_block, previous_hash)

    response = {
        "message": "New Block Forged",
        "index": block["index"],
        "transactions": block["transactions"],
        "proof": block["proof"],
        "previous_hash": block["previous_hash"],
    }
    return jsonify(response), 200


@app.route("/transactions/new", methods=["POST"])
def new_transaction():
    values = request.get_json()

    # Check that the required fields are in the POST'ed data
    required = ["sender", "recipient", "amount", "fee", "signature"]
    if not all(k in values for k in required):
        return (
            "Missing values (sender, recipient, amount, fee, signature are required)",
            400,
        )

    # Create a new Transaction
    index = blockchain.new_transaction(
        values["sender"],
        values["recipient"],
        values["amount"],
        values["fee"],
        values["signature"],
    )

    if index == -1:
        return "Invalid transaction signature", 400

    response = {"message": f"Transaction will be added to Block {index}"}
    return jsonify(response), 201


@app.route("/chain", methods=["GET"])
def full_chain():
    response = {
        "chain": blockchain.chain,
        "length": len(blockchain.chain),
    }
    return jsonify(response), 200


@app.route("/nodes/register", methods=["POST"])
def register_nodes():
    values = request.get_json()

    nodes = values.get("nodes")
    if nodes is None:
        return "Error: Please supply a valid list of nodes", 400

    for node in nodes:
        blockchain.register_node(node)

    response = {
        "message": "New nodes have been added",
        "total_nodes": list(blockchain.nodes),
    }
    return jsonify(response), 201


@app.route("/nodes/resolve", methods=["GET"])
def consensus():
    replaced = blockchain.resolve_conflicts()

    if replaced:
        response = {"message": "Our chain was replaced", "new_chain": blockchain.chain}
    else:
        response = {"message": "Our chain is authoritative", "chain": blockchain.chain}

    return jsonify(response), 200


@app.route("/transactions/pending", methods=["GET"])
def get_pending_transactions():
    """Returns the list of transactions currently waiting to be mined."""
    response = {"transactions": blockchain.current_transactions}
    return jsonify(response), 200


@app.route("/network/graph", methods=["GET"])
def network_graph():
    """
    Generates an interactive HTML graph of the network.
    """
    net = Network(
        height="750px",
        width="100%",
        bgcolor="#222222",
        font_color="white",
        notebook=True,
        cdn_resources="in_line",
    )

    # Add the current node
    net.add_node(
        node_identifier,
        label=f"Node {node_identifier[:6]}...",
        title=f"This Node\n{request.host}",
        color="#00aaff",
    )

    # Add peer nodes
    for node in blockchain.nodes:
        # We assume the node identifier is the host address for simplicity
        peer_id = node.replace("http://", "")
        net.add_node(
            peer_id, label=f"Node {peer_id[:12]}...", title=f"Peer Node\n{node}"
        )
        # Add an edge from this node to the peer
        net.add_edge(node_identifier, peer_id)

    # Generate the HTML file in memory
    return net.generate_html(), 200


if __name__ == "__main__":
    from argparse import ArgumentParser

    parser = ArgumentParser()
    parser.add_argument(
        "-p", "--port", default=5001, type=int, help="port to listen on"
    )
    args = parser.parse_args()
    port = args.port

    app.run(host="0.0.0.0", port=port)
