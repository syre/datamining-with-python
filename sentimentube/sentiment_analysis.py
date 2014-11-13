import nltk.classify.util
from nltk.classify import NaiveBayesClassifier
from nltk.corpus import movie_reviews
import pickle
from youtube import *
import logging


class SentimentAnalysis:

    """Class for making sentiment analysis of video comments"""

    def __init__(self):
        """
        Call the load method to load the classifier from file.
        Creating an object to YouTubeScaper
        """
        self.youtube = YouTubeScraper()
        self.logger = logging.getLogger(__name__)
        file_name = 'my_classifier'
        self.load_classifier(file_name)

    def word_feats_extractor(self, words):
        """
        Extract features from corpus
        :param words: List of words from corpus
        :return: Dict of the words as keys and value True
        """
        #cleanWords = [word for word in words if not word in stopwords.words('english')]
        return dict([(word, True) for word in words])
        #docwords = set(doc)
        #features = {}
        #for i in wordList:
        #    features['contains(%s)' % i] = (i in docwords)
        #return features

    def train(self, file_name):
        """
        Training the Naïve Bayes classifier
        :param file_name: Filename of which the classifier should be saved as
        """
        negids = movie_reviews.fileids('neg')
        posids = movie_reviews.fileids('pos')

        negfeats = [(self.word_feats_extractor(movie_reviews.words(fileids=[f])), 'neg') for f in negids]
        posfeats = [(self.word_feats_extractor(movie_reviews.words(fileids=[f])), 'pos') for f in posids]

        negcutoff = int(len(negfeats)*3/4)
        poscutoff = int(len(posfeats)*3/4)
        self.logger.debug("Number of negative features: {0}".format(negcutoff))
        self.logger.debug("Number of positive features: {0}".format(poscutoff))
        trainfeats = negfeats[:negcutoff] + posfeats[:poscutoff]
        #testfeats = negfeats[negcutoff:] + posfeats[poscutoff:]
        #print('train on {0} instances, test on {1} instances'.format(len(trainfeats), len(testfeats)))

        classifier = NaiveBayesClassifier.train(trainfeats)
        self.save_classifier(classifier, file_name)

    def save_classifier(self, classifier, file_name):
        """
        Saving the classifier to a pickle file
        :param classifier: The trained classifier
        """
        try:
            f = open(file_name + ".pickle", 'wb')
            pickle.dump(classifier, f, 1)
            f.close()
            self.logger.info("Classifier saved successfully!")
        except IOError:
            self.logger.debug("Couldn't save the classifier to pickle")

    def load_classifier(self, file_name):
        """
        Loading a trained classifier from file. If it fails, it's training a new
        :param: file_name: Filename of the file which should be loaded as classifier
        """
        try:
            #with open('my_classifier.pickle', 'rb') as f:
            #classifier = nltk.classifier
            self.classifier = nltk.data.load(file_name + ".pickle", 'pickle', 1) #pickle.load(f)
            self.logger.info("Classifier loaded!")
            #print("Det lykkedes umiddelbart!")
        except FileExistsError:
            self.logger.error("I/O error: file not found")
            self.logger.info("Will train a classifier")
            self.train()

    def classify_comments(self, video_id):
        """
        Classifying a youtube-videos comments, by classify each comments and let the method 'eval' make a decision
        It normalize the ratio between number of positive and negative comments, before calling the 'eval' method
        :param video_id: The ID of youtube-video
        :return:
        """
        clusters = {"pos": 0, "neg": 0}
        comments = self.youtube.fetch_comments(video_id)
        for i, comment in enumerate(comments): #list[index]["content"]
            res = self.classifier.classify(self.word_feats_extractor(comment["content"]))
            print(res)
            clusters[res] += 1
            comments[i]["sentiment"] = res

        total_data = clusters["pos"]+clusters["neg"]
        self.logger.debug("Number of negative comments: {0}".format(clusters["neg"]))
        self.logger.debug("Number of positive comments: {0}".format(clusters["pos"]))
        clusters["pos"] /= total_data
        clusters["neg"] /= total_data
        self.logger.debug("Number of negative comments after normalization: {0}".format(clusters["neg"]))
        self.logger.debug("Number of positive comments after normalization: {0}".format(clusters["pos"]))

        clusters["result"] = self.eval(clusters)
        self.logger.info("The result of the video: {0}".format(clusters["result"]))

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




   # print 'accuracy:', nltk.classify.util.accuracy(classifier, testfeats)
   # classifier.show_most_informative_features()


    # In[4]:

    # while True:
    #     input = raw_input("Please write a sentence to be tested for sentiment. If you type 'exit', the program will quit.    If you want to see the most informative features, type informfeatures.")
    #     if input == 'exit':
    #         break
    #     elif input == 'informfeatures':
    #         print classifier.show_most_informative_features(n=30)
    #         continue
    #     else:
    #         input = input.lower()
    #         input = input.split()
    #         print '\nWe think that the sentiment was ' + classifier.classify(word_feats_extractor(input)) + ' in that sentence.\n'
    #
    #
    #
    #
    # list[index]["content"]









