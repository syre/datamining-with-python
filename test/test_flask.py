#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import webserve
import youtube
import unittest

class WebServeTestCase(unittest.TestCase):
    def setUp(self):
        webserve.app.config["TESTING"] = True
        self.app = webserve.app.test_client()


    def test_start_page_load_correct(self):
        response = self.app.get("/")
        assert "Enter ID or URL" in response.data.decode("utf-8")

    def test_video_page_load_correct(self):
        response = self.app.get("/video?video_id={}".format("oavMtUWDBTM"))
        assert "Analysis of video with ID: oavMtUWDBTM" in response.data.decode("utf-8")

    def test_video_page_load_error_wrong_id(self):
        response = self.app.get("/video?video_id={}".format("wrong_id"))
        assert "Wrong video ID" in response.data.decode("utf-8")
