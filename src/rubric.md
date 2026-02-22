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

## 함수

### `validate_rubric(file_bytes: bytes) -> tuple[bool, str]`
xlsx 바이트를 받아 채점기준표 양식을 검증한다.
- 유효한 xlsx 파일인지 확인
- 헤더가 `["번호", "채점기준", "배점"]`인지 확인
- 데이터 행이 1개 이상 존재하는지 확인
- 배점 열 값이 숫자인지 확인
- 반환: `(True, "")` 유효, `(False, "에러메시지")` 유효하지 않음

### `parse_rubric(file_bytes: bytes) -> list[dict]`
xlsx 바이트를 받아 채점기준표 데이터를 파싱한다.
- 내부적으로 `validate_rubric`을 호출하여 검증
- 유효하지 않으면 `ValueError` 발생
- 반환: `[{"번호": int, "채점기준": str, "배점": int|float}, ...]`
- xlsx 행 순서 보존

### `format_rubric_for_display(rubric_data: list[dict]) -> str`
채점기준표 데이터를 사용자에게 보여줄 문자열로 변환한다.
- 입력: `parse_rubric`이 반환하는 dict 리스트
- 출력 형식: `"번호 | 채점기준 | 배점\n1 | ... | ..."`
- 빈 리스트일 경우 헤더만 반환
