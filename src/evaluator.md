# evaluator.py

3-LLM 평가 모듈.

## 역할
- Gemini 3 Flash, GPT 5.2, Sonnet 4.6에 동일 프롬프트 전송
- 각 LLM 응답의 점수 합산 후 최고점 응답 채택
- prompt injection 방어 문구 포함
- structured output(JSON) 형태로 응답 파싱

## 상수

### `EVALUATION_PROMPT_TEMPLATE`
- 3개 LLM에 전송하는 공통 프롬프트 템플릿
- prompt injection 방어 문구가 앞에 포함됨
- `{rubric}`, `{essay}` 플레이스홀더를 사용하며, 각각 `<content>` 태그로 감싸서 사용자 입력 영역을 명시
- JSON 형식(`scores`, `feedback`) 응답을 요구

## 공개 함수

### `build_evaluation_prompt(rubric_text: str, essay_text: str) -> str`
- `EVALUATION_PROMPT_TEMPLATE`에 채점기준표와 에세이 텍스트를 대입하여 완성된 프롬프트 문자열을 반환

### `call_gemini(prompt: str) -> str`
- `config.get_genai_client()` 싱글턴을 사용하여 Gemini 3 Flash API 호출
- 모델명: `gemini-3-flash-preview`
- 빈 응답(`.text`가 빈 문자열 또는 None)일 경우 `ValueError` 발생
- 응답의 `.text` 반환

### `call_openai(prompt: str) -> str`
- openai SDK를 사용하여 GPT 5.2 API 호출
- `config.OPENAI_API_KEY` 사용, `timeout=180.0` 설정 (3분)
- 모델명: `gpt-5.2`
- 빈 choices 또는 빈 content일 경우 `ValueError` 발생
- user 메시지로 프롬프트를 전달하고 `.choices[0].message.content` 반환

### `call_anthropic(prompt: str) -> str`
- anthropic SDK를 사용하여 Sonnet 4.6 API 호출
- `config.ANTHROPIC_API_KEY` 사용, `timeout=180.0` 설정 (3분)
- 모델명: `claude-sonnet-4-6`, `max_tokens=4096`
- 빈 content일 경우 `ValueError` 발생
- user 메시지로 프롬프트를 전달하고 `.content[0].text` 반환

### `parse_evaluation_response(response_text: str) -> dict | None`
- LLM 응답 텍스트를 JSON으로 파싱
- 마크다운 코드 펜스(` ```json ``` ` 또는 ` ``` ``` `)를 자동 제거
- 구조 검증: `scores`(리스트, 각 항목에 `번호`와 `점수`), `feedback`(문자열)
- 유효하지 않으면 `None` 반환

### `sum_scores(evaluation: dict) -> float`
- `evaluation["scores"]`의 모든 `점수` 값을 합산하여 float 반환

### `evaluate_essay(essay_text: str, rubric_text: str) -> dict | None`
- 프롬프트를 생성하고 3개 LLM을 병렬 호출 (ThreadPoolExecutor, max_workers=3)
- 각 응답을 파싱하고 점수를 합산하여 최고점 응답을 `best`로 선택
- 모든 모델의 결과를 `by_model`에 보존 (실패/파싱 실패 시 `None`)
- 반환 구조: `{"best": {"scores": [...], "feedback": "..."}, "by_model": {"gemini": dict|None, "openai": dict|None, "anthropic": dict|None}}`
- 모든 LLM이 실패하거나 유효한 응답이 없으면 `None` 반환

## 내부 함수

### `_extract_json_string(text: str) -> str`
- 응답 텍스트에서 JSON 문자열을 추출. 1순위: 마크다운 코드 펜스 내부, 2순위: 첫 `{`부터 마지막 `}`까지, 3순위: 원본 텍스트

### `_validate_evaluation_dict(data: dict) -> bool`
- 파싱된 평가 결과의 구조를 검증 (`scores` 리스트, `feedback` 문자열, 각 항목의 `번호`/`점수`)

### `_collect_responses(prompt: str) -> list[tuple[str, str | None]]`
- ThreadPoolExecutor(max_workers=3)로 3개 LLM을 병렬 호출하여 (이름, 응답텍스트) 목록 반환, 실패 시 `None` 기록 및 `logger.warning`으로 에러 로깅

## 타입 표기
- `from __future__ import annotations` 사용
- `dict | None` 유니온 형태 사용 (`Optional` 미사용)
