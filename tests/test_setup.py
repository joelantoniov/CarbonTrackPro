#! /usr/bin/env python
# -*- coding: utf-8 -*-
import pytest
import os
from pathlib import Path

def test_project_structure():
    """Test that all required project files exist"""
    required_files = [
        'README.md',
        'requirements.txt',
        'setup.py',
        'docker-compose.yml',
        'Dockerfile',
        'Makefile',
        '.env.example'
    ]

    project_root = Path(__file__).parent.parent

    for file_path in required_files:
        assert (project_root / file_path).exists(), f"Missing required file: {file_path}"

def test_source_structure():
    """Test that source code structure is correct"""
    src_path = Path(__file__).parent.parent / 'src'

    required_modules = [
        'producers',
        'processors',
        'analytics',
        'utils'
    ]

    for module in required_modules:
        assert (src_path / module).is_dir(), f"Missing source module: {module}"
        assert (src_path / module / '__init__.py').exists(), f"Missing __init__.py in {module}"

def test_environment_variables():
    """Test that environment configuration is valid"""
    env_example = Path(__file__).parent.parent / '.env.example'

    assert env_example.exists(), "Missing .env.example file"

    with open(env_example) as f:
        content = f.read()

    required_vars = [
        'KAFKA_BOOTSTRAP_SERVERS',
        'AZURE_SQL_SERVER',
        'DATABRICKS_HOST',
        'DATABRICKS_TOKEN'
    ]

    for var in required_vars:
        assert var in content, f"Missing required environment variable: {var}"
