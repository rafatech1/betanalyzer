import pytest
from fastapi import HTTPException

from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
)


def test_hash_password_does_not_store_plaintext() -> None:
    hashed = hash_password("minha-senha-secreta")
    assert hashed != "minha-senha-secreta"
    assert verify_password("minha-senha-secreta", hashed) is True


def test_verify_password_rejects_wrong_password() -> None:
    hashed = hash_password("correta")
    assert verify_password("errada", hashed) is False


def test_access_token_round_trip_contains_subject_and_role() -> None:
    token = create_access_token(user_id=42, role="admin")
    payload = decode_token(token)
    assert payload["sub"] == "42"
    assert payload["role"] == "admin"
    assert payload["type"] == "access"


def test_refresh_token_round_trip_contains_jti() -> None:
    token, jti = create_refresh_token(user_id=7)
    payload = decode_token(token)
    assert payload["sub"] == "7"
    assert payload["type"] == "refresh"
    assert payload["jti"] == jti


def test_decode_token_raises_401_for_garbage_token() -> None:
    with pytest.raises(HTTPException) as exc_info:
        decode_token("not-a-valid-token")
    assert exc_info.value.status_code == 401
