-- Database schema set up
DROP TABLE IF EXISTS comments;
DROP TABLE IF EXISTS videos;

CREATE TABLE comments(
  id TEXT PRIMARY KEY NOT NULL,
  video_id TEXT NOT NULL,
  author_id TEXT NOT NULL,
  author_name TEXT NOT NULL,
  content TEXT NOT NULL,
  published TEXT NOT NULL,
  FOREIGN KEY(video_id) REFERENCES videos(id)
);

CREATE TABLE videos(
  id TEXT PRIMARY KEY NOT NULL,
  title TEXT NOT NULL,
  author_id TEXT NOT NULL,
  viewcount INTEGER NOT NULL,
  duration INTEGER NOT NULL,
  published TEXT NOT NULL,
  likes INTEGER NOT NULL,
  dislikes INTEGER NOT NULL,
  rating REAL,
  category TEXT,
  number_of_raters INTEGER
);
