import streamlit as st
import requests
import json
import time
from simple_blockchain.wallet import Wallet

# --- Page Configuration ---
st.set_page_config(
    page_title="Blockchain Interactive Tutorial",
    page_icon="🎓",
    layout="wide",
)

# --- Helper Functions to Interact with the Node API ---


def get_node_status(node_url):
    """Checks if the node is online."""
    try:
        response = requests.get(f"{node_url}/chain", timeout=2)
        return response.status_code == 200
    except requests.exceptions.RequestException:
        return False


def get_node_chain(node_url):
    """Fetches the full chain from a node."""
    try:
        response = requests.get(f"{node_url}/chain")
        response.raise_for_status()
        return list(reversed(response.json()["chain"]))  # Reversed for display
    except requests.exceptions.RequestException as e:
        st.error(f"Could not connect to node at {node_url}. Error: {e}")
        return None


def get_pending_transactions(node_url):
    """Fetches pending transactions from the mempool."""
    try:
        response = requests.get(f"{node_url}/transactions/pending")
        response.raise_for_status()
        return response.json().get("transactions", [])
    except requests.exceptions.RequestException:
        return []


def post_transaction(node_url, sender_wallet, recipient_address, amount, fee):
    """Creates, signs, and posts a transaction."""
    transaction_data = {
        "sender": sender_wallet.address,
        "recipient": recipient_address,
        "amount": float(amount),
        "fee": float(fee),
    }
    transaction_string = json.dumps(transaction_data, sort_keys=True)
    signature = sender_wallet.sign(transaction_string)
    payload = {**transaction_data, "signature": signature}
    st.session_state.last_submitted_tx = {
        "data": transaction_data, "signature": signature
    }

    try:
        response = requests.post(f"{node_url}/transactions/new", json=payload)
        response.raise_for_status()
        st.success("Transaction submitted to the network!")
        st.balloons()
        return True
    except requests.exceptions.RequestException as e:
        st.error(f"Failed to submit transaction. Error: {e.response.text}")
        return False


def calculate_balances(chain: list, wallets: dict) -> dict:
    """Calculates balances by iterating through the entire blockchain."""
    # Create a reverse lookup from address to wallet name for convenience
    address_to_name = {wallet.address: name for name, wallet in wallets.items()}
    balances = {name: 100.0 for name, wallet in wallets.items()}  # Airdrop 100 coins!

    # get_node_chain provides a reversed list (latest block first).
    # To calculate balances chronologically, we reverse it back to genesis block first.
    for block in reversed(chain or []):
        for tx in block.get("transactions", []):
            sender_address = tx.get("sender")
            recipient_address = tx.get("recipient")
            amount = tx.get("amount", 0)
            fee = tx.get("fee", 0)

            # Subtract from sender's balance if they are one of our wallets
            if sender_address in address_to_name:
                balances[address_to_name[sender_address]] -= amount + fee

            # Add to recipient's balance if they are one of our wallets
            if recipient_address in address_to_name:
                balances[address_to_name[recipient_address]] += amount

    return balances


def mine_on_node(node_url):
    """Sends a request to the node to mine a new block."""
    try:
        with st.spinner("Mining a new block... This could take a moment."):
            response = requests.get(f"{node_url}/mine")
            response.raise_for_status()
        st.success("Block mined successfully! ⛏️")
        st.toast("A new block was forged and added to the chain!")
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Failed to mine. Error: {e}")
        return None


def resolve_conflicts_on_node(node_url):
    """Triggers the consensus algorithm on the node."""
    try:
        with st.spinner("Asking the node to check for longer chains from its peers..."):
            response = requests.get(f"{node_url}/nodes/resolve")
            response.raise_for_status()
            data = response.json()
            if data.get("message") == "Our chain was replaced":
                st.success(
                    "Consensus complete: The node's chain was replaced with a longer, authoritative one."
                )
            else:
                st.info(
                    "Consensus complete: The node's chain was already authoritative."
                )
            time.sleep(1)
            st.rerun()
    except requests.exceptions.RequestException as e:
        st.error(f"Failed to run consensus. Error: {e}")


def handle_transaction_submission():
    """Callback function to handle the transaction logic."""
    # Access the widget values via st.session_state using their keys
    sender_name = st.session_state.get("sender")
    recipient_name = st.session_state.get("recipient")
    amount = st.session_state.get("amount")
    fee = st.session_state.get("fee")

    if sender_name and recipient_name and amount > 0 and fee is not None:
        # Overspending Check
        chain_for_balance = get_node_chain(node_url)
        current_balances = calculate_balances(
            chain_for_balance, st.session_state.wallets
        )
        sender_balance = current_balances.get(sender_name, 0)
        total_cost = amount + fee

        if total_cost > sender_balance:
            st.error(
                f"Insufficient funds! {sender_name} has {sender_balance:,.2f} coins, but the transaction costs {total_cost:,.2f} (amount + fee)."
            )
            return

        sender_wallet = st.session_state.wallets[sender_name]
        recipient_address = st.session_state.wallets[recipient_name].address
        # Check if the transaction was successfully posted
        if post_transaction(node_url, sender_wallet, recipient_address, amount, fee):
            # Give the server a moment to update its mempool before Streamlit reruns
            time.sleep(0.5)
    else:
        st.error("Please ensure all fields are filled out correctly before submitting.")


# --- Session State Initialization ---
if "wallets" not in st.session_state:
    st.session_state.wallets = {}  # {name: Wallet_object}

if "last_submitted_tx" not in st.session_state:
    st.session_state.last_submitted_tx = None

# --- Sidebar for Node Control ---
st.sidebar.title("⚙️ Node Control")
node_url = st.sidebar.text_input("Node URL", "http://127.0.0.1:5001")

if st.sidebar.button("Check Node Status"):
    if get_node_status(node_url):
        st.sidebar.success("Node is online and responding.")
    else:
        st.sidebar.error("Node is offline or not responding.")

if st.sidebar.button("Run Consensus Algorithm"):
    if get_node_status(node_url):
        resolve_conflicts_on_node(node_url)
    else:
        st.sidebar.error("Node is offline. Cannot run consensus.")

st.sidebar.markdown("---")
st.sidebar.info(
    "This dashboard is an interactive tutorial. Follow the steps from top to bottom to learn how a blockchain works!"
)


# --- Main Page ---
st.title("🎓 Blockchain: An Interactive Tutorial")
st.markdown(
    "Welcome! This application demonstrates the fundamental concepts of a blockchain. Follow the steps below."
)

# --- Step 1: Wallet Creation ---
with st.container(border=True):
    st.header("Step 1: Create Wallets & View Balances")
    st.markdown(
        """
    A crypto wallet doesn't store coins. Instead, it holds your **keys**. This is the foundation of self-custody.
    As the saying goes: **"Not your keys, not your coins."** By creating wallets here, *you* control the private keys, not a centralized exchange.

    - **Public Key (Address):** Like your bank account number. You can share it with anyone to receive funds.
    - **Private Key:** Like your bank account password. It's a secret key used to *sign* (authorize) transactions. **Never share it!**

    Let's create some wallets for this simulation. We'll give each wallet an initial "airdrop" of **100 coins** to get started.
    """
    )
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Create a Wallet")
        new_wallet_name = st.text_input(
            "New Wallet Name", placeholder="e.g., Alice", key="new_wallet_name"
        )
        if st.button("Create New Wallet"):
            if new_wallet_name and new_wallet_name not in st.session_state.wallets:
                st.session_state.wallets[new_wallet_name] = Wallet()
                st.toast(f"Wallet for '{new_wallet_name}' created!", icon="🎉")
                time.sleep(1)  # Give user time to read success message
                st.rerun()
            else:
                st.warning("Please enter a unique name for the new wallet.")

    with col2:
        st.subheader("💰 Account Balances")
        if not st.session_state.wallets:
            st.info("Create a wallet to see balances.")
        else:
            chain_for_balance = get_node_chain(node_url)
            balances = calculate_balances(chain_for_balance, st.session_state.wallets)
            for name, balance in balances.items():
                st.metric(label=f"{name}'s Balance", value=f"{balance:,.2f} Coins")

    if st.session_state.wallets:
        st.markdown("---")
        st.subheader("🔑 Your Wallet Keys")
        st.info(
            "Expand a wallet to inspect its public and private keys. Notice how the private key is a secret you must choose to reveal."
        )
        for name, wallet in st.session_state.wallets.items():
            with st.expander(f"Wallet: **{name}**"):
                st.markdown(f"**Public Key (Address):**")
                st.code(wallet.address, language=None)

                if st.toggle("Reveal Private Key", key=f"toggle_{name}"):
                    st.markdown(f"**Private Key (Secret):**")
                    st.code(wallet.get_private_key_hex(), language=None)
                    st.warning("This is your secret key! Keep it safe.", icon="⚠️")

# --- Step 2: Create a Transaction ---
with st.container(border=True):
    st.header("Step 2: Create and Sign a Transaction")
    st.markdown(
        """
    A transaction is a record stating that one wallet is sending currency to another. To be valid, it must be **cryptographically signed**.

    - **Signing:** The sender's **private key** is used to create a unique mathematical signature for this specific transaction (including the amount, recipient, and fee).
    - **Verification:** Anyone on the network can use the sender's **public key** to verify that the signature is authentic without ever knowing the private key.
    - **Transaction Fees:** You must include a small fee, which is paid to the miner who includes your transaction in a block. Higher fees can incentivize miners to prioritize your transaction.
    """
    )
    if len(st.session_state.wallets) < 2:
        st.info("Create at least two wallets in Step 1 to send a transaction.")
    else:
        wallet_names = list(st.session_state.wallets.keys())
        col1, col2, col3, col4 = st.columns(4)
        sender_name = col1.selectbox(
            "➡️ From (Sender)", options=wallet_names, key="sender"
        )
        recipient_name = col2.selectbox(
            "⬅️ To (Recipient)",
            options=[n for n in wallet_names if n != sender_name],
            key="recipient",
        )
        amount = col3.number_input(
            "Amount", min_value=0.01, value=10.0, format="%.2f", key="amount"
        )
        fee = col4.number_input(
            "Fee", min_value=0.00, value=0.01, format="%.2f", key="fee"
        )
        # Use the on_click callback to handle the logic.
        # Streamlit will automatically rerun the script after the callback completes.
        st.button(
            "Sign and Submit Transaction",
            on_click=handle_transaction_submission,
            key="submit_transaction",
        )
        # After a transaction is submitted, show its anatomy
        if st.session_state.last_submitted_tx:
            with st.expander("🔬 Anatomy of the Last Submitted Transaction"):
                st.markdown(
                    "The data below was serialized into a string, hashed, and then the hash was signed with the sender's private key to produce the unique signature."
                )
                st.write("**Transaction Data:**")
                st.json(st.session_state.last_submitted_tx["data"])
                st.write("**Resulting Signature:**")
                st.code(st.session_state.last_submitted_tx["signature"], language=None)


# --- Step 3: The Mempool ---
with st.container(border=True):
    st.header("Step 3: The Mempool (Pending Transactions)")
    st.markdown(
        """
    After a transaction is submitted, it doesn't go onto the blockchain immediately. It sits in a waiting area called the **Mempool** (Memory Pool) along with other pending transactions, waiting for a "miner" to include it in the next block.
    """
    )
    if st.button("Refresh Mempool"):
        st.rerun()

    pending_tx = get_pending_transactions(node_url)
    if pending_tx:
        total_fees = sum(tx.get("fee", 0) for tx in pending_tx)
        st.metric(
            "Transactions in Mempool",
            f"{len(pending_tx)}",
            f"{total_fees:,.4f} Coins in available fees",
            help="This is the total reward available to the next miner, on top of the base reward.",
        )

        # Format for better display in a dataframe
        display_data = [
            {
                "Sender": tx["sender"][:40] + "...",
                "Recipient": tx["recipient"][:40] + "...",
                "Amount": tx["amount"],
                "Fee": tx["fee"],
            }
            for tx in pending_tx
        ]
        st.dataframe(display_data, use_container_width=True)
    else:
        st.info("The mempool is currently empty. Submit a transaction in Step 2!")

# --- Step 4: Mining a Block ---
with st.container(border=True):
    st.header("Step 4: Mine a New Block")
    st.markdown(
        """
    **Mining** is how new blocks are created. In a **Proof-of-Work** system, miners compete to solve a difficult computational puzzle.
    - The winner gathers pending transactions from the Mempool.
    - They are rewarded with newly created coins (a "coinbase" transaction).
    - They package this all into a new block and add it to the chain.
    """
    )
    if st.button("Mine Block & Collect Reward", type="primary"):
        mined_block = mine_on_node(node_url)
        if mined_block:
            st.write("Mined Block Details:")
            st.json(mined_block)
            time.sleep(1)
            st.rerun()

# --- Step 5: Explore the Final Chain ---
with st.container(border=True):
    st.header("Step 5: Explore the Blockchain")
    st.markdown(
        """
    The blockchain is an immutable, append-only ledger. Each block is cryptographically linked to the previous one using its hash, forming a secure chain. You can now see the new block (and the transactions inside it) as part of the permanent record.
    """
    )
    if st.button("Refresh Chain View"):
        st.rerun()

    chain = get_node_chain(node_url)
    if chain:
        for block in chain:
            st.expander(
                f"Block {block['index']} - (Contains {len(block['transactions'])} transactions)"
            ).json(block)
    else:
        st.warning("Could not fetch the blockchain from the node.")

# --- Step 6: Visualize the Network ---
with st.container(border=True):
    st.header("Step 6: Visualize the Network")
    st.markdown(
        """
        A blockchain is a network of communicating nodes. Your node maintains a list of its peers.
        The link below will open a new tab showing an interactive graph of the network from your node's perspective.
        
        *(Initially, you will only see your own node. If you were to run multiple nodes and register them with each other, this graph would show all the connections.)*
        """
    )
    network_graph_url = f"{node_url}/network/graph"
    st.markdown(f"**[Click here to view the Network Graph]({network_graph_url})**")

    with st.expander("Want to see a real network? Click here for instructions."):
        st.markdown(
            """
        To see more than one node in the graph, you need to run multiple instances of the blockchain server and register them with each other. Here's how:
        
        **1. Start your first node (if not already running):**
        Open a terminal, activate your environment, and run:
        ```sh
        conda activate simple-blockchain-env
        python -m simple_blockchain.blockchain -p 5001
        ```

        **2. Start a second node:**
        Open a **new, separate terminal**, activate the environment again, and run the following command to start a second node on a different port:
        ```sh
        conda activate simple-blockchain-env
        python -m simple_blockchain.blockchain -p 5002
        ```

        **3. Register the nodes with each other:**
        Open a **third terminal** (you don't need to activate the environment for `curl`). Run these two commands to make each node aware of the other:
        ```sh
        # Tell node 5001 about node 5002
        curl -X POST -H "Content-Type: application/json" -d '{"nodes": ["127.0.0.1:5002"]}' http://127.0.0.1:5001/nodes/register
        
        # Tell node 5002 about node 5001
        curl -X POST -H "Content-Type: application/json" -d '{"nodes": ["127.0.0.1:5001"]}' http://127.0.0.1:5002/nodes/register
        ```
        
        **4. View the updated graph:**
        Now, click the network graph link above again (or refresh the graph tab). You should see two nodes connected!
        """
        )
