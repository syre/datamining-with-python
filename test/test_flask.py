#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Module for testing the webserve module
"""

from unittest import TestCase
import webserve
import database
import sqlalchemy
import models
import datetime


class WebServeTestCase(TestCase):
    """
    Class to test webserve module
    """
    @staticmethod
    def insert_rows(video_ids=None, positive_list=None):
        """
            helper method for inserting test rows in the database
        """
        if not video_ids:
            video_ids = ["tkXr3uxM2fy"]
        if not positive_list:
            positive_list = [True]

        for video_index, v_id in enumerate(video_ids):
            database.DB_SESSION.add(models.Video(id=v_id,
                                                 title="test title {}".
                                                 format(v_id),
                                                 author_id="test author {}"
                                                 .format(v_id),
                                                 viewcount=1,
                                                 duration=10,
                                                 likes=1,
                                                 published=datetime.datetime
                                                 .now(),
                                                 dislikes=1,
                                                 rating=3,
                                                 num_of_raters=5,
                                                 num_of_comments=5,
                                                 timestamp=datetime.datetime
                                                 .now()))
            database.DB_SESSION.add(models.VideoSentiment(id=v_id,
                                                          n_pos=5.2,
                                                          n_neg=10.2,
                                                          result="negative"))
            for com_index, pos in enumerate(positive_list):
                database.DB_SESSION.add(models.Comment(id="comment {} {}"
                                                       .format(video_index,
                                                               com_index),
                                                       video_id=v_id,
                                                       author_id="test author "
                                                                 "id {}"
                                                       .format(v_id),
                                                       author_name="test "
                                                                   "author "
                                                                   "name {}"
                                                       .format(v_id),
                                                       content="test comment"
                                                               " text {}"
                                                       .format(v_id),
                                                       published=datetime
                                                       .datetime.now()))

                database.DB_SESSION.add(
                    models.CommentSentiment(
                        id="comment {} {}".format(video_index,
                                                  com_index),
                        video_id=v_id, positive=pos))
        database.DB_SESSION.commit()

    def setUp(self):
        """
        set up method, running before
        each test, sets up an in-memory sqlite database
        for use as test database and
        set flask up for testing
        """
        webserve.APP.config["TESTING"] = True
        self.app = webserve.APP.test_client()
        database.ENGINE = sqlalchemy.create_engine("sqlite://", echo=False)
        database.DB_SESSION = \
            sqlalchemy.orm.scoped_session(sqlalchemy.orm
                                          .sessionmaker(
                                              autocommit=False,
                                              autoflush=False,
                                              bind=database.ENGINE))
        database.init_db()

    def tearDown(self):
        """
        tear down method, running after
        each test, closes the session
        """
        database.DB_SESSION.close()

    def test_start_page_load_correct(self):
        """
        test that the start page is loading correctly
        """
        response = self.app.get("/")
        assert "Enter ID or URL" in response.data.decode("utf-8")

    def test_video_page_load_correct_from_database(self):
        """
        test that video loads from database directly if found
        """
        v_id = "tkXr3uxM2fY"
        WebServeTestCase.insert_rows([v_id])
        response = self.app.get("/video?video_id={}".format(v_id))
        assert "Analysis of video with ID: {}".format(v_id) in \
               response.data.decode("utf-8")

    def test_video_page_load_error_wrong_id(self):
        """
        test that tries to input an invalid video id at the start page
        """
        response = self.app.get("/video?video_id={}".format("wrong_id"))
        assert "Error: invalid video id" in response.data.decode("utf-8")

    def test_video_page_load_correct_full_youtubeurl(self):
        """
        test that loads video page when given a full youtube url like:
        "https://www.youtube.com/watch?v=tkXr3uxM2fY"
        """
        v_id = "tkXr3uxM2fY"
        response = self.app.get(
            "/video?video_id=https://www.youtube.com/watch?v={}".format(v_id))
        assert "Analysis of video with ID: {}".format(v_id) in\
            response.data.decode("utf-8")

    def test_video_page_load_correct_from_youtube(self):
        """
        test that fetches youtube information and loads video page
        "normal use case"
        """
        v_id = "tkXr3uxM2fY"
        response = self.app.get("/video?video_id={}".format(v_id))
        assert "Analysis of video with ID: {}".format(v_id) in \
               response.data.decode("utf-8")

    def test_video_page_saves_video_in_db(self):
        """
        Test asserting video is saved in database after video page load
        """
        v_id = "tkXr3uxM2fY"
        self.app.get("/video?video_id={}".format(v_id))
        vid = database.DB_SESSION.query(models.Video).filter_by(
            id=v_id).first()
        assert vid

    def test_video_page_updates_sentiment_in_db(self):
        """
        Test asserting sentiment is updated in the database
        if video previously saved in database is updated
        at youtube (contains new comments)
        """
        v_id = "tkXr3uxM2fY"
        now = datetime.datetime.now()
        negative_score = 100
        positive_score = 100
        database.DB_SESSION.add(models.VideoSentiment(id=v_id,
                                                      n_neg=negative_score,
                                                      n_pos=positive_score,
                                                      result="test positive"))

        database.DB_SESSION.add(models.Video(id=v_id, title="test title",
                                             author_id="test author id",
                                             viewcount=1, duration=5, likes=1,
                                             published=now,
                                             dislikes=1, rating=5,
                                             num_of_raters=1,
                                             timestamp=now,
                                             num_of_comments=10))
        database.DB_SESSION.add(models.Comment(id="comment {}".format(v_id),
                                               video_id=v_id,
                                               author_id="test author id",
                                               author_name="test author",
                                               content="test comment",
                                               published=now))
        database.DB_SESSION.commit()

        self.app.get("/video?video_id={}".format(v_id))

        sentiment = database.DB_SESSION.query(
            models.VideoSentiment).filter_by(id=v_id).first()
        assert sentiment.n_neg != negative_score
        assert sentiment.n_pos != positive_score
        assert sentiment.result == "neutral"

    def test_video_page_saves_comment_in_db(self):
        """
        Test asserting comments are saved after video page load
        """
        v_id = "tkXr3uxM2fY"
        self.app.get("/video?video_id={}".format(v_id))
        comment = database.DB_SESSION.query(
            models.Comment).filter_by(video_id=v_id).first()
        assert comment

    def test_video_page_saves_commentsentiment_in_db(self):
        """
        Test asserting commentsentiments are saved
        after video page load
        """
        v_id = "tkXr3uxM2fY"
        self.app.get("/video?video_id={}".format(v_id))
        sentiment = database.DB_SESSION.query(
            models.CommentSentiment).filter_by(video_id=v_id).first()
        assert sentiment

    def test_video_page_saves_videosentiment_in_db(self):
        """
        Test asserting a videosentiment is saved
        after video page load
        """
        v_id = "tkXr3uxM2fY"
        self.app.get("/video?video_id={}".format(v_id))
        sentiment = database.DB_SESSION.query(
            models.VideoSentiment).filter_by(id=v_id).first()
        assert sentiment

    def test_video_page_comment_sentiment_plot_only_negative(self):
        """
        Test asserting the comment sentiment plot works
        with only negative comment sentiments
        """
        v_id = "tkXr3uxM2fY"
        WebServeTestCase.insert_rows(positive_list=[False])
        response = self.app.get("/comment_sentiment_plot.png?video_id={}"
                                .format(v_id))
        assert response.status_code == 200

    def test_video_page_comment_sentiment_plot_only_positive(self):
        """
        Test asserting the comment sentiment plot works
        with only positive comment sentiments
        """
        v_id = "tkXr3uxM2fY"
        WebServeTestCase.insert_rows(positive_list=[True])
        response = self.app.get("/comment_sentiment_plot.png?video_id={}"
                                .format(v_id))
        assert response.status_code == 200

    def test_video_page_comment_sentiment_plot_mixed(self):
        """
        Test asserting the comment sentiment plot works
        with mixed comment sentiments (positive and negative)
        """
        v_id = "tkXr3uxM2fY"
        WebServeTestCase.insert_rows(positive_list=[True, False])
        response = self.app.get("/comment_sentiment_plot.png?video_id={}"
                                .format(v_id))
        assert response.status_code == 200

    def test_video_page_video_sentiment_plot_correct(self):
        """
        Test that video sentiment on video page load works correctly
        """
        v_id = "tkXr3uxM2fY"
        WebServeTestCase.insert_rows()
        response = self.app.get("/video_sentiment_plot.png?video_id={}"
                                .format(v_id))
        assert response.status_code == 200

    def test_previous_page_taking_newest(self):
        """
        Test that the previous page shows the 5 most recent analyses
        """
        v_ids = ["5nO7IA1DeeI", "vykkfDITkQs",
                 "C3zqYM3Rkpg", "0piaF7P3404",
                 "Ek_cufWYvjE", "zNJJBD_I5EU",
                 "v2zTVZFlCZ0", "ZLa6sX9N3Jw",
                 "c6qOBFkvdG0", "eYhHyUU-CYU"]
        WebServeTestCase.insert_rows(v_ids)

        response = self.app.get("/previous")
        for v_id in v_ids[5:]:
            assert v_id in response.data.decode("utf-8")

    def test_about_page_load_correct(self):
        """
        Tests about page loads correctly
        """
        response = self.app.get("/about")
        assert "Created by Søren Howe Gersager and Anders Rahbek" in \
               response.data.decode("utf-8")

    def test_error_page_load_from_wrong_url(self):
        """
        Test that ensures an appropriate response is returned
        when trying to load a page that does not exist
        """
        response = self.app.get("/verywrongurl")
        assert "Error: 404: Not Found" in \
               response.data.decode("utf-8")

    def test_video_page_error_disallowed_comments_video(self):
        """
        Test that ensures an appropriate response is returned
        when trying to analyze a video with comments disabled
        """
        response = self.app.get("/video?video_id={}".format("NZQQdlPoz5g"))
        assert "Error: Comments disallowed for video" in \
               response.data.decode("utf-8")
