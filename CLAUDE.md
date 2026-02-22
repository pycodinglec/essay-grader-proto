# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

서논술형 에세이 자동 채점 및 피드백 웹 프로토타입. 학생 에세이(이미지/PDF)를 OCR 후 채점기준표에 따라 3개 LLM(Gemini 3 Flash, GPT 5.2, Sonnet 4.6)으로 평가하고 report.xlsx를 생성한다.

## Tech Stack

- **Python** + **Streamlit** (웹 UI)
- **LLM APIs**: OpenAI (GPT 5.2), Anthropic (Sonnet 4.6), Google (Gemini 3 Flash)
- **OCR**: Google Nano Banana Pro API (최상급 버전만 사용)
- **파일 처리**: openpyxl (xlsx), Pillow/pdf2image (이미지 변환)

## Commands

```bash
# Run app
streamlit run app.py

# Run tests
pytest

# Run single test
pytest tests/test_<module>.py -v

# Run with coverage
pytest --cov=src
```

## Critical Constraints

### Privacy (needs.md #1)
사용자 업로드 데이터, 처리 부산물, 결과 데이터 일체를 서버에 영구 저장하지 않는다. 예외 발생 시 반드시 README.md에 명시.

### Code Size Limits (needs.md #3)
- 함수: **최대 55줄**
- 클래스: **최대 550줄**
- 이 제한을 초과하면 분리/리팩터링 필수

### TDD (needs.md #3)
Unit 단위 TDD 적용. 구현 전에 테스트를 먼저 작성한다.

### Companion Documentation (needs.md #4)
모든 코드 파일에는 동일 이름의 .md 설명 파일이 반드시 함께 존재해야 한다. 예: `ocr.py` → `ocr.md`. 문서 파일(.md, .txt)은 자유 생성 가능.

### Prompt Archiving (needs.md #2)
소프트웨어 기획/설계에 사용된 모든 프롬프트는 .md 파일로 레포지토리에 저장. 요약 가능하나 변경 후 프롬프트도 반드시 저장.

## Architecture — Processing Pipeline

```
1. 인증        → 패스워드 해시 검증 후 메뉴 표시
2. 파일 업로드  → PDF/이미지/ZIP 수용 → 이미지 변환
3. OCR         → Nano Banana Pro API → JSON{학번, 이름, 에세이텍스트} 추출
4. 제출물 식별  → 다중 페이지 병합 → 표로 사용자 확인
5. 채점기준 검증 → xlsx(번호/채점기준/배점) 양식 확인
6. 평가         → 3 LLM 동일 프롬프트 평가 → 최고점 응답 채택
7. 리포트 생성  → report.xlsx(학번/이름/작품번호/피드백) + 진행률 표시
8. 다운로드     → 완성본 다운로드 / 에러 시 중간결과 다운로드 안내
```

## LLM Evaluation Rules

- 3개 LLM에 보내는 프롬프트의 자연어 부분은 **반드시 동일**해야 함
- structured output(JSON) 파라미터 강제 불가 시에 한해 프롬프트 차이 허용
- 합산 점수가 가장 높은 응답 1개만 채택
- 프롬프트 앞에 prompt injection 방어 문구 포함 필수

## ZIP File Rules

- ZIP 내 폴더 포함 시 에러 메시지 표시 후 실행 중단
- 파일명 규칙 없음 (파일명을 힌트로 사용 불가)
- 학생 식별은 전적으로 OCR 내용에 의존

## Error Handling

- 채점 도중 에러 발생 시 중간 결과 다운로드 안내 메시지 제공
- 사용자 임의 중단 버튼은 제공하지 않음 (사용자가 업로드 분량 조절)

## Student ID Format (학번)

5자리 숫자: `[학년 1자리][학급 2자리][번호 2자리]` — 예: `10305` = 1학년 3반 5번
