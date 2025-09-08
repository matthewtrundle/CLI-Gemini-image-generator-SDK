#!/usr/bin/env python3
"""
Command-line interface for Gemini Image Generator SDK
"""

import argparse
import asyncio
import json
from pathlib import Path
import sys
sys.path.append(str(Path(__file__).parent.parent))

from gemini_image_sdk import (
    ImageGenerator,
    ImageGeneratorAgent,
    Config,
    BatchConfig,
    ImagePrompt
)


def parse_arguments():
    """Parse command-line arguments"""
    parser = argparse.ArgumentParser(
        description="Gemini Image Generator CLI Tool",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Single image generation
    single_parser = subparsers.add_parser("single", help="Generate a single image")
    single_parser.add_argument("prompt", help="Image generation prompt")
    single_parser.add_argument("filename", help="Output filename")
    single_parser.add_argument("--output", default="./generated", help="Output directory")
    
    # Batch generation
    batch_parser = subparsers.add_parser("batch", help="Generate images from JSON file")
    batch_parser.add_argument("config", help="Path to batch configuration JSON")
    batch_parser.add_argument("--parallel", action="store_true", help="Generate in parallel")
    
    # Agent chat
    chat_parser = subparsers.add_parser("chat", help="Interactive agent chat")
    chat_parser.add_argument("message", help="Message to the agent")
    chat_parser.add_argument("--memory", help="Path to agent memory file")
    
    # Style transfer
    style_parser = subparsers.add_parser("style", help="Apply artistic style")
    style_parser.add_argument("prompt", help="Base prompt")
    style_parser.add_argument("style", choices=[
        "cyberpunk", "watercolor", "oil_painting", "anime", "photorealistic"
    ])
    
    # Variations
    var_parser = subparsers.add_parser("variations", help="Generate variations")
    var_parser.add_argument("prompt", help="Base prompt")
    var_parser.add_argument("--count", type=int, default=3, help="Number of variations")
    
    # Theme batch
    theme_parser = subparsers.add_parser("theme", help="Generate themed batch")
    theme_parser.add_argument("theme", choices=["website_hero", "social_media", "marketing"])
    theme_parser.add_argument("--count", type=int, default=5, help="Number of images")
    
    parser.add_argument("--env", help="Path to .env file")
    parser.add_argument("--verbose", action="store_true", help="Verbose output")
    
    return parser.parse_args()


async def cmd_single(args, config):
    """Handle single image generation"""
    
    print(f"🎨 Generating: {args.filename}")
    print(f"   Prompt: {args.prompt[:50]}...")
    
    async with ImageGenerator(config) as generator:
        result = await generator.generate_single(args.prompt, args.filename, args.output)
    
    if result.success:
        print(f"✅ Success! Image saved to: {result.path}")
        if args.verbose:
            print(f"   Duration: {result.duration_ms}ms")
    else:
        print(f"❌ Failed: {result.error}")
        return 1
    
    return 0


async def cmd_batch(args, config):
    """Handle batch generation"""
    with open(args.config, 'r') as f:
        batch_data = json.load(f)
    
    images = [
        ImagePrompt(**img) for img in batch_data.get("images", [])
    ]
    
    batch_config = BatchConfig(
        images=images,
        output_dir=batch_data.get("output_dir", "./generated"),
        parallel=args.parallel
    )
    
    print(f"📋 Processing batch: {len(images)} images")
    if args.parallel:
        print("   Mode: Parallel")
    
    async with ImageGenerator(config) as generator:
        results = await generator.generate_batch(batch_config)
    
    successful = sum(1 for r in results if r.success)
    print(f"\n📊 Results: {successful}/{len(results)} successful")
    
    if args.verbose:
        for result in results:
            status = "✅" if result.success else "❌"
            print(f"   {status} {result.filename}")
    
    return 0 if successful == len(results) else 1


async def cmd_chat(args, config):
    """Handle agent chat interaction"""
    agent = ImageGeneratorAgent(config, name="CLI_Agent")
    
    # Load memory if provided
    if args.memory and Path(args.memory).exists():
        agent.load_memory(args.memory)
        print("💾 Loaded agent memory")
    
    print(f"🤖 Agent: Processing your request...")
    response = await agent.chat(args.message)
    
    print(f"\n📝 Actions taken:")
    for action in response["actions"]:
        print(f"   - {action}")
    
    print(f"\n📸 Results:")
    for result in response["results"]:
        if result.success:
            print(f"   ✅ {result.filename}: {result.path}")
        else:
            print(f"   ❌ Failed: {result.error}")
    
    if response["suggestions"]:
        print(f"\n💡 Suggestions:")
        for suggestion in response["suggestions"][:2]:
            print(f"   - {suggestion}")
    
    # Save memory
    if args.memory:
        agent.save_memory(args.memory)
        print(f"\n💾 Memory saved to {args.memory}")
    
    return 0


async def cmd_style(args, config):
    """Handle style transfer"""
    agent = ImageGeneratorAgent(config)
    
    print(f"🎨 Applying {args.style} style to: {args.prompt}")
    
    result = await agent._style_transfer(args.prompt, args.style)
    
    if result.success:
        print(f"✅ Success! Image saved to: {result.path}")
    else:
        print(f"❌ Failed: {result.error}")
        return 1
    
    return 0


async def cmd_variations(args, config):
    """Handle variation generation"""
    agent = ImageGeneratorAgent(config)
    
    print(f"🎨 Generating {args.count} variations of: {args.prompt}")
    
    results = await agent._generate_variations(args.prompt, args.count)
    
    successful = sum(1 for r in results if r.success)
    print(f"\n📊 Generated {successful}/{args.count} variations")
    
    for i, result in enumerate(results, 1):
        if result.success:
            print(f"   ✅ Variation {i}: {result.filename}")
        else:
            print(f"   ❌ Variation {i}: Failed")
    
    return 0 if successful == args.count else 1


async def cmd_theme(args, config):
    """Handle themed batch generation"""
    agent = ImageGeneratorAgent(config)
    
    print(f"🎨 Generating {args.theme} theme ({args.count} images)")
    
    results = await agent._batch_theme_generation(args.theme, args.count)
    
    successful = sum(1 for r in results if r.success)
    print(f"\n📊 Generated {successful}/{args.count} images")
    
    for result in results:
        if result.success:
            print(f"   ✅ {result.filename}")
        else:
            print(f"   ❌ Failed: {result.error}")
    
    return 0 if successful == args.count else 1


async def main():
    """Main CLI entry point"""
    args = parse_arguments()
    
    if not args.command:
        print("❌ No command specified. Use --help for usage information.")
        return 1
    
    # Load configuration
    try:
        env_file = args.env if args.env else ".env"
        config = Config.from_env(env_file)
        config.logging_enabled = args.verbose
    except Exception as e:
        print(f"❌ Configuration error: {e}")
        return 1
    
    # Execute command
    try:
        if args.command == "single":
            return await cmd_single(args, config)
        elif args.command == "batch":
            return await cmd_batch(args, config)
        elif args.command == "chat":
            return await cmd_chat(args, config)
        elif args.command == "style":
            return await cmd_style(args, config)
        elif args.command == "variations":
            return await cmd_variations(args, config)
        elif args.command == "theme":
            return await cmd_theme(args, config)
        else:
            print(f"❌ Unknown command: {args.command}")
            return 1
    except Exception as e:
        print(f"❌ Error: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)