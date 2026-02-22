# test_essay_splitter.py

`essay_splitter` 모듈의 단위 테스트.

## 테스트 클래스 구조

### TestBuildSplitterPrompt (4 tests)
`build_splitter_prompt` 함수의 프롬프트 생성 검증.
- 페이지 에세이텍스트 포함 여부
- 학번 포함 여부
- prompt injection 방어 문구 포함 여부
- 에세이텍스트 100자 절삭

### TestParseBoundaryResponse (7 tests)
`parse_boundary_response` 함수의 파싱 및 유효성 검증.
- 유효 JSON 배열 파싱
- 마크다운 코드 펜스 내 JSON 파싱
- 유효하지 않은 JSON 폴백
- 빈 응답 폴백
- 범위 초과 인덱스 폴백
- 누락 페이지 폴백
- 단일 그룹 유효 처리

### TestCallSplitterLlm (3 tests)
`call_splitter_llm` 함수의 API 호출 검증. `google.genai` 모킹.
- 올바른 모델명 (gemini-3.1-pro-preview)
- 프롬프트를 contents 파라미터로 전달
- 응답 텍스트 반환

### TestDetectBoundaries (3 tests)
`detect_boundaries` 함수의 통합 검증. `call_splitter_llm` 모킹.
- 정상 LLM 응답에서 올바른 그룹 반환
- LLM 호출 예외 시 폴백
- 유효하지 않은 LLM 응답 시 폴백

### TestSplitEssays (8 tests)
`split_essays` 함수의 분할 로직 검증. `call_splitter_llm` 모킹.
- 단일 페이지 파일: LLM 미호출, 그대로 반환
- 다중 페이지 단일 에세이: 원본 파일명 유지
- 다중 페이지 복수 에세이: 분리 및 #N 접미사
- 파일명 접미사 규칙 (#1, #2)
- 단일 에세이 시 접미사 미부착
- 단일/다중 파일 혼합 처리
- LLM 실패 시 전체 페이지 보존
- 빈 입력 처리
