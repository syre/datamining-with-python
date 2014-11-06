#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sqlite3
import os
class Persister:
  def __init__(self,file):
    path = os.path.join(os.path.dirname(__file__),file)
    self.connection = sqlite3.connect(path)

  def __del__(self):
    self.connection.close()

  def get_video_comments(self, id):
      c = self.connection.cursor()
      c.execute("SELECT * FROM comments WHERE video_id=?",id)
      return c.fetchall()

  def is_existing_video(self, id):
      c = self.connection.cursor()
      c.execute("SELECT * FROM videos where id=?",id)
      if c.fetchone():
          return True
      return False


  def save_comment(self, comment):
    c = self.connection.cursor()
    insertion = (comment["id"],
                 comment["video_id"],
                 comment["author_id"],
                 comment["author_name"],
                 comment["content"],
                 comment["published"])
    c.execute("INSERT INTO comments VALUES (?, ?, ?, ?, ?, ?)",insertion)
    self.connection.commit()

  def save_video(self, video):
    c = self.connection.cursor()
    insertion = (video["id"],
                 video["title"],
                 video["author_id"],
                 video["viewcount"],
                 video["duration"],
                 video["published"],
                 video["likes"],
                 video["dislikes"],
                 video["rating"],
                 video["category"],
                 video["number_of_raters"])
    c.execute("INSERT INTO videos VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",insertion)
    self.connection.commit()
