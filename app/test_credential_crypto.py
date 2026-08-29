from app.services.credential_crypto import (
    EncryptionError,
    decrypt_credentials,
    encrypt_credentials,
)


def _assert(cond, msg):
    if not cond:
        raise AssertionError(msg)
    print(f"  [PASS] {msg}")


def run():
    print("Test 1: encrypt -> decrypt round-trip")
    plain = '{"token": "secret-value-123"}'
    blob = encrypt_credentials(plain)
    _assert(decrypt_credentials(blob) == plain, "round-trip decrypt returned original plaintext")

    print("Test 2: plaintext is not stored in the encrypted blob")
    plain_bytes = plain.encode("utf-8")
    _assert(plain_bytes not in blob, "plaintext bytes not in blob")
    _assert(b"token" not in blob, "no plaintext substring remains in blob")

    print("Test 3: fresh random nonce -> same plaintext yields different blob each time")
    blob1 = encrypt_credentials(plain)
    blob2 = encrypt_credentials(plain)
    _assert(blob1 != blob2, "two encrypts of same plaintext differ (new nonce)")

    print("Test 4: wrong key is rejected")
    wrong_blob = encrypt_credentials(plain)
    wrong_key_raw = "ff" * 32  # 32 bytes, not the real key
    import os
    prev = os.environ.get("CREDENTIAL_ENCRYPTION_KEY")
    os.environ["CREDENTIAL_ENCRYPTION_KEY"] = wrong_key_raw
    rejected = False
    try:
        decrypt_credentials(wrong_blob)
    except EncryptionError:
        rejected = True
    finally:
        if prev is None:
            os.environ.pop("CREDENTIAL_ENCRYPTION_KEY", None)
        else:
            os.environ["CREDENTIAL_ENCRYPTION_KEY"] = prev
    _assert(rejected, "decrypt with wrong key raised EncryptionError")

    print("Test 5: tampered ciphertext is rejected")
    tampered = bytearray(encrypt_credentials(plain))
    tampered[-1] ^= 0xFF  # flip the last byte (inside GCM tag)
    rejected = False
    try:
        decrypt_credentials(bytes(tampered))
    except EncryptionError:
        rejected = True
    _assert(rejected, "decrypt of tampered ciphertext raised EncryptionError")

    print("Test 6: missing key raises EncryptionError")
    prev = os.environ.get("CREDENTIAL_ENCRYPTION_KEY")
    os.environ.pop("CREDENTIAL_ENCRYPTION_KEY", None)
    raised = False
    try:
        encrypt_credentials(plain)
    except EncryptionError:
        raised = True
    finally:
        if prev is not None:
            os.environ["CREDENTIAL_ENCRYPTION_KEY"] = prev
    _assert(raised, "encrypt without key raised EncryptionError")

    print("Test 7: no plaintext appears in logs (module contains no logging)")
    import inspect
    import app.services.credential_crypto as mod
    src = inspect.getsource(mod)
    _assert("print(" not in src and "logging" not in src, "crypto module has no print/log statements")

    print("\nALL TESTS PASSED")


if __name__ == "__main__":
    run()
