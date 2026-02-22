"""앱 설정 및 API 키 관리 모듈."""

from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv
from google import genai
from google.genai.types import HttpOptions

load_dotenv(Path(__file__).resolve().parent.parent / ".env")

OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "")
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")
GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY", "")

# 패스워드 해시 (SHA-256)
PASSWORD_HASH = os.environ.get("APP_PASSWORD_HASH", "")

# 학번 형식: 5자리 숫자 [학년1][학급2][번호2]
STUDENT_ID_PATTERN = r"^\d{5}$"

_genai_client: genai.Client | None = None


def get_genai_client() -> genai.Client:
    """genai.Client 싱글턴을 반환한다.

    최초 호출 시 lazy 초기화하며, timeout=1,800,000ms(1800초)를 설정한다.
    """
    global _genai_client  # noqa: PLW0603
    if _genai_client is None:
        _genai_client = genai.Client(
            api_key=GOOGLE_API_KEY,
            http_options=HttpOptions(timeout=1_800_000),
        )
    return _genai_client
