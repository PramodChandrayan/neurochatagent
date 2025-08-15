#!/usr/bin/env python3
"""
Setup script for Intelligent CI/CD Toolbox
"""

import os

from setuptools import find_packages, setup


# Read the README file
def read_readme():
    readme_path = os.path.join(os.path.dirname(__file__), "README.md")
    if os.path.exists(readme_path):
        with open(readme_path, "r", encoding="utf-8") as f:
            return f.read()
    return "Intelligent CI/CD Toolbox - Project-agnostic automation with intelligent analysis"


# Read requirements
def read_requirements():
    req_path = os.path.join(os.path.dirname(__file__), "requirements.txt")
    if os.path.exists(req_path):
        with open(req_path, "r", encoding="utf-8") as f:
            return [
                line.strip() for line in f if line.strip() and not line.startswith("#")
            ]
    return []


setup(
    name="intelligent-cicd-toolbox",
    version="1.0.0",
    author="Intelligent CI/CD Toolbox Team",
    author_email="",
    description="Project-agnostic CI/CD automation toolbox with intelligent analysis",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: System :: Systems Administration",
        "Topic :: Software Development :: Build Tools",
    ],
    python_requires=">=3.8",
    install_requires=read_requirements(),
    extras_require={
        "dev": [
            "pytest>=6.0",
            "black>=22.0",
            "flake8>=4.0",
            "mypy>=0.950",
        ],
        "gui": [
            "streamlit>=1.28.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "intelligent-cicd=intelligent_cicd_toolbox.cli:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
    keywords="ci-cd, devops, automation, cloud, gcp, aws, azure, github-actions, deployment",
    project_urls={
        "Bug Reports": "",
        "Source": "",
        "Documentation": "",
    },
)
