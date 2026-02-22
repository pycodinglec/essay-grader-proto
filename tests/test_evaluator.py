"""evaluator 모듈 단위 테스트."""

import json
from unittest.mock import patch, MagicMock

import pytest

from src.evaluator import (
    EVALUATION_PROMPT_TEMPLATE,
    _EVALUATION_JSON_SCHEMA,
    build_evaluation_prompt,
    call_gemini,
    call_openai,
    call_anthropic,
    parse_evaluation_response,
    sum_scores,
    evaluate_essay,
)


# ---------------------------------------------------------------------------
# 공통 fixture / 상수
# ---------------------------------------------------------------------------

SAMPLE_RUBRIC = "1. 주제 파악 (10점)\n2. 논리적 전개 (10점)"
SAMPLE_ESSAY = "이 에세이는 환경 보호의 중요성에 대해 논합니다."

VALID_RESPONSE_DICT = {
    "scores": [{"번호": 1, "점수": 8}, {"번호": 2, "점수": 7}],
    "feedback": "주제 파악이 우수하나 논리 전개에 보완이 필요합니다.",
}

VALID_RESPONSE_JSON = json.dumps(VALID_RESPONSE_DICT, ensure_ascii=False)


# ---------------------------------------------------------------------------
# build_evaluation_prompt 테스트
# ---------------------------------------------------------------------------


class TestBuildEvaluationPrompt:
    """build_evaluation_prompt 함수 테스트."""

    def test_includes_rubric_text(self):
        """프롬프트에 채점기준표 텍스트가 포함된다."""
        result = build_evaluation_prompt(SAMPLE_RUBRIC, SAMPLE_ESSAY)

        assert SAMPLE_RUBRIC in result

    def test_includes_essay_text(self):
        """프롬프트에 에세이 텍스트가 포함된다."""
        result = build_evaluation_prompt(SAMPLE_RUBRIC, SAMPLE_ESSAY)

        assert SAMPLE_ESSAY in result

    def test_includes_injection_defense(self):
        """프롬프트에 prompt injection 방어 문구가 포함된다."""
        result = build_evaluation_prompt(SAMPLE_RUBRIC, SAMPLE_ESSAY)

        assert "prompt injection" in result

    def test_includes_json_format_instruction(self):
        """프롬프트에 JSON 형식 지시가 포함된다."""
        result = build_evaluation_prompt(SAMPLE_RUBRIC, SAMPLE_ESSAY)

        assert "JSON" in result
        assert "scores" in result
        assert "feedback" in result

    def test_returns_string(self):
        """문자열을 반환한다."""
        result = build_evaluation_prompt(SAMPLE_RUBRIC, SAMPLE_ESSAY)

        assert isinstance(result, str)

    def test_wraps_rubric_with_content_tags(self):
        """채점기준표가 <content> 태그로 감싸진다."""
        result = build_evaluation_prompt(SAMPLE_RUBRIC, SAMPLE_ESSAY)

        assert f"<content>\n{SAMPLE_RUBRIC}\n</content>" in result

    def test_wraps_essay_with_content_tags(self):
        """에세이가 <content> 태그로 감싸진다."""
        result = build_evaluation_prompt(SAMPLE_RUBRIC, SAMPLE_ESSAY)

        assert f"<content>\n{SAMPLE_ESSAY}\n</content>" in result

    def test_uses_template(self):
        """EVALUATION_PROMPT_TEMPLATE을 기반으로 프롬프트를 생성한다."""
        result = build_evaluation_prompt(SAMPLE_RUBRIC, SAMPLE_ESSAY)
        expected = EVALUATION_PROMPT_TEMPLATE.format(
            rubric=SAMPLE_RUBRIC, essay=SAMPLE_ESSAY
        )

        assert result == expected


# ---------------------------------------------------------------------------
# call_gemini 테스트
# ---------------------------------------------------------------------------


class TestCallGemini:
    """call_gemini 함수 테스트."""

    @patch("src.evaluator.config.get_genai_client")
    def test_uses_correct_model(self, mock_get_client: MagicMock) -> None:
        """gemini-3-flash-preview 모델을 사용하여 호출한다."""
        mock_client = MagicMock()
        mock_get_client.return_value = mock_client
        mock_response = MagicMock()
        mock_response.text = VALID_RESPONSE_JSON
        mock_client.models.generate_content.return_value = mock_response

        call_gemini("test prompt")

        call_kwargs = mock_client.models.generate_content.call_args
        assert call_kwargs.kwargs["model"] == "gemini-3-flash-preview"

    @patch("src.evaluator.config.get_genai_client")
    def test_sends_prompt_as_contents(self, mock_get_client: MagicMock) -> None:
        """프롬프트를 contents 파라미터로 전달한다."""
        mock_client = MagicMock()
        mock_get_client.return_value = mock_client
        mock_response = MagicMock()
        mock_response.text = VALID_RESPONSE_JSON
        mock_client.models.generate_content.return_value = mock_response

        call_gemini("my prompt")

        call_kwargs = mock_client.models.generate_content.call_args
        assert call_kwargs.kwargs["contents"] == "my prompt"

    @patch("src.evaluator.config.get_genai_client")
    def test_returns_response_text(self, mock_get_client: MagicMock) -> None:
        """API 응답의 텍스트를 반환한다."""
        mock_client = MagicMock()
        mock_get_client.return_value = mock_client
        mock_response = MagicMock()
        mock_response.text = "응답 텍스트입니다"
        mock_client.models.generate_content.return_value = mock_response

        result = call_gemini("prompt")

        assert result == "응답 텍스트입니다"

    @patch("src.evaluator.config.get_genai_client")
    def test_uses_genai_singleton(self, mock_get_client: MagicMock) -> None:
        """config.get_genai_client 싱글턴을 사용한다."""
        mock_client = MagicMock()
        mock_get_client.return_value = mock_client
        mock_response = MagicMock()
        mock_response.text = "text"
        mock_client.models.generate_content.return_value = mock_response

        call_gemini("prompt")

        mock_get_client.assert_called_once()

    @patch("src.evaluator.config.get_genai_client")
    def test_uses_json_response_mode(self, mock_get_client: MagicMock) -> None:
        """response_mime_type='application/json'으로 JSON 응답을 강제한다."""
        mock_client = MagicMock()
        mock_get_client.return_value = mock_client
        mock_response = MagicMock()
        mock_response.text = VALID_RESPONSE_JSON
        mock_client.models.generate_content.return_value = mock_response

        call_gemini("prompt")

        call_kwargs = mock_client.models.generate_content.call_args
        cfg = call_kwargs.kwargs["config"]
        assert cfg.response_mime_type == "application/json"


class TestCallGeminiEmptyResponse:
    """call_gemini 빈 응답 처리 테스트."""

    @patch("src.evaluator.config.get_genai_client")
    def test_empty_text_raises_value_error(self, mock_get_client: MagicMock) -> None:
        """빈 텍스트 응답은 ValueError를 발생시킨다."""
        mock_client = MagicMock()
        mock_get_client.return_value = mock_client
        mock_response = MagicMock()
        mock_response.text = ""
        mock_client.models.generate_content.return_value = mock_response

        with pytest.raises(ValueError, match="빈 응답"):
            call_gemini("prompt")

    @patch("src.evaluator.config.get_genai_client")
    def test_none_text_raises_value_error(self, mock_get_client: MagicMock) -> None:
        """None 텍스트 응답은 ValueError를 발생시킨다."""
        mock_client = MagicMock()
        mock_get_client.return_value = mock_client
        mock_response = MagicMock()
        mock_response.text = None
        mock_client.models.generate_content.return_value = mock_response

        with pytest.raises(ValueError, match="빈 응답"):
            call_gemini("prompt")


# ---------------------------------------------------------------------------
# call_openai 테스트
# ---------------------------------------------------------------------------


class TestCallOpenai:
    """call_openai 함수 테스트."""

    @patch("src.evaluator.openai")
    def test_uses_correct_model(self, mock_openai: MagicMock) -> None:
        """gpt-5.2 모델을 사용하여 호출한다."""
        mock_client = MagicMock()
        mock_openai.OpenAI.return_value = mock_client
        mock_choice = MagicMock()
        mock_choice.message.content = VALID_RESPONSE_JSON
        mock_response = MagicMock()
        mock_response.choices = [mock_choice]
        mock_client.chat.completions.create.return_value = mock_response

        call_openai("test prompt")

        call_kwargs = mock_client.chat.completions.create.call_args
        assert call_kwargs.kwargs["model"] == "gpt-5.2"

    @patch("src.evaluator.openai")
    def test_sends_prompt_as_user_message(self, mock_openai: MagicMock) -> None:
        """프롬프트를 user 메시지로 전달한다."""
        mock_client = MagicMock()
        mock_openai.OpenAI.return_value = mock_client
        mock_choice = MagicMock()
        mock_choice.message.content = VALID_RESPONSE_JSON
        mock_response = MagicMock()
        mock_response.choices = [mock_choice]
        mock_client.chat.completions.create.return_value = mock_response

        call_openai("my prompt")

        call_kwargs = mock_client.chat.completions.create.call_args
        messages = call_kwargs.kwargs["messages"]
        assert messages == [{"role": "user", "content": "my prompt"}]

    @patch("src.evaluator.openai")
    def test_returns_response_content(self, mock_openai: MagicMock) -> None:
        """API 응답의 content를 반환한다."""
        mock_client = MagicMock()
        mock_openai.OpenAI.return_value = mock_client
        mock_choice = MagicMock()
        mock_choice.message.content = "GPT 응답"
        mock_response = MagicMock()
        mock_response.choices = [mock_choice]
        mock_client.chat.completions.create.return_value = mock_response

        result = call_openai("prompt")

        assert result == "GPT 응답"

    @patch("src.evaluator.openai")
    def test_uses_openai_api_key(self, mock_openai: MagicMock) -> None:
        """config.OPENAI_API_KEY를 사용한다."""
        mock_client = MagicMock()
        mock_openai.OpenAI.return_value = mock_client
        mock_choice = MagicMock()
        mock_choice.message.content = "text"
        mock_response = MagicMock()
        mock_response.choices = [mock_choice]
        mock_client.chat.completions.create.return_value = mock_response

        with patch("src.evaluator.config.OPENAI_API_KEY", "test-key-o"):
            call_openai("prompt")

        mock_openai.OpenAI.assert_called_once_with(
            api_key="test-key-o", timeout=180.0
        )

    @patch("src.evaluator.openai")
    def test_uses_json_response_format(self, mock_openai: MagicMock) -> None:
        """response_format으로 JSON 응답을 강제한다."""
        mock_client = MagicMock()
        mock_openai.OpenAI.return_value = mock_client
        mock_choice = MagicMock()
        mock_choice.message.content = VALID_RESPONSE_JSON
        mock_response = MagicMock()
        mock_response.choices = [mock_choice]
        mock_client.chat.completions.create.return_value = mock_response

        call_openai("prompt")

        call_kwargs = mock_client.chat.completions.create.call_args
        assert call_kwargs.kwargs["response_format"] == {"type": "json_object"}


class TestCallOpenaiEmptyResponse:
    """call_openai 빈 응답 처리 테스트."""

    @patch("src.evaluator.openai")
    def test_empty_choices_raises_value_error(self, mock_openai: MagicMock) -> None:
        """빈 choices는 ValueError를 발생시킨다."""
        mock_client = MagicMock()
        mock_openai.OpenAI.return_value = mock_client
        mock_response = MagicMock()
        mock_response.choices = []
        mock_client.chat.completions.create.return_value = mock_response

        with pytest.raises(ValueError, match="빈 choices"):
            call_openai("prompt")

    @patch("src.evaluator.openai")
    def test_none_content_raises_value_error(self, mock_openai: MagicMock) -> None:
        """None content는 ValueError를 발생시킨다."""
        mock_client = MagicMock()
        mock_openai.OpenAI.return_value = mock_client
        mock_choice = MagicMock()
        mock_choice.message.content = None
        mock_response = MagicMock()
        mock_response.choices = [mock_choice]
        mock_client.chat.completions.create.return_value = mock_response

        with pytest.raises(ValueError, match="빈 응답"):
            call_openai("prompt")


# ---------------------------------------------------------------------------
# call_anthropic 테스트
# ---------------------------------------------------------------------------


class TestCallAnthropic:
    """call_anthropic 함수 테스트."""

    @patch("src.evaluator.anthropic")
    def test_uses_correct_model(self, mock_anthropic: MagicMock) -> None:
        """claude-sonnet-4-6 모델을 사용하여 호출한다."""
        mock_client = MagicMock()
        mock_anthropic.Anthropic.return_value = mock_client
        mock_content_block = MagicMock()
        mock_content_block.text = VALID_RESPONSE_JSON
        mock_response = MagicMock()
        mock_response.content = [mock_content_block]
        mock_client.messages.create.return_value = mock_response

        call_anthropic("test prompt")

        call_kwargs = mock_client.messages.create.call_args
        assert call_kwargs.kwargs["model"] == "claude-sonnet-4-6"

    @patch("src.evaluator.anthropic")
    def test_sends_prompt_as_user_message(
        self, mock_anthropic: MagicMock
    ) -> None:
        """프롬프트를 user 메시지로 전달한다."""
        mock_client = MagicMock()
        mock_anthropic.Anthropic.return_value = mock_client
        mock_content_block = MagicMock()
        mock_content_block.text = VALID_RESPONSE_JSON
        mock_response = MagicMock()
        mock_response.content = [mock_content_block]
        mock_client.messages.create.return_value = mock_response

        call_anthropic("my prompt")

        call_kwargs = mock_client.messages.create.call_args
        assert call_kwargs.kwargs["messages"] == [
            {"role": "user", "content": "my prompt"}
        ]

    @patch("src.evaluator.anthropic")
    def test_sets_max_tokens(self, mock_anthropic: MagicMock) -> None:
        """max_tokens를 4096으로 설정한다."""
        mock_client = MagicMock()
        mock_anthropic.Anthropic.return_value = mock_client
        mock_content_block = MagicMock()
        mock_content_block.text = VALID_RESPONSE_JSON
        mock_response = MagicMock()
        mock_response.content = [mock_content_block]
        mock_client.messages.create.return_value = mock_response

        call_anthropic("prompt")

        call_kwargs = mock_client.messages.create.call_args
        assert call_kwargs.kwargs["max_tokens"] == 4096

    @patch("src.evaluator.anthropic")
    def test_returns_response_text(self, mock_anthropic: MagicMock) -> None:
        """API 응답의 텍스트를 반환한다."""
        mock_client = MagicMock()
        mock_anthropic.Anthropic.return_value = mock_client
        mock_content_block = MagicMock()
        mock_content_block.text = "Anthropic 응답"
        mock_response = MagicMock()
        mock_response.content = [mock_content_block]
        mock_client.messages.create.return_value = mock_response

        result = call_anthropic("prompt")

        assert result == "Anthropic 응답"

    @patch("src.evaluator.anthropic")
    def test_uses_anthropic_api_key(self, mock_anthropic: MagicMock) -> None:
        """config.ANTHROPIC_API_KEY를 사용한다."""
        mock_client = MagicMock()
        mock_anthropic.Anthropic.return_value = mock_client
        mock_content_block = MagicMock()
        mock_content_block.text = "text"
        mock_response = MagicMock()
        mock_response.content = [mock_content_block]
        mock_client.messages.create.return_value = mock_response

        with patch("src.evaluator.config.ANTHROPIC_API_KEY", "test-key-a"):
            call_anthropic("prompt")

        mock_anthropic.Anthropic.assert_called_once_with(
            api_key="test-key-a", timeout=180.0
        )

    @patch("src.evaluator.anthropic")
    def test_uses_json_schema_output_config(
        self, mock_anthropic: MagicMock
    ) -> None:
        """output_config으로 JSON 스키마 응답을 강제한다."""
        mock_client = MagicMock()
        mock_anthropic.Anthropic.return_value = mock_client
        mock_content_block = MagicMock()
        mock_content_block.text = VALID_RESPONSE_JSON
        mock_response = MagicMock()
        mock_response.content = [mock_content_block]
        mock_client.messages.create.return_value = mock_response

        call_anthropic("prompt")

        call_kwargs = mock_client.messages.create.call_args
        output_config = call_kwargs.kwargs["output_config"]
        assert output_config["format"]["type"] == "json_schema"
        assert output_config["format"]["schema"] == _EVALUATION_JSON_SCHEMA


class TestCallAnthropicEmptyResponse:
    """call_anthropic 빈 응답 처리 테스트."""

    @patch("src.evaluator.anthropic")
    def test_empty_content_raises_value_error(self, mock_anthropic: MagicMock) -> None:
        """빈 content는 ValueError를 발생시킨다."""
        mock_client = MagicMock()
        mock_anthropic.Anthropic.return_value = mock_client
        mock_response = MagicMock()
        mock_response.content = []
        mock_client.messages.create.return_value = mock_response

        with pytest.raises(ValueError, match="빈 content"):
            call_anthropic("prompt")


# ---------------------------------------------------------------------------
# parse_evaluation_response 테스트
# ---------------------------------------------------------------------------


class TestParseEvaluationResponse:
    """parse_evaluation_response 함수 테스트."""

    def test_parses_valid_json(self):
        """유효한 JSON 응답을 파싱한다."""
        result = parse_evaluation_response(VALID_RESPONSE_JSON)

        assert result is not None
        assert result["scores"] == VALID_RESPONSE_DICT["scores"]
        assert result["feedback"] == VALID_RESPONSE_DICT["feedback"]

    def test_parses_json_in_markdown_fences(self):
        """마크다운 코드 펜스로 감싸진 JSON을 파싱한다."""
        wrapped = f"```json\n{VALID_RESPONSE_JSON}\n```"

        result = parse_evaluation_response(wrapped)

        assert result is not None
        assert result["scores"] == VALID_RESPONSE_DICT["scores"]

    def test_parses_json_in_plain_fences(self):
        """언어 지정 없는 코드 펜스로 감싸진 JSON을 파싱한다."""
        wrapped = f"```\n{VALID_RESPONSE_JSON}\n```"

        result = parse_evaluation_response(wrapped)

        assert result is not None
        assert result["feedback"] == VALID_RESPONSE_DICT["feedback"]

    def test_parses_json_with_prefix_text(self):
        """JSON 앞에 설명 텍스트가 있어도 파싱한다."""
        response = f"다음은 채점 결과입니다:\n{VALID_RESPONSE_JSON}"

        result = parse_evaluation_response(response)

        assert result is not None
        assert result["scores"] == VALID_RESPONSE_DICT["scores"]
        assert result["feedback"] == VALID_RESPONSE_DICT["feedback"]

    def test_parses_json_with_suffix_text(self):
        """JSON 뒤에 설명 텍스트가 있어도 파싱한다."""
        response = f"{VALID_RESPONSE_JSON}\n\n이상입니다."

        result = parse_evaluation_response(response)

        assert result is not None
        assert result["scores"] == VALID_RESPONSE_DICT["scores"]

    def test_returns_none_for_invalid_json(self):
        """유효하지 않은 JSON은 None을 반환한다."""
        result = parse_evaluation_response("이것은 JSON이 아닙니다")

        assert result is None

    def test_returns_none_for_missing_scores(self):
        """scores 키가 없으면 None을 반환한다."""
        response = json.dumps({"feedback": "피드백만 있음"})

        result = parse_evaluation_response(response)

        assert result is None

    def test_returns_none_for_missing_feedback(self):
        """feedback 키가 없으면 None을 반환한다."""
        response = json.dumps(
            {"scores": [{"번호": 1, "점수": 5}]}
        )

        result = parse_evaluation_response(response)

        assert result is None

    def test_returns_none_for_scores_not_list(self):
        """scores가 리스트가 아니면 None을 반환한다."""
        response = json.dumps({"scores": "not a list", "feedback": "fb"})

        result = parse_evaluation_response(response)

        assert result is None

    def test_returns_none_for_feedback_not_string(self):
        """feedback이 문자열이 아니면 None을 반환한다."""
        response = json.dumps(
            {"scores": [{"번호": 1, "점수": 5}], "feedback": 123}
        )

        result = parse_evaluation_response(response)

        assert result is None

    def test_returns_none_for_score_item_missing_fields(self):
        """scores 항목에 '번호' 또는 '점수'가 없으면 None을 반환한다."""
        response = json.dumps(
            {"scores": [{"번호": 1}], "feedback": "피드백"}
        )

        result = parse_evaluation_response(response)

        assert result is None

    def test_returns_none_for_empty_string(self):
        """빈 문자열은 None을 반환한다."""
        result = parse_evaluation_response("")

        assert result is None

    def test_handles_extra_fields_gracefully(self):
        """추가 필드가 있어도 정상 파싱한다."""
        data = {
            "scores": [{"번호": 1, "점수": 9}],
            "feedback": "우수함",
            "extra": "무시됨",
        }
        response = json.dumps(data, ensure_ascii=False)

        result = parse_evaluation_response(response)

        assert result is not None
        assert result["scores"] == [{"번호": 1, "점수": 9}]


# ---------------------------------------------------------------------------
# sum_scores 테스트
# ---------------------------------------------------------------------------


class TestSumScores:
    """sum_scores 함수 테스트."""

    def test_sums_multiple_scores(self):
        """여러 항목의 점수를 합산한다."""
        evaluation = {
            "scores": [{"번호": 1, "점수": 8}, {"번호": 2, "점수": 7}],
            "feedback": "피드백",
        }

        result = sum_scores(evaluation)

        assert result == 15.0

    def test_sums_single_score(self):
        """단일 항목의 점수를 반환한다."""
        evaluation = {
            "scores": [{"번호": 1, "점수": 10}],
            "feedback": "피드백",
        }

        result = sum_scores(evaluation)

        assert result == 10.0

    def test_sums_zero_scores(self):
        """점수가 0인 경우에도 정상 합산한다."""
        evaluation = {
            "scores": [{"번호": 1, "점수": 0}, {"번호": 2, "점수": 0}],
            "feedback": "피드백",
        }

        result = sum_scores(evaluation)

        assert result == 0.0

    def test_sums_float_scores(self):
        """소수점 점수도 합산한다."""
        evaluation = {
            "scores": [{"번호": 1, "점수": 8.5}, {"번호": 2, "점수": 7.3}],
            "feedback": "피드백",
        }

        result = sum_scores(evaluation)

        assert result == pytest.approx(15.8)

    def test_returns_float(self):
        """반환값이 float 타입이다."""
        evaluation = {
            "scores": [{"번호": 1, "점수": 5}],
            "feedback": "피드백",
        }

        result = sum_scores(evaluation)

        assert isinstance(result, float)


# ---------------------------------------------------------------------------
# evaluate_essay 테스트
# ---------------------------------------------------------------------------


class TestEvaluateEssay:
    """evaluate_essay 함수 테스트."""

    @patch("src.evaluator.call_anthropic")
    @patch("src.evaluator.call_openai")
    @patch("src.evaluator.call_gemini")
    def test_returns_all_model_results(
        self,
        mock_gemini: MagicMock,
        mock_openai: MagicMock,
        mock_anthropic: MagicMock,
    ) -> None:
        """3개 모델 응답이 by_model에 모두 포함된다."""
        gemini_d = {"scores": [{"번호": 1, "점수": 5}], "feedback": "G"}
        openai_d = {"scores": [{"번호": 1, "점수": 7}], "feedback": "O"}
        anthro_d = {"scores": [{"번호": 1, "점수": 6}], "feedback": "A"}

        mock_gemini.return_value = json.dumps(gemini_d, ensure_ascii=False)
        mock_openai.return_value = json.dumps(openai_d, ensure_ascii=False)
        mock_anthropic.return_value = json.dumps(anthro_d, ensure_ascii=False)

        result = evaluate_essay(SAMPLE_ESSAY, SAMPLE_RUBRIC)

        assert result is not None
        assert "by_model" in result
        assert result["by_model"]["gemini"] == gemini_d
        assert result["by_model"]["openai"] == openai_d
        assert result["by_model"]["anthropic"] == anthro_d

    @patch("src.evaluator.call_anthropic")
    @patch("src.evaluator.call_openai")
    @patch("src.evaluator.call_gemini")
    def test_best_is_highest_score(
        self,
        mock_gemini: MagicMock,
        mock_openai: MagicMock,
        mock_anthropic: MagicMock,
    ) -> None:
        """best가 합산 점수가 가장 높은 응답이다."""
        low = {"scores": [{"번호": 1, "점수": 5}], "feedback": "낮음"}
        mid = {"scores": [{"번호": 1, "점수": 7}], "feedback": "중간"}
        high = {"scores": [{"번호": 1, "점수": 10}], "feedback": "높음"}

        mock_gemini.return_value = json.dumps(low, ensure_ascii=False)
        mock_openai.return_value = json.dumps(high, ensure_ascii=False)
        mock_anthropic.return_value = json.dumps(mid, ensure_ascii=False)

        result = evaluate_essay(SAMPLE_ESSAY, SAMPLE_RUBRIC)

        assert result is not None
        assert result["best"]["feedback"] == "높음"
        assert result["best"]["scores"] == high["scores"]

    @patch("src.evaluator.call_anthropic")
    @patch("src.evaluator.call_openai")
    @patch("src.evaluator.call_gemini")
    def test_failed_model_is_none_in_by_model(
        self,
        mock_gemini: MagicMock,
        mock_openai: MagicMock,
        mock_anthropic: MagicMock,
    ) -> None:
        """실패 모델은 by_model에 None으로 기록된다."""
        mock_gemini.side_effect = Exception("Gemini 에러")
        valid = {"scores": [{"번호": 1, "점수": 8}], "feedback": "유효"}
        mock_openai.return_value = json.dumps(valid, ensure_ascii=False)
        mock_anthropic.return_value = json.dumps(valid, ensure_ascii=False)

        result = evaluate_essay(SAMPLE_ESSAY, SAMPLE_RUBRIC)

        assert result is not None
        assert result["by_model"]["gemini"] is None
        assert result["by_model"]["openai"] is not None
        assert result["by_model"]["anthropic"] is not None

    @patch("src.evaluator.call_anthropic")
    @patch("src.evaluator.call_openai")
    @patch("src.evaluator.call_gemini")
    def test_invalid_response_is_none_in_by_model(
        self,
        mock_gemini: MagicMock,
        mock_openai: MagicMock,
        mock_anthropic: MagicMock,
    ) -> None:
        """파싱 실패 모델도 by_model에 None으로 기록된다."""
        mock_gemini.return_value = "invalid json"
        valid = {"scores": [{"번호": 1, "점수": 8}], "feedback": "유효"}
        mock_openai.return_value = json.dumps(valid, ensure_ascii=False)
        mock_anthropic.return_value = "{bad"

        result = evaluate_essay(SAMPLE_ESSAY, SAMPLE_RUBRIC)

        assert result is not None
        assert result["by_model"]["gemini"] is None
        assert result["by_model"]["openai"] == valid
        assert result["by_model"]["anthropic"] is None

    @patch("src.evaluator.call_anthropic")
    @patch("src.evaluator.call_openai")
    @patch("src.evaluator.call_gemini")
    def test_all_fail_returns_none(
        self,
        mock_gemini: MagicMock,
        mock_openai: MagicMock,
        mock_anthropic: MagicMock,
    ) -> None:
        """모든 LLM이 실패하면 None을 반환한다."""
        mock_gemini.side_effect = Exception("Gemini 에러")
        mock_openai.side_effect = Exception("OpenAI 에러")
        mock_anthropic.side_effect = Exception("Anthropic 에러")

        result = evaluate_essay(SAMPLE_ESSAY, SAMPLE_RUBRIC)

        assert result is None

    @patch("src.evaluator.call_anthropic")
    @patch("src.evaluator.call_openai")
    @patch("src.evaluator.call_gemini")
    def test_calls_build_evaluation_prompt(
        self,
        mock_gemini: MagicMock,
        mock_openai: MagicMock,
        mock_anthropic: MagicMock,
    ) -> None:
        """build_evaluation_prompt로 생성된 프롬프트를 3개 LLM에 전달한다."""
        valid = {"scores": [{"번호": 1, "점수": 5}], "feedback": "fb"}
        response_json = json.dumps(valid, ensure_ascii=False)
        mock_gemini.return_value = response_json
        mock_openai.return_value = response_json
        mock_anthropic.return_value = response_json

        evaluate_essay(SAMPLE_ESSAY, SAMPLE_RUBRIC)

        expected_prompt = build_evaluation_prompt(SAMPLE_RUBRIC, SAMPLE_ESSAY)
        mock_gemini.assert_called_once_with(expected_prompt)
        mock_openai.assert_called_once_with(expected_prompt)
        mock_anthropic.assert_called_once_with(expected_prompt)
