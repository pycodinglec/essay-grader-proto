# rubric.py

채점기준표 검증 모듈.

## 역할
- xlsx 파일에서 채점기준표 읽기
- 양식 검증 (번호/채점기준/배점 3개 열)
- 검증된 기준표 데이터 반환
- 채점기준표를 사용자 표시용 문자열로 변환

## 의존성
- `openpyxl`: xlsx 파일 읽기

## xlsx 양식 요구사항
| 열 | 헤더 이름 | 타입 |
|----|-----------|------|
| A  | 번호      | any  |
| B  | 채점기준  | str  |
| C  | 배점      | int 또는 float |

- 첫 번째 행은 반드시 헤더: `번호`, `채점기준`, `배점`
- 데이터 행이 최소 1개 이상 존재해야 함
- 배점 열은 반드시 숫자(int 또는 float)

## 내부 구조

### `_read_and_validate(file_bytes: bytes) -> tuple[bool, str, list[tuple]]`
xlsx 바이트를 **1회만 읽어** 검증과 데이터 행 반환을 동시에 수행한다.
- `validate_rubric`과 `parse_rubric` 모두 이 함수를 호출하여 중복 읽기를 방지한다.
- 반환: `(유효여부, 에러메시지, 데이터행_리스트)` 튜플

## 함수

### `validate_rubric(file_bytes: bytes) -> tuple[bool, str]`
xlsx 바이트를 받아 채점기준표 양식을 검증한다.
- `_read_and_validate`를 호출하여 `(ok, msg)`만 반환
- 반환: `(True, "")` 유효, `(False, "에러메시지")` 유효하지 않음

### `parse_rubric(file_bytes: bytes) -> list[dict]`
xlsx 바이트를 받아 채점기준표 데이터를 파싱한다.
- `_read_and_validate`를 호출하여 행 데이터로 직접 dict 리스트 생성
- 유효하지 않으면 `ValueError` 발생
- 반환: `[{"번호": int, "채점기준": str, "배점": int|float}, ...]`
- xlsx 행 순서 보존

### `format_rubric_for_display(rubric_data: list[dict]) -> str`
채점기준표 데이터를 사용자에게 보여줄 문자열로 변환한다.
- 입력: `parse_rubric`이 반환하는 dict 리스트
- 출력 형식: `"번호 | 채점기준 | 배점\n1 | ... | ..."`
- 빈 리스트일 경우 헤더만 반환
