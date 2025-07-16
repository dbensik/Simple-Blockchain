from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import ec


class Wallet:
    """
    Manages an ECDSA key pair for signing and verifying transactions.
    """

    def __init__(self):
        """Generates a new private/public key pair."""
        self.private_key = ec.generate_private_key(ec.SECP256R1())
        self.public_key = self.private_key.public_key()
        # The public key is serialized to be used as the wallet's address
        self.address = self.public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo,
        ).hex()

    def get_private_key_hex(self) -> str:
        """Returns the private key serialized as PEM and then hex-encoded."""
        return self.private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption(),
        ).hex()

    def sign(self, data: str) -> str:
        """
        Generates a signature for the given data using the private key.
        """
        signature = self.private_key.sign(
            data.encode("utf-8"), ec.ECDSA(hashes.SHA256())
        )
        return signature.hex()

    @staticmethod
    def verify_signature(public_key_hex: str, signature_hex: str, data: str) -> bool:
        """
        Verifies a signature against the data using the public key.
        Static method so anyone can verify a transaction without needing a private key.
        """
        try:
            public_key = serialization.load_pem_public_key(
                bytes.fromhex(public_key_hex)
            )
            public_key.verify(
                bytes.fromhex(signature_hex),
                data.encode("utf-8"),
                ec.ECDSA(hashes.SHA256()),
            )
            return True
        except Exception:
            return False
