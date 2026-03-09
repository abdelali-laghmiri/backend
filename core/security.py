from typing import Any, Optional,Dict
from datetime import datetime, timedelta
from jose import JWTError, jwt

from core.settings import settings


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    """Generate a signed JWT access token for the provided payload."""
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )

    to_encode.update({"exp": expire})

    encoded_jwt = jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM,
    )

    return encoded_jwt


def verify_access_token(token: str)-> Optional[Dict[str, Any]]:
    """Decode a JWT token and return its payload when valid."""
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM],
        )
        return payload
    except JWTError:
        return None
