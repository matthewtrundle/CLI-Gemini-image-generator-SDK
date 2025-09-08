"""Core image generation functionality"""

import base64
import json
import time
import asyncio
from pathlib import Path
from typing import Optional, List, Dict, Any
import aiohttp
from PIL import Image
from io import BytesIO

from .config import Config
from .types import GenerationResult, ImagePrompt, BatchConfig


class ImageGenerator:
    """Core image generation class"""
    
    def __init__(self, config: Config):
        self.config = config
        self.config.validate()
        self._session: Optional[aiohttp.ClientSession] = None
        self._request_times: List[float] = []
    
    async def __aenter__(self):
        """Async context manager entry"""
        self._session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self._session:
            await self._session.close()
    
    async def _check_rate_limit(self):
        """Check and enforce rate limiting"""
        now = time.time()
        self._request_times = [t for t in self._request_times if now - t < 60]
        
        if len(self._request_times) >= self.config.rate_limit.requests_per_minute:
            sleep_time = 60 - (now - self._request_times[0])
            if sleep_time > 0:
                await asyncio.sleep(sleep_time)
        
        self._request_times.append(now)
    
    async def _call_api(self, prompt: str) -> Optional[str]:
        """Call the Gemini API"""
        await self._check_rate_limit()
        
        if not self._session:
            self._session = aiohttp.ClientSession()
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.config.api.key}",
            **self.config.api.headers
        }
        
        payload = {
            "model": self.config.api.model,
            "messages": [{"role": "user", "content": prompt}]
        }
        
        async with self._session.post(
            f"{self.config.api.base_url}/chat/completions",
            headers=headers,
            json=payload
        ) as response:
            if response.status != 200:
                error_text = await response.text()
                raise Exception(f"API Error ({response.status}): {error_text}")
            
            data = await response.json()
            message = data.get("choices", [{}])[0].get("message", {})
            
            if images := message.get("images"):
                image_data = images[0].get("image_url", {}).get("url", "")
                if image_data.startswith("data:image"):
                    return image_data
            
            raise Exception("No image data in response")
    
    async def generate_with_retry(self, prompt: str) -> Optional[str]:
        """Generate image with retry logic"""
        last_error = None
        
        for attempt in range(1, self.config.rate_limit.max_retries + 1):
            try:
                if attempt > 1:
                    await asyncio.sleep(self.config.rate_limit.retry_delay_ms / 1000)
                
                return await self._call_api(prompt)
            except Exception as e:
                last_error = e
                if self.config.logging_enabled:
                    print(f"Attempt {attempt} failed: {e}")
        
        raise last_error or Exception("Failed to generate image")
    
    def _save_image(self, base64_data: str, output_path: str) -> str:
        """Save base64 image data to file"""
        # Remove data URL prefix
        if "," in base64_data:
            base64_data = base64_data.split(",")[1]
        
        # Decode base64
        image_data = base64.b64decode(base64_data)
        image = Image.open(BytesIO(image_data))
        
        # Resize if needed
        if image.size != (self.config.output.width, self.config.output.height):
            image = image.resize(
                (self.config.output.width, self.config.output.height),
                Image.Resampling.LANCZOS
            )
        
        # Ensure output directory exists
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        
        # Save as WebP or specified format
        if self.config.output.format == "webp":
            image.save(output_path, "WEBP", quality=self.config.output.quality)
        else:
            image.save(output_path, quality=self.config.output.quality)
        
        return output_path
    
    async def generate_single(
        self,
        prompt: str,
        filename: str,
        output_dir: Optional[str] = None
    ) -> GenerationResult:
        """Generate a single image"""
        start_time = time.time()
        
        try:
            if self.config.logging_enabled:
                print(f"Generating: {filename}")
            
            image_data = await self.generate_with_retry(prompt)
            
            if not image_data:
                raise Exception("No image data received")
            
            output_dir = output_dir or self.config.output.base_dir
            output_path = str(Path(output_dir) / filename)
            
            self._save_image(image_data, output_path)
            
            duration_ms = int((time.time() - start_time) * 1000)
            
            return GenerationResult(
                success=True,
                id=filename,
                filename=filename,
                path=output_path,
                duration_ms=duration_ms
            )
        except Exception as e:
            return GenerationResult(
                success=False,
                id=filename,
                filename=filename,
                error=str(e),
                duration_ms=int((time.time() - start_time) * 1000)
            )
    
    async def generate_batch(self, batch_config: BatchConfig) -> List[GenerationResult]:
        """Generate multiple images from batch configuration"""
        results = []
        
        if batch_config.parallel:
            # Parallel generation with limited workers
            semaphore = asyncio.Semaphore(batch_config.max_workers)
            
            async def generate_with_semaphore(image: ImagePrompt):
                async with semaphore:
                    return await self.generate_single(
                        image.prompt,
                        image.filename,
                        batch_config.output_dir
                    )
            
            tasks = [generate_with_semaphore(img) for img in batch_config.images]
            results = await asyncio.gather(*tasks)
        else:
            # Sequential generation with delays
            for i, image in enumerate(batch_config.images):
                result = await self.generate_single(
                    image.prompt,
                    image.filename,
                    batch_config.output_dir
                )
                results.append(result)
                
                if i < len(batch_config.images) - 1:
                    await asyncio.sleep(batch_config.delay_ms / 1000)
        
        return results
    
    def generate(self, prompt: str, filename: str, output_dir: Optional[str] = None) -> GenerationResult:
        """Synchronous wrapper for single image generation"""
        return asyncio.run(self.generate_single(prompt, filename, output_dir))
    
    def generate_batch_sync(self, batch_config: BatchConfig) -> List[GenerationResult]:
        """Synchronous wrapper for batch generation"""
        return asyncio.run(self.generate_batch(batch_config))