"""Model-specific MiniMax Anthropic options, without provider calls."""

from __future__ import annotations

from typing import Any


M3_MODEL = "MiniMax-M3"
FLASH_MODEL = "MiniMax-M3.1-Flash"
SUPPORTED_MODELS = (M3_MODEL, FLASH_MODEL)
EFFORT_LEVELS = ("low", "medium", "high", "xhigh", "max")


def model_options(model: str, effort: str | None = None) -> dict[str, Any]:
    if model not in SUPPORTED_MODELS:
        raise ValueError(f"unsupported MiniMax media model: {model}")
    if effort is not None and effort not in EFFORT_LEVELS:
        raise ValueError(f"unsupported MiniMax thinking effort: {effort}")
    if model == M3_MODEL:
        if effort is not None:
            raise ValueError("--effort is supported only with MiniMax-M3.1-Flash")
        return {"thinking": {"type": "disabled"}}
    return {
        "thinking": {"type": "adaptive"},
        "output_config": {"effort": effort or "max"},
    }


def fingerprint_model_options(
    model: str, effort: str | None, legacy_temperature: float
) -> dict[str, Any]:
    options = model_options(model, effort)
    if model == M3_MODEL:
        # Existing M3 operations hashed this ignored parameter. Preserve those
        # identities so completed/accepted/unknown operations remain resumable
        # without resetting or replacing their billing evidence.
        return {"temperature": legacy_temperature, **options}
    return options
