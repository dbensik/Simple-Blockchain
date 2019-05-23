from blockchain import *
# Instantiate Node
app = Flask(__name__)

# Generate a globally unique address for the node
node_id = str(uuid4()).replace('-', '')

# Instantiate the Blockchain
my_blockchain = Blockchain()

@app.route('/mine', methods=['GET'])
def mine():
    # run POW algo to get next proof
    last_block = my_blockchain.last_block
    last_proof = last_block['proof']
    proof = my_blockchain.proof_of_work(last_proof)

    # receive reward for mining the block
    # sender = "0" signifies the node has mined a new coin
    my_blockchain.new_transaction(
    sender="0",
    recipient=node_id,
    amount="1",
    )

    # add new block to the blockchain
    previous_hash = my_blockchain.hash(last_block)
    block = my_blockchain.new_block(proof, previous_hash)

    response = {
        'message': "New Block Added",
        'index': block['index'],
        'transactions': block['transactions'],
        'proof': block['proof'],
        'previous_hash': block['previous_hash'],
    }
    return jsonify(response), 200


@app.route('/transactions/new', methods=['POST'])
def new_transaction():
    values = request.get_json()
    # verify that required fields are in the POST'ed data
    required = ['sender', 'recipient', 'amount']
    if not all(k in values for k in required):
        return 'Missing values', 400

    # new transaction
    index = my_blockchain.new_transaction(values['sender'], values['recipient'], values['amount'])

    response = {'message': f'Transaction will be added to the Block {index}'}
    return jsonify(response), 201

@app.route('/chain', methods=['GET'])
def full_chain():
    response = {
        'chain': my_blockchain.chain,
        'length': len(my_blockchain.chain),
    }
    return jsonify(response), 200

@app.route('/nodes/register', methods=['POST'])
def register_nodes():
    values = request.get_json()
    nodes = values.get('nodes')
    if nodes is None:
        return "Error: Please provide valid list of nodes", 400

    for node in nodes:
        my_blockchain.register_node(node)

    response = {
        'message': 'New nodes added',
        'total_nodes': list(my_blockchain.nodes),
    }
    return jsonify(response), 201

@app.route('/nodes/resolve', methods=['GET'])
def consensus():
    replaced = my_blockchain.resolve_conflicts()
    if replaced:
        response = {
            'message': 'Chain replaced',
            'new_chain': my_blockchain.chain,
        }
    else:
        response = {
            'message': 'Chain is correct',
            'chain': my_blockchain.chain,
        }

    return jsonify(response), 200
