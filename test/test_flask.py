#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from unittest import TestCase
import webserve
import database
import sqlalchemy
import models
import datetime

class WebServeTestCase(TestCase):

    def insert_rows(self, video_ids=["Video 1"], positive_list=[True]):
        for video_index, id in enumerate(video_ids):
            database.db_session.add(models.Video(id=id, 
                                             title="test title {}".format(id),
                                             author_id="test author {}".format(id),
                                             viewcount=1,
                                             duration=10,
                                             likes=1,
                                             published=datetime.datetime.now(),
                                             dislikes=1,
                                             rating=3,
                                             num_of_raters=5,
                                             timestamp=datetime.datetime.now()))
            database.db_session.add(models.VideoSentiment(id=id,
                                                      n_pos=5.2,
                                                      n_neg=10.2,
                                                      result="significantly negative"))
            for comment_index, pos in enumerate(positive_list):
                database.db_session.add(models.Comment(id="comment {} {}".format(video_index, comment_index),
                                                  video_id=id,
                                                  author_id="test author id {}".format(id),
                                                  author_name="test author name {}".format(id),
                                                  content="test comment text {}".format(id),
                                                  published=datetime.datetime.now()))
                database.db_session.add(models.CommentSentiment(id="comment {} {}".format(video_index, comment_index),
                                                            video_id=id,
                                                            positive=pos))
        database.db_session.commit()


    def setUp(self):
        webserve.app.config["TESTING"] = True
        self.app = webserve.app.test_client()
        database.engine = sqlalchemy.create_engine("sqlite://", echo=True)
        database.db_session = sqlalchemy.orm.scoped_session(sqlalchemy.orm.sessionmaker(
                                           autocommit=False, autoflush=False,
                                           bind=database.engine))
        database.init_db()
        
    
    def tearDown(self):
        database.db_session.close()

    def test_start_page_load_correct(self):
        response = self.app.get("/")
        assert "Enter ID or URL" in response.data.decode("utf-8")

    def test_video_page_load_correct_from_database(self):
        self.insert_rows()
        response = self.app.get("/video?video_id={}".format("Video 1"))
        assert "Analysis of video with ID: Video 1" in response.data.decode("utf-8")

    def test_video_page_load_error_wrong_id(self):
        response = self.app.get("/video?video_id={}".format("wrong_id"))
        assert "Error: invalid video id" in response.data.decode("utf-8")

    def test_video_page_load_correct_full_youtubeurl(self):
        self.insert_rows(["Video 1"])
        response = self.app.get("/video?video_id=https://www.youtube.com/watch?v=Video 1")
        assert "Analysis of video with ID: Video 1" in response.data.decode("utf-8")

    def test_video_page_load_correct_from_youtube(self):
        response = self.app.get("/video?video_id=tkXr3uxM2fY")
        assert "Analysis of video with ID: tkXr3uxM2fY" in response.data.decode("utf-8")

    def test_video_page_comment_sentiment_plot_only_negative(self):
        self.insert_rows(positive_list=[False])
        response = self.app.get("/comment_sentiment_plot.png?video_id={}".format("Video 1"))
        assert response.status_code == 200

    def test_video_page_comment_sentiment_plot_only_positive(self):
        self.insert_rows(["Video 1"],positive_list=[True])
        response = self.app.get("/comment_sentiment_plot.png?video_id={}".format("Video 1"))
        assert response.status_code == 200

    def test_video_page_comment_sentiment_plot_mixed(self):
        self.insert_rows(["Video 1"],positive_list=[True, False])
        response = self.app.get("/comment_sentiment_plot.png?video_id={}".format("Video 1"))
        assert response.status_code == 200

    def test_video_page_video_sentiment_plot_correct(self):
        self.insert_rows()
        response = self.app.get("/video_sentiment_plot.png?video_id={}".format("Video 1"))
        assert response.status_code == 200
    
    def test_previous_page_taking_newest(self):
        self.insert_rows(["Video {}".format(i) for i in range(1,10)])
        response = self.app.get("/previous")
        assert "Video 5" in response.data.decode("utf-8")
        assert "Video 6" in response.data.decode("utf-8")
        assert "Video 7" in response.data.decode("utf-8")
        assert "Video 8" in response.data.decode("utf-8")
        assert "Video 9" in response.data.decode("utf-8")

    def test_about_page_load_correct(self):
        response = self.app.get("/about")
        assert "Created by Søren Howe Gersager and Anders Rahbek" in response.data.decode("utf-8")

    def test_error_page_load_from_wrong_url(self):
        response = self.app.get("/verywrongurl")
        assert "We did not find the page you were looking for." in response.data.decode("utf-8")