import nltk.classify.util
from nltk.classify import NaiveBayesClassifier
from nltk.corpus import movie_reviews
import pickle
from youtube import *

class SentimentAnalysis:
    def __init__(self):
        self.youtube = YouTubeScraper()
        try:
            #with open('my_classifier.pickle', 'rb') as f:
            #classifier = nltk.classifier
            self.classifier = nltk.data.load('my_classifier.pickle', 'pickle', 1) #pickle.load(f)
            print("Det lykkedes umiddelbart!")
        except LookupError as e:
            print("I/O error: file not found")
            self.train()



    def word_feats_extractor(self, words):

        #cleanWords = [word for word in words if not word in stopwords.words('english')]
        return dict([(word, True) for word in words])
        #docwords = set(doc)
        #features = {}
        #for i in wordList:
        #    features['contains(%s)' % i] = (i in docwords)
        #return features
    def train(self):
        negids = movie_reviews.fileids('neg')
        posids = movie_reviews.fileids('pos')

        negfeats = [(self.word_feats_extractor(movie_reviews.words(fileids=[f])), 'neg') for f in negids]
        posfeats = [(self.word_feats_extractor(movie_reviews.words(fileids=[f])), 'pos') for f in posids]

        negcutoff = int(len(negfeats)*3/4)
        poscutoff = int(len(posfeats)*3/4)
        print(negcutoff)
        print(poscutoff)
        trainfeats = negfeats[:negcutoff] + posfeats[:poscutoff]
        testfeats = negfeats[negcutoff:] + posfeats[poscutoff:]
        print('train on {0} instances, test on {1} instances'.format(len(trainfeats), len(testfeats)))

        classifier = NaiveBayesClassifier.train(trainfeats)

        f = open('my_classifier.pickle', 'wb')
        pickle.dump(classifier, f, 1)
        f.close()

    def classify_comments(self, video_id=None):
        clusters = {"pos": 0, "neg": 0}
        comments = self.youtube.fetch_comments(video_id)
        for i, comment in enumerate(comments): #list[index]["content"]
            res = self.classifier.classify(self.word_feats_extractor(comment["content"]))
            print(res)
            clusters[res] += 1
            comments[i]["sentiment"] = res

        total_data = clusters["pos"]+clusters["neg"]
        print(clusters["pos"])
        print(clusters["neg"])
        clusters["pos"] /= total_data
        clusters["neg"] /= total_data
        print(clusters["pos"])
        print(clusters["neg"])

        clusters["result"] = self.eval(clusters)
        print(clusters["result"])

    def eval(self, clusters):
        total_data = clusters["pos"]+clusters["neg"]

        #eval_dict = {"Strong negative": 0, "Slight negative": 0,
         #            "Neutral": 0, "Slight positive": 0, "Strong positive": 0}
        if clusters["pos"] < .25:
            res = "strong negative"
            return res
        elif clusters["pos"] >= .25 and clusters["pos"] < .4:
            res = "slight negative"
            return res
        elif clusters["pos"] >= .4 and clusters["pos"] < .55:
            res = "neutral"
            return res
        elif clusters["pos"] >= .55 and clusters["pos"] < .75:
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









