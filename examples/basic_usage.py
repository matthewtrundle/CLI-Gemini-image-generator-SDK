#!/usr/bin/env python3
"""
Basic usage example for Gemini Image Generator SDK
"""

import asyncio
from pathlib import Path
import sys
sys.path.append(str(Path(__file__).parent.parent))

from gemini_image_sdk import ImageGenerator, Config


def example_single_image():
    """Generate a single image synchronously"""
    print("=== Single Image Generation ===")
    
    # Initialize configuration
    config = Config.from_env("../.env")
    generator = ImageGenerator(config)
    
    # Generate image
    result = generator.generate(
        prompt="A modern minimalist home office with natural lighting",
        filename="office.webp",
        output_dir="./output"
    )
    
    if result.success:
        print(f"✅ Image generated successfully!")
        print(f"   Path: {result.path}")
        print(f"   Time: {result.duration_ms}ms")
    else:
        print(f"❌ Generation failed: {result.error}")


async def example_async_generation():
    """Generate multiple images asynchronously"""
    print("\n=== Async Image Generation ===")
    
    config = Config.from_env("../.env")
    
    prompts = [
        ("Sunrise over mountains", "sunrise.webp"),
        ("City skyline at night", "cityscape.webp"),
        ("Tropical beach paradise", "beach.webp")
    ]
    
    async with ImageGenerator(config) as generator:
        tasks = [
            generator.generate_single(prompt, filename, "./output")
            for prompt, filename in prompts
        ]
        
        results = await asyncio.gather(*tasks)
        
        for result in results:
            status = "✅" if result.success else "❌"
            print(f"{status} {result.filename}: {result.path if result.success else result.error}")


async def example_with_retry():
    """Example with retry logic and error handling"""
    print("\n=== Generation with Retry ===")
    
    config = Config.from_env("../.env")
    config.rate_limit.max_retries = 3
    
    async with ImageGenerator(config) as generator:
        try:
            result = await generator.generate_single(
                prompt="Abstract art with vibrant colors and geometric shapes",
                filename="abstract.webp"
            )
            
            if result.success:
                print(f"✅ Generated after retries: {result.path}")
            else:
                print(f"❌ Failed after retries: {result.error}")
                
        except Exception as e:
            print(f"❌ Unexpected error: {e}")


def main():
    """Run all examples"""
    print("🎨 Gemini Image Generator SDK - Basic Examples\n")
    
    # Run synchronous example
    example_single_image()
    
    # Run async examples
    asyncio.run(example_async_generation())
    asyncio.run(example_with_retry())
    
    print("\n✨ Examples completed!")


if __name__ == "__main__":
    main()