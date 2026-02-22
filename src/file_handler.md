# file_handler.py

파일 업로드 및 이미지 변환 모듈.

## 역할
- PDF/PNG/JPG/JPEG 단일 파일 또는 ZIP 아카이브 처리
- PDF를 이미지로 변환
- 업로드 파일 유효성 검사

## 상수

- `VALID_EXTENSIONS`: 허용되는 파일 확장자 집합 (`{".pdf", ".png", ".jpg", ".jpeg"}`)

## 함수

### `validate_file_type(filename: str) -> bool`
파일 확장자가 허용 목록(pdf/png/jpg/jpeg)에 포함되는지 검사한다. 대소문자 구분 없이 처리한다.

- **입력**: 파일 이름 문자열
- **출력**: 유효하면 `True`, 아니면 `False`

### `extract_zip(zip_bytes: bytes) -> list[tuple[str, bytes]]`
ZIP 바이트에서 유효한 파일을 추출한다.

- ZIP 안에 폴더(디렉터리)가 포함되어 있으면 `ValueError`를 발생시킨다
- 파일 경로에 `/`가 포함된 경우에도 폴더로 간주하여 거부한다
- 유효 확장자(pdf/png/jpg/jpeg)를 가진 파일만 추출한다
- **입력**: ZIP 파일의 바이트 데이터
- **출력**: `(파일이름, 파일바이트)` 튜플의 리스트
- **예외**: `ValueError` -- ZIP에 폴더가 포함된 경우

### `pdf_to_images(pdf_bytes: bytes) -> list[PIL.Image.Image]`
PDF 바이트를 PIL Image 리스트로 변환한다. 내부적으로 `pdf2image.convert_from_bytes`를 사용한다.

- **입력**: PDF 파일의 바이트 데이터
- **출력**: 각 페이지에 해당하는 PIL Image 객체의 리스트
- **의존성**: `pdf2image` (poppler 시스템 라이브러리 필요)

### `process_uploaded_file(filename: str, file_bytes: bytes) -> list[tuple[str, bytes]]`
업로드된 파일을 유형별로 라우팅하여 처리한다.

- ZIP 파일 -> `extract_zip`으로 위임
- PDF/이미지 파일 -> `[(filename, file_bytes)]` 반환
- 지원하지 않는 형식 -> `ValueError` 발생
- **입력**: 파일 이름, 파일 바이트 데이터
- **출력**: `(파일이름, 파일바이트)` 튜플의 리스트

## 의존성
- `pdf2image`: PDF를 이미지로 변환 (poppler 시스템 패키지 필요)
- `Pillow`: PIL Image 타입
- Python 표준 라이브러리: `io`, `os`, `zipfile`
