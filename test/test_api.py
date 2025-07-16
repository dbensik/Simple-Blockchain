# tests/test_api.py
import pytest
from src.simple_blockchain.blockchain import app


@pytest.fixture
def client():
    """Creates a test client for the Flask app."""
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


def test_get_chain(client):
    """Tests the /chain endpoint."""
    response = client.get("/chain")
    assert response.status_code == 200
    data = response.get_json()
    assert "chain" in data
    assert "length" in data
    assert data["length"] >= 1  # Should have at least the genesis block


def test_mine_block(client):
    """Tests the /mine endpoint."""
    response = client.get("/mine")
    assert response.status_code == 200
    data = response.get_json()
    assert data["message"] == "New Block Forged"
    assert "index" in data
    # After mining, the chain length should increase
    chain_response = client.get("/chain")
    assert chain_response.get_json()["length"] == data["index"]
