import secrets

from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError, VerificationError, InvalidHashError
from itsdangerous import BadSignature, URLSafeSerializer

from .config import settings

_ph = PasswordHasher()
_serializer = URLSafeSerializer(settings.secret_key, salt="session")

SESSION_COOKIE = "bc_session"


def hash_password(password: str) -> str:
    return _ph.hash(password)


def verify_password(password: str, password_hash: str) -> bool:
    try:
        return _ph.verify(password_hash, password)
    except (VerifyMismatchError, VerificationError, InvalidHashError):
        return False


def new_session_token() -> str:
    """Token casuale memorizzato nel DB (sessione server-side)."""
    return secrets.token_urlsafe(32)


def sign_token(token: str) -> str:
    """Valore firmato da mettere nel cookie (non manomettibile dal client)."""
    return _serializer.dumps(token)


def unsign_token(signed: str) -> str | None:
    try:
        return _serializer.loads(signed)
    except BadSignature:
        return None
