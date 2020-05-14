from setuptools import setup, find_packages


setup(
    name="bodb",
    version="0.0.1",
    description="A simple database class for storing function evaluations",
    author="Alexander Chambers",
    author_email="alexander.chambers8472@gmail.com",
    install_requires=[
        "sqlalchemy",
        ""
    ]
    package_dir={"": "src"},
    packages=find_packages(where="src"),
)
