from setuptools import setup, find_packages

setup(
    name="pandas-explore",
    version="1.0.0",
    author="Marlon Nienaber",
    author_email="ge64vol@mytum.de",
    description="A package for exploring columns of pandas data frames containing raw data.",
    url="https://github.com/marlonnienaber/pandas-explore",
    packages=find_packages(),
    install_requires=[
        "pandas>=2.2.3",
        "matplotlib>=3.9.3",
        "IPython>=8.18.1"
    ],
    python_requires=">=3.9",
)