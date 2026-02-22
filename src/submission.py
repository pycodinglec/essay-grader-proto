"""제출물 식별 및 구성 모듈.

OCR에서 반환한 구조화된 dict(학번, 이름, 에세이텍스트)를 사용하여
제출물 목록을 구성한다.
"""


def merge_ocr_pages(pages: list[dict]) -> dict:
    """여러 OCR 페이지 결과를 하나의 제출물로 병합한다.

    학번과 이름은 페이지들 중 첫 번째 비어있지 않은 값을 사용하고,
    에세이텍스트는 모든 페이지의 텍스트를 줄바꿈으로 연결한다.

    Args:
        pages: OCR 페이지별 dict 리스트.
            각 dict는 {"학번": str, "이름": str, "에세이텍스트": str}.

    Returns:
        병합된 {"학번": str, "이름": str, "에세이텍스트": str} dict.
    """
    student_id = ""
    name = ""
    essay_parts: list[str] = []

    for page in pages:
        if not student_id and page.get("학번"):
            student_id = page["학번"]
        if not name and page.get("이름"):
            name = page["이름"]
        essay_text = page.get("에세이텍스트", "")
        if essay_text:
            essay_parts.append(essay_text)

    return {
        "학번": student_id,
        "이름": name,
        "에세이텍스트": "\n".join(essay_parts),
    }


def build_submissions(
    file_ocr_results: list[tuple[str, list[dict]]],
) -> tuple[list[dict], list[str]]:
    """파일별 OCR 결과로부터 제출물 목록을 구성한다.

    Args:
        file_ocr_results: (파일명, [페이지별_dict, ...]) 튜플 리스트.

    Returns:
        (식별된_제출물_리스트, 미식별_파일명_리스트) 튜플.
    """
    submissions: list[dict] = []
    unidentified: list[str] = []

    for filename, pages in file_ocr_results:
        merged = merge_ocr_pages(pages)
        if merged["학번"]:
            submissions.append(merged)
        else:
            unidentified.append(filename)

    return submissions, unidentified


def _truncate_preview(text: str, max_len: int = 50) -> str:
    """텍스트를 미리보기용으로 줄바꿈 제거 후 잘라낸다."""
    flat = text.replace("\n", " ")
    if len(flat) > max_len:
        return flat[:max_len] + "..."
    return flat


def format_submissions_for_display(submissions: list[dict]) -> str:
    """제출물 목록을 사용자 확인용 테이블 문자열로 포매팅한다.

    Args:
        submissions: {"학번", "이름", "에세이텍스트"} dict 리스트.

    Returns:
        "학번 | 이름 | 에세이 미리보기" 형식의 테이블 문자열.
    """
    header = "학번 | 이름 | 에세이 미리보기"
    lines = [header]

    for sub in submissions:
        preview = _truncate_preview(sub["에세이텍스트"])
        lines.append(f"{sub['학번']} | {sub['이름']} | {preview}")

    return "\n".join(lines)
