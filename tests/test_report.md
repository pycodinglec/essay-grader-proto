# test_report.py

report 모듈(`src/report.py`) 단위 테스트.

## 테스트 대상 함수

### TestAssignWorkNumbers (11개 테스트)
- `test_single_student_single_work`: 학생 1명, 작품 1개 -> 작품번호 1
- `test_single_student_multiple_works`: 학생 1명, 작품 3개 -> 순서대로 1, 2, 3
- `test_multiple_students_independent_numbering`: 학생별 독립 번호 부여
- `test_output_has_11_keys`: 반환 dict에 11개 키 존재 확인
- `test_model_scores_extracted`: 모델별 점수(GPT/Gemini/Claude) 추출 확인
- `test_model_feedbacks_extracted`: 모델별 피드백 추출 확인
- `test_failed_model_shows_empty_string`: 실패 모델은 빈 문자열로 표시
- `test_final_score_from_best`: 최종 점수가 best의 합산 점수
- `test_essay_text_preserved`: 에세이 원문 보존 확인
- `test_empty_input`: 빈 리스트 입력 -> 빈 리스트 반환
- `test_student_name_preserved`: 학번, 이름 원본 값 유지

### TestGenerateReportBytes (7개 테스트)
- `test_returns_bytes`: 반환값이 bytes 타입
- `test_valid_xlsx`: 유효한 xlsx 파일로 로드 가능
- `test_correct_headers`: 첫 행에 11개 헤더
- `test_correct_data_rows`: 데이터 행 값이 정확
- `test_sorted_by_student_id_then_work_number`: 학번 -> 작품번호 오름차순 정렬
- `test_empty_data_returns_headers_only`: 빈 데이터 -> 헤더만
- `test_multiple_rows_count`: 행 수가 입력과 일치

### TestBuildReport (4개 테스트)
- `test_returns_bytes`: bytes 반환 확인
- `test_end_to_end_single_student`: 단일 학생 통합 검증 (모델별 점수/최종 점수)
- `test_end_to_end_multiple_students_sorted`: 다수 학생 정렬 통합 검증
- `test_empty_submissions`: 빈 제출물 -> 헤더만 있는 xlsx

## 헬퍼
- `_make_submission()`: 테스트용 제출물 dict 생성 (새 `best`/`by_model` 구조 지원, `failed_models` 파라미터)
- `_make_report_row()`: 테스트용 11개 키 리포트 데이터 dict 생성

## 총 테스트 수: 22개
