"""패스워드 인증 모듈."""

import hashlib


def hash_password(password: str) -> str:
    """SHA-256 해시를 생성하여 hex digest 문자열로 반환한다.

    Args:
        password: 해시할 비밀번호 문자열.

    Returns:
        64자 길이의 SHA-256 hex digest.
    """
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


def verify_password(password: str, stored_hash: str) -> bool:
    """입력 비밀번호의 해시가 저장된 해시와 일치하는지 검증한다.

    Args:
        password: 사용자가 입력한 비밀번호.
        stored_hash: 저장된 SHA-256 hex digest.

    Returns:
        일치하면 True, 불일치하면 False.
    """
    if not stored_hash:
        return False
    return hash_password(password) == stored_hash
