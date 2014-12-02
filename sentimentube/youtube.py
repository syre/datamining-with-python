#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# pylint: disable=R0201
""" This module scrapes/download contents from a youtube video. """
import requests
import dateutil.parser
import logging
import datetime

import models


class YouTubeScraper:

    """ Class for communicating with the gdata youtube API. """

    def __init__(self):
        """ Set the gdata youtube urls and the logger. """
        self.comment_url = "https://gdata.youtube.com/feeds/api/videos/{0}/" \
                           "comments"
        self.video_url = "https://gdata.youtube.com/feeds/api/videos/{0}"
        self.logger = logging.getLogger(__name__)

    def _comment_generator(self, video_id):
        """
        A generator for fetching one "page" of youtube comments.

        For a youtube video, it returns a list of comment dictionaries
        with keys: author_name, author_id, content, video_id, id, published
        It should not be used directly, it is private and the fetch_comments
        method should be used instead.

        Parameters:
        - video_id : the id of the youtube video
        """
        next_url = self.comment_url.format(video_id)
        params = {"v": 2, "alt": "json", "max-results": 50,
                  "orderby": "published"}

        while True:
            if next_url:
                try:
                    response = requests.get(next_url, params=params)
                except requests.exceptions.RequestException:
                    self.logger.exception("_comment_generator: request failed")
                    raise
                else:
                    if not response:
                        error = "_comment_generator: invalid video id: " \
                            "{}".format(video_id)
                        self.logger.error(error)
                        raise ValueError(error)
                    response = response.json()
            else:
                raise StopIteration
            comments = []
            if "entry" not in response["feed"]:
                raise RuntimeError("no comments for video")
            for comment in response["feed"]["entry"]:
                author_name = comment["author"][0]["name"]["$t"]
                author_id = comment["author"][0]["yt$userId"]["$t"]
                content = comment["content"]["$t"]
                comment_id = comment["id"]["$t"]
                published = dateutil.parser.parse(comment["published"]["$t"])

                comment = models.Comment(id=comment_id,
                                         video_id=video_id,
                                         author_id=author_id,
                                         author_name=author_name,
                                         content=content,
                                         published=published)

                comments.append(comment)
            next_url = [link["href"] for link in response["feed"]["link"]
                        if link["rel"] == "next"]
            if next_url:
                next_url = next_url[0]
            yield comments

    def fetch_comments(self, video_id, number=0):
        """
        fetch a number of youtube comments using _comment_generator.

        Parameters:
        - video_id : the id of the youtube video
        - number : the number of comments to fetch (0 = all comments)

        Returns:
        - list of Comment objects
        """
        comments = []
        fetch = self._comment_generator(video_id)
        while True:
            try:
                comments += next(fetch)
                if len(comments) > number and number > 0:
                    return comments[:number]
            except StopIteration:
                return comments

    def fetch_videoinfo(self, video_id):
        """
        fetch relevant information about the video from the gdata youtube API.

        Parameters:
        - video_id : the id of the youtube video

        Returns:
        - tuple of Video object and list of Category objects
        """
        req = requests.get(self.video_url.format(video_id),
                           params={"v": 2, "alt": "json"})
        if not req:
            self.logger.error("fetch_videoinfo: invalid video id")
            raise ValueError("invalid video id")

        req = req.json()
        comment_permission = [entry["permission"] for entry in
                              req["entry"]["yt$accessControl"] if
                              entry["action"] == "comment"][0]

        if comment_permission == "denied":
            self.logger.error("fetch_videoinfo: comments disallowed for video")

            raise RuntimeError("Comments disallowed for video {0}".format(
                video_id))

        video = self.extract_video(req, video_id)
        categories = self.extract_categories(req, video_id)
        return video, categories

    def extract_categories(self, req, video_id):
        """
        extract categories from a json-converted gdata video HTTP response.

        Parameters:
        - req : the gdata video HTTP response
        - video_id: the youtube video id
        Returns:
        - list of Category objects
        """
        categories = req["entry"]["media$group"]["media$category"]
        categories = [models.VideoCategory(type=category["$t"],
                                           video_id=video_id)
                      for category in categories]
        return categories

    def extract_video(self, req, video_id):
        """
        extract video object from a json-converted gdata video HTTP response.

        Parameters:
        - req: the gdata video HTTP response
        - video_id: the youtube video id
        Returns:
        - a Video object
        """
        rating, numraters = None, None
        if "gd$rating" in req["entry"]:
            rating = req["entry"]["gd$rating"]["average"]
            numraters = req["entry"]["gd$rating"]["numRaters"]
        likes, dislikes = None, None
        if "yt$rating" in req["entry"]:
            likes = req["entry"]["yt$rating"]["numLikes"]
            dislikes = req["entry"]["yt$rating"]["numDislikes"]

        title = req["entry"]["title"]["$t"]
        author_id = req["entry"]["author"][0]["yt$userId"]["$t"]
        viewcount = req["entry"]["yt$statistics"]["viewCount"]
        duration = req["entry"]["media$group"]["media$content"][0]["duration"]
        published = dateutil.parser.parse(req["entry"]["published"]["$t"])
        num_of_comments = \
            req["entry"]["gd$comments"]["gd$feedLink"]["countHint"]
        video = models.Video(id=video_id,
                             title=title,
                             author_id=author_id,
                             viewcount=viewcount,
                             duration=duration,
                             published=published,
                             rating=rating,
                             num_of_raters=numraters,
                             likes=likes,
                             dislikes=dislikes,
                             num_of_comments=num_of_comments,
                             timestamp=datetime.datetime.now())
        return video

if __name__ == '__main__':
    YOU = YouTubeScraper()
    print(YOU.fetch_comments("wrong_url"))
