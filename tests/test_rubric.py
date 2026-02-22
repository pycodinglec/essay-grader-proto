"""채점기준표 검증 모듈 테스트."""

from io import BytesIO

import pytest
from openpyxl import Workbook

from src.rubric import format_rubric_for_display, parse_rubric, validate_rubric


# ── 헬퍼: 테스트용 xlsx bytes 생성 ──────────────────────────────


def _make_xlsx(headers: list[str], rows: list[list]) -> bytes:
    """헤더와 데이터 행으로 xlsx 바이트를 생성한다."""
    wb = Workbook()
    ws = wb.active
    ws.append(headers)
    for row in rows:
        ws.append(row)
    buf = BytesIO()
    wb.save(buf)
    return buf.getvalue()


def _make_valid_xlsx() -> bytes:
    """유효한 채점기준표 xlsx 바이트를 반환한다."""
    return _make_xlsx(
        ["번호", "채점기준", "배점"],
        [
            [1, "주제에 대한 이해도", 10],
            [2, "논리적 전개", 15],
            [3, "문법 및 맞춤법", 5],
        ],
    )


# ── validate_rubric 테스트 ──────────────────────────────────────


class TestValidateRubric:
    """validate_rubric 함수 테스트."""

    def test_valid_rubric_returns_true(self):
        """유효한 채점기준표는 (True, '')을 반환한다."""
        data = _make_valid_xlsx()
        ok, msg = validate_rubric(data)
        assert ok is True
        assert msg == ""

    def test_missing_column_returns_false(self):
        """열이 2개만 있으면 (False, 에러메시지)를 반환한다."""
        data = _make_xlsx(["번호", "채점기준"], [[1, "기준A"]])
        ok, msg = validate_rubric(data)
        assert ok is False
        assert "번호" in msg or "채점기준" in msg or "배점" in msg

    def test_wrong_column_name_returns_false(self):
        """열 이름이 다르면 (False, 에러메시지)를 반환한다."""
        data = _make_xlsx(
            ["번호", "기준", "배점"],
            [[1, "기준A", 10]],
        )
        ok, msg = validate_rubric(data)
        assert ok is False

    def test_empty_data_rows_returns_false(self):
        """헤더만 있고 데이터 행이 없으면 (False, 에러메시지)를 반환한다."""
        data = _make_xlsx(["번호", "채점기준", "배점"], [])
        ok, msg = validate_rubric(data)
        assert ok is False
        assert "데이터" in msg or "행" in msg

    def test_non_numeric_score_returns_false(self):
        """배점 열에 숫자가 아닌 값이 있으면 (False, 에러메시지)를 반환한다."""
        data = _make_xlsx(
            ["번호", "채점기준", "배점"],
            [[1, "기준A", "높음"]],
        )
        ok, msg = validate_rubric(data)
        assert ok is False
        assert "배점" in msg or "숫자" in msg

    def test_float_score_is_valid(self):
        """배점이 float여도 유효하다."""
        data = _make_xlsx(
            ["번호", "채점기준", "배점"],
            [[1, "기준A", 7.5]],
        )
        ok, msg = validate_rubric(data)
        assert ok is True
        assert msg == ""

    def test_invalid_bytes_returns_false(self):
        """xlsx가 아닌 바이트는 (False, 에러메시지)를 반환한다."""
        ok, msg = validate_rubric(b"not an xlsx file")
        assert ok is False


# ── parse_rubric 테스트 ─────────────────────────────────────────


class TestParseRubric:
    """parse_rubric 함수 테스트."""

    def test_parse_returns_list_of_dicts(self):
        """유효한 파일을 파싱하면 dict 리스트를 반환한다."""
        data = _make_valid_xlsx()
        result = parse_rubric(data)
        assert isinstance(result, list)
        assert len(result) == 3

    def test_parse_dict_keys(self):
        """각 dict에 번호, 채점기준, 배점 키가 존재한다."""
        data = _make_valid_xlsx()
        result = parse_rubric(data)
        for item in result:
            assert "번호" in item
            assert "채점기준" in item
            assert "배점" in item

    def test_parse_preserves_order(self):
        """xlsx의 행 순서가 보존된다."""
        data = _make_valid_xlsx()
        result = parse_rubric(data)
        assert result[0]["번호"] == 1
        assert result[1]["번호"] == 2
        assert result[2]["번호"] == 3

    def test_parse_values_correct(self):
        """파싱된 값이 원본과 일치한다."""
        data = _make_valid_xlsx()
        result = parse_rubric(data)
        assert result[0]["채점기준"] == "주제에 대한 이해도"
        assert result[0]["배점"] == 10
        assert result[1]["배점"] == 15

    def test_parse_invalid_file_raises_value_error(self):
        """유효하지 않은 파일은 ValueError를 발생시킨다."""
        data = _make_xlsx(["번호", "채점기준", "배점"], [])
        with pytest.raises(ValueError):
            parse_rubric(data)

    def test_parse_corrupt_bytes_raises_value_error(self):
        """손상된 바이트는 ValueError를 발생시킨다."""
        with pytest.raises(ValueError):
            parse_rubric(b"corrupted")


# ── format_rubric_for_display 테스트 ────────────────────────────


class TestFormatRubricForDisplay:
    """format_rubric_for_display 함수 테스트."""

    def test_format_includes_header(self):
        """출력 첫 줄에 헤더가 포함된다."""
        rubric = [{"번호": 1, "채점기준": "기준A", "배점": 10}]
        result = format_rubric_for_display(rubric)
        first_line = result.split("\n")[0]
        assert "번호" in first_line
        assert "채점기준" in first_line
        assert "배점" in first_line

    def test_format_includes_data_rows(self):
        """데이터 행이 포함된다."""
        rubric = [
            {"번호": 1, "채점기준": "기준A", "배점": 10},
            {"번호": 2, "채점기준": "기준B", "배점": 20},
        ]
        result = format_rubric_for_display(rubric)
        lines = result.strip().split("\n")
        assert len(lines) == 3  # 헤더 + 2 데이터 행

    def test_format_uses_pipe_separator(self):
        """| 구분자를 사용한다."""
        rubric = [{"번호": 1, "채점기준": "기준A", "배점": 10}]
        result = format_rubric_for_display(rubric)
        for line in result.strip().split("\n"):
            assert "|" in line

    def test_format_data_values_present(self):
        """데이터 값이 정확히 포함된다."""
        rubric = [{"번호": 1, "채점기준": "주제 이해도", "배점": 10}]
        result = format_rubric_for_display(rubric)
        assert "1" in result
        assert "주제 이해도" in result
        assert "10" in result

    def test_format_empty_list(self):
        """빈 리스트는 헤더만 반환한다."""
        result = format_rubric_for_display([])
        lines = result.strip().split("\n")
        assert len(lines) == 1
        assert "번호" in lines[0]
