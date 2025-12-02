"""Setup script for ZaloKit."""

from setuptools import setup, find_packages
from pathlib import Path

# Read the README file
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding="utf-8")

# Read requirements
requirements = [
    "requests>=2.28.0",
    "websocket-client>=1.4.0",
    "cryptography>=38.0.0",
    "pydantic>=2.0.0",
]

dev_requirements = [
    "pytest>=7.0.0",
    "pytest-cov>=4.0.0",
    "pytest-asyncio>=0.21.0",
    "black>=23.0.0",
    "isort>=5.12.0",
    "flake8>=6.0.0",
    "mypy>=1.0.0",
    "mkdocs>=1.5.0",
    "mkdocs-material>=9.0.0",
    "pre-commit>=3.0.0",
    "responses>=0.23.0",
]

setup(
    name="zalokit",
    version="0.1.0",
    author="jvunder",
    author_email="jvunder@users.noreply.github.com",
    description="A powerful Python SDK for the Zalo API",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/jvunder/ZaloKit",
    project_urls={
        "Documentation": "https://jvunder.github.io/ZaloKit/",
        "Bug Tracker": "https://github.com/jvunder/ZaloKit/issues",
        "Source Code": "https://github.com/jvunder/ZaloKit",
    },
    packages=find_packages(exclude=["tests", "tests.*", "examples", "docs"]),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Communications :: Chat",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Typing :: Typed",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        "dev": dev_requirements,
    },
    keywords=[
        "zalo",
        "zalo-api",
        "messaging",
        "chat",
        "sdk",
        "vietnam",
        "social-media",
    ],
    include_package_data=True,
    zip_safe=False,
)
