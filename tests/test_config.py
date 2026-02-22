"""config 모듈 단위 테스트."""

from unittest.mock import patch, MagicMock

import src.config as config_module


class TestGetGenaiClient:
    """get_genai_client 함수 테스트."""

    def setup_method(self):
        """각 테스트 전에 싱글턴 상태를 초기화한다."""
        config_module._genai_client = None

    @patch("src.config.genai")
    def test_lazy_initialization(self, mock_genai: MagicMock) -> None:
        """최초 호출 시 genai.Client를 생성한다."""
        mock_client = MagicMock()
        mock_genai.Client.return_value = mock_client

        result = config_module.get_genai_client()

        assert result is mock_client
        mock_genai.Client.assert_called_once()

    @patch("src.config.genai")
    def test_returns_same_instance(self, mock_genai: MagicMock) -> None:
        """두 번째 호출부터는 동일 인스턴스를 반환한다."""
        mock_client = MagicMock()
        mock_genai.Client.return_value = mock_client

        first = config_module.get_genai_client()
        second = config_module.get_genai_client()

        assert first is second
        assert mock_genai.Client.call_count == 1

    @patch("src.config.genai")
    def test_passes_http_options_with_timeout(
        self, mock_genai: MagicMock
    ) -> None:
        """HttpOptions(timeout=1800)을 전달한다."""
        mock_client = MagicMock()
        mock_genai.Client.return_value = mock_client

        config_module.get_genai_client()

        call_kwargs = mock_genai.Client.call_args
        http_opts = call_kwargs.kwargs["http_options"]
        assert http_opts.timeout == 1800
