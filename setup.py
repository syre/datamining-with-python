import os
import sys

from setuptools import setup
from setuptools.command.test import test as TestCommand

import sentimentube

class ToxTestCommand(TestCommand):

    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        sys.exit(os.system('tox'))

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
