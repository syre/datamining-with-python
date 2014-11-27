#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
This module test the other module using some test methods:
 - PEP8
 - Unittest
 - Pylint
 - Pyflakes

 The Unittest is defined individually in modules pr. modules wanted to be
 tested
"""

import pep8
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
    """
    Creating, listing and running tests
    """
    def test_pep8_compliance(self):
        """
        Test the modules for PEP8 violations
        """
        pep8style = pep8.StyleGuide()
        result = pep8style.check_files(FULL_PATHS)
        self.assertEqual(result.total_errors, 0,
                         "Found code style errors (and warnings).")

    def test_pylint_compliance(self):
        """
        Test the modules for pylint violations
        """
        cmd = ["pylint", "--rcfile={}".format(os.path.join(CWD, os.pardir,
                                                           "pylint.rc")),
               "sentimentube", "test"]
        try:
            subprocess.check_output(cmd, universal_newlines=True)
        except subprocess.CalledProcessError as error:
            errors = [line for line in error.output.split("\n")
                      if not line.startswith("*") or not
                      line.find("Locally disabling")]
            if errors:
                for error in errors:
                    print(error)
                self.assertTrue(False, msg="pylint fail")

    def test_pyflakes_compliance(self):
        """
        Test the modules for pyflakes violations
        :return:
        """
        cmd = ["pyflakes", "sentimentube", "test"]
        try:
            subprocess.check_output(cmd, universal_newlines=True)
        except subprocess.CalledProcessError as err:
            errors = err.output.split("\n")
            if errors:
                for error in errors:
                    print(error)
                self.assertTrue(False, msg="pyflakes fail")
