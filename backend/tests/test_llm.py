from unittest.mock import MagicMock, patch
import pytest
from app.llm.client import generate_response
from app.config import settings


def test_generate_response_default_model() -> None:
    mock_choice = MagicMock()
    mock_choice.message.content = "Mocked answer from default model"
    mock_completion_response = MagicMock(choices=[mock_choice])

    with patch("litellm.completion", return_value=mock_completion_response) as mock_litellm:
        messages = [{"role": "user", "content": "Hello world"}]
        result = generate_response(messages)

        assert result == "Mocked answer from default model"
        mock_litellm.assert_called_once_with(
            model=settings.model_1,
            messages=messages,
        )


def test_generate_response_custom_model() -> None:
    mock_choice = MagicMock()
    mock_choice.message.content = "Mocked answer from model 2"
    mock_completion_response = MagicMock(choices=[mock_choice])

    with patch("litellm.completion", return_value=mock_completion_response) as mock_litellm:
        messages = [{"role": "user", "content": "What is AI?"}]
        result = generate_response(messages, model=settings.model_2)

        assert result == "Mocked answer from model 2"
        mock_litellm.assert_called_once_with(
            model=settings.model_2,
            messages=messages,
        )


def test_generate_response_error_handling() -> None:
    with patch("litellm.completion", side_effect=Exception("API connection timeout")):
        messages = [{"role": "user", "content": "Trigger failure"}]
        with pytest.raises(RuntimeError) as exc_info:
            generate_response(messages)
        assert "LiteLLM call failed" in str(exc_info.value)
