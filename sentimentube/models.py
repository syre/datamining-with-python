#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sqlalchemy
from database import base

class Comment(base):
    __tablename__ = "comments"
    __table_args__ = {'extend_existing':True}
    id = sqlalchemy.Column(sqlalchemy.String, primary_key=True)
    video_id = sqlalchemy.Column(sqlalchemy.String, sqlalchemy.ForeignKey("videos.id"))
    author_id = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    author_name = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    content = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    published = sqlalchemy.Column(sqlalchemy.DateTime, nullable=False)
    def __repr__(self):
        return self.content

class Video(base):
    __tablename__ = "videos"
    __table_args__ = {'extend_existing':True}
    id = sqlalchemy.Column(sqlalchemy.String, primary_key=True, nullable=False)
    title = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    author_id = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    viewcount = sqlalchemy.Column(sqlalchemy.Integer, nullable=False)
    duration = sqlalchemy.Column(sqlalchemy.Integer, nullable=False)
    likes = sqlalchemy.Column(sqlalchemy.Integer, nullable=False)
    published = sqlalchemy.Column(sqlalchemy.DateTime, nullable=False)
    dislikes = sqlalchemy.Column(sqlalchemy.Integer, nullable=False)
    rating = sqlalchemy.Column(sqlalchemy.Float, nullable=False)
    num_of_raters = sqlalchemy.Column(sqlalchemy.Integer, nullable=False)
    def __repr__(self):
        return self.title

class VideoSentiment(base):
    __tablename__ = "videosentiments"
    __table_args__ = {'extend_existing':True}
    id = sqlalchemy.Column(sqlalchemy.String, sqlalchemy.ForeignKey("videos.id"),primary_key=True, nullable=False)
    n_pos = sqlalchemy.Column(sqlalchemy.Float, nullable=False)
    n_neg = sqlalchemy.Column(sqlalchemy.Float, nullable=False)
    result = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    def __repr__(self):
        return self.result

class CommentSentiment(base):
    __tablename__ = "commentsentiments"
    __table_args__ = {'extend_existing':True}
    id = sqlalchemy.Column(sqlalchemy.String, sqlalchemy.ForeignKey("comments.id"),primary_key=True, nullable=False)
    video_id = sqlalchemy.Column(sqlalchemy.String, sqlalchemy.ForeignKey("videos.id"), nullable=False)
    positive = sqlalchemy.Column(sqlalchemy.Boolean, nullable=False)
    def __repr__(self):
        return self.positive

class VideoCategory(base):
    __tablename__ = "videocategories"
    __table_args__ = {'extend_existing':True}
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, nullable=False)
    video_id = sqlalchemy.Column(sqlalchemy.String, sqlalchemy.ForeignKey("videos.id"), nullable=False)
    type = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    def __repr__(self):
        return self.type
