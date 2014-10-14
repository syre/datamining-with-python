#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sqlite

class Persister:
  def __init__(file):
    self.connection = sqlite3.connect(file)
  def __del__():
    self.connection.close()

  def save_comment(self, comment):
    pass
  def save_video(self, video):
    pass
