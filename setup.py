from setuptools import setup, find_packages
from os.path import dirname, join

setup(
    name="kw-template-matcher",
    version="0.0.1",
    author="JarbasAI",
    author_email="jarbasai@mailfence.com",
    description="A lightweight Python utility for template expansion and matching with slots and fuzzy matching.",
    long_description=open(join(dirname(__file__), 'README.md')).read(),
    long_description_content_type="text/markdown",
    url="https://github.com/TigreGotico/kw-template-matcher",  # Update with your repo URL
    packages=find_packages(),
    install_requires=[
        "rapidfuzz>=2.0.0",
        "simplematch>=0.1.0",
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',  # Adjust the required Python version as needed
)
