# test_file_handler.py

`src/file_handler.py` 모듈의 단위 테스트.

## 테스트 클래스 및 커버리지

### TestValidateFileType (7개 테스트)
`validate_file_type` 함수의 확장자 검증 로직을 테스트한다.

| 테스트 | 설명 |
|--------|------|
| `test_valid_extensions` | pdf/png/jpg/jpeg 확장자에 대해 True 반환 확인 (parametrize) |
| `test_case_insensitive` | PDF/Png/JPG/JPEG/JpEg 등 대소문자 혼합에 대해 True 반환 확인 |
| `test_invalid_extensions` | txt/xlsx/py/zip/md/확장자없음에 대해 False 반환 확인 |
| `test_empty_string` | 빈 문자열 입력 시 False 반환 확인 |
| `test_dot_only` | 점으로 시작하는 히든 파일(.pdf) 및 점만 있는 경우 False 반환 확인 |

### TestExtractZip (7개 테스트)
`extract_zip` 함수의 ZIP 추출 로직을 테스트한다. 인메모리 `zipfile`을 사용하여 테스트용 ZIP을 생성한다.

| 테스트 | 설명 |
|--------|------|
| `test_extract_valid_files` | 유효한 확장자 파일 3개가 모두 추출되는지 확인 |
| `test_filter_invalid_extensions` | txt/xlsx 등 비유효 확장자 파일이 필터링되는지 확인 |
| `test_folder_detected_raises_value_error` | 명시적 디렉터리 엔트리 포함 시 ValueError 발생 확인 |
| `test_nested_path_detected_as_folder` | 경로에 / 포함된 파일이 폴더로 간주되어 ValueError 발생 확인 |
| `test_preserves_file_content` | 추출된 파일의 바이트 내용이 원본과 동일한지 확인 |
| `test_empty_zip_returns_empty_list` | 유효한 파일 없는 ZIP에서 빈 리스트 반환 확인 |
| `test_completely_empty_zip` | 파일이 전혀 없는 빈 ZIP에서 빈 리스트 반환 확인 |

### TestPdfToImages (2개 테스트)
`pdf_to_images` 함수를 테스트한다. `pdf2image.convert_from_bytes`를 mock하여 poppler 시스템 의존성 없이 테스트한다.

| 테스트 | 설명 |
|--------|------|
| `test_returns_list_of_images` | 다중 페이지 PDF에서 Image 리스트 반환 확인 |
| `test_single_page_pdf` | 단일 페이지 PDF에서 길이 1 리스트 반환 확인 |

### TestProcessUploadedFile (9개 테스트)
`process_uploaded_file` 함수의 파일 유형별 라우팅 로직을 테스트한다.

| 테스트 | 설명 |
|--------|------|
| `test_pdf_file_returns_single_tuple` | PDF 파일이 단일 튜플 리스트로 반환되는지 확인 |
| `test_png_image_returns_single_tuple` | PNG 파일 라우팅 확인 |
| `test_jpg_image_returns_single_tuple` | JPG 파일 라우팅 확인 |
| `test_jpeg_image_returns_single_tuple` | JPEG 파일 라우팅 확인 |
| `test_zip_file_delegates_to_extract_zip` | ZIP 파일이 extract_zip으로 위임되는지 확인 |
| `test_unsupported_type_raises_value_error` | xlsx 등 미지원 형식에서 ValueError 발생 확인 |
| `test_unsupported_txt_raises_value_error` | txt 파일에서 ValueError 발생 확인 |
| `test_case_insensitive_zip` | .ZIP 대문자 확장자 처리 확인 |
| `test_case_insensitive_pdf` | .PDF 대문자 확장자 처리 확인 |

## 헬퍼 함수

- `_create_zip_bytes(entries)`: dict로부터 인메모리 ZIP bytes 생성
- `_create_zip_with_directory(files, dir_name)`: 폴더 엔트리가 포함된 ZIP bytes 생성

## 총 테스트 수: 35개 (parametrize 포함)
