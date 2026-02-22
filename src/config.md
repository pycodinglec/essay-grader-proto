# config.py

앱 설정 및 API 키 관리 모듈.

## 역할
- 프로젝트 루트의 `.env` 파일에서 환경변수를 자동 로드 (`python-dotenv`)
- API 키 로드 (OpenAI, Anthropic, Google)
- 패스워드 해시 관리
- 학번 형식 등 상수 정의
- genai.Client 싱글턴 관리

## 환경변수
| 변수명 | 설명 |
|--------|------|
| `OPENAI_API_KEY` | GPT 5.2 API 키 |
| `ANTHROPIC_API_KEY` | Sonnet 4.6 API 키 |
| `GOOGLE_API_KEY` | Gemini 3 Flash / Nano Banana Pro API 키 |
| `APP_PASSWORD_HASH` | 접근 제어용 SHA-256 패스워드 해시 |

## 함수

### `get_genai_client() -> genai.Client`
- Google genai.Client 싱글턴을 반환한다.
- 최초 호출 시 lazy 초기화: `genai.Client(api_key=GOOGLE_API_KEY, http_options=HttpOptions(timeout=1_800_000))` (밀리초 단위, 1800초)
- 이후 호출에서는 동일 인스턴스를 재사용한다.
- `src.ocr`, `src.evaluator`, `src.essay_splitter`에서 공통으로 사용한다.

## 의존성
- `python-dotenv`: .env 파일 로드
- `google-genai`: genai.Client, HttpOptions
