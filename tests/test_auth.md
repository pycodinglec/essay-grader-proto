# test_auth.py

`src/auth.py` 모듈의 단위 테스트.

## 테스트 커버리지: 100%

## TestHashPassword (4개 테스트)

| 테스트 | 검증 내용 |
|--------|-----------|
| `test_returns_consistent_sha256_hex_digest` | 동일 입력에 대해 표준 SHA-256 hex digest와 일치하는 결과를 반환 |
| `test_returns_64_char_hex_string` | 반환값이 64자 16진수 문자열인지 확인 |
| `test_different_passwords_produce_different_hashes` | 서로 다른 비밀번호가 서로 다른 해시를 생성 |
| `test_empty_string_hashes` | 빈 문자열 입력 시에도 유효한 SHA-256 해시를 반환 |

## TestVerifyPassword (5개 테스트)

| 테스트 | 검증 내용 |
|--------|-----------|
| `test_returns_true_for_correct_password` | 올바른 비밀번호 입력 시 `True` 반환 |
| `test_returns_false_for_wrong_password` | 틀린 비밀번호 입력 시 `False` 반환 |
| `test_returns_false_for_empty_password_against_nonempty_hash` | 빈 비밀번호와 비어있지 않은 해시 비교 시 `False` 반환 |
| `test_returns_true_for_empty_password_when_hash_matches` | 빈 비밀번호의 해시가 stored_hash와 일치하면 `True` 반환 |
| `test_returns_false_for_empty_stored_hash` | `stored_hash`가 빈 문자열이면 항상 `False` 반환 |

## 총 9개 테스트
