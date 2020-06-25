from setuptools import setup, find_packages
from os import path

here = path.abspath(path.dirname(__file__))

with open(path.join(here, "README.md"), encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="bodb",
    version="0.2.0",
    description="Simple class for abstracting database table access",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/achambers8472/bodb",
    author="Alexander Chambers",
    author_email="alexander.chambers8472@gmail.com",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        # "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
    ],
    keywords="bayesian optimisation sql",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    python_requires=">=3.6",
    install_requires=["sqlalchemy"],
    extras_require={"examples": ["bayesian-optimization", "toolz", "click"]},
    project_urls={
        "Bug Reports": "https://github.com/achambers8472/bodb/issues",
        "Source": "https://github.com/achambers8472/bodb/",
    },
)
