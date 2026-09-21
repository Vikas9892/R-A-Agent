import logging
from typing import Any
import litellm
from app.config import settings

logger = logging.getLogger(__name__)


def generate_response(
    messages: list[dict[str, str]],
    model: str | None = None,
    **kwargs: Any,
) -> str:
    """Generate an assistant response using LiteLLM.

    Args:
        messages: List of message dictionaries with 'role' and 'content'.
        model: Optional model identifier. Defaults to settings.model_1.
        **kwargs: Additional parameters forwarded to litellm.completion.

    Returns:
        The assistant response string.

    Raises:
        RuntimeError: If LiteLLM completion encounters an error.
    """
    selected_model = model or settings.model_1
    try:
        response = litellm.completion(
            model=selected_model,
            messages=messages,
            **kwargs,
        )
        content = response.choices[0].message.content
        return content or ""
    except Exception as exc:
        logger.error("LiteLLM generation failed for model '%s': %s", selected_model, exc)
        raise RuntimeError(f"LiteLLM call failed for model '{selected_model}': {exc}") from exc
