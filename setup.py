"""
Contains the instructions to build and distribute this application
"""
from setuptools import setup, find_packages

setup(
    name="Fast_API_Boilerplate",
    version="0.1.0",
    description="A FastAPI application",
    packages=find_packages(include=["app", "appfrwk", "appfrwk.*"]),
)
