# test_ocr.py

`src/ocr.py` 모듈의 단위 테스트.

## 테스트 클래스 및 커버리지

### TestParseOcrResponse (7개 테스트)
`parse_ocr_response` 함수의 JSON 파싱 및 폴백 로직을 테스트한다.

| 테스트 | 설명 |
|--------|------|
| `test_valid_json` | 올바른 JSON 응답을 정상적으로 파싱하는지 확인 |
| `test_json_in_markdown_fences` | ```json 코드 펜스로 감싼 JSON을 파싱하는지 확인 |
| `test_json_in_plain_fences` | 언어 태그 없는 코드 펜스 JSON을 파싱하는지 확인 |
| `test_invalid_json_fallback` | 유효하지 않은 JSON에서 폴백 dict를 반환하는지 확인 |
| `test_missing_keys_fallback` | 필수 키 누락 시 폴백 dict를 반환하는지 확인 |
| `test_missing_essay_key_fallback` | 에세이텍스트 키 누락 시 폴백 dict를 반환하는지 확인 |
| `test_whitespace_around_json` | 앞뒤 공백이 있는 JSON을 올바르게 파싱하는지 확인 |

### TestExtractTextFromImage (5개 테스트)
`extract_text_from_image` 함수의 Google Nano Banana Pro API 호출 및 dict 반환 로직을 테스트한다. `google.genai` 모듈을 mock하여 실제 API 호출 없이 테스트한다.

| 테스트 | 설명 |
|--------|------|
| `test_calls_generate_content_with_correct_model` | 올바른 모델 이름(gemini-3.1-pro-preview)으로 generate_content를 호출하는지 확인 |
| `test_sends_image_and_prompt_as_contents` | contents에 이미지와 OCR 프롬프트가 함께 전달되는지 확인 |
| `test_returns_parsed_dict` | API 응답을 파싱하여 dict(학번/이름/에세이텍스트)를 반환하는지 확인 |
| `test_returns_fallback_dict_on_invalid_response` | 유효하지 않은 응답에서 폴백 dict를 반환하는지 확인 |
| `test_uses_google_api_key_from_config` | config.GOOGLE_API_KEY를 사용하여 클라이언트를 생성하는지 확인 |

### TestExtractTextFromImages (4개 테스트)
`extract_text_from_images` 함수의 다중 이미지 처리 로직을 테스트한다. `extract_text_from_image`를 mock하여 테스트한다.

| 테스트 | 설명 |
|--------|------|
| `test_processes_all_images` | 모든 이미지에 대해 extract_text_from_image를 호출하는지 확인 |
| `test_preserves_order` | 이미지 순서대로 결과를 반환하는지 확인 |
| `test_empty_list_returns_empty` | 빈 이미지 리스트 입력 시 빈 리스트 반환 확인 |
| `test_single_image` | 단일 이미지도 리스트로 반환하는지 확인 |

### TestOcrFile (8개 테스트)
`ocr_file` 함수의 파일 유형별 OCR 라우팅 로직을 테스트한다. `file_handler.pdf_to_images`, `Image.open`, `extract_text_from_image`, `extract_text_from_images`를 mock하여 테스트한다.

| 테스트 | 설명 |
|--------|------|
| `test_pdf_converts_and_ocrs` | PDF 파일이 이미지로 변환 후 OCR되는지 확인 |
| `test_pdf_case_insensitive` | PDF 확장자 대소문자 구분 없이 처리하는지 확인 |
| `test_png_image_loads_and_ocrs` | PNG 이미지 파일을 로드하여 OCR하는지 확인 |
| `test_jpg_image_loads_and_ocrs` | JPG 이미지 파일을 로드하여 OCR하는지 확인 |
| `test_jpeg_image_loads_and_ocrs` | JPEG 이미지 파일을 로드하여 OCR하는지 확인 |
| `test_invalid_file_type_raises_value_error` | txt 등 미지원 형식에서 ValueError 발생 확인 |
| `test_xlsx_file_raises_value_error` | xlsx 파일에서 ValueError 발생 확인 |
| `test_image_wraps_single_result_in_list` | 이미지 파일의 OCR 결과가 단일 요소 리스트(dict)로 반환되는지 확인 |

## Mocking 전략
- `src.ocr.genai`: Google genai SDK 전체를 mock하여 API 호출 차단
- `src.ocr.config.GOOGLE_API_KEY`: API 키 값을 테스트용으로 대체
- `src.ocr.extract_text_from_image`: 단일 이미지 OCR 함수를 mock하여 상위 함수 테스트
- `src.ocr.extract_text_from_images`: 다중 이미지 OCR 함수를 mock하여 ocr_file 테스트
- `src.ocr.file_handler.pdf_to_images`: PDF 변환 의존성 mock
- `src.ocr.Image.open`: PIL 이미지 로드 의존성 mock

## 총 테스트 수: 24개
