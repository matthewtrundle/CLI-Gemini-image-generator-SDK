"""Configuration management for Gemini Image SDK"""

import os
from typing import Optional, Dict, Any
from dataclasses import dataclass, field


@dataclass
class APIConfig:
    """API configuration"""
    key: str
    base_url: str = "https://openrouter.ai/api/v1"
    model: str = "google/gemini-2.5-flash-image-preview"
    headers: Dict[str, str] = field(default_factory=lambda: {
        "HTTP-Referer": "https://github.com/matthewtrundle/CLI-Gemini-image-generator-SDK",
        "X-Title": "Gemini Image Generator SDK"
    })


@dataclass
class OutputConfig:
    """Output configuration"""
    base_dir: str = "./generated"
    format: str = "webp"
    quality: int = 90
    aspect_ratio: Optional[str] = None  # e.g., "1:1", "16:9", "9:16", "4:3", "3:4", etc.

    VALID_ASPECT_RATIOS = {
        "1:1": (1024, 1024),
        "16:9": (1536, 864),
        "9:16": (864, 1536),
        "4:3": (1152, 896),
        "3:4": (896, 1152),
        "21:9": (1536, 672)
    }


@dataclass
class RateLimitConfig:
    """Rate limiting configuration"""
    max_retries: int = 3
    retry_delay_ms: int = 5000
    delay_ms: int = 2000
    requests_per_minute: int = 30
    timeout_seconds: int = 30  # Request timeout
    max_backoff_seconds: int = 60  # Maximum exponential backoff delay


@dataclass
class Config:
    """Main SDK configuration"""
    api: APIConfig
    output: OutputConfig = field(default_factory=OutputConfig)
    rate_limit: RateLimitConfig = field(default_factory=RateLimitConfig)
    logging_enabled: bool = True
    # TODO: Caching feature not yet implemented - these settings are placeholders for future use
    cache_enabled: bool = False  # Not implemented yet
    cache_dir: str = "./.cache/gemini_images"  # Not implemented yet
    
    @classmethod
    def from_env(cls, env_file: Optional[str] = None) -> 'Config':
        """Create config from environment variables"""
        if env_file and os.path.exists(env_file):
            from dotenv import load_dotenv
            load_dotenv(env_file)
        
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY environment variable is required")
        
        return cls(
            api=APIConfig(key=api_key),
            output=OutputConfig(
                base_dir=os.getenv("OUTPUT_DIR", "./generated"),
                quality=int(os.getenv("IMAGE_QUALITY", "90")),
                aspect_ratio=os.getenv("ASPECT_RATIO")
            ),
            logging_enabled=os.getenv("LOGGING_ENABLED", "true").lower() == "true"
        )
    
    def validate(self) -> bool:
        """Validate configuration"""
        if not self.api.key:
            raise ValueError("API key is required")
        if self.output.quality < 1 or self.output.quality > 100:
            raise ValueError("Image quality must be between 1 and 100")
        if self.output.aspect_ratio and self.output.aspect_ratio not in OutputConfig.VALID_ASPECT_RATIOS:
            valid_ratios = ", ".join(OutputConfig.VALID_ASPECT_RATIOS.keys())
            raise ValueError(f"Invalid aspect ratio. Must be one of: {valid_ratios}")
        return True