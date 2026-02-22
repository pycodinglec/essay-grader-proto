"""리포트 생성 모듈 (report.xlsx).

채점 결과를 취합하여 학번/이름/작품번호/피드백 열을 가진
report.xlsx 바이트를 생성한다.
"""

from __future__ import annotations

from collections import defaultdict
from io import BytesIO

import openpyxl

_HEADERS = ["학번", "이름", "작품번호", "피드백"]


def assign_work_numbers(submissions: list[dict]) -> list[dict]:
    """제출물 리스트에 학생별 작품번호를 부여한다.

    동일 학번의 제출물은 등장 순서에 따라 1, 2, 3... 번호를 받는다.
    evaluation dict에서 feedback을 추출하여 피드백 키로 매핑한다.

    Args:
        submissions: {"학번", "이름", "evaluation": {"scores", "feedback"}} 리스트.

    Returns:
        {"학번", "이름", "작품번호", "피드백"} 형태의 dict 리스트.
    """
    counters: dict[str, int] = defaultdict(int)
    result: list[dict] = []

    for sub in submissions:
        student_id = sub["학번"]
        counters[student_id] += 1
        result.append({
            "학번": student_id,
            "이름": sub["이름"],
            "작품번호": counters[student_id],
            "피드백": sub["evaluation"]["feedback"],
        })

    return result


def generate_report_bytes(report_data: list[dict]) -> bytes:
    """리포트 데이터를 xlsx 바이트로 변환한다.

    행은 학번 오름차순, 그 다음 작품번호 오름차순으로 정렬된다.

    Args:
        report_data: {"학번", "이름", "작품번호", "피드백"} dict 리스트.

    Returns:
        xlsx 파일의 바이트 데이터.
    """
    wb = openpyxl.Workbook()
    ws = wb.active

    for col_idx, header in enumerate(_HEADERS, start=1):
        ws.cell(row=1, column=col_idx, value=header)

    sorted_data = sorted(
        report_data, key=lambda r: (r["학번"], r["작품번호"])
    )

    for row_idx, record in enumerate(sorted_data, start=2):
        ws.cell(row=row_idx, column=1, value=record["학번"])
        ws.cell(row=row_idx, column=2, value=record["이름"])
        ws.cell(row=row_idx, column=3, value=record["작품번호"])
        ws.cell(row=row_idx, column=4, value=record["피드백"])

    buffer = BytesIO()
    wb.save(buffer)
    return buffer.getvalue()


def build_report(graded_submissions: list[dict]) -> bytes:
    """채점 완료된 제출물로부터 report.xlsx 바이트를 생성한다.

    assign_work_numbers와 generate_report_bytes를 순차 호출하는
    상위 수준 함수이다.

    Args:
        graded_submissions: {"학번", "이름", "evaluation"} dict 리스트.

    Returns:
        다운로드 가능한 xlsx 바이트.
    """
    report_data = assign_work_numbers(graded_submissions)
    return generate_report_bytes(report_data)
