#!/usr/bin/env python3
"""
Agent-based intelligent image generation examples
"""

import asyncio
import json
from pathlib import Path
import sys
sys.path.append(str(Path(__file__).parent.parent))

from gemini_image_sdk import ImageGeneratorAgent, Config


async def example_chat_interface():
    """Interactive chat with the image generation agent"""
    print("=== Agent Chat Interface ===\n")
    
    config = Config.from_env("../.env")
    agent = ImageGeneratorAgent(config, name="CreativeBot")
    
    # Simulate chat interactions
    conversations = [
        "Create a professional headshot background",
        "enhance modern office space with plants",
        "generate variations of sunset landscape",
        "cyberpunk style futuristic cityscape"
    ]
    
    for user_input in conversations:
        print(f"User: {user_input}")
        response = await agent.chat(user_input)
        
        print(f"Agent: {response['agent']}")
        print(f"Actions: {', '.join(response['actions'])}")
        
        for result in response['results']:
            if result.success:
                print(f"  ✅ Generated: {result.filename}")
            else:
                print(f"  ❌ Failed: {result.error}")
        
        if response['suggestions']:
            print(f"Suggestions: {response['suggestions'][0]}")
        print()
    
    # Save conversation memory
    agent.save_memory("./output/agent_memory.json")
    print("💾 Agent memory saved\n")


async def example_tool_chaining():
    """Execute complex workflows with tool chaining"""
    print("=== Tool Chaining Workflow ===\n")
    
    config = Config.from_env("../.env")
    agent = ImageGeneratorAgent(config)
    
    # Define a creative workflow
    workflow = [
        {
            "tool": "enhance_prompt",
            "params": {"base_prompt": "mountain landscape"}
        },
        {
            "tool": "generate_variations",
            "params": {"base_prompt": "mountain landscape", "count": 2}
        },
        {
            "tool": "style_transfer",
            "params": {
                "prompt": "mountain landscape",
                "style": "watercolor"
            }
        }
    ]
    
    print("Executing workflow:")
    for step in workflow:
        print(f"  - {step['tool']}: {step['params']}")
    print()
    
    results = await agent.execute_chain(workflow)
    
    print(f"Workflow completed with {len(results)} outputs:")
    for result in results:
        if result.success:
            print(f"  ✅ {result.filename}")
        else:
            print(f"  ❌ Failed: {result.error}")


async def example_themed_batch():
    """Generate themed batches for different use cases"""
    print("\n=== Themed Batch Generation ===\n")
    
    config = Config.from_env("../.env")
    agent = ImageGeneratorAgent(config)
    
    themes = ["website_hero", "social_media", "marketing"]
    
    for theme in themes:
        print(f"Generating {theme} batch...")
        results = await agent._batch_theme_generation(theme, count=3)
        
        successful = sum(1 for r in results if r.success)
        print(f"  Generated {successful}/{len(results)} images")
        
        for result in results[:2]:  # Show first 2
            if result.success:
                print(f"    - {result.filename}")


async def example_custom_tool():
    """Register and use custom tools"""
    print("\n=== Custom Tool Registration ===\n")
    
    config = Config.from_env("../.env")
    agent = ImageGeneratorAgent(config)
    
    # Define a custom tool
    async def brand_watermark(prompt: str, brand: str = "MyBrand"):
        """Add brand watermark to generated images"""
        watermarked_prompt = f"{prompt}, subtle '{brand}' watermark in corner"
        async with agent.generator:
            return await agent.generator.generate_single(
                watermarked_prompt,
                f"branded_{brand.lower()}.webp"
            )
    
    # Register the tool
    agent.register_tool("brand_watermark", brand_watermark)
    
    # Use the custom tool
    result = await agent.tools["brand_watermark"](
        prompt="Professional product photography",
        brand="TechCorp"
    )
    
    if result.success:
        print(f"✅ Custom tool generated: {result.filename}")
    else:
        print(f"❌ Custom tool failed: {result.error}")


async def example_style_gallery():
    """Create a gallery of different artistic styles"""
    print("\n=== Style Gallery Creation ===\n")
    
    config = Config.from_env("../.env")
    agent = ImageGeneratorAgent(config)
    
    base_prompt = "serene japanese garden"
    styles = ["watercolor", "oil_painting", "anime", "photorealistic"]
    
    print(f"Creating style gallery for: '{base_prompt}'")
    print("Styles:", ", ".join(styles))
    print()
    
    for style in styles:
        result = await agent._style_transfer(base_prompt, style)
        if result.success:
            print(f"  ✅ {style}: {result.filename}")
        else:
            print(f"  ❌ {style}: Failed")
        
        # Rate limiting
        await asyncio.sleep(2)


async def main():
    """Run all agent examples"""
    print("🤖 Gemini Image Generator SDK - Agent Examples\n")
    
    # Create output directory
    Path("./output").mkdir(exist_ok=True)
    
    # Run examples
    await example_chat_interface()
    await example_tool_chaining()
    await example_themed_batch()
    await example_custom_tool()
    await example_style_gallery()
    
    print("\n✨ Agent examples completed!")


if __name__ == "__main__":
    asyncio.run(main())