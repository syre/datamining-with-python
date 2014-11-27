#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from unittest import TestCase
import webserve
import database
import sqlalchemy
import models
import datetime


class WebServeTestCase(TestCase):

    def insert_rows(self, video_ids=["tkXr3uxM2fY"], positive_list=[True]):
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

                database.DB_SESSION.add(models.CommentSentiment(id="comment {}"
                                                                   " {}"
                                                                .format(
                                                                   video_index,
                                                                   com_index),
                                                                video_id=v_id,
                                                                positive=pos))
        database.DB_SESSION.commit()

    def setUp(self):
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
        database.DB_SESSION.close()

    def test_start_page_load_correct(self):
        response = self.app.get("/")
        assert "Enter ID or URL" in response.data.decode("utf-8")

    def test_video_page_load_correct_from_database(self):
        id = "tkXr3uxM2fY"
        self.insert_rows([id])
        response = self.app.get("/video?video_id={}".format(id))
        assert "Analysis of video with ID: {}".format(id) in \
               response.data.decode("utf-8")

    def test_video_page_load_error_wrong_id(self):
        response = self.app.get("/video?video_id={}".format("wrong_id"))
        assert "Error: invalid video id" in response.data.decode("utf-8")

    def test_video_page_load_correct_full_youtubeurl(self):
        id = "tkXr3uxM2fY"
        response = self.app.get(
            "/video?video_id=https://www.youtube.com/watch?v={}".format(id))
        assert "Analysis of video with ID: {}".format(id) in\
            response.data.decode("utf-8")

    def test_video_page_load_correct_from_youtube(self):
        id = "tkXr3uxM2fY"
        response = self.app.get("/video?video_id={}".format(id))
        assert "Analysis of video with ID: {}".format(id) in \
               response.data.decode("utf-8")

    def test_video_page_saves_video_in_db(self):
        id = "tkXr3uxM2fY"
        self.app.get("/video?video_id={}".format(id))
        vid = database.DB_SESSION.query(models.Video).filter_by(id=id).first()
        assert vid

    def test_video_page_updates_sentiment_in_db(self):
        id = "tkXr3uxM2fY"
        now = datetime.datetime.now()
        negative_score = 100
        positive_score = 100
        database.DB_SESSION.add(models.VideoSentiment(id=id,
                                                      n_neg=negative_score,
                                                      n_pos=positive_score,
                                                      result="test positive"))

        database.DB_SESSION.add(models.Video(id=id, title="test title",
                                             author_id="test author id",
                                             viewcount=1, duration=5, likes=1,
                                             published=now,
                                             dislikes=1, rating=5,
                                             num_of_raters=1,
                                             timestamp=now,
                                             num_of_comments=10))
        database.DB_SESSION.add(models.Comment(id="comment {}".format(id),
                                               video_id=id,
                                               author_id="test author id",
                                               author_name="test author",
                                               content="test comment",
                                               published=now))
        database.DB_SESSION.commit()

        self.app.get("/video?video_id={}".format(id))

        sentiment = database.DB_SESSION.query(
            models.VideoSentiment).filter_by(id=id).first()
        assert sentiment.n_neg != negative_score
        assert sentiment.n_pos != positive_score
        assert sentiment.result == "neutral"

    def test_video_page_saves_comment_in_db(self):
        id = "tkXr3uxM2fY"
        self.app.get("/video?video_id={}".format(id))
        comment = database.DB_SESSION.query(
            models.Comment).filter_by(video_id=id).first()
        assert comment

    def test_video_page_saves_commentsentiment_in_db(self):
        id = "tkXr3uxM2fY"
        self.app.get("/video?video_id={}".format(id))
        sentiment = database.DB_SESSION.query(
            models.CommentSentiment).filter_by(video_id=id).first()
        assert sentiment

    def test_video_page_saves_videosentiment_in_db(self):
        id = "tkXr3uxM2fY"
        self.app.get("/video?video_id={}".format(id))
        sentiment = database.DB_SESSION.query(
            models.VideoSentiment).filter_by(id=id).first()
        assert sentiment

    def test_video_page_comment_sentiment_plot_only_negative(self):
        v_id = "tkXr3uxM2fY"
        self.insert_rows(positive_list=[False])
        response = self.app.get("/comment_sentiment_plot.png?video_id={}"
                                .format(v_id))
        assert response.status_code == 200

    def test_video_page_comment_sentiment_plot_only_positive(self):
        v_id = "tkXr3uxM2fY"
        self.insert_rows(positive_list=[True])
        response = self.app.get("/comment_sentiment_plot.png?video_id={}"
                                .format(v_id))
        assert response.status_code == 200

    def test_video_page_comment_sentiment_plot_mixed(self):
        v_id = "tkXr3uxM2fY"
        self.insert_rows(positive_list=[True, False])
        response = self.app.get("/comment_sentiment_plot.png?video_id={}"
                                .format(v_id))
        assert response.status_code == 200

    def test_video_page_video_sentiment_plot_correct(self):
        v_id = "tkXr3uxM2fY"
        self.insert_rows()
        response = self.app.get("/video_sentiment_plot.png?video_id={}"
                                .format(v_id))
        assert response.status_code == 200

    def test_previous_page_taking_newest(self):
        ids = ["5nO7IA1DeeI", "vykkfDITkQs",
               "C3zqYM3Rkpg", "0piaF7P3404",
               "Ek_cufWYvjE", "zNJJBD_I5EU",
               "v2zTVZFlCZ0", "ZLa6sX9N3Jw",
               "c6qOBFkvdG0", "eYhHyUU-CYU"]
        self.insert_rows(ids)
        response = self.app.get("/previous")
        for v_id in ids[5:]:
            assert v_id in response.data.decode("utf-8")

    def test_about_page_load_correct(self):
        response = self.app.get("/about")
        assert "Created by Søren Howe Gersager and Anders Rahbek" in \
               response.data.decode("utf-8")

    def test_error_page_load_from_wrong_url(self):
        response = self.app.get("/verywrongurl")
        assert "We did not find the page you were looking for." in \
               response.data.decode("utf-8")
