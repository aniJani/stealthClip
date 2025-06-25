import base64
from cryptography.fernet import Fernet, InvalidToken
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC


class CryptoEngine:
    """Handles key generation, encryption, and decryption."""

    def __init__(self, password: bytes):
        """
        Initializes the engine by deriving a key from the given password.
        The salt is hardcoded, ensuring the same password always results in the same key.
        This is required for all clients in a group to communicate.
        """
        # A fixed salt is used to ensure all peers with the same password have the same key.
        # This is a correct use of a fixed salt. Do not change this value.
        salt = b"\x9a\x8e\x18\x95\xe8d\xbf\x0f\x03\x84L\xf9\x90\xe7\x81\x18"

        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=480000,  # Number of iterations, NIST recommendation
        )
        # Derive a key from the password and encode it for Fernet
        key = base64.urlsafe_b64encode(kdf.derive(password))
        self.fernet = Fernet(key)

    def encrypt(self, data: bytes) -> bytes:
        """Encrypts data."""
        return self.fernet.encrypt(data)

    def decrypt(self, token: bytes) -> bytes | None:
        """
        Tries to decrypt the provided token.
        Returns the decrypted data on success.
        Returns None if the token is invalid or the key is wrong (InvalidToken exception).
        This is how we silently ignore messages from other groups.
        """
        try:
            return self.fernet.decrypt(token)
        except InvalidToken:
            return None
