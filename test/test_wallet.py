# tests/test_wallet.py
from simple_blockchain.wallet import Wallet
import json


def test_wallet_creation():
    """Tests if a wallet is created with a private key, public key, and address."""
    wallet = Wallet()
    assert wallet.private_key is not None
    assert wallet.public_key is not None
    assert isinstance(wallet.address, str)
    assert len(wallet.address) > 100  # PEM format is long


def test_sign_and_verify():
    """Tests that a signature created by a wallet can be successfully verified."""
    wallet = Wallet()
    data = {"message": "hello world"}
    data_string = json.dumps(data, sort_keys=True)

    signature = wallet.sign(data_string)
    assert isinstance(signature, str)

    # Verification should succeed with the correct data and public key
    is_valid = Wallet.verify_signature(wallet.address, signature, data_string)
    assert is_valid is True


def test_verify_invalid_signature():
    """Tests that verification fails for a tampered signature or data."""
    wallet1 = Wallet()
    wallet2 = Wallet()  # A different wallet
    data = {"message": "secret data"}
    data_string = json.dumps(data, sort_keys=True)
    tampered_data_string = json.dumps({"message": "tampered!"}, sort_keys=True)

    signature = wallet1.sign(data_string)

    # Fails: Data was changed
    assert (
        Wallet.verify_signature(wallet1.address, signature, tampered_data_string)
        is False
    )

    # Fails: Signature from a different wallet
    assert Wallet.verify_signature(wallet2.address, signature, data_string) is False
