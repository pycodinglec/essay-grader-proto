"""file_handler 모듈 단위 테스트."""

import io
import zipfile
from unittest.mock import patch, MagicMock

import pytest

from src.file_handler import (
    validate_file_type,
    extract_zip,
    pdf_to_images,
    process_uploaded_file,
)


# ---------------------------------------------------------------------------
# validate_file_type 테스트
# ---------------------------------------------------------------------------


class TestValidateFileType:
    """validate_file_type 함수 테스트."""

    @pytest.mark.parametrize(
        "filename",
        ["essay.pdf", "scan.png", "photo.jpg", "image.jpeg"],
    )
    def test_valid_extensions(self, filename: str) -> None:
        """허용 확장자(pdf/png/jpg/jpeg)는 True를 반환한다."""
        assert validate_file_type(filename) is True

    @pytest.mark.parametrize(
        "filename",
        ["essay.PDF", "scan.Png", "photo.JPG", "image.JPEG", "doc.JpEg"],
    )
    def test_case_insensitive(self, filename: str) -> None:
        """확장자 대소문자 구분 없이 True를 반환한다."""
        assert validate_file_type(filename) is True

    @pytest.mark.parametrize(
        "filename",
        ["notes.txt", "data.xlsx", "script.py", "archive.zip", "readme.md", "no_ext"],
    )
    def test_invalid_extensions(self, filename: str) -> None:
        """허용되지 않은 확장자는 False를 반환한다."""
        assert validate_file_type(filename) is False

    def test_empty_string(self) -> None:
        """빈 문자열은 False를 반환한다."""
        assert validate_file_type("") is False

    def test_dot_only(self) -> None:
        """점으로 시작하는 히든 파일이나 점만 있는 경우 False를 반환한다."""
        # ".pdf"는 Unix 히든 파일(확장자 없음) — os.path.splitext(".pdf") == (".pdf", "")
        assert validate_file_type(".pdf") is False
        assert validate_file_type(".") is False


# ---------------------------------------------------------------------------
# extract_zip 테스트 — 헬퍼
# ---------------------------------------------------------------------------


def _create_zip_bytes(entries: dict[str, bytes]) -> bytes:
    """entries = {파일이름: 파일내용} 으로부터 ZIP bytes 생성."""
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        for name, data in entries.items():
            zf.writestr(name, data)
    return buf.getvalue()


def _create_zip_with_directory(
    files: dict[str, bytes], dir_name: str = "subdir/"
) -> bytes:
    """폴더 엔트리가 포함된 ZIP bytes 생성."""
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        # 디렉터리 엔트리 추가
        zf.writestr(dir_name, "")
        for name, data in files.items():
            zf.writestr(name, data)
    return buf.getvalue()


# ---------------------------------------------------------------------------
# extract_zip 테스트
# ---------------------------------------------------------------------------


class TestExtractZip:
    """extract_zip 함수 테스트."""

    def test_extract_valid_files(self) -> None:
        """유효한 확장자를 가진 파일만 추출한다."""
        entries = {
            "essay1.pdf": b"pdf-content",
            "scan.png": b"png-content",
            "photo.jpg": b"jpg-content",
        }
        result = extract_zip(_create_zip_bytes(entries))

        assert len(result) == 3
        names = [name for name, _ in result]
        assert "essay1.pdf" in names
        assert "scan.png" in names
        assert "photo.jpg" in names

    def test_filter_invalid_extensions(self) -> None:
        """유효하지 않은 확장자 파일은 제외한다."""
        entries = {
            "essay.pdf": b"pdf-data",
            "notes.txt": b"text-data",
            "data.xlsx": b"xlsx-data",
            "image.jpeg": b"jpeg-data",
        }
        result = extract_zip(_create_zip_bytes(entries))

        assert len(result) == 2
        names = [name for name, _ in result]
        assert "essay.pdf" in names
        assert "image.jpeg" in names

    def test_folder_detected_raises_value_error(self) -> None:
        """ZIP에 폴더가 포함되면 ValueError를 발생시킨다."""
        zip_bytes = _create_zip_with_directory(
            {"essay.pdf": b"data"}, dir_name="folder/"
        )
        with pytest.raises(ValueError, match="ZIP 파일에 폴더가 포함되어 있습니다"):
            extract_zip(zip_bytes)

    def test_nested_path_detected_as_folder(self) -> None:
        """파일 경로에 '/'가 포함되면 폴더로 간주하여 ValueError를 발생시킨다."""
        entries = {"subdir/essay.pdf": b"data"}
        zip_bytes = _create_zip_bytes(entries)
        with pytest.raises(ValueError, match="ZIP 파일에 폴더가 포함되어 있습니다"):
            extract_zip(zip_bytes)

    def test_preserves_file_content(self) -> None:
        """추출된 파일의 내용이 원본과 동일한지 확인한다."""
        content = b"original-pdf-content-12345"
        entries = {"test.pdf": content}
        result = extract_zip(_create_zip_bytes(entries))

        assert len(result) == 1
        assert result[0][0] == "test.pdf"
        assert result[0][1] == content

    def test_empty_zip_returns_empty_list(self) -> None:
        """유효한 파일이 없는 ZIP은 빈 리스트를 반환한다."""
        entries = {"readme.txt": b"text"}
        result = extract_zip(_create_zip_bytes(entries))
        assert result == []

    def test_completely_empty_zip(self) -> None:
        """파일이 전혀 없는 빈 ZIP은 빈 리스트를 반환한다."""
        result = extract_zip(_create_zip_bytes({}))
        assert result == []


# ---------------------------------------------------------------------------
# pdf_to_images 테스트
# ---------------------------------------------------------------------------


class TestPdfToImages:
    """pdf_to_images 함수 테스트 (pdf2image 의존성 mock)."""

    @patch("src.file_handler.convert_from_bytes")
    def test_returns_list_of_images(self, mock_convert: MagicMock) -> None:
        """PDF bytes를 PIL Image 리스트로 변환한다."""
        fake_img_1 = MagicMock(name="Image1")
        fake_img_2 = MagicMock(name="Image2")
        mock_convert.return_value = [fake_img_1, fake_img_2]

        result = pdf_to_images(b"fake-pdf-bytes")

        mock_convert.assert_called_once_with(b"fake-pdf-bytes")
        assert len(result) == 2
        assert result[0] is fake_img_1
        assert result[1] is fake_img_2

    @patch("src.file_handler.convert_from_bytes")
    def test_single_page_pdf(self, mock_convert: MagicMock) -> None:
        """단일 페이지 PDF도 리스트로 반환한다."""
        fake_img = MagicMock(name="SingleImage")
        mock_convert.return_value = [fake_img]

        result = pdf_to_images(b"single-page-pdf")

        assert len(result) == 1
        assert result[0] is fake_img


# ---------------------------------------------------------------------------
# process_uploaded_file 테스트
# ---------------------------------------------------------------------------


class TestProcessUploadedFile:
    """process_uploaded_file 함수 테스트."""

    def test_pdf_file_returns_single_tuple(self) -> None:
        """PDF 파일은 [(filename, bytes)] 형태로 반환한다."""
        data = b"pdf-content"
        result = process_uploaded_file("essay.pdf", data)

        assert result == [("essay.pdf", data)]

    def test_png_image_returns_single_tuple(self) -> None:
        """PNG 이미지 파일은 [(filename, bytes)] 형태로 반환한다."""
        data = b"png-content"
        result = process_uploaded_file("scan.png", data)

        assert result == [("scan.png", data)]

    def test_jpg_image_returns_single_tuple(self) -> None:
        """JPG 이미지 파일은 [(filename, bytes)] 형태로 반환한다."""
        data = b"jpg-content"
        result = process_uploaded_file("photo.jpg", data)

        assert result == [("photo.jpg", data)]

    def test_jpeg_image_returns_single_tuple(self) -> None:
        """JPEG 이미지 파일은 [(filename, bytes)] 형태로 반환한다."""
        data = b"jpeg-content"
        result = process_uploaded_file("image.jpeg", data)

        assert result == [("image.jpeg", data)]

    def test_zip_file_delegates_to_extract_zip(self) -> None:
        """ZIP 파일은 extract_zip으로 위임한다."""
        entries = {
            "a.pdf": b"pdf-data",
            "b.png": b"png-data",
        }
        zip_bytes = _create_zip_bytes(entries)
        result = process_uploaded_file("archive.zip", zip_bytes)

        assert len(result) == 2
        names = [name for name, _ in result]
        assert "a.pdf" in names
        assert "b.png" in names

    def test_unsupported_type_raises_value_error(self) -> None:
        """지원하지 않는 파일 형식은 ValueError를 발생시킨다."""
        with pytest.raises(ValueError, match="지원하지 않는 파일 형식"):
            process_uploaded_file("data.xlsx", b"data")

    def test_unsupported_txt_raises_value_error(self) -> None:
        """txt 파일은 ValueError를 발생시킨다."""
        with pytest.raises(ValueError, match="지원하지 않는 파일 형식"):
            process_uploaded_file("notes.txt", b"text")

    def test_case_insensitive_zip(self) -> None:
        """ZIP 확장자도 대소문자 구분 없이 처리한다."""
        entries = {"a.pdf": b"data"}
        zip_bytes = _create_zip_bytes(entries)
        result = process_uploaded_file("archive.ZIP", zip_bytes)

        assert len(result) == 1
        assert result[0][0] == "a.pdf"

    def test_case_insensitive_pdf(self) -> None:
        """PDF 확장자도 대소문자 구분 없이 처리한다."""
        data = b"pdf-content"
        result = process_uploaded_file("essay.PDF", data)

        assert result == [("essay.PDF", data)]
