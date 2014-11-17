#!/usr/bin/env python3
# -*- coding: utf-8 -*-
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
logger = logging.getLogger(__name__)

analyzer = sentiment_analysis.SentimentAnalysis()
scraper = youtube.YouTubeScraper()

app = flask.Flask(__name__)


@app.route("/")
def index():
    return flask.render_template("index.html")

@app.route("/about")
def about():
    return flask.render_template("about.html")

@app.route("/video")
def video():
    video_id = flask.request.args.get("video_id")
    # if in the form of an url, extract id
    if "youtube" in video_id:
        url = urllib.parse.urlparse(video_id)
        query = dict(urllib.parse.parse_qsl(url[4]))
        video_id = query["v"]

    sentiment = database.db_session.query(models.VideoSentiment).filter(models.VideoSentiment.id == video_id).first()
    if sentiment:
        logger.info("sentiment for video with id:{} found in database".format(video_id))
        video = database.db_session.query(models.Video).filter(models.Video.id == video_id).first()
        comments = database.db_session.query(models.Comment).filter(models.Comment.video_id == video_id).all()
    else:
        logger.info("processing new video with id: {}".format(video_id))
        try:
            video, categories = scraper.fetch_videoinfo(video_id)
            comments = scraper.fetch_comments(video_id)
        except ValueError:
            return flask.render_template("error.html", error="invalid video id")
        else:
            exists = database.db_session.query(models.Video).filter(models.Video.id == video_id).first()
            if not exists:
                database.db_session.add(video_info)
                database.db_session.add_all(categories)

            for comment in comments:
                exists = database.db_session.query(models.Comment).filter(models.Comment.id == comment_id).first()
                if not exists:
                    database.db_session.add(comment)
            database.db_session.commit()


        sentiment = analyzer.classify_comments(comments)

    video = {"sentiment": sentiment, "video_info": video, "num_of_comments" : len(comments)}
    return flask.render_template("video.html", video=video)

@app.errorhandler(404)
def not_found(error):
    return flask.render_template("error.html", error=error)

@app.route("/previous")
def previous():
    latest = database.db_session.query(models.Video).order_by(sqlalchemy.desc(models.Video.timestamp)).limit(5)
    return flask.render_template("previous.html", latest=latest)

@app.route("/comment_sentiment_plot.png")
def comment_sentiment_plot():
    video_id = flask.request.args.get("video_id")
    fig = Figure(figsize=(5,5))
    axis = fig.add_subplot(1, 1, 1)
    fig.patch.set_alpha(0)

    query = database.db_session.query(models.CommentSentiment).filter(models.CommentSentiment.video_id == video_id).all()
    xs = [[q.positive for q in query if q.positive], [q.positive for q in query if not q.positive]]

    axis.hist(xs, bins=1, color=["g","r"])
    axis.set_xticklabels(["positive", "negative"])
    axis.set_title("comment sentiment distribution")
    axis.set_ylabel("number of comments")
    axis.set_xticks([0.25, 0.75, 1])
    canvas = FigureCanvas(fig)
    output = io.BytesIO()
    canvas.print_png(output)
    response = flask.make_response(output.getvalue())
    response.mimetype = 'image/png'
    return response

@app.route("/video_sentiment_plot.png")
def video_sentiment_plot():
    video_id = flask.request.args.get("video_id")
    fig = Figure(figsize=(5,5))
    axis = fig.add_subplot(1, 1, 1)
    fig.patch.set_alpha(0)

    videos = database.db_session.query(models.VideoSentiment).all()
    current_video = database.db_session.query(models.VideoSentiment).filter(models.VideoSentiment.id == video_id).first()

    axis.plot([v.n_pos for v in videos], [v.n_neg for v in videos], "gx")
    axis.plot(current_video.n_pos, current_video.n_neg, "rx")
    axis.set_title("video sentiment comparison")
    axis.set_xlabel("measure of positivity")
    axis.set_ylabel("measure of negativity")
    canvas = FigureCanvas(fig)
    output = io.BytesIO()
    canvas.print_png(output)
    response = flask.make_response(output.getvalue())
    response.mimetype = 'image/png'
    return response

if __name__ == "__main__":
    app.run(debug=True)
