from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError

ph = PasswordHasher()


def hash_key(key: str) -> str:
    return ph.hash(key)


def verify_key(key: str, hash: str) -> bool:  # noqa
    try:
        ph.verify(hash=hash, password=key)
        return True
    except VerifyMismatchError:
        return False
