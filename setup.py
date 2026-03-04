from setuptools import setup, find_packages

setup(
    name="cortex-ai",
    version="0.1.0",
    description="Local-first AI Operating System for companies",
    packages=find_packages(),
    entry_points={
        "console_scripts": [
            "cortex=cli.main:app",
        ],
    },
)
