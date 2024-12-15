from setuptools import setup, find_packages

with open("Readme.md", "r") as f:
    long_description = f.read()

setup(
    name="pandas_explore",
    version="1.0.3",
    author="Marlon Nienaber",
    author_email="ge64vol@mytum.de",
    description="A package for exploring columns of pandas data frames containing raw data.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/marlonnienaber/pandas_explore",
    license="MIT",
    package_dir={"": "app"},
    packages=find_packages(where="app"),
    install_requires=[
        "pandas>=2.2.3",
        "matplotlib>=3.9.3",
        "IPython>=8.18.1"
    ],
    python_requires=">=3.9",
)