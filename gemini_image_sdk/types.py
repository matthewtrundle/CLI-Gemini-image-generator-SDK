"""Type definitions for the Gemini Image SDK"""

from typing import Optional, List, Dict, Any
from dataclasses import dataclass
from enum import Enum


class GenerationStatus(Enum):
    """Status of image generation"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class ImagePrompt:
    """Single image generation prompt"""
    id: str
    prompt: str
    filename: str
    dir: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class GenerationResult:
    """Result of image generation attempt"""
    success: bool
    id: str
    filename: str
    path: Optional[str] = None
    error: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    duration_ms: Optional[int] = None


@dataclass
class BatchConfig:
    """Configuration for batch image generation"""
    images: List[ImagePrompt]
    output_dir: Optional[str] = None
    delay_ms: int = 2000
    parallel: bool = False
    max_workers: int = 3


@dataclass
class AgentMemory:
    """Memory for conversation context in agent mode"""
    conversation_history: List[Dict[str, str]]
    generated_images: List[GenerationResult]
    context: Dict[str, Any]
    
    def add_interaction(self, prompt: str, result: GenerationResult):
        """Add an interaction to memory"""
        self.conversation_history.append({
            "prompt": prompt,
            "result_id": result.id,
            "success": result.success
        })
        if result.success:
            self.generated_images.append(result)