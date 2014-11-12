#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sqlalchemy
from sqlalchemy.ext.declarative import declarative_base
from database import base

class Comment(base):
    __tablename__ = "comments"
    __table_args__ = {'extend_existing':True}
    id = sqlalchemy.Column(sqlalchemy.String, primary_key=True)
    video_id = sqlalchemy.Column(sqlalchemy.String, sqlalchemy.ForeignKey("videos.id"))
    author_id = sqlalchemy.Column(sqlalchemy.String)
    author_name = sqlalchemy.Column(sqlalchemy.String)
    content = sqlalchemy.Column(sqlalchemy.String)
    published = sqlalchemy.Column(sqlalchemy.DateTime)

class Video(base):
    __tablename__ = "videos"
    __table_args__ = {'extend_existing':True}
    id = sqlalchemy.Column(sqlalchemy.String, primary_key=True)
    title = sqlalchemy.Column(sqlalchemy.String)
    author_id = sqlalchemy.Column(sqlalchemy.String)
    category = sqlalchemy.Column(sqlalchemy.String)
    viewcount = sqlalchemy.Column(sqlalchemy.Integer)
    duration = sqlalchemy.Column(sqlalchemy.Integer)
    likes = sqlalchemy.Column(sqlalchemy.Integer)
    published = sqlalchemy.Column(sqlalchemy.DateTime)
    dislikes = sqlalchemy.Column(sqlalchemy.Integer)
    rating = sqlalchemy.Column(sqlalchemy.Float)
    num_of_raters = sqlalchemy.Column(sqlalchemy.Integer)

class VideoSentiment(base):
    __tablename__ = "videosentiments"
    __table_args__ = {'extend_existing':True}
    id = sqlalchemy.Column(sqlalchemy.String, sqlalchemy.ForeignKey("videos.id"),primary_key=True)
    n_pos = sqlalchemy.Column(sqlalchemy.Float)
    n_neg = sqlalchemy.Column(sqlalchemy.Float)
    result = sqlalchemy.Column(sqlalchemy.String)

class CommentSentiment(base):
    __tablename__ = "commentsentiments"
    __table_args__ = {'extend_existing':True}
    id = sqlalchemy.Column(sqlalchemy.String, sqlalchemy.ForeignKey("comments.id"),primary_key=True)
    video_id = sqlalchemy.Column(sqlalchemy.String, sqlalchemy.ForeignKey("videos.id"))
    positive = sqlalchemy.Column(sqlalchemy.Boolean)

class VideoCategory(base):
    __tablename__ = "videocategories"
    __table_args__ = {'extend_existing':True}
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    video_id = sqlalchemy.Column(sqlalchemy.String, sqlalchemy.ForeignKey("videos.id"))
    type = sqlalchemy.Column(sqlalchemy.String)
