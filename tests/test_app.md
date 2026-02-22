# test_app.py

`app.py`의 비즈니스 로직 헬퍼 함수에 대한 단위 테스트.

## 테스트 전략

Streamlit UI 렌더링은 직접 테스트하지 않는다. 대신 비즈니스 로직이 담긴 순수 함수들을 외부 의존성 모킹과 함께 테스트한다.

## 테스트 클래스 및 커버리지

### TestRunOcrAndIdentify (4개 테스트)

`run_ocr_and_identify` 함수를 테스트한다. `ocr.ocr_file`과 `submission.build_submissions`를 모킹한다.

- `test_returns_submissions_and_unidentified` -- 정상 흐름에서 식별/미식별 결과 반환 확인
- `test_builds_correct_file_texts_structure` -- `build_submissions`에 전달되는 `(filename, texts)` 구조 검증
- `test_empty_file_list` -- 빈 입력에 대한 빈 결과 반환 확인
- `test_multiple_files_ocr_called_for_each` -- 각 파일별 `ocr_file` 호출 횟수 검증

### TestRunGrading (8개 테스트)

`run_grading` 함수를 테스트한다. `evaluator.evaluate_essay`와 `report.build_report`를 모킹한다.

- `test_normal_flow_all_succeed` -- 전체 성공 시 graded, report_bytes, None 반환
- `test_graded_submissions_contain_evaluation` -- 채점 결과가 `'평가결과'` 키로 추가됨
- `test_mid_process_error_returns_partial_results` -- 중간 에러 시 부분 결과 + 에러 메시지
- `test_error_message_format` -- 에러 메시지 한국어 형식 검증
- `test_evaluate_returns_none_treated_as_error` -- None 반환 시 에러 처리
- `test_report_build_called_with_graded_submissions` -- `build_report` 호출 인자 검증
- `test_empty_submissions_returns_empty` -- 빈 제출물에 대한 처리
- `test_error_on_third_of_five_submissions` -- 5개 중 3번째 에러 시 2개만 결과에 포함

### TestProgressMessage (3개 테스트)

`format_progress_message` 함수를 테스트한다.

- `test_format_progress_message` -- 기본 형식 "n개의 제출물 중 k번째 문서를 채점중..."
- `test_format_progress_message_first` -- 첫 번째 문서
- `test_format_progress_message_last` -- 마지막 문서

### TestBuildErrorMessage (2개 테스트)

`build_error_message` 함수를 테스트한다.

- `test_error_message_contains_index` -- 작업물 번호 포함 여부
- `test_error_message_contains_required_phrases` -- 필수 안내 문구 포함 여부

### TestShowPromptsSection (2개 테스트)

프롬프트 공개 섹션을 테스트한다.

- `test_function_exists` -- `show_prompts_section` 함수 존재 확인
- `test_splitter_prompt_description_exists` -- `SPLITTER_PROMPT_DESCRIPTION` 상수 존재 확인

## 총 테스트 수

21개 테스트
