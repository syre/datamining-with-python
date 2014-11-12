#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from unittest import mock

import youtube
import database
import models

@mock.patch("youtube.YouTubeScraper._comment_generator")
def test_fetch_comments_calls_with_correct_id(mock_comment):
    y = youtube.YouTubeScraper()
    # return dummy list
    cm = models.Comment(id="test", video_id="test", author_id="test",
                                author_name="test", content="test", published="test")
    mock_comment.return_value = iter([[cm for x in range(100)]])
    y.fetch_comments("dQw4w9WgXcQ", 50)
    y._comment_generator.assert_called_with("dQw4w9WgXcQ")

@mock.patch("youtube.YouTubeScraper._comment_generator")
def test_fetch_comments_returns_correct_number_over_zero(mock_comment):
    y = youtube.YouTubeScraper()
    # return dummy list
    cm = models.Comment(id="test", video_id="test", author_id="test",
                            author_name="test", content="test", published="test")
    mock_comment.return_value = iter([[cm for x in range(500)]])
    comments = y.fetch_comments("dQw4w9WgXcQ", 250)
    assert len(comments) == 250

@mock.patch("youtube.YouTubeScraper._comment_generator")
def test_fetch_comments_returns_all_at_zero(mock_comment):
    y = youtube.YouTubeScraper()
    # return dummy list
    cm = models.Comment(id="test", video_id="test", author_id="test",
                                author_name="test", content="test", published="test")
    mock_comment.return_value = iter([[cm for x in range(500)]])
    comments = y.fetch_comments("dQw4w9WgXcQ", 0)
    assert len(comments) == 500
