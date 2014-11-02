#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import requests
import json
import persister

class YouTubeFetcher:
    def __init__(self, video_id):
        self.video_id = video_id
        self.comment_url = "https://gdata.youtube.com/feeds/api/videos/{0}/comments".format(self.video_id)
        self.video_url = "https://gdata.youtube.com/feeds/api/videos/{0}".format(self.video_id)

    def _comment_generator(self):
        """a generator for fetching one "page" of youtube comments
        for a youtube video, it returns a list of comment dictionaries
        with keys: author_name, author_id, content, video_id, id, published """
        next_url = self.comment_url
        params = {"v": 2, "alt": "json", "max-results": 50, "orderby": "published"}

        while(True):
            if next_url:
                r = requests.get(url, params=params).json()
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
                           "video_id": self.video_id,
                           "id": comment_id,
                           "published": published}
                comments.append(comment)
            next_url = [e["href"] for e in r["feed"]["link"] if e["rel"] == "next"]
            if next_url:
                next_url = next_url[0]
            yield comments

    def fetch_comments(self):
        """fetches all youtube comments
        by using the _comment_generator function"""
        comments = []
        f = self._comment_generator()
        while(True):
            try:
                comments += next(f)
            except StopIteration:
                return comments

    def fetch_videoinfo(self):
      """fetches relevant information about the video
      from the gdata youtube API"""
      params = {"v": 2, "alt": "json"}
      r = requests.get(self.video_url, params=params).json()

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
      video_info = {"id" : self.video_id,
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
    c = YouTubeFetcher("OjBPIfpnd_g")
    p = persister.Persister("project.db")
    p.save_video(c.fetch_videoinfo())
    for comment in c.fetch_comments():
      p.save_comment(comment)
