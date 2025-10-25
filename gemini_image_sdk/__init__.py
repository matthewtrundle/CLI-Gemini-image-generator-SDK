"""
Gemini Image Generator SDK
A Python SDK for AI-powered image generation using Gemini 2.5 Flash
"""

from .agent import ImageGeneratorAgent
from .core import ImageGenerator
from .config import Config, APIConfig, OutputConfig
from .types import (
    GenerationResult,
    BatchConfig,
    ImagePrompt,
    GeminiSDKError,
    APIError,
    RateLimitError,
    AuthenticationError,
    InvalidRequestError,
    ServerError
)

__version__ = "1.0.0"
__all__ = [
    "ImageGeneratorAgent",
    "ImageGenerator",
    "Config",
    "APIConfig",
    "OutputConfig",
    "GenerationResult",
    "BatchConfig",
    "ImagePrompt",
    "GeminiSDKError",
    "APIError",
    "RateLimitError",
    "AuthenticationError",
    "InvalidRequestError",
    "ServerError"
]