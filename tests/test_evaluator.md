# test_evaluator.py

evaluator 모듈 단위 테스트.

## 테스트 대상
- `src/evaluator.py`의 모든 공개 함수 및 상수

## 테스트 클래스 및 커버리지

### `TestBuildEvaluationPrompt` (8개 테스트)
- 채점기준표 텍스트 포함 확인
- 에세이 텍스트 포함 확인
- prompt injection 방어 문구 포함 확인
- JSON 형식 지시 포함 확인
- 반환 타입 문자열 확인
- 채점기준표 `<content>` 태그 감싸기 확인
- 에세이 `<content>` 태그 감싸기 확인
- `EVALUATION_PROMPT_TEMPLATE` 기반 생성 확인

### `TestCallGemini` (4개 테스트)
- `gemini-3-flash-preview` 모델명 사용 확인
- 프롬프트를 contents 파라미터로 전달 확인
- API 응답 텍스트 반환 확인
- `config.get_genai_client` 싱글턴 사용 확인

### `TestCallGeminiEmptyResponse` (2개 테스트)
- 빈 텍스트 응답 시 ValueError 발생 확인
- None 텍스트 응답 시 ValueError 발생 확인

### `TestCallOpenai` (4개 테스트)
- `gpt-5.2` 모델명 사용 확인
- user 메시지로 프롬프트 전달 확인
- API 응답 content 반환 확인
- `config.OPENAI_API_KEY` 및 timeout=180.0 사용 확인

### `TestCallOpenaiEmptyResponse` (2개 테스트)
- 빈 choices 응답 시 ValueError 발생 확인
- None content 응답 시 ValueError 발생 확인

### `TestCallAnthropic` (5개 테스트)
- `claude-sonnet-4-6` 모델명 사용 확인
- user 메시지로 프롬프트 전달 확인
- `max_tokens=4096` 설정 확인
- API 응답 텍스트 반환 확인
- `config.ANTHROPIC_API_KEY` 및 timeout=180.0 사용 확인

### `TestCallAnthropicEmptyResponse` (1개 테스트)
- 빈 content 응답 시 ValueError 발생 확인

### `TestParseEvaluationResponse` (13개 테스트)
- 유효한 JSON 파싱
- 마크다운 코드 펜스(```json) 내 JSON 파싱
- 일반 코드 펜스(```) 내 JSON 파싱
- JSON 앞에 설명 텍스트가 있는 경우 파싱
- JSON 뒤에 설명 텍스트가 있는 경우 파싱
- 유효하지 않은 JSON → `None` 반환
- `scores` 키 누락 → `None` 반환
- `feedback` 키 누락 → `None` 반환
- `scores`가 리스트가 아닌 경우 → `None` 반환
- `feedback`이 문자열이 아닌 경우 → `None` 반환
- scores 항목에 `번호`/`점수` 누락 → `None` 반환
- 빈 문자열 → `None` 반환
- 추가 필드가 있어도 정상 파싱

### `TestSumScores` (5개 테스트)
- 복수 항목 합산
- 단일 항목 반환
- 0점 합산
- 소수점 점수 합산
- float 반환 타입 확인

### `TestEvaluateEssay` (6개 테스트)
- `test_returns_all_model_results`: 3개 모델 응답이 `by_model`에 모두 포함
- `test_best_is_highest_score`: `best`가 최고점 응답
- `test_failed_model_is_none_in_by_model`: 실패 모델은 `by_model`에 `None`
- `test_invalid_response_is_none_in_by_model`: 파싱 실패 모델도 `by_model`에 `None`
- `test_all_fail_returns_none`: 전체 실패 시 `None` 반환
- `test_calls_build_evaluation_prompt`: 동일 프롬프트를 3개 LLM에 전달 확인
- 모든 테스트에서 `call_gemini`, `call_openai`, `call_anthropic`를 mock 처리

## 총 테스트 수: 50개
