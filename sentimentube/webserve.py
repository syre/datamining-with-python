#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Flask app for webservice.

handles the interacting between the user and the system.
"""
import flask
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
import io
import urllib
import urllib.parse
import logging
import sqlalchemy

import database
import models
import sentiment_analysis
import youtube

logging.basicConfig(format="%(asctime)s %(message)s", level=logging.DEBUG)
LOGGER = logging.getLogger(__name__)

ANALYZER = sentiment_analysis.SentimentAnalysis("data/classifier.pickle")
SCRAPER = youtube.YouTubeScraper()

APP = flask.Flask(__name__)


def save_sentiment(video_sentiment, comments_sentiment):
    """
    helper function for saving sentiments in the database.

    Saves the results of sentiment analysis to the database.
    The result of each comment and for the whole video is saved
    :param video_sentiment: sentiment result for the whole video:
    number of pos and neg comments (normalized) and final verdict of the video
    :param comments_sentiment: comments of the video with their sentiments
    """
    db_sentiments = database.DB_SESSION.query(models.CommentSentiment).filter(
        models.CommentSentiment.video_id == video_sentiment.id).all()
    db_comment_sentiment_ids = [db_comment.id for db_comment in db_sentiments]

    for comment_sentiment in comments_sentiment:
        if comment_sentiment.id not in db_comment_sentiment_ids:
            database.DB_SESSION.add(comment_sentiment)

    db_videosentiment = database.DB_SESSION.query(
        models.VideoSentiment).filter(
            models.VideoSentiment.id == video_sentiment.id).first()

    if db_videosentiment:
        db_videosentiment = database.DB_SESSION.merge(video_sentiment)
    else:
        database.DB_SESSION.add(video_sentiment)
    database.DB_SESSION.commit()


@APP.route("/")
def index():
    """
    Show the front page to the user.

    :return: the front page (index.html)
    """
    return flask.render_template("index.html")


@APP.route("/about")
def about():
    """
    Show the about page to the user.

    :return: the about page (about.html)
    """
    return flask.render_template("about.html")


@APP.route("/video")
def video():
    """
    Video analysis page.

    Run the classification for the input the user has given
    Checks in database whether the video has been processed before. If it has
    been processed before and there is no changes, it simply shows the result.
    Else, it will process the video and show the result
    :return: The video page (video.html) with the result from database or
            classification.
    """
    video_id = flask.request.args.get("video_id")
    # if in the form of an url, extract id
    if "youtube" in video_id:
        url = urllib.parse.urlparse(video_id)
        query = dict(urllib.parse.parse_qsl(url[4]))
        video_id = query["v"]

    db_video_info = database.DB_SESSION.query(models.Video).filter(
        models.Video.id == video_id).first()
    try:
        video_info, categories = SCRAPER.fetch_videoinfo(video_id)
    except ValueError:
        return flask.render_template("error.html",
                                     error="invalid video id")
    except RuntimeError as err:
        return flask.render_template("error.html", error=str(err))

    if (db_video_info and
            db_video_info.num_of_comments == video_info.num_of_comments):
        LOGGER.info("sentiment for video with id: %r found in database",
                    video_id)

        sentiment = database.DB_SESSION.query(models.VideoSentiment).filter(
            models.VideoSentiment.id == video_id).first()

        comments = database.DB_SESSION.query(models.Comment).filter(
            models.Comment.video_id == video_id).all()
    else:
        LOGGER.info("processing new video with id: %r", video_id)
        if db_video_info:
            db_video_info = database.DB_SESSION.merge(video_info)
        else:
            database.DB_SESSION.add(video_info)
            database.DB_SESSION.add_all(categories)
        try:
            comments = SCRAPER.fetch_comments(video_id)
        except RuntimeError as err:
            return flask.render_template("error.html", error=str(err))

        # get unique comments only
        unique_ids = set([comment.id for comment in comments])
        comments = [next(com for com in comments if com.id == com_id)
                    for com_id in unique_ids]

        for comment in comments:
            comment_in_db = database.DB_SESSION.query(models.Comment).filter(
                models.Comment.id == comment.id).first()

            if not comment_in_db:
                database.DB_SESSION.add(comment)

        database.DB_SESSION.commit()

        sentiment, comment_sentiments = ANALYZER.classify_comments(comments)

        save_sentiment(sentiment, comment_sentiments)
    video_dict = {"sentiment": sentiment, "video_info": video_info,
                  "num_of_comments": len(comments)}
    return flask.render_template("video.html", video=video_dict)


@APP.errorhandler(404)
def not_found(error):
    """
    Show an error message to the user.

    :param error:
    :return: The error page with the message
    """
    return flask.render_template("error.html", error=error)


@APP.route("/previous")
def previous():
    """ return 5 latest sentiment analyses. """
    latest = database.DB_SESSION.query(models.Video).order_by(
        sqlalchemy.desc(models.Video.timestamp)).limit(5)

    return flask.render_template("previous.html", latest=latest)


@APP.route("/comment_sentiment_plot.png")
def comment_sentiment_plot():
    """
    Create comment sentiment plot.

    Creating the histogram-plot for the sentiments of the comments of the video
    :return: PNG file showing the histogram
    """
    video_id = flask.request.args.get("video_id")
    fig = Figure(figsize=(5, 5))
    axis = fig.add_subplot(1, 1, 1)
    fig.patch.set_alpha(0)

    query = database.DB_SESSION.query(models.CommentSentiment).filter(
        models.CommentSentiment.video_id == video_id).all()
    positive = [q.positive for q in query if q.positive]
    negative = [q.positive for q in query if not q.positive]

    if positive:
        axis.hist(positive, color=["g"], align="left", bins=[0, 1])
    if negative:
        axis.hist(negative, color=["r"], align="right", bins=[0, 1])
    axis.set_xlabel("positive        negative")
    axis.set_xticks([])
    axis.set_title("comment sentiment distribution")
    axis.set_ylabel("number of comments")
    canvas = FigureCanvas(fig)
    output = io.BytesIO()
    canvas.print_png(output)
    response = flask.make_response(output.getvalue())
    response.mimetype = 'image/png'
    return response


@APP.route("/video_sentiment_plot.png")
def video_sentiment_plot():
    """
    Create video sentiment plot.

    Creating a scatter-plot for the sentiments of the video against other
    videos with the same youtube-category
    :return: PNG file showing the scatter-plot
    """
    video_id = flask.request.args.get("video_id")
    fig = Figure(figsize=(5, 5))
    axis = fig.add_subplot(1, 1, 1)
    fig.patch.set_alpha(0)

    videos = database.DB_SESSION.query(models.VideoSentiment).all()

    current_video = database.DB_SESSION.query(models.VideoSentiment).filter(
        models.VideoSentiment.id == video_id).first()

    axis.scatter([v.n_pos for v in videos], [v.n_neg for v in videos],
                 color="blue", marker="x", label="previously analysed")
    axis.scatter(current_video.n_pos, current_video.n_neg, color="black",
                 marker="o", label=video_id)
    axis.set_title("video sentiment comparison")
    axis.set_xlabel("measure of positivity")
    axis.set_ylabel("measure of negativity")
    axis.legend()
    canvas = FigureCanvas(fig)
    output = io.BytesIO()
    canvas.print_png(output)
    response = flask.make_response(output.getvalue())
    response.mimetype = 'image/png'
    return response

if __name__ == "__main__":
    APP.run(debug=True)
