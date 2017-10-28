# Tatsuya Yokota
# 

import sys
import data
import classifiers

def main(argv):
	
	if len(argv) < 3:
		print 'Usage: python %s <training data file> <test data file> <optional training category file> <optional test category file>' % (argv[0])
		exit(-1)

	# read the training and test sets
	dtrain = data.Data(argv[1])
	dtest = data.Data(argv[2])

	# get the categories and the training data A and the test data B
	if len(argv) > 4:
		traincatdata = data.Data(argv[3])
		testcatdata = data.Data(argv[4])
		traincats = traincatdata.get_data( [traincatdata.get_headers()[0]] )
		testcats = testcatdata.get_data( [testcatdata.get_headers()[0]] )
		A = dtrain.get_data( dtrain.get_headers() )
		B = dtest.get_data( dtest.get_headers() )
	else:
		# assume the categories are the last column
		traincats = dtrain.get_data( [dtrain.get_headers()[-1]] )
		testcats = dtest.get_data( [dtest.get_headers()[-1]] )
		A = dtrain.get_data( dtrain.get_headers()[:-1] )
		B = dtest.get_data( dtest.get_headers()[:-1] )
	
	userChoice = raw_input("Which classifier would you like to use?\n[n] for Naive Bayes and [k] for KNN: ")
	
	if userChoice.lower() == 'n':
		classifier = classifiers.NaiveBayes()
	elif userChoice.lower() == 'k':
		classifier = classifiers.KNN()
	else:
		print "type in valid classifier type"
		return
	
	# build classfier wwith training set categories
	classifier.build( A, traincats )
	# classify training set
	catsTrain, labelsTrain = classifier.classify( A )
	# print out traiing set confusion matrix
	classifier.confusion_matrix_str(classifier.confusion_matrix(traincats, catsTrain))
	# classify test set
	catsTest, labelsTest = classifier.classify( B )
	# print out test set confusion matrix
	classifier.confusion_matrix_str(classifier.confusion_matrix(testcats, catsTest))
	
	# add category column and write to csv

	dtest.addColumn(['category', 'numeric']+catsTest.T.tolist()[0])
	dtest.writeToCSV('categorizedData.csv', dtest.get_raw_headers())
	
	
if __name__ == "__main__":
	main(sys.argv)