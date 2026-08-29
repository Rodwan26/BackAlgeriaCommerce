import time


def verify(credentials: dict) -> tuple[bool, str]:
    """Mock external carrier result. Returns (ok, code)."""
    if "__timeout__" in credentials.values():
        time.sleep(0.1)
        return False, "timeout"

    if "__fail__" in credentials.values():
        return False, "invalid_credentials"

    return True, ""
