# Tatsuya Yokota
# Spring 2017
# CS 251 Project 8
#
# Classifier class and child definitions

import sys
import data
import analysis as an
import numpy as np

class Classifier:

	def __init__(self, type):
		'''The parent Classifier class stores only a single field: the type of
		the classifier.	 A string makes the most sense.

		'''
		self._type = type

	def type(self, newtype = None):
		'''Set or get the type with this function'''
		if newtype != None:
			self._type = newtype
		return self._type

	def confusion_matrix( self, truecats, classcats ):
		'''Takes in two Nx1 matrices of zero-index numeric categories and
		computes the confusion matrix. The rows represent true
		categories, and the columns represent the classifier output.

		'''
		trueUnique, trueMapping = np.unique(np.array(truecats).T, return_inverse=True)
		classUnique, classMapping = np.unique(np.array(classcats).T, return_inverse=True)
		
		self.cmtx = np.matrix(np.zeros((len(trueUnique),len(classUnique))))
		
		
# 		print len(trueMapping)
# 		print self.cmtx.shape
# 		print len(classMapping)
		for i in range(len(trueMapping)):
			self.cmtx[trueMapping[i], classMapping[i]] += 1
		
# 		print self.cmtx
		
		return self.cmtx.tolist()

	def confusion_matrix_str( self, cmtx ):
		'''Takes in a confusion matrix and returns a string suitable for printing.'''
		
		print "\nConfusion Matrix:\n"
		for i in range(len(cmtx)):
			s = 'Cluster %d' % (i)
			for val in cmtx[i]:
				s += "%10d" % (val)
			print s
		print
		
		return s

	def __str__(self):
		'''Converts a classifier object to a string.  Prints out the type.'''
		return str(self._type)



class NaiveBayes(Classifier):
	'''NaiveBayes implements a simple NaiveBayes classifier using a
	Gaussian distribution as the pdf.

	'''

	def __init__(self, dataObj=None, headers=[], categories=None):
		'''Takes in a Data object with N points, a set of F headers, and a
		matrix of categories, one category label for each data point.'''

		# call the parent init with the type
		Classifier.__init__(self, 'Naive Bayes Classifier')
		
		# store the headers used for classification
		# number of classes and number of features
		self.headers = headers
		self.num_classes = 0
		self.num_features = 0
		self.dataObj = dataObj

		self.categories = categories
		
		if dataObj != None:
			self.build(dataObj, categories)

	def build( self, A, categories ):
		'''Builds the classifier give the data points in A and the categories'''
		
		# figure out how many categories there are and get the mapping (np.unique)
		unique, mapping = np.unique( np.array(categories.T), return_inverse=True)
		
		self.num_classes = len(unique)
		self.num_features = A.shape[1]
		self.class_labels = unique
		
		self.class_means = np.zeros((len(categories), self.num_features))
		self.class_vars = np.zeros((len(categories), self.num_features))
		self.class_scales = np.zeros((len(categories), self.num_features))
		
		# create the matrices for the means, vars, and scales
		# the output matrices will be categories (C) x features (F)
		# compute the means/vars/scales for each class
		for i in range(self.num_classes):
			self.class_means[i,:] = np.mean(A[(mapping==i),:], axis=0)	  
			self.class_vars[i,:] = np.var(A[(mapping==i),:], axis=0 ,ddof=1)
			self.class_scales[i,:] = 1/np.sqrt(2*np.pi*self.class_vars[i,:])
		
		# store any other necessary information: # of classes, # of features, original labels


		return

	def classify( self, A, return_likelihoods=False ):
		'''Classify each row of A into one category. Return a matrix of
		category IDs in the range [0..C-1], and an array of class
		labels using the original label values. If return_likelihoods
		is True, it also returns the NxC likelihood matrix.

		'''

		# error check to see if A has the same number of columns as
		# the class means
		if A.shape[1] != self.class_means.shape[1]:
			return
		
		# make a matrix that is N x C to store the probability of each
		# class for each data point
		P = np.matrix(np.zeros((A.shape[0],self.num_classes))) # a matrix of zeros that is N (rows of A) x C (number of classes)

		# calculate the probabilities by looping over the classes
		#  with numpy-fu you can do this in one line inside a for loop
#		print P.shape
#		print self.class_scales.shape
#		print self.class_vars.shape
#		
#		print self.class_scales
#		print self.class_means
#		print self.class_vars
		
# 		print self.num_classes
		for i in range(self.num_classes):
			# Neil helped me with this formula
			P[:,i] = np.prod(np.multiply(self.class_scales[i,:],np.exp(np.divide(-np.square(A -self.class_means[i,:]),2*self.class_vars[i,:]))),axis=1)
			
			
		# calculate the most likely class for each data point
		cats = np.matrix(np.argmax(P, axis=1)) # take the argmax of P along axis 1
		
		# use the class ID as a lookup to generate the original labels
		labels = self.class_labels[cats]

		if return_likelihoods:
			return cats, labels, P

		return cats, labels

	def __str__(self):
		'''Make a pretty string that prints out the classifier information.'''
		s = "\nNaive Bayes Classifier\n"
		for i in range(self.num_classes):
			s += 'Class %d --------------------\n' % (i)
			s += 'Mean	: ' + str(self.class_means[i,:]) + "\n"
			s += 'Var	: ' + str(self.class_vars[i,:]) + "\n"
			s += 'Scales: ' + str(self.class_scales[i,:]) + "\n"

		s += "\n"
		return s
		
	def write(self, filename):
		'''Writes the Bayes classifier to a file.'''
		# extension
		return

	def read(self, filename):
		'''Reads in the Bayes classifier from the file'''
		# extension
		return

	
class KNN(Classifier):

	def __init__(self, dataObj=None, headers=[], categories=None, K=None):
		'''Take in a Data object with N points, a set of F headers, and a
		matrix of categories, with one category label for each data point.'''

		# call the parent init with the type
		Classifier.__init__(self, 'KNN Classifier')
		
		# store the headers used for classification
		self.headers = headers
		self.num_classes = 0
		self.num_features = 0
		self.dataObj = dataObj

		self.categories = categories
		
		
		if dataObj != None:
			self.build(dataObj, categories)
		# original class labels
		# unique data for the KNN classifier: list of exemplars (matrices)
		# if given data,
			# call the build function

	def build( self, A, categories, K = None ):
		'''Builds the classifier give the data points in A and the categories'''

		# figure out how many categories there are and get the mapping (np.unique)
		unique, mapping = np.unique( np.array(categories.T), return_inverse=True)
		
		self.num_classes = len(unique)
		self.num_features = A.shape[1]
		self.class_labels = unique
		
		self.class_means = np.zeros((len(categories), self.num_features))
		self.class_vars = np.zeros((len(categories), self.num_features))
		self.class_scales = np.zeros((len(categories), self.num_features))
		
		self.exemplars = []
		# for each category i, build the set of exemplars
		for i in range(self.num_classes):
			if K == None:
				self.exemplars.append(A[(mapping==i),:])
			else:
				codebook = an.kmeans_algorithm(A[(mapping==i),:], an.kmeans_init(A[(mapping==i),:], K))[0]
				self.exemplars.append(codebook)
				
			# if K is None
				# append to exemplars a matrix with all of the rows of A where the category/mapping is i
			# else
				# run K-means on the rows of A where the category/mapping is i
				# append the codebook to the exemplars

		# store any other necessary information: # of classes, # of features, original labels

		return

	def classify(self, A, K=3, return_distances=False):
		'''Classify each row of A into one category. Return a matrix of
		category IDs in the range [0..C-1], and an array of class
		labels using the original label values. If return_distances is
		True, it also returns the NxC distance matrix.

		The parameter K specifies how many neighbors to use in the
		distance computation. The default is three.'''

		# error check to see if A has the same number of columns as the class means
		if A.shape[1] != self.class_means.shape[1]:
			return

		# make a matrix that is N x C to store the distance to each class for each data point
		D = np.matrix(np.zeros((A.shape[0],self.num_classes)))	# a matrix of zeros that is N (rows of A) x C (number of classes)
		
		for i in range(self.num_classes):
			temp = np.matrix(np.zeros((A.shape[0],len(self.exemplars[i]))))
			for row in range(len(self.exemplars[i])):
				# print A.shape
#				print temp.shape
#				print len(self.exemplars[i])
#				print row
				distance = np.sqrt(np.sum(np.square(A - self.exemplars[i][row]),axis=1))
# 				print distance
				temp[:,row] = distance
# 			print i
			temp.sort(axis=1)
			D[:,i] = temp[:,0:K].sum(axis=1)

		# calculate the most likely class for each data point
		cats = np.matrix(np.argmin(D, axis=1)) # take the argmin of D along axis 1

		# use the class ID as a lookup to generate the original labels
		labels = self.class_labels[cats]

		if return_distances:
			return cats, labels, D

		return cats, labels

	def __str__(self):
		'''Make a pretty string that prints out the classifier information.'''
		s = "\nKNN Classifier\n"
		for i in range(self.num_classes):
			s += 'Class %d --------------------\n' % (i)
			s += 'Number of Exemplars: %d\n' % (self.exemplars[i].shape[0])
			s += 'Mean of Exemplars	 :' + str(np.mean(self.exemplars[i], axis=0)) + "\n"

		s += "\n"
		return s


	def write(self, filename):
		'''Writes the KNN classifier to a file.'''
		# extension
		return

	def read(self, filename):
		'''Reads in the KNN classifier from the file'''
		# extension
		return
	

