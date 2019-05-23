from blockchain_routes import *
import hashlib
import json
import requests
from time import time
from uuid import uuid4
from flask import Flask, jsonify, request
from urllib.parse import urlparse

class Blockchain:
    def __init__(self):
        self.chain = []
        self.current_transactions = []
        # Create  genesis block
        self.new_block(previous_hash=1, proof=100)
        self.nodes = set()

    def new_block(self, proof, previous_hash=None):
        """
        # Create a new Block in the Blockchain
        parameters:
             proof - The proof given by the Proof of Work algorithm
             previous_hash -  Hash of previous Block
        returns:
            new block
        """

        block = {
            'index': len(self.chain) + 1,
            'timestamp': time(),
            'transactions': self.current_transactions,
            'proof': proof,
            'previous_hash': previous_hash or self.hash(self.chain[-1]),
        }

        # Reset the current list of transactions
        self.current_transactions = []
        self.chain.append(block)
        return block

    def new_transaction(self, sender, recipient, amount):
        """
        Creates a new transaction to go into the next mined Block
        parameters:
            sender - Address of the sender
            recipient - Address of the recipient
            amount - Amount
        returns:
            The index of the Block that will hold this transaction
        """

        self.current_transactions.append({
            'sender': sender,
            'recipient': recipient,
            'amount': amount,
        })

        return self.last_block['index'] + 1

    @staticmethod
    def hash(block):
        # Hashes a block
        """
        Creates a SHA-256 hash of a Block
        parameters:
            block - block
        returns:
            hashed block
        """
        # make sure the Dictionary is Ordered or hashes will be inconsistent
        block_string = json.dumps(block, sort_keys=True).encode()
        return hashlib.sha256(block_string).hexdigest()

    @property
    def last_block(self):
        """
        returns:
            the last block in the chain
        """
        return self.chain[-1]

    def proof_of_work(self, last_proof):
        """
        Proof of Work Algorithm:
         - Find a number p' such that hash(pp') contains leading 4 zeroes, where p is the previous p'
         - p is the previous proof, and p' is the new proof
        parameters:
            last_proof
        returns:
            proof
        """
        proof = 0
        while self.validate_proof(last_proof, proof) is False:
            proof += 1
        return proof

    @staticmethod
    def validate_proof(last_proof, proof):
        """
        Validates the Proof: Does hash(last_proof, proof) contain 4 leading zeroes?
        parameters:
            last_proof - previous proof
            proof - current proof
        returns:
            True if correct, False if not
        """
        guess = f'{last_proof}{proof}'.encode()
        guess_hash = hashlib.sha256(guess).hexdigest()
        return guess_hash[:4] == "0000"

    def register_node(self, address):
        """
        Add a new node to the list of nodes
        :param address: <str> Address of node. Eg. 'http://192.168.0.5:5000'
        :return: None
        """

        parsed_url = urlparse(address)
        self.nodes.add(parsed_url.netloc)

    def validate_chain(self, chain):
        """
        Verify if a blockchain is valid
        parameters:
            blockchain (as list)
        returns:
            True if valid, False if not
        """
        last_block = chain[0]
        current_index = 1

        while current_index < len(chain):
            block = chain[current_index]
            print(f'{last_block}')
            print(f'{block}')
            print("\n------------------------\n")
            # verify block hash
            if block['previous_hash'] != self.hash(last_block):
                return False

            # verify POW
            if not self.validate_proof(last_block['proof'], block['proof']):
                return False

            last_block = block
            current_index += 1

        return True

    def resolve_conflicts(self):
        """
        Consensus Algorithm resolves conflicts in the chain by replacing our chain with the longest chain in the network.

        returns:
            True if our chain replaced, False if not
        """
        neighbors = self.nodes
        new_chain = None

        # look for chains longer than ours
        max_length = len(self.chain)

        # get and verify chains from all nodes in the network
        for node in neighbors:
            response = requests.get(f'http://{node}/chain')

            if response.status_code == 200:
                length = response.json()['length']
                chain = response.json()['chain']

                # is length longer and chain valid?
                if length > max_length and self.validate_chain(chain):
                    max_length = length
                    new_chain = chain

        # replace our chain if valid chain longer than ours
        if new_chain:
            self.chain = new_chain
            return True
        return False


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5001)
