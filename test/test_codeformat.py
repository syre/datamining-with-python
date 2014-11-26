#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pep8
import unittest
import os
import subprocess
from nose.tools import assert_true

source_list = ["youtube.py",
               "webserve.py",
               "sentiment_analysis.py",
               "models.py",
               "database.py"]

test_list = ["test_flask.py",
             "test_codeformat.py",
             "test_sentiment_analysis.py",
             "test_youtube.py"]

cwd = os.path.dirname(__file__)
source_paths = [os.path.join(cwd, os.pardir, "sentimentube", pyfile)
                for pyfile in source_list]
test_paths = [os.path.join(cwd, pyfile) for pyfile in test_list]
full_paths = source_paths+test_paths


class TestCodeFormat(unittest.TestCase):

    def test_pep8_compliance(self):
        pep8style = pep8.StyleGuide()
        result = pep8style.check_files(full_paths)
        self.assertEqual(result.total_errors, 0,
                         "Found code style errors (and warnings).")

    def test_pylint_compliance(self):
        cmd = ["pylint", "--rcfile={}".format(os.path.join(cwd, os.pardir,
                                                           "pylint.rc")),
               "sentimentube", "test"]
        try:
            subprocess.check_output(cmd, universal_newlines=True)
        except subprocess.CalledProcessError as e:
            errors = [line for line in e.output.split("\n")
                      if not line.startswith("*") or
                      "Locally disabling" in line]
            if errors:
                for error in errors:
                    print(error)
                self.assertTrue(False, msg="pylint fail")

    def test_pyflakes_compliance(self):
        cmd = ["pyflakes", "sentimentube", "test"]
        try:
            subprocess.check_output(cmd, universal_newlines=True)
        except subprocess.CalledProcessError as e:
            errors = e.output.split("\n")
            if errors:
                for error in errors:
                    print(error)
                self.assertTrue(False, msg="pyflakes fail")
