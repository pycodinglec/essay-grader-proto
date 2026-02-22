"""파일 업로드 및 이미지 변환 모듈."""

import io
import os
import zipfile

from pdf2image import convert_from_bytes
from PIL import Image

VALID_EXTENSIONS = {".pdf", ".png", ".jpg", ".jpeg"}


def validate_file_type(filename: str) -> bool:
    """파일 확장자가 허용 목록(pdf/png/jpg/jpeg)에 포함되는지 검사한다.

    Args:
        filename: 검사할 파일 이름.

    Returns:
        확장자가 유효하면 True, 아니면 False.
    """
    _, ext = os.path.splitext(filename)
    return ext.lower() in VALID_EXTENSIONS


def extract_zip(zip_bytes: bytes) -> list[tuple[str, bytes]]:
    """ZIP 바이트에서 유효한 파일을 추출한다.

    ZIP 안에 폴더(디렉터리)가 포함되어 있으면 ValueError를 발생시킨다.
    유효 확장자(pdf/png/jpg/jpeg)를 가진 파일만 추출한다.

    Args:
        zip_bytes: ZIP 파일의 바이트 데이터.

    Returns:
        (파일이름, 파일바이트) 튜플의 리스트.

    Raises:
        ValueError: ZIP에 폴더가 포함된 경우.
    """
    result: list[tuple[str, bytes]] = []
    with zipfile.ZipFile(io.BytesIO(zip_bytes), "r") as zf:
        for info in zf.infolist():
            if info.is_dir() or "/" in info.filename:
                raise ValueError(
                    "ZIP 파일에 폴더가 포함되어 있습니다. "
                    "파일만 포함된 ZIP을 업로드해 주세요."
                )
            if validate_file_type(info.filename):
                result.append((info.filename, zf.read(info.filename)))
    return result


def pdf_to_images(pdf_bytes: bytes) -> list[Image.Image]:
    """PDF 바이트를 PIL Image 리스트로 변환한다.

    Args:
        pdf_bytes: PDF 파일의 바이트 데이터.

    Returns:
        각 페이지에 해당하는 PIL Image 객체의 리스트.
    """
    return convert_from_bytes(pdf_bytes)


def process_uploaded_file(
    filename: str, file_bytes: bytes
) -> list[tuple[str, bytes]]:
    """업로드된 파일을 유형별로 라우팅하여 처리한다.

    - ZIP: extract_zip으로 위임
    - PDF/이미지: [(filename, file_bytes)] 반환

    Args:
        filename: 업로드된 파일 이름.
        file_bytes: 파일의 바이트 데이터.

    Returns:
        (파일이름, 파일바이트) 튜플의 리스트.

    Raises:
        ValueError: 지원하지 않는 파일 형식인 경우.
    """
    _, ext = os.path.splitext(filename)
    ext_lower = ext.lower()

    if ext_lower == ".zip":
        return extract_zip(file_bytes)

    if ext_lower in VALID_EXTENSIONS:
        return [(filename, file_bytes)]

    raise ValueError(f"지원하지 않는 파일 형식입니다: {ext}")
