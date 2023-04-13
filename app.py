import sys
from flask import Flask, jsonify, request
from simple_blockchain import SimpleBlockchain, SimpleBlockchainSDK, Block

app = Flask(__name__)

# Initialize the blockchain and SDK
blockchain = SimpleBlockchain()
sdk = SimpleBlockchainSDK(blockchain)

@app.route("/mine", methods=["POST"])
def mine():
    data = request.get_json()
    transactions = data.get("transactions", [])

    def mine_in_thread():
        sdk.mine(transactions)
        print("New block mined")

    mining_thread = threading.Thread(target=mine_in_thread)
    mining_thread.start()

    response = {
        "message": "Mining started in a new thread"
    }

    return jsonify(response), 200

@app.route("/chain", methods=["GET"])
def get_chain():
    chain_data = []
    for block in blockchain.chain:
        chain_data.append({
            "index": block.index,
            "timestamp": block.timestamp,
            "transactions": block.transactions,
            "previous_hash": block.previous_hash,
            "hash": block.hash,
            "nonce": block.nonce
        })

    response = {
        "chain": chain_data,
        "length": len(chain_data)
    }

    return jsonify(response), 200

@app.route("/nodes/register", methods=["POST"])
def register_nodes():
    data = request.get_json()
    nodes = data.get("nodes", [])

    if not nodes:
        return "Error: Please provide a valid list of nodes", 400

    for node in nodes:
        blockchain.register_node(node)

    response = {
        "message": "New nodes have been added",
        "total_nodes": list(blockchain.nodes)
    }

    return jsonify(response), 201

@app.route("/nodes/resolve", methods=["GET"])
def resolve_conflicts():
    replaced = blockchain.resolve_conflicts()

    if replaced:
        response = {
            "message": "Our chain was replaced",
            "new_chain": blockchain.get_serialized_chain()
        }
    else:
        response = {
            "message": "Our chain is authoritative",
            "chain": blockchain.get_serialized_chain()
        }

    return jsonify(response), 200

@app.route('/receive_block', methods=['POST'])
def receive_block():
    block_data = request.get_json()
    new_block = Block.from_dict(block_data)

    if blockchain.is_block_valid(new_block) and new_block not in blockchain.chain:
        blockchain.chain.append(new_block)
        response = {"message": "Block added to the chain", "block": block_data}
    else:
        response = {"message": "Block rejected", "block": block_data}

    return jsonify(response), 200

if __name__ == "__main__":
    if len(sys.argv) > 1:
        port = int(sys.argv[1])
    else:
        port = 5000

    app.run(host="0.0.0.0", port=port)
