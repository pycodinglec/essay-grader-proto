# app.py

Streamlit 웹 애플리케이션 진입점. 서논술형 에세이 자동 채점 전체 파이프라인의 UI 및 흐름 제어를 담당한다.

## 역할

- Streamlit 앱 설정 및 실행
- 파이프라인 단계별 UI 흐름 제어:
  1. 패스워드 인증
  2. 파일 업로드 (에세이 + 채점기준표)
  3. OCR 및 제출물 식별
  4. 채점기준표 검증
  5. 채점 진행 및 진행률 표시
  6. report.xlsx 다운로드

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

## 함수 목록

### 비즈니스 로직 (테스트 가능)

- `init_session_state()` -- 세션 상태 키를 기본값으로 초기화
- `format_progress_message(total, current)` -- "n개의 제출물 중 k번째 문서를 채점중..." 형식 메시지 생성
- `build_error_message(k)` -- 채점 에러 시 한국어 안내 메시지 생성
- `run_ocr_and_identify(files_data)` -- 파일 목록 OCR 수행 후 `submission.build_submissions` 호출, (submissions, unidentified) 반환
- `run_grading(submissions, rubric_text)` -- 제출물별 3-LLM 평가, 에러 시 부분 결과 보존, (graded, report_bytes, error_msg) 반환

### UI 렌더링 (Streamlit 의존)

- `show_login_page()` -- 패스워드 입력 및 인증 처리
- `show_upload_section()` -- 에세이 파일 업로드 UI
- `_process_essay_uploads(uploaded_files)` -- 업로드 파일 처리 헬퍼
- `_run_ocr_with_spinner()` -- OCR 실행 (스피너 표시)
- `show_identification_results(submissions, unidentified)` -- 제출물 식별 결과 표시
- `show_rubric_section()` -- 채점기준표 업로드 및 검증 UI
- `_validate_and_parse_rubric(rubric_file)` -- 채점기준표 검증/파싱 헬퍼
- `show_grading_section()` -- 채점 시작 버튼 및 진행률 UI
- `_execute_grading()` -- 채점 실행 및 진행률 표시
- `show_download_section(report_bytes, error_msg)` -- 리포트 다운로드 버튼 표시
- `main()` -- 앱 진입점, 세션 초기화 및 전체 흐름 제어

## UI 흐름

1. 미인증 -> `show_login_page()` 표시
2. 인증 완료 -> 에세이 업로드 -> OCR 및 식별 -> 결과 표시
3. 채점기준표 업로드 및 검증 -> 기준표 확인
4. 채점 시작 -> 진행률 바 + 상태 메시지 표시
5. 채점 완료 또는 에러 -> 다운로드 버튼 제공

## 에러 처리

- 채점 중 에러 발생 시 앱을 중단하지 않고 부분 결과를 보존한다.
- `evaluate_essay`가 None을 반환해도 에러로 처리한다.
- 에러 메시지: "k번째 작업물에서 에러가 발생하여 작업을 지속할 수 없습니다..."
- 부분 결과 다운로드 버튼을 제공한다.

## 의존 모듈

`src.auth`, `src.config`, `src.evaluator`, `src.file_handler`, `src.ocr`, `src.report`, `src.rubric`, `src.submission`
