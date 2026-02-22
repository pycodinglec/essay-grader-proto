# essay_splitter.py

에세이 경계 감지 및 분할 모듈.

## 목적

하나의 스캔 파일(PDF/이미지)에 여러 학생의 에세이가 포함된 경우, LLM을 사용하여 에세이 경계를 감지하고 개별 에세이로 분할한다.

## 함수 목록

### `split_essays(file_ocr_results: list[tuple[str, list[dict]]]) -> list[tuple[str, list[dict]]]`
진입점. 단일 페이지 파일은 LLM 호출 없이 그대로 반환하고, 다중 페이지 파일은 `detect_boundaries`를 통해 분할한다.

### `detect_boundaries(pages: list[dict]) -> list[list[int]]`
프롬프트 생성 -> LLM 호출 -> 응답 파싱을 수행한다. 예외 발생 시 전체를 하나의 그룹으로 폴백한다.

### `build_splitter_prompt(pages: list[dict]) -> str`
페이지별 OCR 결과를 기반으로 경계 감지 프롬프트를 생성한다. 에세이텍스트는 100자까지만 사용하며, prompt injection 방어 문구를 포함한다.

### `parse_boundary_response(response_text: str, page_count: int) -> list[list[int]]`
LLM 응답을 JSON 파싱하여 페이지 그룹을 반환한다. 마크다운 코드 펜스 처리를 지원하며, 유효하지 않은 응답 시 폴백한다.

### `call_splitter_llm(prompt: str) -> str`
`config.get_genai_client()` 싱글턴을 사용하여 Gemini 3.1 Pro Preview 모델을 호출한다.

## LLM 모델

- **Gemini 3.1 Pro Preview** (`gemini-3.1-pro-preview`)
- genai 클라이언트: `config.get_genai_client()` (싱글턴, timeout=1800)

## 폴백 동작

모든 실패 상황(LLM 에러, 유효하지 않은 JSON, 누락된 페이지 인덱스 등)에서 전체 페이지를 하나의 에세이로 처리한다: `[[0, 1, ..., n-1]]`.

## 파일명 규칙

- 단일 에세이: 원본 파일명 유지 (예: `scan.pdf`)
- 복수 에세이: `#N` 접미사 부착 (예: `scan.pdf#1`, `scan.pdf#2`)
