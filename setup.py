#! /usr/bin/env python
# -*- coding: utf-8 -*-
from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="carbon-track-pro",
    version="1.0.0",
    author="Data Engineering Team",
    author_email="antoniovasquez.joel@gmail.com",
    description="Real-Time Carbon Emissions Monitoring System",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/joelantoniov/carbon-track-pro",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Operating System :: GNU/Linux Ubuntu",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Data Engineering ::",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.9",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "black>=22.0.0",
            "flake8>=5.0.0",
            "mypy>=0.991",
        ],
        "docs": [
            "sphinx>=5.0.0",
            "sphinx-rtd-theme>=1.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "carbon-track=src.main:main",
            "carbon-producer=src.producers.emission_producer:main",
            "carbon-processor=src.processors.stream_processor:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
  )
