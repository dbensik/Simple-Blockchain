# 🧱 Simple Blockchain (Python)

A fully functioning blockchain prototype in Python that demonstrates core concepts of decentralized ledgers — including mining, proof-of-work, transactions, peer-to-peer networking, and a basic consensus algorithm.

Built as an educational and demonstrative project, this codebase uses Flask to expose RESTful endpoints for mining, transaction submission, and node communication.

---

## 🚀 Features

- **Proof-of-Work mining**  
  Simple hash puzzle requiring leading zeroes in SHA-256 for block validation.

- **Transaction ledger**  
  Add transactions that get included in newly mined blocks.

- **Decentralized peer network**  
  Register peer nodes and sync chains via HTTP requests.

- **Consensus mechanism**  
  Longest-chain-wins logic ensures consistency across distributed nodes.

---

## 🛠️ Tech Stack

- **Python 3**
- **Flask** – for HTTP server and RESTful API
- **hashlib** – for SHA-256 hashing
- **requests** – for inter-node communication
- **uuid** – for generating unique node identities

---

## 📦 Getting Started

### 🔧 Install Requirements

```bash
git clone https://github.com/dbensik/Simple-Blockchain.git
cd Simple-Blockchain
pip install -r requirements.txt
```

You may need to manually install:

- "Flask"
- "requests"

```bash
pip install Flask requests
```
---

## 🧪 Run the Blockchain Node
```bash
python blockchain_routes.py
```
By default, this will launch a node on http://127.0.0.1:5001.

To simulate a network, run multiple instances on different ports (e.g., 5002, 5003) and register them with each other.

## 🌐 Available Endpoints
### Mine a Block
```bash
GET /mine
```
Mines a new block, rewards the miner (this node), and adds it to the chain.

### Create a New Transaction
```pgsql
POST /transactions/new
Content-Type: application/json

{
  "sender": "alice",
  "recipient": "bob",
  "amount": 100
}
```
Returns the index of the block that will contain this transaction.

### View the Full Blockchain
```bash
GET /chain
```
Returns the full blockchain and its current length.

### Register New Nodes
```bash
POST /nodes/register
Content-Type: application/json

{
  "nodes": ["http://localhost:5002", "http://localhost:5003"]
}
```
Adds a list of new nodes to the network.

### Resolve Chain Conflicts (Consensus)
```bash
GET /nodes/resolve
```
Triggers a consensus check and replaces the chain if a longer, valid one is found on a peer.

## 🔍 Code Structure
```bash
Simple-Blockchain/
├── blockchain.py           # Core Blockchain class and logic
├── blockchain_routes.py    # Flask server and API endpoints
├── requirements.txt        # Dependencies (Flask, requests)
└── README.md               # You're reading it
```
## 💡 Future Improvements
Store chain data in a local database or file for persistence

Add transaction signatures and validation

Use asynchronous networking (e.g., websockets)

Add automatic peer discovery

Implement smarter fork resolution logic

## 👋 About Me
I'm currently studying for CFA Level II and building technical projects like this to deepen my understanding of both finance and technology. You can find more of my work on GitHub.com/dbensik.

## 🧠 TL;DR
This is a fully interactive Python blockchain demo built from scratch. It’s lightweight, understandable, and ready to expand.
