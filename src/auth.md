# auth.py

패스워드 인증 모듈.

## 역할
- 사용자 입력 패스워드를 SHA-256 해시하여 저장된 해시와 비교
- 인증 성공 시 메뉴 접근 허용

## 함수

### `hash_password(password: str) -> str`
- 입력 비밀번호 문자열을 UTF-8로 인코딩한 뒤 SHA-256 해시를 생성한다.
- 64자 길이의 hex digest 문자열을 반환한다.
- 동일 입력에 대해 항상 동일한 결과를 반환한다(결정적).

### `verify_password(password: str, stored_hash: str) -> bool`
- 입력 비밀번호를 `hash_password`로 해시한 뒤 `stored_hash`와 비교한다.
- 일치하면 `True`, 불일치하면 `False`를 반환한다.
- `stored_hash`가 빈 문자열인 경우 항상 `False`를 반환한다(미설정 방지).

## 의존성
- `hashlib` (표준 라이브러리)

## 사용 예시
```python
from src.auth import hash_password, verify_password
from src.config import PASSWORD_HASH

hashed = hash_password("my_secret")
is_valid = verify_password("my_secret", PASSWORD_HASH)
```
