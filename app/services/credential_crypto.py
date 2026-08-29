import os

from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from dotenv import load_dotenv

load_dotenv()


class EncryptionError(Exception):
    pass


_NONCE_LENGTH = 12
_TAG_LENGTH = 16


def _load_key() -> bytes:
    raw = os.getenv("CREDENTIAL_ENCRYPTION_KEY")

    if not raw:
        raise EncryptionError(
            "CREDENTIAL_ENCRYPTION_KEY is not set"
        )

    try:
        key = bytes.fromhex(raw)
    except ValueError:
        raise EncryptionError(
            "CREDENTIAL_ENCRYPTION_KEY must be a hex string"
        )

    if len(key) != 32:
        raise EncryptionError(
            "CREDENTIAL_ENCRYPTION_KEY must decode to 32 bytes"
        )

    return key


def encrypt_credentials(plaintext: str) -> bytes:
    key = _load_key()
    aesgcm = AESGCM(key)

    nonce = os.urandom(_NONCE_LENGTH)
    ciphertext_with_tag = aesgcm.encrypt(nonce, plaintext.encode("utf-8"), None)

    return nonce + ciphertext_with_tag


def decrypt_credentials(payload: bytes) -> str:
    key = _load_key()
    aesgcm = AESGCM(key)

    if len(payload) < _NONCE_LENGTH + _TAG_LENGTH:
        raise EncryptionError(
            "Encrypted payload is too short"
        )

    nonce = payload[:_NONCE_LENGTH]
    ciphertext_with_tag = payload[_NONCE_LENGTH:]

    try:
        plaintext = aesgcm.decrypt(nonce, ciphertext_with_tag, None)
    except Exception:
        raise EncryptionError(
            "Failed to decrypt credentials: ciphertext was tampered with or key is wrong"
        )

    return plaintext.decode("utf-8")
