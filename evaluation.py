import nltk.classify
import collections, itertools
from nltk.metrics import *
from nltk.classify import util, ClassifierI, MultiClassifierI
from nltk.probability import FreqDist

def precision_recall(classifier, testfeats):
	refsets = collections.defaultdict(set)
	testsets = collections.defaultdict(set)

	for i, (feats, label) in enumerate(testfeats):
		refsets[label].add(i)
		observed = classifier.classify(feats)
		testsets[observed].add(i)

	precisions = {}
	recalls = {}

	for label in classifier.labels():
		precisions[label] = precision(refsets[label], testsets[label])
		recalls[label] = recall(refsets[label], testsets[label])

	return precisions, recalls

# Calculates the f measure for each category using as input the precisions and recalls
def calculate_f(categories, precisions, recalls):
	f_measures = {}
	for category in categories:
		if precisions[category] is None:
			continue
		else:
			f_measures[category] =  (2 * (precisions[category] * recalls[category])) / (precisions[category] + recalls[category])
	return f_measures

# prints accuracy, precision and recall
def evaluation(classifier, test_feats, categories):
	print ("\n##### Evaluation...")
	print("  Accuracy: %f" % nltk.classify.accuracy(classifier, test_feats))
	precisions, recalls = precision_recall(classifier, test_feats)
	print("Precisions: ",precisions,"Recalls: ",recalls)
	f_measures = calculate_f(categories,precisions, recalls)

	print(" |-----------|-----------|-----------|-----------|")
	print(" |%-11s|%-11s|%-11s|%-11s|" % ("category","precision","recall","F-measure"))
	print(" |-----------|-----------|-----------|-----------|")
	for category in categories:
		if precisions[category] is None:
			print(" |%-11s|%-11s|%-11s|%-11s|" % (category, "NA", "NA", "NA"))
		else:
			print(" |%-11s|%-11f|%-11f|%-11f|" % (category, precisions[category], recalls[category], f_measures[category]))
	print(" |-----------|-----------|-----------|-----------|")

# show informative features
def analysis(classifier):
	print("\n##### Analysis...")
	print(classifier.show_most_informative_features())
