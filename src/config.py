"""앱 설정 및 API 키 관리 모듈."""

import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parent.parent / ".env")

OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "")
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")
GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY", "")

# 패스워드 해시 (SHA-256)
PASSWORD_HASH = os.environ.get("APP_PASSWORD_HASH", "")

# 학번 형식: 5자리 숫자 [학년1][학급2][번호2]
STUDENT_ID_PATTERN = r"^\d{5}$"
