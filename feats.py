import collections
from nltk.corpus import stopwords, reuters
from nltk.collocations import BigramCollocationFinder
from nltk.metrics import BigramAssocMeasures
from nltk.probability import FreqDist, ConditionalFreqDist

def bag_of_words(words):
	'''
	>>> bag_of_words(['the', 'quick', 'brown', 'fox'])
	{'quick': True, 'brown': True, 'the': True, 'fox': True}
	'''
	return dict([(word, True) for word in words])

def high_information_words(labelled_words, score_fn=BigramAssocMeasures.chi_sq, min_score=5):
	word_fd = FreqDist()
	label_word_fd = ConditionalFreqDist()

	for label, words in labelled_words:
		for word in words:
			word_fd[word] += 1
			label_word_fd[label][word] += 1

	n_xx = label_word_fd.N()
	high_info_words = set()

	for label in label_word_fd.conditions():
		n_xi = label_word_fd[label].N()
		word_scores = collections.defaultdict(int)

		for word, n_ii in label_word_fd[label].items():
			n_ix = word_fd[word]
			score = score_fn(n_ii, (n_ix, n_xi), n_xx)
			word_scores[word] = score

		bestwords = [word for word, score in word_scores.items() if score >= min_score]
		high_info_words |= set(bestwords)

	return high_info_words
