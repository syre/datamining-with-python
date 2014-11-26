__author__ = 'Anders'

from unittest import mock, TestCase
import sentiment_analysis
import models
from datetime import datetime


class SentimentAnalysisTestCase(TestCase):

    def setUp(self):
        self.sa = sentiment_analysis.SentimentAnalysis(
            "data/classifier.pickle")

    @mock.patch("sentiment_analysis.SentimentAnalysis._train")
    @mock.patch("sentiment_analysis.SentimentAnalysis.load_classifier")
    @mock.patch("nltk.data.load")
    def test_load_classifier(self, train, load_classifier, load_data):
        sa = sentiment_analysis.SentimentAnalysis("data/classifier.pickle")
        train.assert_called()

    def test_classify_comments(self):
        comments = []
        static_comments = ["I love you!", "I hate you!",
                           "I wont talk to you. Idiot!", "you are sweet",
                           "I'm happy", "i'm mad!"]

        for comment in static_comments:
            comments.append(models.Comment(video_id="dQw4w9WgXcQ",
                                           author_id="xxx", author_name="yyy",
                                           content=comment,
                                           published=datetime.now()))

        video_sentiment, comments_sentiment = self.sa.classify_comments(
            comments)
        assert [com.positive for com in comments_sentiment] == [1, 0, 0, 1, 1,
                                                                0]

        assert video_sentiment.n_pos == 0.5
        assert video_sentiment.n_neg == 0.5

    def test_eval(self):
        test_ratios_pos = [0.1, 0.25, 0.35, 0.4, 0.45, 0.5, 0.6, 0.7, 0.85,
                           0.96]
        test_objects = []
        for ratio in test_ratios_pos:
            test_objects.append(models.VideoSentiment(id="dQw4w9WgXcQ",
                                                      n_pos=ratio,
                                                      n_neg=(1-ratio),
                                                      result=""))

        result = []
        for object_test in test_objects:
            result.append(self.sa._eval(object_test))

        assert [res for res in result] == ["strong negative",
                                           "slight negative",
                                           "slight negative",
                                           "neutral",
                                           "neutral",
                                           "neutral",
                                           "slight positive",
                                           "slight positive",
                                           "strong positive",
                                           "strong positive"]
