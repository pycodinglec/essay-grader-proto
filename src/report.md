# report.py

리포트 생성 모듈. 채점 결과를 취합하여 report.xlsx 바이트를 생성한다.

## 역할
- report.xlsx 생성 (11개 컬럼: 학번/이름/작품번호/에세이/모델별 점수·피드백/최종 점수)
- 작품번호는 학생별 순서 자동 부여 (1, 2, ...)
- 중간 결과 다운로드 지원

## 상수

### `_HEADERS`
11개 컬럼 헤더:
`학번`, `이름`, `작품번호`, `에세이(Gemini-3-pro-preview)`, `합산 점수(GPT)`, `합산 점수(Gemini)`, `합산 점수(Claude)`, `피드백(GPT)`, `피드백(Gemini)`, `피드백(Claude)`, `최종 점수`

## 함수

### `_model_total_score(model_eval: dict | None) -> int | float | str`
- 모델 평가 결과에서 점수 합산을 반환. 실패(`None`) 시 빈 문자열 반환.

### `_model_feedback(model_eval: dict | None) -> str`
- 모델 평가 결과에서 피드백을 반환. 실패(`None`) 시 빈 문자열 반환.

### `assign_work_numbers(submissions: list[dict]) -> list[dict]`
- 제출물 리스트에 학생별 작품번호를 부여한다.
- 입력: `{"학번", "이름", "에세이텍스트", "평가결과": {"best": {...}, "by_model": {...}}}` 리스트
- 동일 학번의 제출물은 등장 순서에 따라 1, 2, 3... 번호를 받는다.
- `by_model`에서 모델별 점수/피드백, `best`에서 최종 점수를 추출한다.
- 반환: 11개 키를 가진 dict 리스트

### `generate_report_bytes(report_data: list[dict]) -> bytes`
- 리포트 데이터를 openpyxl로 xlsx 바이트로 변환한다.
- 입력: 11개 키를 가진 dict 리스트
- 행은 학번 오름차순, 그 다음 작품번호 오름차순으로 정렬된다.
- `BytesIO`에 저장 후 `bytes`로 반환

### `build_report(graded_submissions: list[dict]) -> bytes`
- 상위 수준 통합 함수. `assign_work_numbers` + `generate_report_bytes`를 순차 호출.
- 입력: `{"학번", "이름", "에세이텍스트", "평가결과"}` dict 리스트
- 반환: 다운로드 가능한 xlsx 바이트

## 타입 표기
- `from __future__ import annotations` 사용
- `dict | None` 유니온 형태 사용 (`Optional` 미사용)

## 의존성
- `openpyxl`: xlsx 파일 생성
- `collections.defaultdict`: 학생별 작품번호 카운터
- `src.evaluator.sum_scores`: 최종 점수 계산
