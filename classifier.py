# export LC_ALL=en_US.UTF-8
# export LANG=en_US.UTF-8

import re
import sys
import string
import random
import math
from nltk.tokenize import TweetTokenizer
from nltk.tokenize import RegexpTokenizer
from nltk.tokenize.casual import remove_handles
import nltk.classify
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from feats import bag_of_words, high_information_words
from evaluation import evaluation, analysis
from os import listdir
from os.path import isfile, join
from random import shuffle

tknzr = TweetTokenizer(reduce_len=True)
tokenizer = RegexpTokenizer(r'\w+')

def get_filenames_in_folder(folder):
	"""Return filenames that are in both positive and negative folders."""
	return [f for f in listdir(folder) if isfile(join(folder, f))]

def read_files(filemap,categories,stopwordsPunctuationList):
	"""Reads every line in the files from get_filenames_in_folder(),
	tokenizes the lines and creates a bag of words from it with bag_of_words()"""
	feats = list ()
	print("\n##### Reading files...")
	for category in categories:
		files = get_filenames_in_folder(filemap + '/' + category)
		random.shuffle(files)
		num_files=0
		for f in files:
			if not f.startswith('.'):
				data = open(filemap + '/' + category + '/' + f, 'r', encoding='UTF-8').read()
				for line in data.split('\n'):
					line = remove_handles(line)
					line = re.sub(r"http\S+", "", line)
					line = tokenizer.tokenize(line)
					line = ' '.join(line)
					line = line.lower()
					line = tknzr.tokenize(line)
					line = ' '.join(line)

					line = line.split()
					# exclude newlines
					if not line == []:
						filtered_tokens = [w for w in line if not w.isdigit() and w not in stopwordsPunctuationList and w not in ['bitcoin','Bitcoin','btc','BTC']]
						#print(filtered_tokens)
						bag = bag_of_words(filtered_tokens)

						feats.append((bag, category))
						#print(feats)
						#print len(filtered_tokens)
						num_files+=1
						if num_files>=1000: # you may want to de-comment this and the next line if you're doing tests (it just loads N documents instead of the whole collection so it runs faster
							break

		print ("  Category %s, %i files read" % (category, num_files))

	print("  Total, %i files read" % (len(feats)))
	return feats

def high_information(feats, categories):
	"""Creates a high information words dictionary from labelled words."""
	print("\n##### Obtaining high information words...")

	labelled_words = [(category, []) for category in categories]

	#1. convert the formatting of our features to that required by high_information_words
	from collections import defaultdict
	words = defaultdict(list)
	all_words = list()
	for category in categories:
		words[category] = list()

	for feat in feats:
		category = feat[1]
		bag = feat[0]
		for w in bag.keys():
			words[category].append(w)
			all_words.append(w)
		#break

	labelled_words = [(category, words[category]) for category in categories]
	#print(labelled_words)

	#2. calculate high information words
	high_info_words = set(high_information_words(labelled_words, min_score=1.0))
	#print(high_info_words)
	#high_info_words contains a list of high-information words. You may want to use only these for classification.

	print("  Number of words in the data: %i" % len(all_words))
	print("  Number of distinct words in the data: %i" % len(set(all_words)))
	print("  Number of distinct 'high-information' words in the data: %i" % len(high_info_words))

	return high_info_words

def filter_high_information_words(feats, high_information_words):
	"""Compares feats and high information words and returns new_feats that consists
	of feats from both high information words and old feats."""
	newfeats = []
	feats_dict = {}
	for tuple in feats:
		#print(tuple)
		for item in tuple[0].keys():
			#print(item)
			if item in high_information_words:
				feats_dict[item] = True
		newfeats.append((feats_dict, tuple[1]))
		feats_dict = {}
	return newfeats

# splits a labelled dataset into two disjoint subsets train and test
def split_train_test(feats, split=0.7):
	"""Splits the dataset by randomly picking 30% test and 70% train data."""
	train_feats = []
	test_feats = []
	#print (feats[0])
	shuffle(feats) # randomise dataset before splitting into train and test
	cutoff = int(len(feats) * split)
	train_feats, test_feats = feats[:cutoff], feats[cutoff:]
	print("\n##### Splitting datasets...")
	print("  Training set: %i" % len(train_feats))
	print("  Test set: %i" % len(test_feats))
	return train_feats, test_feats

def main():
	stopwordsPunctuationList = stopwords.words('english')
	[stopwordsPunctuationList.append(i) for i in string.punctuation]
	stopwordsPunctuationList.append('not')
	categories = ['positive','negative']
	trainmap = 'trainset'
	feats = read_files(trainmap,categories,stopwordsPunctuationList)

	#print(feats)

	high_info_words = high_information(feats,categories)

	high_info_feats = filter_high_information_words(feats,high_info_words)

	train_feats, test_feats = split_train_test(high_info_feats)

	all_words = []
	for f in feats:
		for word in f[0].keys():
			all_words.append(word)

	frequency = nltk.FreqDist(all_words)
	word_features = frequency.keys()
	#print(word_features)
	# https://www.youtube.com/watch?annotation_id=annotation_3385405775&feature=iv&index=12&list=PLQVvvaa0QuDf2JswnfiGkliBInZnIC4HL&src_vid=zi16nl82AMA&v=-vVskDsHcVc
	def find_features(document):
		words = set(document)
		features = {}
		for w in word_features:
			features[w] = (w in words)
		return features

	train_set = nltk.classify.apply_features(find_features,high_info_feats)
	nb_classifier = nltk.NaiveBayesClassifier.train(train_set)

	testmap = 'testset'
	#test_feats = read_files(testmap,categories,stopwordsPunctuationList)
	test_set = nltk.classify.apply_features(find_features,test_feats)

	accuracy_score = evaluation(nb_classifier,test_set,categories)
	analysis(nb_classifier)

	research_data = ['research_data/07-06-2018.csv','research_data/08-06-2018.csv','research_data/09-06-2018.csv',
	'research_data/10-06-2018.csv','research_data/11-06-2018.csv','research_data/12-06-2018.csv',
	'research_data/13-06-2018.csv','research_data/14-06-2018.csv','research_data/15-06-2018.csv',
	'research_data/16-06-2018.csv','research_data/17-06-2018.csv','research_data/18-06-2018.csv',
	'research_data/19-06-2018.csv','research_data/20-06-2018.csv','research_data/21-06-2018.csv',
	'research_data/22-06-2018.csv','research_data/23-06-2018.csv']

	for file in research_data:
		positives,negatives = 0,0
		with open(file,'r',encoding='UTF-8') as f:
			f_list = list(f)
			for line in f_list:
				line = line.strip()
				#str_list = list(filter(None,line))
				line = line.strip('\n')
				line = remove_handles(line)
				line = re.sub(r"http\S+", "", line)
				line = re.sub(r'\d+','',line)
				line = tokenizer.tokenize(line)
				line = ' '.join(line)
				line = line.lower()
				line = tknzr.tokenize(line)
				line = [w for w in line if not w in stopwordsPunctuationList and w not in ['rt','btc','bitcoin']]
				line = ' '.join(line)

				result = nb_classifier.prob_classify(find_features(line.split()))
				if result.max() == 'positive' and result.prob('positive') >= .7:
					positives += 1
				elif result.max() == 'negative' and result.prob('negative') >= .7:
					negatives += 1
				#break
		print('Data: {} Positives: {} Negatives: {} Confidence Positive: {} Confidence Negative: {}'.format(file,positives,negatives,result.prob('positive'),result.prob('negative')))
main()
