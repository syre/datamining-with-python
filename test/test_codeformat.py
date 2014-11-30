#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
This module contains tests of code formats.

 - Flake8
 - Unittest
 - Pylint

 The Unittest is defined individually in modules pr. modules wanted to be
 tested
"""
import unittest
import os
import subprocess


SOURCE_LIST = ["youtube.py",
               "webserve.py",
               "sentiment_analysis.py",
               "models.py",
               "database.py"]

TEST_LIST = ["test_flask.py",
             "test_codeformat.py",
             "test_sentiment_analysis.py",
             "test_youtube.py"]

CWD = os.path.dirname(__file__)
SOURCE_PATHS = [os.path.join(CWD, os.pardir, "sentimentube", pyfile)
                for pyfile in SOURCE_LIST]
TEST_PATHS = [os.path.join(CWD, pyfile) for pyfile in TEST_LIST]
FULL_PATHS = SOURCE_PATHS+TEST_PATHS


class TestCodeFormat(unittest.TestCase):

    """    Creating, listing and running tests. """

    def test_pylint_compliance(self):
        """ Test the modules for pylint violations. """
        cmd = ["pylint", "--rcfile={}".format(os.path.join(CWD, os.pardir,
                                                           "pylint.rc")),
               "sentimentube", "test"]
        try:
            subprocess.check_output(cmd, universal_newlines=True)
        except subprocess.CalledProcessError as error:
            errors = [line for line in error.output.split("\n")
                      if not line.startswith("*") and
                      "Locally disabling" not in line]
            if errors:
                for error in errors:
                    print(error)
                self.assertTrue(False, msg="pylint fail")

    def test_flake8_compliance(self):
        """ Test the modules for pyflakes violations. """
        cmd = ["flake8", "sentimentube", "test"]
        try:
            subprocess.check_output(cmd, universal_newlines=True)
        except subprocess.CalledProcessError as err:
            errors = err.output.split("\n")
            if errors:
                for error in errors:
                    print(error)
                self.assertTrue(False, msg="flake8 fail")

    def test_pep257_compliance(self):
        """ Test the modules for pep257 violations. """
        cmd = ["pep257", "sentimentube", "test"]
        try:
            subprocess.check_output(cmd, universal_newlines=True)
        except subprocess.CalledProcessError as err:
            errors = err.output.split("\n")
            if errors:
                for error in errors:
                    print(error)
                self.assertTrue(False, msg="pep257 fail")
