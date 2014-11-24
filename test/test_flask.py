#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from unittest import TestCase
import webserve
import database
import sqlalchemy
import models
import datetime

class WebServeTestCase(TestCase):

    def insert_rows(self, video_ids):
        for index, id in enumerate(video_ids):
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
            for i in range(5):
                database.db_session.add(models.Comment(id="comment {} {}".format(id,i),
                                                  video_id=id,
                                                  author_id="test author id {}".format(id),
                                                  author_name="test author name {}".format(id),
                                                  content="test comment text {}".format(id),
                                                  published=datetime.datetime.now()))
                database.db_session.add(models.CommentSentiment(id="comment {} {}".format(id,i),
                                                        video_id=id,
                                                        positive=False))
        database.db_session.commit()


    def setUp(self):
        webserve.app.config["TESTING"] = True
        self.app = webserve.app.test_client()
        database.engine = sqlalchemy.create_engine("sqlite://", echo=True)
        database.db_session = sqlalchemy.orm.scoped_session(sqlalchemy.orm.sessionmaker(
                                           autocommit=False, autoflush=False,
                                           bind=database.engine))
        database.init_db()
        self.insert_rows(["Video {}".format(id) for id in range(10)])
        
    
    def tearDown(self):
        database.db_session.close()

    def test_start_page_load_correct(self):
        response = self.app.get("/")
        assert "Enter ID or URL" in response.data.decode("utf-8")

    def test_video_page_load_correct(self):
        response = self.app.get("/video?video_id={}".format("Video 1"))
        assert "Analysis of video with ID: Video 1" in response.data.decode("utf-8")
    
    def test_previous_page_taking_newest(self):
        response = self.app.get("/previous")
        assert "Video 5" in response.data.decode("utf-8")
        assert "Video 6" in response.data.decode("utf-8")
        assert "Video 7" in response.data.decode("utf-8")
        assert "Video 8" in response.data.decode("utf-8")
        assert "Video 9" in response.data.decode("utf-8")

    def test_video_page_load_error_wrong_id(self):
        response = self.app.get("/video?video_id={}".format("wrong_id"))
        assert "Error: invalid video id" in response.data.decode("utf-8")
