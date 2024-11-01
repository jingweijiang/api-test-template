from setuptools import setup, find_packages

setup(
    name="automation-framework",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        line.strip()
        for line in open("requirements.txt")
        if line.strip() and not line.startswith("#")
    ],
    extras_require={
        "dev": [
            line.strip()
            for line in open("dev-requirements.txt")
            if line.strip() and not line.startswith("#")
            and not line.startswith("-r")
        ],
    },
    python_requires=">=3.9",
) 