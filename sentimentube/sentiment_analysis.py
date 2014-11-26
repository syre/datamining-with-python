#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from urllib.error import URLError

import nltk.classify.util
from nltk.classify import NaiveBayesClassifier
from nltk.corpus import movie_reviews
import pickle
import os
import logging
import models
import database


class SentimentAnalysis:
    """Class for making sentiment analysis of video comments"""

    def __init__(self, file_name):
        """
        Call the load method to load the classifier from file.
        """

        self.logger = logging.getLogger(__name__)
        self.file_path = os.path.join(os.path.dirname(__file__), file_name)
        self.load_classifier()

    def _word_feats_extractor(self, words):
        """
        Extract features from corpus
        :param words: List of words from corpus
        :return: Dict of the words as keys and value True
        """
        return dict([(word, True) for word in words])

    def _train(self):
        """
        Training the Naïve Bayes classifier
        """

        negids = movie_reviews.fileids('neg')
        posids = movie_reviews.fileids('pos')

        negfeats = [(self._word_feats_extractor(
            movie_reviews.words(fileids=[f])), 'neg') for f in negids]
        posfeats = [(self._word_feats_extractor(
            movie_reviews.words(fileids=[f])), 'pos') for f in posids]

        negcutoff = int(len(negfeats) * 3 / 4)
        poscutoff = int(len(posfeats) * 3 / 4)
        self.logger.debug("Number of negative features: {0}".format(negcutoff))
        self.logger.debug("Number of positive features: {0}".format(poscutoff))
        trainfeats = negfeats[:negcutoff] + posfeats[:poscutoff]

        classifier = NaiveBayesClassifier.train(trainfeats)
        self.save_classifier(classifier)

    def _save_classifier(self, classifier):
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

    def load_classifier(self):
        """
        Loading a trained classifier from file.
        If it fails, it's training a new
        """
        try:
            self.classifier = nltk.data.load(
                "file:"+self.file_path, 'pickle', 1)
            self.logger.info("Classifier loaded!")
        except FileExistsError:
            self.logger.error("I/O error: file not found")
            self.logger.info("Will train a classifier")
            self._train()

    def classify_comments(self, comments):
        """
        Classifying a youtube-videos comments, by classify each comments
        and let the method 'eval' make a decision
        It normalize the ratio between number of positive and negative comments
        before calling the 'eval' method
        :param comments: The comments of youtube-video
        :return:
        """
        video_sentiment = models.VideoSentiment(id=comments[0].video_id,
                                                n_pos=0, n_neg=0, result="")

        self.logger.info(
            "Their is a change in comments. We do sentiment analysis")
        comments_sentiment = []
        for comment in comments:
            res = self.classifier.classify(self._word_feats_extractor(
                comment.content.split()))

            if res == "pos":
                video_sentiment.n_pos += 1
                comments_sentiment.append(models.CommentSentiment(
                    id=comment.id, video_id=comment.video_id, positive=1))
            else:
                video_sentiment.n_neg += 1
                comments_sentiment.append(models.CommentSentiment(
                    id=comment.id, video_id=comment.video_id, positive=0))

        total_data = video_sentiment.n_pos + video_sentiment.n_neg
        self.logger.debug("Number of negative comments: {0}".format(
            video_sentiment.n_neg))
        self.logger.debug("Number of positive comments: {0}".format(
            video_sentiment.n_pos))

        video_sentiment.n_pos /= total_data
        video_sentiment.n_neg /= total_data
        self.logger.debug("Number of negative comments after "
                          "normalization: {0}"
                          .format(video_sentiment.n_neg))
        self.logger.debug(
            "Number of positive comments after normalization: {0}".format(
                video_sentiment.n_pos))

        video_sentiment.result = self._eval(video_sentiment)
        self.logger.info("The result of the video: {0}".format(
            video_sentiment.result))
        return video_sentiment, comments_sentiment

    def _eval(self, video_sentiment):
        """
        Taking a decision of the whole youtube-video based on the ratio
        between positive and negative comments
        It takes a decision like so, based on number positive comments (nPos):
            -   nPos <0.25:     Strong negative
            -   nPos >= 0.25 and nPos < 0.4:    Slight negative
            -   nPos >= 0.4 and nPos < 0.6:     Neutral
            -   nPos >= 0.6 ann nPos < 0.75:    Slight positive
            -   nPos >= 0.75:   Strong positive
        :param video_sentiment:
        :return:
        """
        if video_sentiment.n_pos < .25:
            res = "strong negative"
        elif video_sentiment.n_pos >= .25 and video_sentiment.n_pos < .4:
            res = "slight negative"
        elif video_sentiment.n_pos >= .4 and video_sentiment.n_pos < .6:
            res = "neutral"
        elif video_sentiment.n_pos >= .6 and video_sentiment.n_pos < .75:
            res = "slight positive"
        else:
            res = "strong positive"

        return res
