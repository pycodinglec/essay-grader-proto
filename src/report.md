# report.py

리포트 생성 모듈. 채점 결과를 취합하여 report.xlsx 바이트를 생성한다.

## 역할
- report.xlsx 생성 (열: 학번/이름/작품번호/피드백)
- 작품번호는 학생별 순서 자동 부여 (1, 2, ...)
- 중간 결과 다운로드 지원

## 함수

### `assign_work_numbers(submissions: list[dict]) -> list[dict]`
- 제출물 리스트에 학생별 작품번호를 부여한다.
- 입력: `{"학번": str, "이름": str, "evaluation": {"scores": [...], "feedback": str}}` 리스트
- 동일 학번의 제출물은 등장 순서에 따라 1, 2, 3... 번호를 받는다.
- `evaluation["feedback"]` 값을 `"피드백"` 키로 추출한다.
- 반환: `{"학번", "이름", "작품번호", "피드백"}` dict 리스트

### `generate_report_bytes(report_data: list[dict]) -> bytes`
- 리포트 데이터를 openpyxl로 xlsx 바이트로 변환한다.
- 입력: `{"학번", "이름", "작품번호", "피드백"}` dict 리스트
- 행은 학번 오름차순, 그 다음 작품번호 오름차순으로 정렬된다.
- 헤더 행: 학번 / 이름 / 작품번호 / 피드백
- `BytesIO`에 저장 후 `bytes`로 반환

### `build_report(graded_submissions: list[dict]) -> bytes`
- 상위 수준 통합 함수. `assign_work_numbers` + `generate_report_bytes`를 순차 호출.
- 입력: `{"학번", "이름", "evaluation"}` dict 리스트
- 반환: 다운로드 가능한 xlsx 바이트

## 의존성
- `openpyxl`: xlsx 파일 생성
- `collections.defaultdict`: 학생별 작품번호 카운터
