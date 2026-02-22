"""essay_splitter 모듈 단위 테스트."""

import json
from unittest.mock import patch, MagicMock

from src.essay_splitter import (
    build_splitter_prompt,
    parse_boundary_response,
    call_splitter_llm,
    detect_boundaries,
    split_essays,
)


# ---------------------------------------------------------------------------
# 공통 fixture / 상수
# ---------------------------------------------------------------------------

SAMPLE_PAGES = [
    {"학번": "10305", "이름": "홍길동", "에세이텍스트": "첫 번째 에세이 내용입니다."},
    {"학번": "10305", "이름": "홍길동", "에세이텍스트": "첫 번째 에세이 두 번째 페이지."},
    {"학번": "20407", "이름": "김영희", "에세이텍스트": "두 번째 에세이 내용입니다."},
]


# ---------------------------------------------------------------------------
# build_splitter_prompt 테스트
# ---------------------------------------------------------------------------


class TestBuildSplitterPrompt:
    """build_splitter_prompt 함수 테스트."""

    def test_includes_page_texts(self):
        """프롬프트에 페이지 에세이텍스트가 <content> 태그로 감싸여 포함된다."""
        result = build_splitter_prompt(SAMPLE_PAGES)

        assert "<content>첫 번째 에세이 내용입니다.</content>" in result

    def test_includes_student_ids(self):
        """프롬프트에 학번이 포함된다."""
        result = build_splitter_prompt(SAMPLE_PAGES)

        assert "10305" in result
        assert "20407" in result

    def test_includes_injection_defense(self):
        """프롬프트에 prompt injection 방어 문구가 포함된다."""
        result = build_splitter_prompt(SAMPLE_PAGES)

        assert "prompt injection" in result.lower() or "ignore" in result.lower()

    def test_truncates_essay_text_to_100_chars(self):
        """에세이텍스트를 100자까지만 사용한다."""
        long_text = "가" * 200
        pages = [
            {"학번": "10305", "이름": "홍길동", "에세이텍스트": long_text},
        ]

        result = build_splitter_prompt(pages)

        assert "가" * 100 in result
        assert "가" * 101 not in result


# ---------------------------------------------------------------------------
# parse_boundary_response 테스트
# ---------------------------------------------------------------------------


class TestParseBoundaryResponse:
    """parse_boundary_response 함수 테스트."""

    def test_valid_json_array(self):
        """유효한 JSON 배열을 올바르게 파싱한다."""
        response = "[[0,1],[2]]"

        result = parse_boundary_response(response, 3)

        assert result == [[0, 1], [2]]

    def test_valid_json_in_markdown_fences(self):
        """마크다운 코드 펜스로 감싸진 JSON을 파싱한다."""
        response = "```json\n[[0,1],[2]]\n```"

        result = parse_boundary_response(response, 3)

        assert result == [[0, 1], [2]]

    def test_invalid_json_fallback(self):
        """유효하지 않은 JSON은 전체를 하나의 그룹으로 폴백한다."""
        result = parse_boundary_response("not json at all", 3)

        assert result == [[0, 1, 2]]

    def test_empty_response_fallback(self):
        """빈 문자열은 폴백을 반환한다."""
        result = parse_boundary_response("", 3)

        assert result == [[0, 1, 2]]

    def test_out_of_range_indices_fallback(self):
        """인덱스가 page_count 이상이면 폴백을 반환한다."""
        response = "[[0,1],[5]]"

        result = parse_boundary_response(response, 3)

        assert result == [[0, 1, 2]]

    def test_missing_pages_fallback(self):
        """모든 페이지가 커버되지 않으면 폴백을 반환한다."""
        response = "[[0,1]]"

        result = parse_boundary_response(response, 3)

        assert result == [[0, 1, 2]]

    def test_single_group_valid(self):
        """단일 그룹 [[0,1,2]]은 유효하다."""
        response = "[[0,1,2]]"

        result = parse_boundary_response(response, 3)

        assert result == [[0, 1, 2]]


# ---------------------------------------------------------------------------
# call_splitter_llm 테스트
# ---------------------------------------------------------------------------


class TestCallSplitterLlm:
    """call_splitter_llm 함수 테스트."""

    @patch("src.essay_splitter.config.get_genai_client")
    def test_calls_gemini_with_correct_model(
        self, mock_get_client: MagicMock
    ) -> None:
        """gemini-3.1-pro-preview 모델을 사용하여 호출한다."""
        mock_client = MagicMock()
        mock_get_client.return_value = mock_client
        mock_response = MagicMock()
        mock_response.text = "[[0,1]]"
        mock_client.models.generate_content.return_value = mock_response

        call_splitter_llm("test prompt")

        call_kwargs = mock_client.models.generate_content.call_args
        assert call_kwargs.kwargs["model"] == "gemini-3.1-pro-preview"

    @patch("src.essay_splitter.config.get_genai_client")
    def test_sends_prompt_as_contents(self, mock_get_client: MagicMock) -> None:
        """프롬프트를 contents 파라미터로 전달한다."""
        mock_client = MagicMock()
        mock_get_client.return_value = mock_client
        mock_response = MagicMock()
        mock_response.text = "[[0]]"
        mock_client.models.generate_content.return_value = mock_response

        call_splitter_llm("my prompt")

        call_kwargs = mock_client.models.generate_content.call_args
        assert call_kwargs.kwargs["contents"] == "my prompt"

    @patch("src.essay_splitter.config.get_genai_client")
    def test_returns_response_text(self, mock_get_client: MagicMock) -> None:
        """API 응답의 텍스트를 반환한다."""
        mock_client = MagicMock()
        mock_get_client.return_value = mock_client
        mock_response = MagicMock()
        mock_response.text = "[[0,1],[2]]"
        mock_client.models.generate_content.return_value = mock_response

        result = call_splitter_llm("prompt")

        assert result == "[[0,1],[2]]"


# ---------------------------------------------------------------------------
# detect_boundaries 테스트
# ---------------------------------------------------------------------------


class TestDetectBoundaries:
    """detect_boundaries 함수 테스트."""

    @patch("src.essay_splitter.call_splitter_llm")
    def test_returns_boundary_groups(self, mock_llm: MagicMock) -> None:
        """정상적인 LLM 응답으로 올바른 그룹을 반환한다."""
        mock_llm.return_value = "[[0,1],[2]]"

        result = detect_boundaries(SAMPLE_PAGES)

        assert result == [[0, 1], [2]]

    @patch("src.essay_splitter.call_splitter_llm")
    def test_llm_error_fallback(self, mock_llm: MagicMock) -> None:
        """LLM 호출 예외 시 전체를 하나의 그룹으로 폴백한다."""
        mock_llm.side_effect = Exception("API error")

        result = detect_boundaries(SAMPLE_PAGES)

        assert result == [[0, 1, 2]]

    @patch("src.essay_splitter.call_splitter_llm")
    def test_parse_error_fallback(self, mock_llm: MagicMock) -> None:
        """유효하지 않은 LLM 응답은 전체를 하나의 그룹으로 폴백한다."""
        mock_llm.return_value = "garbage response"

        result = detect_boundaries(SAMPLE_PAGES)

        assert result == [[0, 1, 2]]


# ---------------------------------------------------------------------------
# split_essays 테스트
# ---------------------------------------------------------------------------


class TestSplitEssays:
    """split_essays 함수 테스트."""

    @patch("src.essay_splitter.call_splitter_llm")
    def test_single_page_file_no_llm_call(
        self, mock_llm: MagicMock
    ) -> None:
        """단일 페이지 파일은 LLM을 호출하지 않고 그대로 반환한다."""
        file_ocr_results = [
            ("essay.pdf", [
                {"학번": "10305", "이름": "홍길동", "에세이텍스트": "내용"},
            ]),
        ]

        result = split_essays(file_ocr_results)

        mock_llm.assert_not_called()
        assert len(result) == 1
        assert result[0][0] == "essay.pdf"
        assert result[0][1] == file_ocr_results[0][1]

    @patch("src.essay_splitter.call_splitter_llm")
    def test_multi_page_single_essay(self, mock_llm: MagicMock) -> None:
        """여러 페이지가 하나의 에세이인 경우 원본 파일명을 유지한다."""
        mock_llm.return_value = "[[0,1,2]]"
        pages = [
            {"학번": "10305", "이름": "홍길동", "에세이텍스트": "페이지1"},
            {"학번": "10305", "이름": "홍길동", "에세이텍스트": "페이지2"},
            {"학번": "10305", "이름": "홍길동", "에세이텍스트": "페이지3"},
        ]

        result = split_essays([("scan.pdf", pages)])

        assert len(result) == 1
        assert result[0][0] == "scan.pdf"
        assert len(result[0][1]) == 3

    @patch("src.essay_splitter.call_splitter_llm")
    def test_multi_page_two_essays(self, mock_llm: MagicMock) -> None:
        """3페이지에서 2개 에세이를 분리한다."""
        mock_llm.return_value = "[[0,1],[2]]"
        pages = [
            {"학번": "10305", "이름": "홍길동", "에세이텍스트": "에세이1 p1"},
            {"학번": "10305", "이름": "홍길동", "에세이텍스트": "에세이1 p2"},
            {"학번": "20407", "이름": "김영희", "에세이텍스트": "에세이2 p1"},
        ]

        result = split_essays([("scan.pdf", pages)])

        assert len(result) == 2
        assert len(result[0][1]) == 2
        assert len(result[1][1]) == 1

    @patch("src.essay_splitter.call_splitter_llm")
    def test_filename_suffix_on_split(self, mock_llm: MagicMock) -> None:
        """분리 시 파일명에 #1, #2 접미사를 붙인다."""
        mock_llm.return_value = "[[0,1],[2]]"
        pages = [
            {"학번": "10305", "이름": "홍길동", "에세이텍스트": "에세이1 p1"},
            {"학번": "10305", "이름": "홍길동", "에세이텍스트": "에세이1 p2"},
            {"학번": "20407", "이름": "김영희", "에세이텍스트": "에세이2 p1"},
        ]

        result = split_essays([("scan.pdf", pages)])

        assert result[0][0] == "scan.pdf#1"
        assert result[1][0] == "scan.pdf#2"

    @patch("src.essay_splitter.call_splitter_llm")
    def test_filename_no_suffix_single_essay(
        self, mock_llm: MagicMock
    ) -> None:
        """단일 에세이는 원본 파일명을 유지한다."""
        mock_llm.return_value = "[[0,1]]"
        pages = [
            {"학번": "10305", "이름": "홍길동", "에세이텍스트": "p1"},
            {"학번": "10305", "이름": "홍길동", "에세이텍스트": "p2"},
        ]

        result = split_essays([("scan.pdf", pages)])

        assert result[0][0] == "scan.pdf"

    @patch("src.essay_splitter.call_splitter_llm")
    def test_multiple_files_mixed(self, mock_llm: MagicMock) -> None:
        """단일/다중 페이지 파일 혼합 처리."""
        mock_llm.return_value = "[[0],[1]]"
        file_ocr_results = [
            ("single.pdf", [
                {"학번": "10305", "이름": "홍길동", "에세이텍스트": "내용"},
            ]),
            ("multi.pdf", [
                {"학번": "10305", "이름": "홍길동", "에세이텍스트": "p1"},
                {"학번": "20407", "이름": "김영희", "에세이텍스트": "p2"},
            ]),
        ]

        result = split_essays(file_ocr_results)

        assert len(result) == 3
        assert result[0][0] == "single.pdf"
        assert result[1][0] == "multi.pdf#1"
        assert result[2][0] == "multi.pdf#2"

    @patch("src.essay_splitter.call_splitter_llm")
    def test_llm_failure_fallback_preserves_all_pages(
        self, mock_llm: MagicMock
    ) -> None:
        """LLM 실패 시 모든 페이지를 하나의 에세이로 보존한다."""
        mock_llm.side_effect = Exception("API error")
        pages = [
            {"학번": "10305", "이름": "홍길동", "에세이텍스트": "p1"},
            {"학번": "20407", "이름": "김영희", "에세이텍스트": "p2"},
        ]

        result = split_essays([("scan.pdf", pages)])

        assert len(result) == 1
        assert result[0][0] == "scan.pdf"
        assert len(result[0][1]) == 2

    def test_empty_input(self):
        """빈 입력에서는 빈 리스트를 반환한다."""
        result = split_essays([])

        assert result == []
