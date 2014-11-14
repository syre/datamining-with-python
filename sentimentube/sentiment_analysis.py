#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import nltk.classify.util
from nltk.classify import NaiveBayesClassifier
from nltk.corpus import movie_reviews
import pickle
import os
import logging

import youtube
import models
import database

class SentimentAnalysis:
    """Class for making sentiment analysis of video comments"""

    def __init__(self):
        """
        Call the load method to load the classifier from file.
        Creating an object to YouTubeScaper
        """
        self.youtube = youtube.YouTubeScraper()
        self.logger = logging.getLogger(__name__)
        self.file_path = os.path.join(os.path.dirname(__file__), "data", "classifier.pickle")
        self.load_classifier(self.file_path)

    def word_feats_extractor(self, words):
        """
        Extract features from corpus
        :param words: List of words from corpus
        :return: Dict of the words as keys and value True
        """

        return dict([(word, True) for word in words])

    def train(self, file_name):
        """
        Training the Naïve Bayes classifier
        :param file_name: Filename of which the classifier should be saved as
        """
        negids = movie_reviews.fileids('neg')
        posids = movie_reviews.fileids('pos')

        negfeats = [(self.word_feats_extractor(movie_reviews.words(fileids=[f])), 'neg') for f in negids]
        posfeats = [(self.word_feats_extractor(movie_reviews.words(fileids=[f])), 'pos') for f in posids]

        negcutoff = int(len(negfeats) * 3 / 4)
        poscutoff = int(len(posfeats) * 3 / 4)
        self.logger.debug("Number of negative features: {0}".format(negcutoff))
        self.logger.debug("Number of positive features: {0}".format(poscutoff))
        trainfeats = negfeats[:negcutoff] + posfeats[:poscutoff]

        classifier = NaiveBayesClassifier.train(trainfeats)
        self.save_classifier(classifier, file_name)

    def save_classifier(self, classifier, file_name):
        """
        Saving the classifier to a pickle file
        :param classifier: The trained classifier
        """
        try:
            f = open(self.filepath, 'wb')
            pickle.dump(classifier, f, 1)
            f.close()
            self.logger.info("Classifier saved successfully!")
        except IOError:
            self.logger.debug("Couldn't save the classifier to pickle")

    def load_classifier(self, filepath):
        """
        Loading a trained classifier from file. If it fails, it's training a new
        :param: filepath: Filepath of the file which should be loaded as classifier
        """
        try:
            self.classifier = nltk.data.load(filepath, 'pickle', 1)
            self.logger.info("Classifier loaded!")
        except FileExistsError:
            self.logger.error("I/O error: file not found")
            self.logger.info("Will train a classifier")
            self.train()

    def compare_comments_number(self, video_id, n_comments):
        db_res = database.db_session.query(models.VideoSentiment).filter(
            models.VideoSentiment.id == video_id).first()
        if not db_res:
            return False
        else:
            if (db_res.n_pos + db_res.n_neg) == n_comments:
                return True
            else:
                return False

    def save_sentiment(self, clusters, comments):
        """

        :param comments:
        """
        db_comments = database.db_session.query(models.Comment).filter(models.Comment.video_id == comments[0].video_id).all()
        db_comment_ids = [db_comment.id for db_comment in db_comments]
        for comment in comments:
            if comment.id not in db_comment_ids:
                database.db_session.add(models.CommentSentiment(id=comment.id, video_id=comment.video_id, positive=comment.sentiment))

        db_videosentiment = database.db_session.query(models.VideoSentiment).filter(models.VideoSentiment.id ==
                                                                         comments[0].video_id).all()
        if db_videosentiment:
            result_db = database.db_session.query(models.VideoSentiment).filter(models.VideoSentiment.id == comments[0].video_id).first()
            result_db.result = clusters["result"]
            database.db_session.add(result_db)
        else:
            database.db_session.add(models.VideoSentiment(id=comments[0].video_id,
                                                                                n_pos=clusters["pos"],
                                                                                n_neg=clusters["neg"],
                                                                                result=clusters["result"]))
        database.db_session.commit()

    def classify_comments(self, video_id):
        """
        Classifying a youtube-videos comments, by classify each comments and let the method 'eval' make a decision
        It normalize the ratio between number of positive and negative comments, before calling the 'eval' method
        :param video_id: The ID of youtube-video
        :return:
        """
        clusters = {"pos": 0, "neg": 0}
        comments = self.youtube.fetch_comments(video_id)
        result = self.compare_comments_number(video_id, len(comments))
        if result:
            self.logger.info("Last sentiment analysis were done on the same number of as we have now. "
                             "So no reason to make sentiment")
        else:
            self.logger.info(
                "Their is a change in comments. We do sentiment analysis")
            for i, comment in enumerate(comments):  # list[index]["content"]
                print(comment.content)
                res = self.classifier.classify(self.word_feats_extractor(comment.content))
                print(res)
                clusters[res] += 1
                if res == "pos":
                    comments[i].sentiment = 1
                else:
                    comments[i].sentiment = 0

            total_data = clusters["pos"] + clusters["neg"]
            self.logger.debug("Number of negative comments: {0}".format(clusters["neg"]))
            self.logger.debug("Number of positive comments: {0}".format(clusters["pos"]))
            print("hej hej hej")
            clusters["pos"] /= total_data
            clusters["neg"] /= total_data
            self.logger.debug("Number of negative comments after normalization: {0}".format(clusters["neg"]))
            self.logger.debug("Number of positive comments after normalization: {0}".format(clusters["pos"]))
            print("hej hej ")
            clusters["result"] = self.eval(clusters)
            print("farvel eval")
            self.logger.info("The result of the video: {0}".format(clusters["result"]))
            self.save_sentiment(clusters, comments)

            print("hej")

    def eval(self, clusters):
        """
        Taking a decision of the whole youtube-video based on the ratio between positive and negative comments
        It takes a decision like so, based on number positive comments (nPos):
            -   nPos <0.25:     Strong negative
            -   nPos >= 0.25 and nPos < 0.4:    Slight negative
            -   nPos >= 0.4 and nPos < 0.6:     Neutral
            -   nPos >= 0.6 ann nPos < 0.75:    Slight positive
            -   nPos >= 0.75:   Strong positive
        :param clusters:
        :return:
        """
        print("Hej eval")
        if clusters["pos"] < .25:
            res = "strong negative"
            return res
        elif clusters["pos"] >= .25 and clusters["pos"] < .4:
            res = "slight negative"
            return res
        elif clusters["pos"] >= .4 and clusters["pos"] < .6:
            res = "neutral"
            return res
        elif clusters["pos"] >= .6 and clusters["pos"] < .75:
            res = "slight positive"
            return res
        else:
            res = "strong positive"
            return res
        print("Hej eval ")
