#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# pylint: disable=W0232, R0903

""" Handling objects """
import sqlalchemy
from database import BASE


class Comment(BASE):
    """
    Comment object
    """

    __tablename__ = "comments"
    __table_args__ = {'extend_existing': True}
    id = sqlalchemy.Column(sqlalchemy.String, primary_key=True)
    video_id = sqlalchemy.Column(sqlalchemy.String,
                                 sqlalchemy.ForeignKey("videos.id"))
    author_id = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    author_name = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    content = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    published = sqlalchemy.Column(sqlalchemy.DateTime, nullable=False)

    def __repr__(self):
        return "{}(id={}, video_id={}, author_id={}, content={})".format(
            self.__class__.__name__, self.id, self.video_id, self.author_id,
            self.content)


class Video(BASE):
    """
    Video object
    """
    __tablename__ = "videos"
    __table_args__ = {'extend_existing': True}
    id = sqlalchemy.Column(sqlalchemy.String, primary_key=True, nullable=False)
    title = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    author_id = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    viewcount = sqlalchemy.Column(sqlalchemy.Integer, nullable=False)
    duration = sqlalchemy.Column(sqlalchemy.Integer, nullable=False)
    likes = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)
    published = sqlalchemy.Column(sqlalchemy.DateTime, nullable=False)
    dislikes = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)
    rating = sqlalchemy.Column(sqlalchemy.Float, nullable=True)
    num_of_raters = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)
    timestamp = sqlalchemy.Column(sqlalchemy.DateTime, nullable=False)
    num_of_comments = sqlalchemy.Column(sqlalchemy.Integer,
                                        nullable=False)

    def __repr__(self):
        return "{}(id={}, title={}, author_id={})".format(
            self.__class__.__name__, self.id, self.title, self.author_id)


class VideoSentiment(BASE):
    """
    VideoSentiment object
    """
    __tablename__ = "videosentiments"
    __table_args__ = {'extend_existing': True}
    id = sqlalchemy.Column(sqlalchemy.String,
                           sqlalchemy.ForeignKey("videos.id"),
                           primary_key=True, nullable=False)
    n_pos = sqlalchemy.Column(sqlalchemy.Float, nullable=False)
    n_neg = sqlalchemy.Column(sqlalchemy.Float, nullable=False)
    result = sqlalchemy.Column(sqlalchemy.String, nullable=False)

    def __repr__(self):
        return "{}(id={}, n_pos={:.3}, n_neg={:.3}, result={})".format(
            self.__class__.__name__, self.id, self.n_pos, self.n_neg,
            self.result)


class CommentSentiment(BASE):
    """
    CommentSentiment object
    """
    __tablename__ = "commentsentiments"
    __table_args__ = {'extend_existing': True}
    id = sqlalchemy.Column(sqlalchemy.String,
                           sqlalchemy.ForeignKey("comments.id"),
                           primary_key=True, nullable=False)
    video_id = sqlalchemy.Column(sqlalchemy.String,
                                 sqlalchemy.ForeignKey("videos.id"),
                                 nullable=False)
    positive = sqlalchemy.Column(sqlalchemy.Boolean, nullable=False)

    def __repr__(self):
        return "{}(id={}, video_id={}, positive={})".format(
            self.__class__.__name__, self.id, self.video_id, self.positive)


class VideoCategory(BASE):
    """
    VideoCategory object
    """
    __tablename__ = "videocategories"
    __table_args__ = {'extend_existing': True}
    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, nullable=False)
    video_id = sqlalchemy.Column(sqlalchemy.String,
                                 sqlalchemy.ForeignKey("videos.id"),
                                 nullable=False)
    type = sqlalchemy.Column(sqlalchemy.String, nullable=False)

    def __repr__(self):
        return "{}(id={}, video_id={}, type={})".format(
            self.__class__.__name__, self.id, self.video_id, self.type)
