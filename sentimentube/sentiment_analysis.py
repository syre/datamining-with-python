#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# pylint: disable=R0201
"""
Module for sentiment analysis.

This module has 3 purposes:
1: Can load an existing classifier from a pickle file
2: Train and save a classifier to a pickle file
3: Can classify multiple comments objects (from a list) and deduct an overall
   classification of the video
The comments object, is the comments from the youtube video which want to be
classified.
"""

import nltk.classify.util
import pickle
import os
import logging
import models
from nltk.corpus import stopwords
CUSTOM_STOP_WORDS = ['band', 'they', 'them']


def create_word_list(text_words_tuples):
    """
    Create a big set with ALL of the words from the corpus.

    :param text_words_tuples: Tuple with all text and their sentiments
    :return words_list: The big set with all the words
    """
    words_list = set()
    for (words, _) in text_words_tuples:
        for word in words:
            words_list.add(word.lower())
    return words_list


def create_tagged_text(tuples):
    """
    Create a list of tuples containing words of the text and its sentiment.

    :param tuples: Tuples with text (as strings) and its sentiment
    :return tuples_text: The list of tuples
    """
    tuple_text = []
    stop = stopwords.words('english')
    for (text, sentiment) in tuples:
        words = text.split()
        clean_word = ([i.lower() for i in words
                       if not i.lower() in stop])
        tuple_text.append((clean_word, sentiment))
    return tuple_text


class SentimentAnalysis:

    """ Class for making sentiment analysis of video comments. """

    def __init__(self, file_name):
        """ Call the load method to load the classifier from file. """
        corpus_path = "data/corpus.txt"
        self.logger = logging.getLogger(__name__)
        _, self.word_list = self.create_words_and_tuples(corpus_path)
        self.file_path = os.path.join(os.path.dirname(__file__), file_name)
        self.classifier = self.load_classifier(corpus_path)

    def load_corpus(self, file_name, split=","):
        """
        Load corpus from file and stores it in a tuple.

        :param file_name: Name of the corpus file
        :param split: How to split a line in the corpus (text vs. sentiment).
                      Default split: ','
        :return: pt and nt: Respectively positive and negative tuple
                            (text, sentiment)
        """
        self.logger.debug("Loading corpus file")
        file_path = os.path.join(os.path.dirname(__file__), file_name)
        try:
            with open(file_path, 'r') as read_file:
                lines = read_file.readlines()[1:]
        except(FileExistsError, LookupError):
            self.logger.error("I/O error: corpus file not found")
            raise
        else:
            sentiment_dict = {0: "negative", 1: "positive"}
            return [(line.split(split)[1].strip(),
                     sentiment_dict[int(line.split(split)[0])])
                    for line in lines]

    def _word_feats_extractor(self, doc):
        """
        Extract features from corpus.

        :param words: List of words from corpus
        :return: Dict of the words as keys and True/False as values
        """
        doc_words = set(doc)
        return dict([("contains({})".format(i), i in doc_words)
                     for i in self.word_list])

    def create_words_and_tuples(self, corpus_filename):
        """
        load corpus and create tagged text and word_list.

        tagged text is the words of the text and their sentiment,
        word_list is the words in the corpus

        :param corpus_filename: the filepath of the corpus
        """
        text = self.load_corpus(corpus_filename, ";")
        tagged_text = create_tagged_text(text)
        word_list = create_word_list(tagged_text)
        return tagged_text, word_list

    def _train(self, corpus_filename):
        """
        Train the classifier.

        Training the Naïve Bayes classifier, by calling the following methods:
        - load_corpus
        - create_tagged_text
        - create_word_list
        - word_feats_extractor
        """
        tagged_text, _ = self.create_words_and_tuples(corpus_filename)

        self.logger.debug("Making training set (apply features)...")

        training_set = nltk.classify.apply_features(
            self._word_feats_extractor, tagged_text)

        classifier = nltk.NaiveBayesClassifier.train(training_set)
        self._save_classifier(classifier)
        return classifier

    def _save_classifier(self, classifier):
        """
        Save the classifier to a pickle file.

        :param classifier: The trained classifier
        """
        try:
            file_open = open(self.file_path, 'wb')
            pickle.dump(classifier, file_open, 1)
            file_open.close()
            self.logger.info("Classifier saved successfully!")
        except IOError:
            self.logger.debug("Couldn't save the classifier to pickle")

    def load_classifier(self, corpus_path):
        """
        Load a trained classifier from file.

        If it fails, it's training a new
        """
        try:
            classifier = nltk.data.load(
                "file:"+self.file_path, 'pickle', 1)
            self.logger.info("Classifier loaded!")
            return classifier
        except (FileExistsError, LookupError):
            self.logger.error("I/O error: classifier file not found")
            self.logger.info("Will train a classifier")
            return self._train(corpus_path)

    def classify_comments(self, comments):
        """
        Classify youtube-videos comments.

        performs classification on each comment
        and let the method 'eval' make a decision
        It normalize the ratio between number of positive and negative comments
        before calling the 'eval' method
        :param comments: The comments of youtube-video
        :return:
        """
        video_sentiment = models.VideoSentiment(id=comments[0].video_id,
                                                n_pos=0, n_neg=0, result="")

        self.logger.info(
            "There is a change in comments. We do sentiment analysis")
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
        self.logger.debug("Number of negative comments: %d",
                          video_sentiment.n_neg)
        self.logger.debug("Number of positive comments: %d",
                          video_sentiment.n_pos)

        video_sentiment.n_pos /= total_data
        video_sentiment.n_neg /= total_data
        self.logger.debug("Number of negative comments after "
                          "normalization: %.2f", video_sentiment.n_neg)
        self.logger.debug(
            "Number of positive comments after normalization: %.2f",
            video_sentiment.n_pos)

        video_sentiment.result = self._eval(video_sentiment)
        self.logger.info("The result of the video: %s",
                         video_sentiment.result)
        return video_sentiment, comments_sentiment

    def _eval(self, video_sentiment):
        """
        evaluate the overall sentiment of the youtube video.

        Taking a decision of the sentiment of the youtube-video
        based on the ratio between positive and negative comments
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
