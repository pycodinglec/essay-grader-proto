# essay-grader-proto

채점 기준에 따른 서논술형 에세이 자동 채점 및 피드백 웹 프로토타입.

## 개요

학생 에세이(이미지/PDF)를 OCR 처리한 뒤, 채점기준표(xlsx)에 따라 3개 LLM(Gemini 3 Flash, GPT 5.2, Sonnet 4.6)으로 평가하고 `report.xlsx`를 생성한다.

## 설치

### 1. Python 가상환경

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 2. 시스템 의존성 (poppler)

PDF → 이미지 변환에 필요하다.

```bash
# macOS
brew install poppler

# Ubuntu/Debian
sudo apt-get install poppler-utils
```

### 3. 환경변수 (.env)

프로젝트 루트에 `.env` 파일을 생성하고 API 키와 패스워드 해시를 입력한다.

```bash
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
GOOGLE_API_KEY=AI...
APP_PASSWORD_HASH=sha256해시값
```

패스워드 해시 생성:
```bash
python3 -c "import hashlib; print(hashlib.sha256('비밀번호'.encode()).hexdigest())"
```

## 실행

```bash
source .venv/bin/activate
streamlit run app.py
```

## 테스트

```bash
pytest
pytest --cov=src
```

## 프로젝트 구조

```
├── app.py              # Streamlit 웹 앱 진입점
├── src/
│   ├── config.py       # 설정 및 API 키 관리 (.env 자동 로드)
│   ├── auth.py         # 패스워드 인증
│   ├── file_handler.py # 파일 업로드 및 이미지 변환
│   ├── ocr.py          # OCR (Google Nano Banana Pro API)
│   ├── submission.py   # 제출물 식별 및 구성
│   ├── rubric.py       # 채점기준표 검증
│   ├── evaluator.py    # 3-LLM 평가
│   └── report.py       # report.xlsx 생성
├── tests/              # 단위 테스트
├── prompts/            # 설계 프롬프트 아카이브
├── .env                # API 키 및 패스워드 해시 (git 미추적)
├── needs.md            # 요구사항 원문
└── CLAUDE.md           # 개발 가이드라인
```

## 개인정보보호

사용자가 업로드한 데이터, 처리 부산물, 결과 데이터 일체를 서버에 영구 저장하지 않는다.
