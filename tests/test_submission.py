"""submission 모듈 단위 테스트."""

from src.submission import (
    build_submissions,
    format_submissions_for_display,
    merge_ocr_pages,
)


class TestMergeOcrPages:
    """merge_ocr_pages 함수 테스트."""

    def test_single_page(self):
        """단일 페이지 OCR 결과를 그대로 반환한다."""
        pages = [
            {"학번": "10305", "이름": "홍길동", "에세이텍스트": "에세이 본문"},
        ]
        result = merge_ocr_pages(pages)

        assert result["학번"] == "10305"
        assert result["이름"] == "홍길동"
        assert result["에세이텍스트"] == "에세이 본문"

    def test_multi_page_merge(self):
        """여러 페이지의 학번/이름은 첫 번째 비어있지 않은 값을 사용한다."""
        pages = [
            {"학번": "10305", "이름": "홍길동", "에세이텍스트": "첫째 페이지"},
            {"학번": "10305", "이름": "홍길동", "에세이텍스트": "둘째 페이지"},
        ]
        result = merge_ocr_pages(pages)

        assert result["학번"] == "10305"
        assert result["이름"] == "홍길동"

    def test_empty_id_on_first_page_uses_second(self):
        """첫 페이지에 학번이 없으면 두 번째 페이지의 학번을 사용한다."""
        pages = [
            {"학번": "", "이름": "", "에세이텍스트": "첫째 페이지"},
            {"학번": "20407", "이름": "김영희", "에세이텍스트": "둘째 페이지"},
        ]
        result = merge_ocr_pages(pages)

        assert result["학번"] == "20407"
        assert result["이름"] == "김영희"

    def test_all_pages_empty_ids(self):
        """모든 페이지의 학번이 비어있으면 빈 문자열을 반환한다."""
        pages = [
            {"학번": "", "이름": "", "에세이텍스트": "텍스트1"},
            {"학번": "", "이름": "", "에세이텍스트": "텍스트2"},
        ]
        result = merge_ocr_pages(pages)

        assert result["학번"] == ""
        assert result["이름"] == ""

    def test_essay_text_concatenation(self):
        """여러 페이지의 에세이텍스트를 줄바꿈으로 연결한다."""
        pages = [
            {"학번": "10305", "이름": "홍길동", "에세이텍스트": "첫째 페이지"},
            {"학번": "", "이름": "", "에세이텍스트": "둘째 페이지"},
            {"학번": "", "이름": "", "에세이텍스트": "셋째 페이지"},
        ]
        result = merge_ocr_pages(pages)

        assert result["에세이텍스트"] == "첫째 페이지\n둘째 페이지\n셋째 페이지"

    def test_single_page_no_trailing_newline(self):
        """단일 페이지일 때 불필요한 줄바꿈이 없어야 한다."""
        pages = [
            {"학번": "10305", "이름": "홍길동", "에세이텍스트": "에세이 본문"},
        ]
        result = merge_ocr_pages(pages)

        assert result["에세이텍스트"] == "에세이 본문"

    def test_name_from_first_nonempty_page(self):
        """이름은 첫 번째 비어있지 않은 페이지에서 가져온다."""
        pages = [
            {"학번": "10305", "이름": "", "에세이텍스트": "페이지1"},
            {"학번": "", "이름": "홍길동", "에세이텍스트": "페이지2"},
        ]
        result = merge_ocr_pages(pages)

        assert result["학번"] == "10305"
        assert result["이름"] == "홍길동"

    def test_empty_pages_list(self):
        """빈 페이지 리스트는 모두 빈 값을 반환한다."""
        result = merge_ocr_pages([])

        assert result["학번"] == ""
        assert result["이름"] == ""
        assert result["에세이텍스트"] == ""


class TestBuildSubmissions:
    """build_submissions 함수 테스트."""

    def test_normal_case_with_multiple_files(self):
        """여러 파일에서 정상적으로 제출물 목록을 생성한다."""
        file_ocr_results = [
            ("essay1.pdf", [
                {"학번": "10305", "이름": "홍길동", "에세이텍스트": "에세이1 내용"},
            ]),
            ("essay2.jpg", [
                {"학번": "20407", "이름": "김영희", "에세이텍스트": "에세이2 내용"},
            ]),
        ]
        submissions, unidentified = build_submissions(file_ocr_results)

        assert len(submissions) == 2
        assert submissions[0]["학번"] == "10305"
        assert submissions[1]["학번"] == "20407"
        assert len(unidentified) == 0

    def test_unidentified_files_returned_separately(self):
        """학번이 비어있는 파일은 미식별 목록에 포함된다."""
        file_ocr_results = [
            ("good.pdf", [
                {"학번": "10305", "이름": "홍길동", "에세이텍스트": "내용"},
            ]),
            ("bad.pdf", [
                {"학번": "", "이름": "", "에세이텍스트": "학번 없는 에세이"},
            ]),
        ]
        submissions, unidentified = build_submissions(file_ocr_results)

        assert len(submissions) == 1
        assert submissions[0]["학번"] == "10305"
        assert len(unidentified) == 1
        assert unidentified[0] == "bad.pdf"

    def test_empty_input(self):
        """빈 입력에서는 빈 목록 튜플을 반환한다."""
        submissions, unidentified = build_submissions([])

        assert submissions == []
        assert unidentified == []

    def test_multi_page_text_concatenated(self):
        """여러 페이지의 에세이텍스트가 연결된다."""
        file_ocr_results = [
            ("doc.pdf", [
                {"학번": "10305", "이름": "홍길동", "에세이텍스트": "페이지1"},
                {"학번": "", "이름": "", "에세이텍스트": "페이지2"},
            ]),
        ]
        submissions, unidentified = build_submissions(file_ocr_results)

        assert len(submissions) == 1
        assert "페이지1" in submissions[0]["에세이텍스트"]
        assert "페이지2" in submissions[0]["에세이텍스트"]

    def test_all_files_unidentified(self):
        """모든 파일이 미식별인 경우."""
        file_ocr_results = [
            ("a.pdf", [{"학번": "", "이름": "", "에세이텍스트": "no info"}]),
            ("b.jpg", [{"학번": "", "이름": "", "에세이텍스트": "also nothing"}]),
        ]
        submissions, unidentified = build_submissions(file_ocr_results)

        assert len(submissions) == 0
        assert len(unidentified) == 2

    def test_id_from_second_page_identifies_file(self):
        """두 번째 페이지에 학번이 있으면 식별된 제출물로 처리된다."""
        file_ocr_results = [
            ("doc.pdf", [
                {"학번": "", "이름": "", "에세이텍스트": "첫째 페이지 내용"},
                {"학번": "10305", "이름": "홍길동", "에세이텍스트": "둘째 페이지"},
            ]),
        ]
        submissions, unidentified = build_submissions(file_ocr_results)

        assert len(submissions) == 1
        assert submissions[0]["학번"] == "10305"
        assert len(unidentified) == 0


class TestFormatSubmissionsForDisplay:
    """format_submissions_for_display 함수 테스트."""

    def test_correct_table_format(self):
        """올바른 테이블 형식으로 출력한다."""
        submissions = [
            {"학번": "10305", "이름": "홍길동", "에세이텍스트": "짧은 에세이"},
        ]
        result = format_submissions_for_display(submissions)
        lines = result.strip().split("\n")

        assert lines[0] == "학번 | 이름 | 에세이 미리보기"
        assert "10305" in lines[1]
        assert "홍길동" in lines[1]
        assert "짧은 에세이" in lines[1]

    def test_text_preview_truncation_at_50_chars(self):
        """에세이 미리보기가 50자에서 잘린다."""
        long_text = "가" * 100
        submissions = [
            {"학번": "10305", "이름": "홍길동", "에세이텍스트": long_text},
        ]
        result = format_submissions_for_display(submissions)
        lines = result.strip().split("\n")

        preview_part = lines[1].split(" | ")[2]
        assert preview_part == "가" * 50 + "..."

    def test_text_exactly_50_chars_no_ellipsis(self):
        """에세이가 정확히 50자이면 말줄임표를 붙이지 않는다."""
        text_50 = "나" * 50
        submissions = [
            {"학번": "10305", "이름": "홍길동", "에세이텍스트": text_50},
        ]
        result = format_submissions_for_display(submissions)
        lines = result.strip().split("\n")

        preview_part = lines[1].split(" | ")[2]
        assert preview_part == text_50

    def test_multiple_submissions_formatting(self):
        """여러 제출물이 각각 한 줄씩 포매팅된다."""
        submissions = [
            {"학번": "10305", "이름": "홍길동", "에세이텍스트": "에세이A"},
            {"학번": "20407", "이름": "김영희", "에세이텍스트": "에세이B"},
        ]
        result = format_submissions_for_display(submissions)
        lines = result.strip().split("\n")

        assert len(lines) == 3  # header + 2 rows

    def test_empty_submissions_returns_header_only(self):
        """빈 목록이면 헤더만 반환한다."""
        result = format_submissions_for_display([])
        lines = result.strip().split("\n")

        assert len(lines) == 1
        assert lines[0] == "학번 | 이름 | 에세이 미리보기"

    def test_newlines_in_essay_replaced_for_preview(self):
        """에세이 미리보기에서 줄바꿈이 공백으로 대체된다."""
        submissions = [
            {"학번": "10305", "이름": "홍길동", "에세이텍스트": "첫줄\n둘째줄"},
        ]
        result = format_submissions_for_display(submissions)
        lines = result.strip().split("\n")

        preview_part = lines[1].split(" | ")[2]
        assert "\n" not in preview_part
        assert "첫줄 둘째줄" in preview_part
