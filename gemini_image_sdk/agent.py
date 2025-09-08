"""Agent-oriented features for intelligent image generation"""

import json
import asyncio
from typing import Optional, List, Dict, Any, Callable
from pathlib import Path

from .core import ImageGenerator
from .config import Config
from .types import GenerationResult, ImagePrompt, AgentMemory, BatchConfig


class ImageGeneratorAgent:
    """AI Agent for intelligent image generation with memory and tool chaining"""
    
    def __init__(self, config: Config, name: str = "ImageAgent"):
        self.config = config
        self.name = name
        self.generator = ImageGenerator(config)
        self.memory = AgentMemory(
            conversation_history=[],
            generated_images=[],
            context={}
        )
        self.tools: Dict[str, Callable] = {}
        self._register_default_tools()
    
    def _register_default_tools(self):
        """Register default agent tools"""
        self.register_tool("enhance_prompt", self._enhance_prompt)
        self.register_tool("generate_variations", self._generate_variations)
        self.register_tool("style_transfer", self._style_transfer)
        self.register_tool("batch_theme", self._batch_theme_generation)
    
    def register_tool(self, name: str, func: Callable):
        """Register a new tool for the agent"""
        self.tools[name] = func
    
    async def _enhance_prompt(self, base_prompt: str) -> str:
        """Enhance a basic prompt with artistic details"""
        enhancements = [
            "high quality, professional",
            "detailed, photorealistic",
            "artistic composition",
            "perfect lighting"
        ]
        
        # Check memory for style preferences
        if "preferred_style" in self.memory.context:
            enhancements.append(self.memory.context["preferred_style"])
        
        enhanced = f"{base_prompt}, {', '.join(enhancements)}"
        return enhanced
    
    async def _generate_variations(
        self,
        base_prompt: str,
        count: int = 3
    ) -> List[GenerationResult]:
        """Generate multiple variations of a prompt"""
        variations = [
            f"{base_prompt}, morning light",
            f"{base_prompt}, sunset atmosphere",
            f"{base_prompt}, dramatic lighting",
            f"{base_prompt}, minimalist style",
            f"{base_prompt}, vibrant colors"
        ][:count]
        
        results = []
        async with self.generator:
            for i, variant_prompt in enumerate(variations):
                filename = f"variation_{i+1}.{self.config.output.format}"
                result = await self.generator.generate_single(
                    variant_prompt,
                    filename
                )
                results.append(result)
                await asyncio.sleep(self.config.rate_limit.delay_ms / 1000)
        
        return results
    
    async def _style_transfer(
        self,
        prompt: str,
        style: str
    ) -> GenerationResult:
        """Apply a specific artistic style to the prompt"""
        style_mappings = {
            "cyberpunk": "cyberpunk style, neon lights, futuristic",
            "watercolor": "watercolor painting style, soft edges, artistic",
            "oil_painting": "oil painting style, rich textures, classical art",
            "anime": "anime style, manga aesthetic, Japanese art",
            "photorealistic": "photorealistic, 8K resolution, ultra detailed"
        }
        
        styled_prompt = f"{prompt}, {style_mappings.get(style, style)}"
        
        async with self.generator:
            return await self.generator.generate_single(
                styled_prompt,
                f"{style}_{Path(prompt).stem}.{self.config.output.format}"
            )
    
    async def _batch_theme_generation(
        self,
        theme: str,
        count: int = 5
    ) -> List[GenerationResult]:
        """Generate a themed batch of images"""
        theme_prompts = {
            "website_hero": [
                f"Modern website hero section, {theme} theme",
                f"Professional team photo, {theme} industry",
                f"Product showcase, {theme} style",
                f"Office environment, {theme} company",
                f"Customer testimonial background, {theme}"
            ],
            "social_media": [
                f"Instagram post background, {theme}",
                f"Twitter header image, {theme}",
                f"LinkedIn banner, professional {theme}",
                f"Facebook cover photo, {theme}",
                f"YouTube thumbnail background, {theme}"
            ],
            "marketing": [
                f"Email header image, {theme}",
                f"Landing page hero, {theme}",
                f"Advertisement background, {theme}",
                f"Presentation slide background, {theme}",
                f"Brochure cover, {theme}"
            ]
        }
        
        prompts = theme_prompts.get(theme, [f"{theme} image {i+1}" for i in range(count)])[:count]
        
        batch_config = BatchConfig(
            images=[
                ImagePrompt(
                    id=f"{theme}_{i}",
                    prompt=prompt,
                    filename=f"{theme}_{i}.{self.config.output.format}"
                )
                for i, prompt in enumerate(prompts)
            ],
            parallel=True,
            max_workers=3
        )
        
        async with self.generator:
            return await self.generator.generate_batch(batch_config)
    
    async def chat(self, user_input: str) -> Dict[str, Any]:
        """Interactive chat interface for the agent"""
        response = {
            "agent": self.name,
            "input": user_input,
            "actions": [],
            "results": [],
            "suggestions": []
        }
        
        # Parse user intent
        user_input_lower = user_input.lower()
        
        if "enhance" in user_input_lower:
            # Extract base prompt
            base_prompt = user_input.replace("enhance", "").strip()
            enhanced = await self._enhance_prompt(base_prompt)
            response["actions"].append(f"Enhanced prompt: {enhanced}")
            
            async with self.generator:
                result = await self.generator.generate_single(
                    enhanced,
                    f"enhanced_{len(self.memory.generated_images)}.{self.config.output.format}"
                )
            response["results"].append(result)
            self.memory.add_interaction(user_input, result)
        
        elif "variations" in user_input_lower:
            base_prompt = user_input.replace("variations", "").replace("of", "").strip()
            response["actions"].append(f"Generating variations of: {base_prompt}")
            results = await self._generate_variations(base_prompt)
            response["results"].extend(results)
            for result in results:
                self.memory.add_interaction(user_input, result)
        
        elif "style" in user_input_lower:
            # Extract style and prompt
            parts = user_input.split("style")
            if len(parts) >= 2:
                style = parts[0].strip()
                prompt = parts[1].strip()
                response["actions"].append(f"Applying {style} style to: {prompt}")
                result = await self._style_transfer(prompt, style)
                response["results"].append(result)
                self.memory.add_interaction(user_input, result)
        
        elif "batch" in user_input_lower or "theme" in user_input_lower:
            # Extract theme
            theme = "website_hero"  # default
            if "social" in user_input_lower:
                theme = "social_media"
            elif "marketing" in user_input_lower:
                theme = "marketing"
            
            response["actions"].append(f"Generating {theme} batch")
            results = await self._batch_theme_generation(theme)
            response["results"].extend(results)
            for result in results:
                self.memory.add_interaction(user_input, result)
        
        else:
            # Direct generation
            response["actions"].append("Direct image generation")
            async with self.generator:
                result = await self.generator.generate_single(
                    user_input,
                    f"image_{len(self.memory.generated_images)}.{self.config.output.format}"
                )
            response["results"].append(result)
            self.memory.add_interaction(user_input, result)
        
        # Add suggestions based on context
        if self.memory.generated_images:
            response["suggestions"].extend([
                "Try 'variations' to generate different versions",
                "Use 'enhance' for better quality",
                "Apply styles like 'cyberpunk', 'watercolor', or 'anime'",
                "Generate themed batches with 'batch website_hero' or 'batch social_media'"
            ])
        
        return response
    
    async def execute_chain(self, chain: List[Dict[str, Any]]) -> List[GenerationResult]:
        """Execute a chain of image generation tasks"""
        results = []
        
        for step in chain:
            tool_name = step.get("tool")
            params = step.get("params", {})
            
            if tool_name in self.tools:
                tool_result = await self.tools[tool_name](**params)
                if isinstance(tool_result, list):
                    results.extend(tool_result)
                else:
                    results.append(tool_result)
            
            # Add delay between steps
            await asyncio.sleep(self.config.rate_limit.delay_ms / 1000)
        
        return results
    
    def save_memory(self, filepath: str):
        """Save agent memory to file"""
        memory_data = {
            "conversation_history": self.memory.conversation_history,
            "generated_images": [
                {
                    "id": img.id,
                    "filename": img.filename,
                    "path": img.path,
                    "success": img.success
                }
                for img in self.memory.generated_images
            ],
            "context": self.memory.context
        }
        
        with open(filepath, "w") as f:
            json.dump(memory_data, f, indent=2)
    
    def load_memory(self, filepath: str):
        """Load agent memory from file"""
        with open(filepath, "r") as f:
            memory_data = json.load(f)
        
        self.memory.conversation_history = memory_data.get("conversation_history", [])
        self.memory.context = memory_data.get("context", {})
        # Note: generated_images would need reconstruction from paths