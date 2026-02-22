# config.py

앱 설정 및 API 키 관리 모듈.

## 역할
- 프로젝트 루트의 `.env` 파일에서 환경변수를 자동 로드 (`python-dotenv`)
- API 키 로드 (OpenAI, Anthropic, Google)
- 패스워드 해시 관리
- 학번 형식 등 상수 정의

## 환경변수
| 변수명 | 설명 |
|--------|------|
| `OPENAI_API_KEY` | GPT 5.2 API 키 |
| `ANTHROPIC_API_KEY` | Sonnet 4.6 API 키 |
| `GOOGLE_API_KEY` | Gemini 3 Flash / Nano Banana Pro API 키 |
| `APP_PASSWORD_HASH` | 접근 제어용 SHA-256 패스워드 해시 |
