# submission.py

제출물 식별 및 구성 모듈.

## 역할
- OCR에서 반환한 구조화된 dict(학번, 이름, 에세이텍스트)를 사용하여 제출물 목록 구성
- 여러 페이지의 OCR 결과를 하나의 제출물로 병합
- 미식별 파일 추적 및 사용자 표시용 테이블 생성

## 함수

### `merge_ocr_pages(pages: list[dict]) -> dict`
여러 OCR 페이지 결과를 하나의 제출물로 병합한다.

- 학번: 페이지들 중 첫 번째 비어있지 않은 값 사용
- 이름: 페이지들 중 첫 번째 비어있지 않은 값 사용
- 에세이텍스트: 모든 페이지의 텍스트를 줄바꿈(`\n`)으로 연결
- 빈 페이지 리스트 입력 시 모두 빈 문자열 반환
- **입력**: `list[dict]` (각 dict는 `{"학번", "이름", "에세이텍스트"}`)
- **출력**: 병합된 `{"학번": str, "이름": str, "에세이텍스트": str}` dict

### `build_submissions(file_ocr_results) -> tuple[list[dict], list[str]]`
파일별 OCR 결과로부터 제출물 목록을 구성한다.

- 입력: `list[tuple[str, list[dict]]]` (파일명, 페이지별 OCR dict 리스트)
- 각 파일에 대해 `merge_ocr_pages`로 페이지 병합
- 병합 후 학번이 비어있으면 미식별 파일로 분류
- **반환**: (식별된 제출물 리스트, 미식별 파일명 리스트)

### `format_submissions_for_display(submissions: list[dict]) -> str`
제출물 목록을 파이프(|) 구분 테이블 문자열로 포매팅한다.

- 헤더: `학번 | 이름 | 에세이 미리보기`
- 에세이 미리보기: 줄바꿈을 공백으로 대체, 50자 초과 시 잘라내고 "..." 추가

## 내부 함수

### `_truncate_preview(text, max_len=50) -> str`
텍스트를 미리보기용으로 줄바꿈 제거 후 max_len 이내로 잘라낸다.
