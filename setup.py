#!/usr/bin/env python3
"""
Setup script for WIZARD-2.1

Scientific Data Analysis and Visualization Tool
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read README file
readme_file = Path(__file__).parent / "README.md"
long_description = readme_file.read_text(encoding="utf-8") if readme_file.exists() else ""

# Read requirements
requirements_file = Path(__file__).parent / "requirements.txt"
requirements = []
if requirements_file.exists():
    with open(requirements_file, 'r', encoding='utf-8') as f:
        requirements = [line.strip() for line in f if line.strip() and not line.startswith('#')]

setup(
    name="wizard-2.1",
    version="2.1.0",
    author="FIELAX Development Team",
    author_email="dev@fielax.com",
    description="Scientific Data Analysis and Visualization Tool",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/fielax/wizard-2.1",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Science/Research",
        "License :: Other/Proprietary License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.13",
        "Topic :: Scientific/Engineering :: Information Analysis",
    ],
    python_requires=">=3.13",
    install_requires=requirements,
    extras_require={
        "dev": [
            "black>=23.11.0",
            "pylint>=3.0.3",
            "mypy>=1.7.1",
            "pytest>=7.4.3",
            "pytest-qt>=4.2.0",
            "pytest-cov>=4.1.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "wizard-2.1=main:main",
        ],
    },
    include_package_data=True,
    package_data={
        "": ["*.ui", "*.qm", "*.ts", "*.ico", "*.png", "*.svg"],
    },
    zip_safe=False,
)
