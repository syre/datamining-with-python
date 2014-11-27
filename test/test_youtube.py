#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Tests for the module "youtube"
"""

from unittest import mock, TestCase
import youtube
import models
import requests


class YouTubeTestCase(TestCase):
    """
    This class has test-methods for "youtube" module
    """

    @mock.patch("youtube.YouTubeScraper._comment_generator")
    def test_fetch_comments_correct_id(self, mock_comment):
        """
        This methods test the fetch_comments method in youtube module, when
        it's been called with a correct video id
        :param mock_comment: Mock object for comment method. The method is not
                             been called
        """
        scraper = youtube.YouTubeScraper()
        # return dummy list
        cm = models.Comment(id="test", video_id="test", author_id="test",
                            author_name="test", content="test",
                            published="test")
        mock_comment.return_value = iter([[cm for x in range(100)]])
        scraper.fetch_comments("dQw4w9WgXcQ", 50)
        scraper._comment_generator.assert_called_with("dQw4w9WgXcQ")

    @mock.patch("youtube.YouTubeScraper._comment_generator")
    def test_fetch_comments_returns_correct_over_zero(self, mock_comment):

        scraper = youtube.YouTubeScraper()
        # return dummy list
        cm = models.Comment(id="test", video_id="test", author_id="test",
                            author_name="test", content="test",
                            published="test")
        mock_comment.return_value = iter([[cm for x in range(500)]])
        comments = scraper.fetch_comments("dQw4w9WgXcQ", 250)
        assert len(comments) == 250

    @mock.patch("youtube.YouTubeScraper._comment_generator")
    def test_fetch_comments_returns_all_at_zero(self, mock_comment):
        scraper = youtube.YouTubeScraper()
        # return dummy list
        cm = models.Comment(id="test", video_id="test", author_id="test",
                            author_name="test", content="test",
                            published="test")
        mock_comment.return_value = iter([[cm for x in range(500)]])
        comments = scraper.fetch_comments("dQw4w9WgXcQ", 0)
        assert len(comments) == 500

    @mock.patch("logging.Logger.error")
    def test_comment_generator_wrong_videoid_gracefully(self, mock_logger):
        scraper = youtube.YouTubeScraper()
        generator = scraper._comment_generator("wrong url")
        self.assertRaises(ValueError, next, generator)
        mock_logger.assert_called()

    @mock.patch("logging.Logger.error")
    def test_fetch_videoinfo_wrong_videoid_gracefully(self, mock_logger):
        scraper = youtube.YouTubeScraper()
        self.assertRaises(ValueError, scraper.fetch_videoinfo, "wrong url")
        mock_logger.assert_called()

    @mock.patch("logging.Logger.exception")
    @mock.patch("requests.get")
    def test_fetchcomments_no_connection(self, mock_requests, mock_logger):
        scraper = youtube.YouTubeScraper()
        mock_requests.side_effect = requests.exceptions.RequestException
        assert mock_logger.assert_called()
        self.assertRaises(requests.exceptions.RequestException,
                          scraper.fetch_comments, "dQw4w9WgXcQ")
