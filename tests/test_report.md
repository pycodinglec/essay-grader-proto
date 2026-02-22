# test_report.py

report 모듈(`src/report.py`) 단위 테스트.

## 테스트 대상 함수

### TestAssignWorkNumbers (8개 테스트)
- `test_single_student_single_work`: 학생 1명, 작품 1개 -> 작품번호 1
- `test_single_student_multiple_works`: 학생 1명, 작품 3개 -> 순서대로 1, 2, 3
- `test_multiple_students_independent_numbering`: 학생별 독립 번호 부여
- `test_preserves_appearance_order`: 원본 등장 순서 기반 번호 부여
- `test_feedback_extracted_from_evaluation`: evaluation.feedback -> 피드백 키 추출
- `test_output_keys`: 반환 dict에 학번/이름/작품번호/피드백 키만 존재
- `test_empty_input`: 빈 리스트 입력 -> 빈 리스트 반환
- `test_student_name_preserved`: 학번, 이름 원본 값 유지

### TestGenerateReportBytes (7개 테스트)
- `test_returns_bytes`: 반환값이 bytes 타입
- `test_valid_xlsx`: 유효한 xlsx 파일로 로드 가능
- `test_correct_headers`: 첫 행에 학번/이름/작품번호/피드백 헤더
- `test_correct_data_rows`: 데이터 행 값이 정확
- `test_sorted_by_student_id_then_work_number`: 학번 -> 작품번호 오름차순 정렬
- `test_empty_data_returns_headers_only`: 빈 데이터 -> 헤더만
- `test_multiple_rows_count`: 행 수가 입력과 일치

### TestBuildReport (4개 테스트)
- `test_returns_bytes`: bytes 반환 확인
- `test_end_to_end_single_student`: 단일 학생 통합 검증
- `test_end_to_end_multiple_students_sorted`: 다수 학생 정렬 통합 검증
- `test_empty_submissions`: 빈 제출물 -> 헤더만 있는 xlsx

## 헬퍼
- `_make_submission()`: 테스트용 제출물 dict 생성 유틸리티

## 총 테스트 수: 19개
