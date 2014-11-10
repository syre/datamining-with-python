#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sentimentube
import sentimentube.webserve

def test_start_page():
    y = sentimentube.youtube.YouTubeScraper()
    # return dummy list
    sentimentube.webserve.app.config["TESTING"] = True
    app = sentimentube.webserve.app.test_client()
    response = app.get("/")
    assert response
