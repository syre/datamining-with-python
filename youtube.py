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

    def _make_request(self, url, para):
        f = requests.get(url, params=para)
        return f.json()

    def _comment_generator(self):
        next_url = self.comment_url
        params = {"v": 2, "alt": "json", "max-results": 50, "orderby": "published"}

        while(True):
            if next_url:
                r = self._make_request(next_url, params)
            else:
                raise StopIteration
            comments = []
            for comment in r["feed"]["entry"]:
                author_name = comment["author"][0]["name"]["$t"]
                author_id = comment["author"][0]["yt$userId"]["$t"]
                content = comment["content"]["$t"]
                comment = {"author_name": author_name,
                           "author_id": author_id,
                           "content": content,
                           "video_id": self.video_id,
                           "id": comment["id"]["$t"]}
                comments.append(comment)
            next_url = [e["href"] for e in r["feed"]["link"] if e["rel"] == "next"]
            if next_url:
                next_url = next_url[0]
            yield comments

    def fetch_comments(self):
        comments = []
        f = self._comment_generator()
        while(True):
            try:
                comments += next(f)
            except StopIteration:
                return comments

    def fetch_videoinfo(self):
      params = {"v": 2, "alt": "json"}
      r = self._make_request(self.video_url, params)

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
