# 🎨 Gemini Image Generator SDK

An intelligent Python SDK for AI-powered image generation using Google's Gemini 2.5 Flash. Features an agent-based architecture with conversation memory, tool chaining, and natural language understanding.

Built with Claude Code 🤖

## ✨ Features

### 🧠 Intelligent Agent System
- **Conversation Memory**: Remembers your preferences and past generations
- **Tool Chaining**: Execute complex multi-step workflows
- **Natural Language**: Chat with it like an assistant, not a tool
- **Smart Enhancement**: Automatically improves your prompts

### 🚀 Core Capabilities
- **Async/Sync Support**: Use with `async/await` or synchronously
- **Batch Processing**: Generate multiple images efficiently
- **Style Transfer**: Apply artistic styles (cyberpunk, watercolor, anime, etc.)
- **Variations**: Create multiple versions from a single prompt
- **Rate Limiting**: Built-in protection and retry logic

## 📦 Installation

```bash
# Clone the repository
git clone https://github.com/matthewtrundle/CLI-Gemini-image-generator-SDK.git
cd CLI-Gemini-image-generator-SDK

# Install dependencies
pip install -r requirements.txt

# Set up your API key
cp .env.example .env
# Edit .env and add your OpenRouter API key
```

Get your API key from [OpenRouter](https://openrouter.ai/)

## 🚀 Quick Start

### Basic Image Generation

```python
from gemini_image_sdk import ImageGenerator, Config

# Initialize
config = Config.from_env()
generator = ImageGenerator(config)

# Generate an image
result = generator.generate(
    prompt="A serene mountain landscape at sunset",
    filename="landscape.webp"
)

if result.success:
    print(f"Image saved to: {result.path}")
```

### Using the Agent

```python
import asyncio
from gemini_image_sdk import ImageGeneratorAgent, Config

async def main():
    config = Config.from_env()
    agent = ImageGeneratorAgent(config)
    
    # Chat naturally with the agent
    response = await agent.chat("enhance a photo of modern office space")
    
    # The agent automatically:
    # - Enhances your prompt
    # - Generates the image
    # - Remembers this interaction
    # - Suggests next steps

asyncio.run(main())
```

## 💻 CLI Usage

The SDK includes a powerful command-line interface:

```bash
# Single image
python examples/cli_tool.py single "prompt" output.webp

# Variations
python examples/cli_tool.py variations "base prompt" --count 3

# Style transfer
python examples/cli_tool.py style "prompt" cyberpunk

# Themed batch
python examples/cli_tool.py theme website_hero --count 5

# Interactive chat
python examples/cli_tool.py chat "enhance modern kitchen"
```

## 🔧 Advanced Features

### Tool Chaining

Execute complex workflows:

```python
chain = [
    {"tool": "enhance_prompt", "params": {"base_prompt": "city"}},
    {"tool": "generate_variations", "params": {"base_prompt": "city", "count": 3}},
    {"tool": "style_transfer", "params": {"prompt": "city", "style": "cyberpunk"}}
]

results = await agent.execute_chain(chain)
```

### Memory Persistence

The agent remembers across sessions:

```python
# Save conversation and preferences
agent.save_memory("session.json")

# Load in new session
new_agent = ImageGeneratorAgent(config)
new_agent.load_memory("session.json")
# Agent remembers your style preferences!
```

### Custom Tools

Extend the agent with your own tools:

```python
async def watermark_tool(prompt: str, text: str):
    return await generator.generate_single(
        f"{prompt}, with '{text}' watermark",
        "watermarked.webp"
    )

agent.register_tool("add_watermark", watermark_tool)
```

## 📂 Project Structure

```
CLI-Gemini-image-generator-SDK/
├── gemini_image_sdk/       # Core SDK package
│   ├── __init__.py
│   ├── agent.py           # Intelligent agent
│   ├── core.py            # Image generation
│   ├── config.py          # Configuration
│   └── types.py           # Type definitions
├── examples/              # Example scripts
│   ├── basic_usage.py     # Simple examples
│   ├── agent_demo.py      # Agent features
│   └── cli_tool.py        # CLI interface
├── requirements.txt       # Python dependencies
├── .env.example          # Environment template
└── README.md             # This file
```

## 🎯 Use Cases

- **Web Development**: Generate hero images, backgrounds, product shots
- **Social Media**: Create Instagram posts, Twitter headers, YouTube thumbnails
- **Marketing**: Email headers, landing pages, advertisements
- **Prototyping**: Quick mockups and concept art
- **Content Creation**: Blog images, presentation slides, documentation

## 🛠️ Configuration

Create a `.env` file:

```env
GEMINI_API_KEY=your_openrouter_api_key
OUTPUT_DIR=./generated
IMAGE_QUALITY=90
LOGGING_ENABLED=true
```

Or configure programmatically:

```python
from gemini_image_sdk import Config, APIConfig, OutputConfig

config = Config(
    api=APIConfig(key="your_key"),
    output=OutputConfig(
        base_dir="./images",
        format="webp",
        width=1920,
        height=1080,
        quality=95
    )
)
```

## 📊 Performance

- **Rate Limiting**: 30 images/minute (configurable)
- **Retry Logic**: Automatic retry with exponential backoff
- **Parallel Processing**: Batch generation with worker pools
- **Memory Efficient**: Async operations and streaming

## 🤝 Contributing

Contributions welcome! Please feel free to submit issues and pull requests.

## 📄 License

MIT License - Free to use and modify for your projects.

## 🙏 Acknowledgments

- Built with [Claude Code](https://claude.ai/code)
- Powered by [Google Gemini 2.5 Flash](https://ai.google.dev/)
- API access via [OpenRouter](https://openrouter.ai/)

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/matthewtrundle/CLI-Gemini-image-generator-SDK/issues)
- **Discussions**: [GitHub Discussions](https://github.com/matthewtrundle/CLI-Gemini-image-generator-SDK/discussions)

---

Made with ❤️ by Matt | Powered by AI 🚀
