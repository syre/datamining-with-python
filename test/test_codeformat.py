#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pep8
from unittest import TestCase
import os

class TestCodeFormat(TestCase):

    def test_pep8_compliance(self):
        pep8style = pep8.StyleGuide()
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
        source_paths = [os.path.join(cwd, os.pardir, "sentimentube", pyfile) for pyfile in source_list]
        test_paths = [os.path.join(cwd, pyfile) for pyfile in test_list]
        full_paths = source_paths+test_paths

        result = pep8style.check_files(full_paths)
        self.assertEqual(result.total_errors, 0,
                         "Found code style errors (and warnings).")