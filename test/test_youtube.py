#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from unittest import mock, TestCase
import youtube
import database
import models

class YouTubeTestCase(TestCase):

    @mock.patch("youtube.YouTubeScraper._comment_generator")
    def test_fetch_comments_calls_with_correct_id(self, mock_comment):
        y = youtube.YouTubeScraper()
        # return dummy list
        cm = models.Comment(id="test", video_id="test", author_id="test",
                                    author_name="test", content="test", published="test")
        mock_comment.return_value = iter([[cm for x in range(100)]])
        y.fetch_comments("dQw4w9WgXcQ", 50)
        y._comment_generator.assert_called_with("dQw4w9WgXcQ")

    @mock.patch("youtube.YouTubeScraper._comment_generator")
    def test_fetch_comments_returns_correct_number_over_zero(self, mock_comment):
        y = youtube.YouTubeScraper()
        # return dummy list
        cm = models.Comment(id="test", video_id="test", author_id="test",
                                author_name="test", content="test", published="test")
        mock_comment.return_value = iter([[cm for x in range(500)]])
        comments = y.fetch_comments("dQw4w9WgXcQ", 250)
        assert len(comments) == 250

    @mock.patch("youtube.YouTubeScraper._comment_generator")
    def test_fetch_comments_returns_all_at_zero(self, mock_comment):
        y = youtube.YouTubeScraper()
        # return dummy list
        cm = models.Comment(id="test", video_id="test", author_id="test",
                                    author_name="test", content="test", published="test")
        mock_comment.return_value = iter([[cm for x in range(500)]])
        comments = y.fetch_comments("dQw4w9WgXcQ", 0)
        assert len(comments) == 500

    @mock.patch("logging.Logger.error")
    def test_comment_generator_wrong_videoid_handles_gracefully(self, mock_logger):
        y = youtube.YouTubeScraper()
        generator = y._comment_generator("wrong url")
        self.assertRaises(ValueError, next, generator)
        mock_logger.assert_called()

    @mock.patch("logging.Logger.error")
    def test_fetch_videoinfo_wrong_videoid_handles_gracefully(self, mock_logger):
        y = youtube.YouTubeScraper()
        self.assertRaises(ValueError, y.fetch_videoinfo, "wrong url")
        mock_logger.assert_called()
