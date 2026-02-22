"""auth 모듈 단위 테스트."""

import hashlib

from src.auth import hash_password, verify_password


class TestHashPassword:
    """hash_password 함수 테스트."""

    def test_returns_consistent_sha256_hex_digest(self):
        """동일 입력에 대해 항상 같은 SHA-256 hex digest를 반환한다."""
        password = "mySecret123"
        expected = hashlib.sha256(password.encode("utf-8")).hexdigest()

        result = hash_password(password)

        assert result == expected

    def test_returns_64_char_hex_string(self):
        """SHA-256 hex digest는 항상 64자 16진수 문자열이다."""
        result = hash_password("test")

        assert len(result) == 64
        assert all(c in "0123456789abcdef" for c in result)

    def test_different_passwords_produce_different_hashes(self):
        """서로 다른 비밀번호는 서로 다른 해시를 생성한다."""
        hash_a = hash_password("password_a")
        hash_b = hash_password("password_b")

        assert hash_a != hash_b

    def test_empty_string_hashes(self):
        """빈 문자열도 유효한 SHA-256 해시를 반환한다."""
        expected = hashlib.sha256(b"").hexdigest()

        result = hash_password("")

        assert result == expected


class TestVerifyPassword:
    """verify_password 함수 테스트."""

    def test_returns_true_for_correct_password(self):
        """올바른 비밀번호 입력 시 True를 반환한다."""
        password = "correct_password"
        stored_hash = hashlib.sha256(password.encode("utf-8")).hexdigest()

        assert verify_password(password, stored_hash) is True

    def test_returns_false_for_wrong_password(self):
        """틀린 비밀번호 입력 시 False를 반환한다."""
        stored_hash = hashlib.sha256(b"correct_password").hexdigest()

        assert verify_password("wrong_password", stored_hash) is False

    def test_returns_false_for_empty_password_against_nonempty_hash(self):
        """빈 문자열 비밀번호가 비어 있지 않은 해시와 불일치 시 False를 반환한다."""
        stored_hash = hashlib.sha256(b"some_password").hexdigest()

        assert verify_password("", stored_hash) is False

    def test_returns_true_for_empty_password_when_hash_matches(self):
        """빈 문자열 비밀번호와 빈 문자열 해시가 일치하면 True를 반환한다."""
        empty_hash = hashlib.sha256(b"").hexdigest()

        assert verify_password("", empty_hash) is True

    def test_returns_false_for_empty_stored_hash(self):
        """stored_hash가 빈 문자열이면 항상 False를 반환한다."""
        assert verify_password("any_password", "") is False
