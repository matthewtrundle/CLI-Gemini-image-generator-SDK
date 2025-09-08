"""
Setup script for Gemini Image Generator SDK
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="gemini-image-sdk",
    version="1.0.0",
    author="Matthew Trundle",
    author_email="",
    description="An intelligent AI agent SDK for image generation using Gemini 2.5 Flash",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/matthewtrundle/CLI-Gemini-image-generator-SDK",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Multimedia :: Graphics",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.8",
    install_requires=[
        "aiohttp>=3.9.0",
        "pillow>=10.0.0",
        "python-dotenv>=1.0.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-asyncio>=0.21.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
        ]
    },
    entry_points={
        "console_scripts": [
            "gemini-sdk=examples.cli_tool:main",
        ],
    },
    keywords="ai image generation gemini agent sdk",
    project_urls={
        "Bug Reports": "https://github.com/matthewtrundle/CLI-Gemini-image-generator-SDK/issues",
        "Source": "https://github.com/matthewtrundle/CLI-Gemini-image-generator-SDK",
    },
)