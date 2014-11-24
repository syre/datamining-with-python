__author__ = 'Anders'

from unittest import mock, TestCase
import sentiment_analysis
import models
from datetime import date

class SentimentAnalysisTestCase(TestCase):

    @mock.patch("sentiment_analysis.SentimentAnalysis._train")
    @mock.patch("sentiment_analysis.SentimentAnalysis.load_classifier")
    #@mock.patch("youtube.SentimentAnalysis.load_classifier", return_value="loaded")
    @mock.patch("nltk.data.load")
    def test_load_classifier(self, train, load_classifier, load_data):
        sa = sentiment_analysis.SentimentAnalysis("data/classifier.pickle")
        train.assert_called()

    #control = ["pos", "neg", "neg", "pos", "pos", "neg"]
    @mock.patch("sentiment_analysis.SentimentAnalysis.compare_comments_number")
    #@mock.patch("classifier.classify", return_value=control)
    def test_classify_comments(self, comments_compare):
        sa = sentiment_analysis.SentimentAnalysis("data/classifier.pickle")
        comments = []
        static_comments = ["I love you!", "I hate you!", "I wont talk to you. Idiot!", "you are sweet", "I'm happy",
                           "i'm mad!"]

        for comment in static_comments:
            comments.append(models.Comment(video_id="dQw4w9WgXcQ", author_id="xxx", author_name="yyy", content=comment,
                                           published=date.now()))

        comments_compare.return_value = False
        video_sentiment, comments_sentiment = sa.classify_comments(comments)
        assert [com.positive for com in comments_sentiment] == [1, 0, 0, 1, 1, 0]

        assert video_sentiment.n_pos == 0.5
        assert video_sentiment.n_neg == 0.5


    def test_eval(self):
        print("hej")
        #assert sa.classifier == "loaded"
        print("hej")