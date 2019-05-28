from nltk.tokenize import word_tokenize
from stopwords import slo_stopwords
from bs4 import BeautifulSoup
from string import punctuation


class Preprocessor:

    def __init__(self):
        self.stopwords = set(slo_stopwords())
        # download()

    def preprocess_webpage(self, webpage):
        bs = BeautifulSoup(webpage, "lxml")
        # Get body and remove script tags
        body = bs.find("body")
        [s.extract() for s in body.findAll("script")]
        return body.text

    def preprocess_text(self, text):
        # TODO: lemmatization maybe?
        # Remove whitespace, to lowercase, split by words, remove stopwords and punctuations
        s = text.strip().lower()
        s = word_tokenize(s)
        s = [x for x in s if x not in self.stopwords and x not in punctuation]
        s = [self.remove_punctuations_from_word(x) for x in s]
        s = [x for x in s if len(x) > 0]
        return s

    def preprocess_and_clean_text(self, text):
        # Remove whitespace, to lowercase, split by words, remove punctuations
        s = text.strip().lower().split()
        s = [self.remove_punctuations_from_word(x) for x in s]
        return s

    # Used for document preprocessing - document is then used to count frequency of words -
    # should have same word positions as original webpage text
    def preprocess_document(self, text):
        s = text.lower()
        s = self.tokenize_document(s)
        return s

    def tokenize_document(self, text):
        return word_tokenize(text)

    def remove_punctuations_from_word(self, word):
        w = word
        for p in punctuation:
            w = w.replace(p, "")
        return w
