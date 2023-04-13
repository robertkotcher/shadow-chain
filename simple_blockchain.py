import hashlib
import requests
import time

DEFAULT_DIFFICULTY=5

class Block:
    def __init__(self, index, transactions, previous_hash):
        self.index = index
        self.timestamp = time.time()
        self.transactions = transactions
        self.previous_hash = previous_hash
        self.nonce = 0
        self.hash = self.compute_hash()

    def compute_hash(self):
        block_string = "{}{}{}{}{}".format(self.index, self.timestamp, self.transactions, self.previous_hash, self.nonce)
        return hashlib.sha256(block_string.encode()).hexdigest()

    @classmethod
    def from_dict(cls, block_data):
        block = cls(block_data["index"], block_data["transactions"], block_data["previous_hash"])
        block.timestamp = block_data["timestamp"]
        block.hash = block_data["hash"]
        block.nonce = block_data["nonce"]
        return block

class SimpleBlockchain:
    def __init__(self):
        self.chain = [self.create_genesis_block()]
        self.nodes = set()

    def create_genesis_block(self):
        return Block(0, [], "0")

    def add_block(self, transactions, difficulty=DEFAULT_DIFFICULTY):
        previous_block = self.chain[-1]
        new_block = Block(len(self.chain), transactions, previous_block.hash)
        mined_block = self.mine_block(new_block, difficulty)
        self.chain.append(mined_block)

    def mine_block(self, block, difficulty):
        prefix = "0" * difficulty
        while not block.hash.startswith(prefix):
            block.nonce += 1
            block.hash = block.compute_hash()

        self.broadcast_block(block)

        return block

    def register_node(self, address):
        self.nodes.add(address)

    def broadcast_block(self, block):
        serialized_block = {
            "index": block.index,
            "timestamp": block.timestamp,
            "transactions": block.transactions,
            "previous_hash": block.previous_hash,
            "hash": block.hash,
            "nonce": block.nonce
        }

        for node in self.nodes:
            requests.post(f"http://{node}/receive_block", json=serialized_block)

    def resolve_conflicts(self):
        longest_chain = None
        max_length = len(self.chain)

        for node in self.nodes:
            response = requests.get(f"http://{node}/chain")

            if response.status_code == 200:
                length = response.json()["length"]
                chain = response.json()["chain"]

                if length > max_length and self.is_chain_valid(chain):
                    max_length = length
                    longest_chain = chain

        if longest_chain:
            self.chain = self.deserialize_chain(longest_chain)
            return True

        return False

    def is_chain_valid(self, chain):
        for i in range(1, len(chain)):
            current_block = Block.from_dict(chain[i])
            previous_block = Block.from_dict(chain[i - 1])

            if current_block.previous_hash != previous_block.hash:
                return False

            if current_block.hash != current_block.compute_hash():
                return False

        return True

    def is_block_valid(self, block):
        last_block = self.chain[-1]

        if last_block.hash != block.previous_hash:
            return False

        if block.hash != block.compute_hash():
            return False

        if block.timestamp <= last_block.timestamp:
            return False

        return True

    def deserialize_chain(self, chain_data):
        new_chain = []
        for block_data in chain_data:
            new_block = Block.from_dict(block_data)
            new_chain.append(new_block)

        return new_chain

    def get_serialized_chain(self):
        chain_data = []
        for block in self.chain:
            chain_data.append({
                "index": block.index,
                "timestamp": block.timestamp,
                "transactions": block.transactions,
                "previous_hash": block.previous_hash,
                "hash": block.hash,
                "nonce": block.nonce
            })
        return chain_data

class SimpleBlockchainSDK:
    def __init__(self, blockchain):
        self.blockchain = blockchain

    def mine(self, transactions, difficulty=DEFAULT_DIFFICULTY):
        self.blockchain.add_block(transactions, difficulty)



