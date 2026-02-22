# test_rubric.py

`src/rubric.py` 모듈의 단위 테스트.

## 테스트 헬퍼

### `_make_xlsx(headers, rows) -> bytes`
openpyxl Workbook을 이용해 인메모리 xlsx 바이트를 생성한다.

### `_make_valid_xlsx() -> bytes`
유효한 채점기준표(3행 데이터) xlsx 바이트를 반환한다.

## 테스트 커버리지

### TestValidateRubric (7개 테스트)
| 테스트 | 설명 |
|--------|------|
| `test_valid_rubric_returns_true` | 유효한 파일은 (True, "") 반환 |
| `test_missing_column_returns_false` | 열이 부족하면 False 반환 |
| `test_wrong_column_name_returns_false` | 열 이름이 틀리면 False 반환 |
| `test_empty_data_rows_returns_false` | 데이터 행 없으면 False 반환 |
| `test_non_numeric_score_returns_false` | 배점이 문자열이면 False 반환 |
| `test_float_score_is_valid` | 배점이 float이면 유효 |
| `test_invalid_bytes_returns_false` | xlsx가 아닌 바이트는 False 반환 |

### TestParseRubric (6개 테스트)
| 테스트 | 설명 |
|--------|------|
| `test_parse_returns_list_of_dicts` | dict 리스트 반환 확인 |
| `test_parse_dict_keys` | 번호/채점기준/배점 키 존재 확인 |
| `test_parse_preserves_order` | 행 순서 보존 확인 |
| `test_parse_values_correct` | 파싱 값 정확성 확인 |
| `test_parse_invalid_file_raises_value_error` | 유효하지 않은 파일 시 ValueError |
| `test_parse_corrupt_bytes_raises_value_error` | 손상된 바이트 시 ValueError |

### TestFormatRubricForDisplay (5개 테스트)
| 테스트 | 설명 |
|--------|------|
| `test_format_includes_header` | 첫 줄에 헤더 포함 확인 |
| `test_format_includes_data_rows` | 데이터 행 수 확인 |
| `test_format_uses_pipe_separator` | 파이프 구분자 사용 확인 |
| `test_format_data_values_present` | 데이터 값 정확성 확인 |
| `test_format_empty_list` | 빈 리스트 시 헤더만 반환 확인 |

## 총 테스트: 18개
