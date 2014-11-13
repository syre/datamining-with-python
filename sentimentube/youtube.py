#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import requests
import dateutil.parser
import logging

import models


class YouTubeScraper:

    """ Class for communicating with the gdata youtube API. """

    def __init__(self):
        """ Set the gdata youtube urls. """
        self.comment_url = "https://gdata.youtube.com/feeds/api/videos/{0}/comments"
        self.video_url = "https://gdata.youtube.com/feeds/api/videos/{0}"

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
        params = {"v": 2, "alt": "json", "max-results": 50, "orderby": "published"}

        while(True):
            if next_url:
                try:
                    req = requests.get(next_url, params=params)
                    if not req:
                        logging.error("_comment_generator: invalid video id")
                        yield None
                    r = req.json()
                except requests.ConnectionError as e:
                    logging.error("caught ConnectionError {}".format(e))
            else:
                raise StopIteration
            comments = []
            for comment in r["feed"]["entry"]:
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
            next_url = [n["href"] for n in r["feed"]["link"] if n["rel"] == "next"]
            if next_url:
                next_url = next_url[0]
            yield comments

    def fetch_comments(self, video_id, number=0):
        """
        fetch a number of youtube comments by using the _comment_generator function.

        Parameters:
        - video_id : the id of the youtube video
        - number : the number of comments to fetch (0 = all comments)

        Returns:
        - list of Comment objects
        """
        comments = []
        f = self._comment_generator(video_id)
        while(True):
            try:
                comments += next(f)
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
      - tuple of Video object and list of Categories
      """
      params = {"v": 2, "alt": "json"}
      req = requests.get(self.video_url.format(video_id), params=params)
      if not req:
          logging.error("fetch_videoinfo: invalid video id")
          raise RuntimeError("invalid video id")

      r = req.json()

      title = r["entry"]["title"]["$t"]
      author_id = r["entry"]["author"][0]["yt$userId"]["$t"]
      rating = r["entry"]["gd$rating"]["average"]
      viewcount = int(r["entry"]["yt$statistics"]["viewCount"])
      duration = r["entry"]["media$group"]["media$content"][0]["duration"]
      categories = r["entry"]["media$group"]["media$category"]
      published = r["entry"]["published"]["$t"]
      numraters = r["entry"]["gd$rating"]["numRaters"]
      likes = r["entry"]["yt$rating"]["numLikes"]
      dislikes = r["entry"]["yt$rating"]["numDislikes"]
      categories = [models.VideoCategory(type=c["$t"],video_id=video_id) for c in categories]
      video = models.Video(id=video_id,
                    title=title,
                    author_id=author_id,
                    viewcount=viewcount,
                    duration=duration,
                    published=published,
                    rating=rating,
                    num_of_raters=numraters,
                    likes=likes,
                    dislikes=dislikes)
      return video, categories

if __name__ == '__main__':
    c = YouTubeScraper()
    print(c.fetch_videoinfo("wrong_url"))
