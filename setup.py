# -*- coding: utf-8 -*-
""" setup.py file for sentimentube. """
from setuptools import setup

setup(
    name="sentimentube",
    version="0.1.0",
    author="Søren Howe Gersager, Anders Lundberg Rahbek",
    author_email="s094557@student.dtu.dk, s107029@student.dtu.dk",
    description="Youtube sentiment analysis with webinterface",
    license="MIT",
    keywords="youtube sentiment analysis",
    url="https://github.com/syre/datamining-with-python",
    packages=["sentimentube", "test"],
    scripts=["sentimentube/webserve.py"],
    long_description=open('README.md').read(),
    install_requires=["requests", "flask", "matplotlib", "sqlalchemy", "nltk"],
    tests_require=["tox", "nose", "nose-pathmunge", "flake8", "pylint"],
    classifiers=[
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3.4",
        "License :: OSI Approved :: MIT License",
    ],
)
