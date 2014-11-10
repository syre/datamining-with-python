import os
import sys

from setuptools import setup
from setuptools.command.test import test as TestCommand

import sentimentube

setup(
    license="MIT",
    keywords="youtube sentiment analysis",
    url="https://github.com/syre/datamining-with-python",
    # packages=find_packages(),
    packages=["sentimentube"],
    long_description=open('README.md').read(),
    install_requires=["requests"],
    cmdclass={"test": ToxTestCommand},
    tests_require=["tox"],
    classifiers=[
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3.4",
        "License :: OSI Approved :: MIT License",
    ],
)
