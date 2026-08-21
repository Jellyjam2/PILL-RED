from setuptools import setup, find_packages

setup(
    name="pillred",
    version="1.0.0",
    description="Universal Cryptographic Evidence & Model Audit Protocol",
    packages=find_packages(include=["pillred*"]),
    entry_points={
        "console_scripts": [
            "pillred=pillred.cli:main",
        ],
    },
    python_requires=">=3.8",
)
