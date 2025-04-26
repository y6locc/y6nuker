from setuptools import setup, find_packages

setup(
    name="y6nuker",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        "requests",
    ],
    entry_points={
        "console_scripts": [
            "y6nuker=y6nuker.main:main",
        ],
    },
)
