#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import requests
import json

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
                r = requests.get(next_url, params=params).json()
            else:
                raise StopIteration
            comments = []
            for comment in r["feed"]["entry"]:
                author_name = comment["author"][0]["name"]["$t"]
                author_id = comment["author"][0]["yt$userId"]["$t"]
                content = comment["content"]["$t"]
                comment_id = comment["id"]["$t"]
                published = comment["published"]["$t"]
                comment = {"author_name": author_name,
                           "author_id": author_id,
                           "content": content,
                           "video_id": video_id,
                           "id": comment_id,
                           "published": published}
                comments.append(comment)
            next_url = [e["href"] for e in r["feed"]["link"] if e["rel"] == "next"]
            if next_url:
                next_url = next_url[0]
            yield comments

    def fetch_comments(self, video_id, number=0):
        """
        fetch a number of youtube comments by using the _comment_generator function.

        Parameters:
        - video_id : the id of the youtube video
        - number : the number of comments to fetch (0 = all comments)

        """
        comments = []
        f = self.__comment_generator(video_id)
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

      """
      params = {"v": 2, "alt": "json"}
      r = requests.get(self.video_url.format(video_id), params=params).json()

      title = r["entry"]["title"]["$t"]
      author_id = r["entry"]["author"][0]["yt$userId"]["$t"]
      rating = r["entry"]["gd$rating"]["average"]
      viewcount = int(r["entry"]["yt$statistics"]["viewCount"])
      duration = r["entry"]["media$group"]["media$content"][0]["duration"]
      category = r["entry"]["media$group"]["media$category"][0]["$t"]
      published = r["entry"]["published"]["$t"]
      numraters = r["entry"]["gd$rating"]["numRaters"]
      likes = r["entry"]["yt$rating"]["numLikes"]
      dislikes = r["entry"]["yt$rating"]["numDislikes"]
      video_info = {"id" : video_id,
                    "title": title,
                    "author_id": author_id,
                    "category": category,
                    "viewcount": viewcount,
                    "duration": duration,
                    "published": published,
                    "rating": rating,
                    "number_of_raters": numraters,
                    "likes": likes,
                    "dislikes": dislikes}
      return video_info


if __name__ == '__main__':
    c = YouTubeScraper()
    print(c.fetch_comments("DfVSsWEiq8c",20))
