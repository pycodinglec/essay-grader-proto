# ocr.py

OCR 모듈 (Google Nano Banana Pro API).

## 역할
- Google Nano Banana Pro API(gemini-3.1-pro-preview)를 사용한 이미지 OCR
- 학번, 이름, 에세이텍스트를 구조화된 JSON으로 추출
- PDF 파일의 이미지 변환 후 OCR 처리
- 이미지 파일(png/jpg/jpeg) 직접 OCR 처리

## 상수

- `OCR_PROMPT`: OCR 요청에 사용되는 한국어 프롬프트. prompt injection 방어 문구가 앞에 포함되며, 이미지에서 학번, 이름, 에세이 본문을 분리하여 JSON으로 반환하도록 지시한다. 인쇄된 지시문과 손 글씨 에세이를 구분하며, 악필 시 무리한 추측을 하지 않도록 안내한다.
- `MODEL_NAME`: `"gemini-3.1-pro-preview"` — Google Nano Banana Pro API의 모델 식별자.
- `_REQUIRED_KEYS`: `{"학번", "이름", "에세이텍스트"}` — OCR 응답에 필수인 JSON 키.
- `_CODE_FENCE_RE`: 마크다운 코드 펜스(```json ... ```)를 매칭하는 정규식.

## 함수

### `parse_ocr_response(response_text: str) -> dict`
OCR 모델 응답을 구조화된 dict로 파싱한다.

- 마크다운 코드 펜스(```json ... ``` 또는 ``` ... ```) 제거 후 JSON 파싱
- 필수 키(학번, 이름, 에세이텍스트) 존재 여부 검증
- 파싱 실패 또는 키 누락 시 폴백: `{"학번": "", "이름": "", "에세이텍스트": 원문텍스트}`
- **입력**: OCR 모델의 응답 텍스트
- **출력**: `{"학번": str, "이름": str, "에세이텍스트": str}` dict

### `extract_text_from_image(image: PIL.Image.Image) -> dict`
단일 PIL Image에서 학생 정보와 에세이 텍스트를 추출한다.

- Google Nano Banana Pro API를 호출하여 구조화된 OCR 수행
- `config.get_genai_client()` 싱글턴을 사용하여 genai 클라이언트 획득
- contents로 이미지와 OCR 프롬프트를 함께 전달
- 응답을 `parse_ocr_response`로 파싱
- **입력**: PIL Image 객체
- **출력**: `{"학번": str, "이름": str, "에세이텍스트": str}` dict

### `extract_text_from_images(images: list[PIL.Image.Image]) -> list[dict]`
여러 PIL Image에서 순차적으로 학생 정보와 텍스트를 추출한다.

- 각 이미지에 대해 `extract_text_from_image`를 호출
- 이미지 순서가 결과 리스트 순서에 보존됨
- **입력**: PIL Image 객체들의 리스트
- **출력**: 각 이미지에서 추출된 dict의 리스트

### `ocr_file(filename: str, file_bytes: bytes) -> list[dict]`
파일에서 OCR 결과를 구조화하여 추출하는 고수준 함수.

- PDF: `file_handler.pdf_to_images`로 이미지 변환 후 `extract_text_from_images`로 OCR
- 이미지(png/jpg/jpeg): `PIL.Image.open`으로 로드 후 `extract_text_from_image`로 OCR
- 지원하지 않는 파일 형식: `ValueError` 발생
- `file_handler.validate_file_type`으로 파일 유형 검증
- **입력**: 파일 이름, 파일 바이트 데이터
- **출력**: 페이지/이미지별 추출 dict의 리스트 (이미지 파일은 단일 요소 리스트)
- **예외**: `ValueError` -- 지원하지 않는 파일 형식인 경우

## 의존성
- `Pillow`: PIL Image 타입 및 이미지 로드
- `src.config`: `get_genai_client()` 싱글턴 및 API 키
- `src.file_handler`: 파일 유형 검증 및 PDF 이미지 변환
- Python 표준 라이브러리: `io`, `json`, `os`, `re`
