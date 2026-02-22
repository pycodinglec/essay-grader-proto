# app.py

Streamlit 웹 애플리케이션 진입점. 서논술형 에세이 자동 채점 전체 파이프라인의 UI 및 흐름 제어를 담당한다.

## 역할

- Streamlit 앱 설정 및 실행
- 파이프라인 단계별 UI 흐름 제어:
  1. 패스워드 인증
  2. 채점기준표 업로드 및 검증 (Step 1)
  3. 에세이 파일 업로드 + 자동 OCR 및 제출물 식별 (채점기준표 검증 후 활성화, Step 2)
  4. 채점 진행 및 진행률 표시 (Step 4)
  5. report.xlsx 다운로드 (Step 5)

## 세션 상태 관리

`st.session_state`를 사용하여 파이프라인 단계 간 상태를 유지한다.

| 키 | 타입 | 설명 |
|---|---|---|
| `authenticated` | bool | 패스워드 인증 여부 |
| `uploaded_files_data` | list[tuple[str, bytes]] | 처리된 업로드 파일 |
| `submissions` | list[dict] | 식별된 제출물 |
| `unidentified` | list[str] | 미식별 파일명 |
| `rubric_data` | list[dict] | 파싱된 채점기준표 |
| `rubric_text` | str | LLM 프롬프트용 채점기준 텍스트 |
| `grading_complete` | bool | 채점 완료 여부 |
| `report_bytes` | bytes | 생성된 xlsx 바이트 |
| `grading_error` | str \| None | 채점 중 에러 메시지 |

## 상수

### `SPLITTER_PROMPT_DESCRIPTION`
에세이 분할 프롬프트의 구조를 설명하는 텍스트. 프롬프트 공개 섹션에서 표시된다.

## 함수 목록

### 비즈니스 로직 (테스트 가능)

- `init_session_state()` -- 세션 상태 키를 기본값으로 초기화
- `format_progress_message(total, current)` -- "n개의 제출물 중 k번째 문서를 채점중..." 형식 메시지 생성
- `build_error_message(k)` -- 채점 에러 시 한국어 안내 메시지 생성
- `run_ocr_and_identify(files_data, on_progress=None)` -- 파일 목록 OCR 수행 후 `essay_splitter.split_essays`로 에세이 분리, `submission.build_submissions` 호출, (submissions, unidentified) 반환. `on_progress` 콜백으로 OCR 진행률 알림
- `format_ocr_progress_message(total, current)` -- "N개 파일 중 K번째 파일 OCR 중..." 형식 메시지 생성
- `run_grading(submissions, rubric_text, on_progress=None)` -- 제출물별 3-LLM 평가, `on_progress(current, total)` 콜백으로 진행률 알림, 에러 시 부분 결과 보존, (graded, report_bytes, error_msg) 반환

### UI 렌더링 (Streamlit 의존)

- `show_prompts_section()` -- 사용 중인 LLM 프롬프트를 expander로 표시 (OCR/에세이 분할/채점 프롬프트). 인증 직후 `main()`에서 호출
- `show_login_page()` -- 패스워드 입력 및 인증 처리
- `show_upload_section()` -- 에세이 파일 업로드 UI (채점기준표 검증 후 표시, 파일 처리 시 자동 OCR 실행)
- `_process_essay_uploads(uploaded_files)` -- 업로드 파일 처리 헬퍼
- `_run_ocr_with_progress()` -- OCR 실행 (진행률 바 + 상태 텍스트 표시)
- `show_identification_results(submissions, unidentified)` -- 제출물 식별 결과 표시
- `show_rubric_section()` -- 채점기준표 업로드 및 검증 UI (인증 후 항상 표시)
- `_validate_and_parse_rubric(rubric_file)` -- 채점기준표 검증/파싱 헬퍼
- `show_grading_section()` -- 채점 시작 버튼 및 진행률 UI
- `_execute_grading()` -- `run_grading`을 `on_progress` 콜백과 함께 호출하여 채점 실행 및 진행률 표시. 채점 로직을 자체 구현하지 않고 `run_grading`에 위임.
- `show_download_section(report_bytes, error_msg)` -- 리포트 다운로드 버튼 표시
- `main()` -- 앱 진입점, 세션 초기화 및 전체 흐름 제어

## 진행률 표시

- `_execute_grading`은 `run_grading`에 `on_progress` 콜백을 전달한다.
- 콜백은 각 에세이 채점 **시작 전**에 호출된다: `on_progress(current, total)`
- 진행률 바: `progress_bar.progress((current - 1) / total)` — 완료된 분량만 반영
- 모두 성공 시에만 `progress_bar.progress(1.0)` + "채점이 완료되었습니다!"

### OCR 진행률 표시

- `_run_ocr_with_progress`는 `run_ocr_and_identify`에 `on_progress` 콜백을 전달한다.
- 콜백은 각 파일 OCR **시작 전**에 호출된다: `on_progress(current, total)`
- 진행률 바: `progress_bar.progress((current - 1) / total)` — 완료된 분량만 반영
- 완료 시 `progress_bar.progress(1.0)` + "OCR 완료!"

## UI 흐름

1. 미인증 -> `show_login_page()` 표시
2. 인증 완료 -> 프롬프트 공개 (`show_prompts_section()`)
3. 채점기준표 업로드 및 검증 -> 기준표 확인
4. (rubric_data 존재 시) 에세이 업로드 -> 파일 처리 버튼 -> 자동 OCR+식별 (진행률 바)
5. 제출물 식별 결과 표시
6. 채점 시작 -> 진행률 바 + 상태 메시지 표시
7. 채점 완료 또는 에러 -> 다운로드 버튼 제공

## 에러 처리

- 채점 중 에러 발생 시 앱을 중단하지 않고 부분 결과를 보존한다.
- `evaluate_essay`가 None을 반환해도 에러로 처리한다.
- 에러 메시지: "k번째 작업물에서 에러가 발생하여 작업을 지속할 수 없습니다..."
- 부분 결과 다운로드 버튼을 제공한다.

## 의존 모듈

`collections.abc`, `src.auth`, `src.config`, `src.essay_splitter`, `src.evaluator`, `src.file_handler`, `src.ocr`, `src.report`, `src.rubric`, `src.submission`

## 파이프라인 변경 사항

OCR 결과를 바로 `build_submissions`에 전달하지 않고, `essay_splitter.split_essays`를 거쳐 에세이를 분리한 후 전달한다:
OCR -> `essay_splitter.split_essays` -> `submission.build_submissions`
