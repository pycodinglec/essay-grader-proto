"""ocr 모듈 단위 테스트."""

import io
from unittest.mock import patch, MagicMock, call

import pytest
from PIL import Image

from src.ocr import (
    OCR_PROMPT,
    extract_text_from_image,
    extract_text_from_images,
    ocr_file,
    parse_ocr_response,
)

MODEL_NAME = "gemini-3.1-pro-preview"


# ---------------------------------------------------------------------------
# parse_ocr_response 테스트
# ---------------------------------------------------------------------------


class TestParseOcrResponse:
    """parse_ocr_response 함수 테스트."""

    def test_valid_json(self) -> None:
        """올바른 JSON 응답을 파싱한다."""
        response = '{"학번": "10305", "이름": "홍길동", "에세이텍스트": "에세이 본문"}'
        result = parse_ocr_response(response)

        assert result == {
            "학번": "10305",
            "이름": "홍길동",
            "에세이텍스트": "에세이 본문",
        }

    def test_json_in_markdown_fences(self) -> None:
        """마크다운 코드 펜스로 감싼 JSON을 파싱한다."""
        response = (
            '```json\n'
            '{"학번": "20407", "이름": "김영희", "에세이텍스트": "본문 내용"}\n'
            '```'
        )
        result = parse_ocr_response(response)

        assert result == {
            "학번": "20407",
            "이름": "김영희",
            "에세이텍스트": "본문 내용",
        }

    def test_json_in_plain_fences(self) -> None:
        """언어 태그 없는 코드 펜스로 감싼 JSON을 파싱한다."""
        response = (
            '```\n'
            '{"학번": "30101", "이름": "박철수", "에세이텍스트": "내용"}\n'
            '```'
        )
        result = parse_ocr_response(response)

        assert result == {
            "학번": "30101",
            "이름": "박철수",
            "에세이텍스트": "내용",
        }

    def test_invalid_json_fallback(self) -> None:
        """유효하지 않은 JSON은 원문을 에세이텍스트로 반환한다."""
        raw_text = "이것은 JSON이 아닌 일반 텍스트입니다."
        result = parse_ocr_response(raw_text)

        assert result == {
            "학번": "",
            "이름": "",
            "에세이텍스트": raw_text,
        }

    def test_missing_keys_fallback(self) -> None:
        """필수 키가 누락된 JSON은 폴백 결과를 반환한다."""
        response = '{"학번": "10305"}'
        result = parse_ocr_response(response)

        assert result == {
            "학번": "",
            "이름": "",
            "에세이텍스트": response,
        }

    def test_missing_essay_key_fallback(self) -> None:
        """에세이텍스트 키가 누락된 JSON은 폴백 결과를 반환한다."""
        response = '{"학번": "10305", "이름": "홍길동"}'
        result = parse_ocr_response(response)

        assert result == {
            "학번": "",
            "이름": "",
            "에세이텍스트": response,
        }

    def test_whitespace_around_json(self) -> None:
        """앞뒤 공백이 있는 JSON을 올바르게 파싱한다."""
        response = '  \n {"학번": "10305", "이름": "홍길동", "에세이텍스트": "본문"} \n  '
        result = parse_ocr_response(response)

        assert result["학번"] == "10305"
        assert result["이름"] == "홍길동"
        assert result["에세이텍스트"] == "본문"

    def test_ocr_prompt_includes_injection_defense(self) -> None:
        """OCR 프롬프트에 prompt injection 방어 문구가 포함된다."""
        assert "prompt injection" in OCR_PROMPT


# ---------------------------------------------------------------------------
# extract_text_from_image 테스트
# ---------------------------------------------------------------------------


class TestExtractTextFromImage:
    """extract_text_from_image 함수 테스트."""

    @patch("src.ocr.config.get_genai_client")
    def test_calls_generate_content_with_correct_model(
        self, mock_get_client: MagicMock
    ) -> None:
        """올바른 모델 이름으로 generate_content를 호출한다."""
        mock_client = MagicMock()
        mock_get_client.return_value = mock_client
        mock_response = MagicMock()
        mock_response.text = '{"학번": "10305", "이름": "홍길동", "에세이텍스트": "텍스트"}'
        mock_client.models.generate_content.return_value = mock_response

        fake_image = MagicMock(spec=Image.Image)
        extract_text_from_image(fake_image)

        mock_client.models.generate_content.assert_called_once()
        call_kwargs = mock_client.models.generate_content.call_args
        assert call_kwargs.kwargs["model"] == MODEL_NAME

    @patch("src.ocr.config.get_genai_client")
    def test_sends_image_and_prompt_as_contents(
        self, mock_get_client: MagicMock
    ) -> None:
        """contents에 이미지와 OCR 프롬프트를 함께 전달한다."""
        mock_client = MagicMock()
        mock_get_client.return_value = mock_client
        mock_response = MagicMock()
        mock_response.text = '{"학번": "", "이름": "", "에세이텍스트": "텍스트"}'
        mock_client.models.generate_content.return_value = mock_response

        fake_image = MagicMock(spec=Image.Image)
        extract_text_from_image(fake_image)

        call_kwargs = mock_client.models.generate_content.call_args
        contents = call_kwargs.kwargs["contents"]
        assert fake_image in contents
        assert OCR_PROMPT in contents

    @patch("src.ocr.config.get_genai_client")
    def test_returns_parsed_dict(self, mock_get_client: MagicMock) -> None:
        """API 응답을 파싱하여 dict를 반환한다."""
        mock_client = MagicMock()
        mock_get_client.return_value = mock_client
        mock_response = MagicMock()
        mock_response.text = '{"학번": "10305", "이름": "홍길동", "에세이텍스트": "에세이 본문"}'
        mock_client.models.generate_content.return_value = mock_response

        fake_image = MagicMock(spec=Image.Image)
        result = extract_text_from_image(fake_image)

        assert isinstance(result, dict)
        assert result["학번"] == "10305"
        assert result["이름"] == "홍길동"
        assert result["에세이텍스트"] == "에세이 본문"

    @patch("src.ocr.config.get_genai_client")
    def test_returns_fallback_dict_on_invalid_response(
        self, mock_get_client: MagicMock
    ) -> None:
        """API가 유효하지 않은 JSON을 반환하면 폴백 dict를 반환한다."""
        mock_client = MagicMock()
        mock_get_client.return_value = mock_client
        mock_response = MagicMock()
        mock_response.text = "일반 텍스트 응답"
        mock_client.models.generate_content.return_value = mock_response

        fake_image = MagicMock(spec=Image.Image)
        result = extract_text_from_image(fake_image)

        assert isinstance(result, dict)
        assert result["학번"] == ""
        assert result["이름"] == ""
        assert result["에세이텍스트"] == "일반 텍스트 응답"

    @patch("src.ocr.config.get_genai_client")
    def test_uses_genai_singleton(
        self, mock_get_client: MagicMock
    ) -> None:
        """config.get_genai_client 싱글턴을 사용한다."""
        mock_client = MagicMock()
        mock_get_client.return_value = mock_client
        mock_response = MagicMock()
        mock_response.text = '{"학번": "", "이름": "", "에세이텍스트": "텍스트"}'
        mock_client.models.generate_content.return_value = mock_response

        fake_image = MagicMock(spec=Image.Image)
        extract_text_from_image(fake_image)

        mock_get_client.assert_called_once()


# ---------------------------------------------------------------------------
# extract_text_from_images 테스트
# ---------------------------------------------------------------------------


class TestExtractTextFromImages:
    """extract_text_from_images 함수 테스트."""

    @patch("src.ocr.extract_text_from_image")
    def test_processes_all_images(
        self, mock_extract: MagicMock
    ) -> None:
        """모든 이미지에 대해 extract_text_from_image를 호출한다."""
        mock_extract.side_effect = [
            {"학번": "10305", "이름": "홍길동", "에세이텍스트": "텍스트1"},
            {"학번": "20407", "이름": "김영희", "에세이텍스트": "텍스트2"},
            {"학번": "", "이름": "", "에세이텍스트": "텍스트3"},
        ]

        images = [
            MagicMock(spec=Image.Image),
            MagicMock(spec=Image.Image),
            MagicMock(spec=Image.Image),
        ]
        result = extract_text_from_images(images)

        assert mock_extract.call_count == 3
        assert len(result) == 3
        assert result[0]["학번"] == "10305"
        assert result[2]["에세이텍스트"] == "텍스트3"

    @patch("src.ocr.extract_text_from_image")
    def test_preserves_order(self, mock_extract: MagicMock) -> None:
        """이미지 순서대로 결과를 반환한다."""
        mock_extract.side_effect = [
            {"학번": "10305", "이름": "홍길동", "에세이텍스트": "첫째"},
            {"학번": "20407", "이름": "김영희", "에세이텍스트": "둘째"},
        ]

        img1 = MagicMock(spec=Image.Image)
        img2 = MagicMock(spec=Image.Image)
        result = extract_text_from_images([img1, img2])

        mock_extract.assert_has_calls([call(img1), call(img2)])
        assert result[0]["에세이텍스트"] == "첫째"
        assert result[1]["에세이텍스트"] == "둘째"

    @patch("src.ocr.extract_text_from_image")
    def test_empty_list_returns_empty(
        self, mock_extract: MagicMock
    ) -> None:
        """빈 이미지 리스트는 빈 리스트를 반환한다."""
        result = extract_text_from_images([])

        mock_extract.assert_not_called()
        assert result == []

    @patch("src.ocr.extract_text_from_image")
    def test_single_image(self, mock_extract: MagicMock) -> None:
        """단일 이미지도 리스트로 반환한다."""
        mock_extract.return_value = {
            "학번": "10305", "이름": "홍길동", "에세이텍스트": "유일한 텍스트"
        }

        img = MagicMock(spec=Image.Image)
        result = extract_text_from_images([img])

        assert len(result) == 1
        assert result[0]["에세이텍스트"] == "유일한 텍스트"


# ---------------------------------------------------------------------------
# ocr_file 테스트
# ---------------------------------------------------------------------------


class TestOcrFile:
    """ocr_file 함수 테스트."""

    @patch("src.ocr.extract_text_from_images")
    @patch("src.ocr.file_handler.pdf_to_images")
    def test_pdf_converts_and_ocrs(
        self,
        mock_pdf_to_images: MagicMock,
        mock_extract_texts: MagicMock,
    ) -> None:
        """PDF 파일은 이미지로 변환 후 OCR을 수행한다."""
        fake_img1 = MagicMock(spec=Image.Image)
        fake_img2 = MagicMock(spec=Image.Image)
        mock_pdf_to_images.return_value = [fake_img1, fake_img2]
        mock_extract_texts.return_value = [
            {"학번": "10305", "이름": "홍길동", "에세이텍스트": "페이지1 텍스트"},
            {"학번": "", "이름": "", "에세이텍스트": "페이지2 텍스트"},
        ]

        result = ocr_file("essay.pdf", b"fake-pdf-bytes")

        mock_pdf_to_images.assert_called_once_with(b"fake-pdf-bytes")
        mock_extract_texts.assert_called_once_with([fake_img1, fake_img2])
        assert len(result) == 2
        assert result[0]["에세이텍스트"] == "페이지1 텍스트"

    @patch("src.ocr.extract_text_from_images")
    @patch("src.ocr.file_handler.pdf_to_images")
    def test_pdf_case_insensitive(
        self,
        mock_pdf_to_images: MagicMock,
        mock_extract_texts: MagicMock,
    ) -> None:
        """PDF 확장자 대소문자 구분 없이 처리한다."""
        mock_pdf_to_images.return_value = [MagicMock(spec=Image.Image)]
        mock_extract_texts.return_value = [
            {"학번": "", "이름": "", "에세이텍스트": "텍스트"}
        ]

        result = ocr_file("essay.PDF", b"fake-pdf")

        mock_pdf_to_images.assert_called_once()
        assert len(result) == 1

    @patch("src.ocr.extract_text_from_image")
    @patch("src.ocr.Image.open")
    def test_png_image_loads_and_ocrs(
        self,
        mock_image_open: MagicMock,
        mock_extract_text: MagicMock,
    ) -> None:
        """PNG 이미지 파일을 로드하여 OCR을 수행한다."""
        fake_img = MagicMock(spec=Image.Image)
        mock_image_open.return_value = fake_img
        mock_extract_text.return_value = {
            "학번": "10305", "이름": "홍길동", "에세이텍스트": "이미지 텍스트"
        }

        result = ocr_file("scan.png", b"fake-png-bytes")

        mock_image_open.assert_called_once()
        mock_extract_text.assert_called_once_with(fake_img)
        assert result == [{"학번": "10305", "이름": "홍길동", "에세이텍스트": "이미지 텍스트"}]

    @patch("src.ocr.extract_text_from_image")
    @patch("src.ocr.Image.open")
    def test_jpg_image_loads_and_ocrs(
        self,
        mock_image_open: MagicMock,
        mock_extract_text: MagicMock,
    ) -> None:
        """JPG 이미지 파일을 로드하여 OCR을 수행한다."""
        fake_img = MagicMock(spec=Image.Image)
        mock_image_open.return_value = fake_img
        mock_extract_text.return_value = {
            "학번": "", "이름": "", "에세이텍스트": "JPG 텍스트"
        }

        result = ocr_file("photo.jpg", b"fake-jpg-bytes")

        mock_image_open.assert_called_once()
        mock_extract_text.assert_called_once_with(fake_img)
        assert result == [{"학번": "", "이름": "", "에세이텍스트": "JPG 텍스트"}]

    @patch("src.ocr.extract_text_from_image")
    @patch("src.ocr.Image.open")
    def test_jpeg_image_loads_and_ocrs(
        self,
        mock_image_open: MagicMock,
        mock_extract_text: MagicMock,
    ) -> None:
        """JPEG 이미지 파일을 로드하여 OCR을 수행한다."""
        fake_img = MagicMock(spec=Image.Image)
        mock_image_open.return_value = fake_img
        mock_extract_text.return_value = {
            "학번": "", "이름": "", "에세이텍스트": "JPEG 텍스트"
        }

        result = ocr_file("image.jpeg", b"fake-jpeg-bytes")

        mock_image_open.assert_called_once()
        mock_extract_text.assert_called_once_with(fake_img)
        assert result == [{"학번": "", "이름": "", "에세이텍스트": "JPEG 텍스트"}]

    def test_invalid_file_type_raises_value_error(self) -> None:
        """지원하지 않는 파일 형식은 ValueError를 발생시킨다."""
        with pytest.raises(ValueError, match="지원하지 않는 파일 형식"):
            ocr_file("notes.txt", b"text-data")

    def test_xlsx_file_raises_value_error(self) -> None:
        """xlsx 파일은 ValueError를 발생시킨다."""
        with pytest.raises(ValueError, match="지원하지 않는 파일 형식"):
            ocr_file("data.xlsx", b"xlsx-data")

    @patch("src.ocr.extract_text_from_image")
    @patch("src.ocr.Image.open")
    def test_image_wraps_single_result_in_list(
        self,
        mock_image_open: MagicMock,
        mock_extract_text: MagicMock,
    ) -> None:
        """이미지 파일의 OCR 결과는 단일 요소 리스트로 반환한다."""
        fake_img = MagicMock(spec=Image.Image)
        mock_image_open.return_value = fake_img
        mock_extract_text.return_value = {
            "학번": "30101", "이름": "박철수", "에세이텍스트": "단일 결과"
        }

        result = ocr_file("scan.PNG", b"png-bytes")

        assert isinstance(result, list)
        assert len(result) == 1
        assert isinstance(result[0], dict)
        assert result[0]["에세이텍스트"] == "단일 결과"
