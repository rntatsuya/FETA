# Tatsuya Yokota
# analysis.py
#

from data import Data
from pcaData import PCAData
import numpy as np
import scipy.stats
import scipy.cluster.vq as vq
import math
import random

# class Analysis():
	# takes in data object and list of column headers and returns matrix with lists of 
	# min and max value for each column
def data_range(colHeaders, dataClass):
	dataMatrix = dataClass.get_data(colHeaders)
#		print dataMatrix
	min = np.nanmin(dataMatrix, axis=0)
	max = np.nanmax(dataMatrix, axis=0)
#		print min
#		print max
	return np.vstack([min, max]).T

# takes in data object and list of column headers and returns the mean for each column
def mean(colHeaders, dataClass):
	dataMatrix = dataClass.get_data(colHeaders)
	mean = np.nanmean(dataMatrix, axis=0)
	
	return mean.tolist()[0]

# takes in data object and list of column headers and returns the standard deviation 
# for each column
def stdev(colHeaders, dataClass):
	dataMatrix = dataClass.get_data(colHeaders)
	stdev = np.nanstd(dataMatrix, axis=0)
	
	return stdev.tolist()[0]

# normalize all columns of inputted column headers separately 
def normalize_columns_separately(colHeaders, dataClass):
	dataMatrix = dataClass.get_data(colHeaders)
	# subtract each column by the column's min value
	# print dataMatrix.T
	#print self.data_range(colHeaders, dataClass)[:,0]
	#print dataMatrix.T - self.data_range(colHeaders, dataClass)[:,0]
	# divide each column by the column's max value - min value
	#print np.max(dataMatrix.T - self.data_range(colHeaders, dataClass)[:,0], axis=1)
	
	return (dataMatrix - np.min(dataMatrix, axis=0)) / (np.max(dataMatrix, axis=0) - np.min(dataMatrix, axis=0))

def normalize_columns_together(colHeaders, dataClass):
	dataMatrix = dataClass.get_data(colHeaders)
	# subtract each entry by the matrix's min value
#		print dataMatrix.T
#		print np.min(dataMatrix)
#		print dataMatrix.T - np.min(dataMatrix)
	# divide each entry by the matrix's max value - min value
#		print np.max(dataMatrix.T - np.min(dataMatrix))
	return ((dataMatrix.T - np.nanmin(dataMatrix))/np.nanmax(dataMatrix.T - np.nanmin(dataMatrix))).T

def linear_regression(dataClass, indList, depVar):
# assign to y 
  # assign to A 
  #	   It's best if both y and A are numpy matrices
  # add a column of 1's to A to represent the constant term in the 
  #	   regression equation.	 Remember, this is just y = mx + b (even 
  #	   if m and x are vectors).
	# the column of data for the dependent variable
	y = dataClass.get_data([depVar])
	# the columns of data for the independent variables
	A = dataClass.get_data(indList)
	
	oneCol = np.asmatrix(np.ones(A.shape[0])).T
	A = np.hstack([A, oneCol])
	
  # assign to AAinv the result of calling numpy.linalg.inv( np.dot(A.T, A))
  #	   The matrix A.T * A is the covariancde matrix of the independent
  #	   data, and we will use it for computing the standard error of the 
  #	   linear regression fit below.
	
	AAinv = np.linalg.inv(np.dot(A.T, A))
	
  # assign to x the result of calling numpy.linalg.lstsq( A, y )
  #	   This solves the equation y = Ab, where A is a matrix of the 
  #	   independent data, b is the set of unknowns as a column vector, 
  #	   and y is the dependent column of data.  The return value x 
  #	   contains the solution for b.
	
	x = np.linalg.lstsq( A, y )
	
 
 
	
	#This is the solution that provides the best fit regression
	b = x[0]
	
	# assign to N the number of data points (rows in y)
	N = y.shape[0]
	# assign to C the number of coefficients (rows in b)
	C = b.shape[0]
	# assign to df_e the value N-C, 
	#	 This is the number of degrees of freedom of the error
	df_e = N - C
	# assign to df_r the value C-1
	#	 This is the number of degrees of freedom of the model fit
	#	 It means if you have C-1 of the values of b you can find the last one.
	df_r = C - 1
	
	
  # assign to error, the error of the model prediction.	 Do this by 
  #	   taking the difference between the value to be predicted and
  #	   the prediction. These are the vertical differences between the
  #	   regression line and the data.
  #	   y - numpy.dot(A, b)
	
	error = y - np.dot(A,b)
	
  # assign to sse, the sum squared error, which is the sum of the
  #	   squares of the errors computed in the prior step, divided by the
  #	   number of degrees of freedom of the error.  The result is a 1x1 matrix.
  #	   numpy.dot(error.T, error) / df_e

	sse = np.dot(error.T, error) / df_e
	
  # assign to stderr, the standard error, which is the square root
  #	   of the diagonals of the sum-squared error multiplied by the
  #	   inverse covariance matrix of the data. This will be a Cx1 vector.
  #	   numpy.sqrt( numpy.diagonal( sse[0, 0] * AAinv ) )

	stderr = np.sqrt( np.diagonal( sse[0, 0] * AAinv ) )

  # assign to t, the t-statistic for each independent variable by dividing 
  #	   each coefficient of the fit by the standard error.
  #	   t = b.T / stderr

	t = b.T / stderr

  # assign to p, the probability of the coefficient indicating a
  #	   random relationship (slope = 0). To do this we use the 
  #	   cumulative distribution function of the student-t distribution.	
  #	   Multiply by 2 to get the 2-sided tail.
  #	   2*(1 - scipy.stats.t.cdf(abs(t), df_e))

	p = 2*(1 - scipy.stats.t.cdf(abs(t), df_e))

  # assign to r2, the r^2 coefficient indicating the quality of the fit.
  #	   1 - error.var() / y.var()

	r2 = 1 - error.var() / y.var()

  # Return the values of the fit (b), the sum-squared error, the
  #		R^2 fit quality, the t-statistic, and the probability of a
  #		random relationship.
	
	print "fit: ", b
	print "SSE: ", sse
	print "R^2 fit quality: ", r2
	print "t-statistic: ", t
	print "probability of a random relationship: ", p
	
	ret = ""
	for var in indList:
		ret += var
	
	text_file = open(depVar+ret+".txt", "w")
	text_file.write("Fit: %s \nSSE: %s \nR^2 Fit Quality: %s \nT-Statistic: %s \nProbability of a Random Relationship: %s" % (b,sse,r2,t,p))
	text_file.close()
	
	return b, sse, r2, t, p

def pca(dataClass, colHeaders, normalize=True):
	# assign to A the desired data. Use either normalize_columns_separately 
	#	or get_data, depending on the value of the normalize argument.
	if normalize:
		A = normalize_columns_separately(colHeaders, dataClass)
	else:
		A = dataClass.get_data(colHeaders)
		
  # assign to m the mean values of the columns of A
	m = A.mean(axis=0)
	# print m
# 		print A

  # assign to D the difference matrix A - m
	D = A - m
	# print D
	
  # assign to U, S, V the result of running np.svd on D, with full_matrices=False
	U, S, V = np.linalg.svd(D, full_matrices=False)
	
# 		print U
# 		print S
# 		print V
  # the eigenvalues of cov(A) are the squares of the singular values (S matrix)
  #	  divided by the degrees of freedom (N-1). The values are sorted.

	eVals = np.square(S)/(A.shape[0] - 1)
# 		print eigVals
  # project the data onto the eigenvectors. Treat V as a transformation 
  #	  matrix and right-multiply it by D transpose. The eigenvectors of A 
  #	  are the rows of V. The eigenvectors match the order of the eigenvalues.
	eVecs = V
# 	print V
# 		print D.T
# 		print eigVecs
	
  # create and return a PCA data object with the headers, projected data, 
  # eigenvectors, eigenvalues, and mean vector.
	projData = (D * eVecs.T  )
	
	
	return PCAData( colHeaders, projData, eVals.round(decimals=4), eVecs.round(decimals=4), m)
	#return colHeaders, dataClass.get_data(dataClass.get_headers()), eigVecs, eigVals, m
	
def kmeans_numpy( data, headers, K, whiten = True):
	'''Takes in a Data object, a set of headers, and the number of clusters to create
	Computes and returns the codebook, codes, and representation error.
	'''
	A = data.get_data(headers)
	W = vq.whiten(A)

	codebook, bookerror= vq.kmeans(W,K)
	
	codes, error = vq.vq(W, codebook)
	
	
	return codebook, codes, error

def kmeans(data, headers, K, whiten=True, categories = ''):
	'''Takes in a Data object, a set of headers, and the number of clusters to create
	Computes and returns the codebook, codes and representation errors. 
	If given an Nx1 matrix of categories, it uses the category labels 
	to calculate the initial cluster means.
	'''
	
	# assign to A the result getting the data given the headers
	# if whiten is True
	  # assign to W the result of calling vq.whiten on the data
	# else
	  # assign to W the matrix A
	A = data.get_data(headers)
	if whiten:
		W = vq.whiten(A)
# 		print "W"
# 		print W
	else:
		W = A
# 		print "W"
# 		print W
	
	# assign to codebook the result of calling kmeans_init with W, K, and categories
	codebook = kmeans_init(W, K, categories)
	# assign to codebook, codes, errors, the result of calling kmeans_algorithm with W and codebook		   
	codebook, codes, errors = kmeans_algorithm(W, codebook)
	# return the codebook, codes, and representation error
# 	print "codebook",codebook
# 	print "codes", codes
# 	print "errors", errors
	return codebook, codes, errors

def kmeans_init(data, K, categories=""):
	ret = []
	
	if categories == "": # check if categories is a numpy matrix
		chosenIndices = []
		for mean in range(K):
			index = random.randint(0,K)
			while index in chosenIndices:
				index = random.randint(0,data.shape[0]-1)
			
			chosenIndices.append(index)
# 			print data[index,:].tolist()

			if isinstance(data[index,:].tolist()[0], list):
				ret.append(data[index,:].tolist()[0])
			else:
				ret.append(data[index,:].tolist())
		return np.matrix(ret)
	else:
		# category is a matrix with the category of the data in each row, which corresponds to 
		# the data matrix's row
		
		cats = {}
		for row in range(categories.shape[0]):
			currentCat = categories[row,0]
			if currentCat in cats:
				cats[currentCat] = cats.get(currentCat)+data[row,:]
			else:
				cats[currentCat] = data[row,:]
		
		for i in range(len(cats.keys())):
			ret.append(cats.get(i).tolist())
		
# 		print ret
# 		print len(ret)
		
		
		return np.matrix(ret)
	
	
def kmeans_classify(data, means):
# 	print "means", means
	classifiedData = []
	
# 	print "shape"
# 	print data.shape[0]
	for row in range(data.shape[0]):
		distance = float("inf")
		newCluster = 0
# 		print row
		for mean in means:
			# print "mean\n", mean
# 			print "data row\n", data[row]
			newDistance = math.sqrt(np.sum(np.square(data[row] - mean))) # sum squared distance for a point 
			if newDistance < distance:
				distance = newDistance
				cluster = newCluster
			newCluster += 1
		
		classifiedData.append([cluster, distance])
	
# 	print np.matrix(classifiedData).T[0,:]
	return np.matrix(classifiedData)[:,0], np.matrix(classifiedData)[:,1]

def kmeans_algorithm(A, means):
	# set up some useful constants
	MIN_CHANGE = 1e-7
	MAX_ITERATIONS = 100
	D = means.shape[1]
	K = means.shape[0]
	N = A.shape[0]

	# iterate no more than MAX_ITERATIONS
	for i in range(MAX_ITERATIONS):
# 		print "loop ", i
		# calculate the codes
		codes, errors = kmeans_classify( A, means )

		# calculate the new means
		newmeans = np.zeros_like( means )
		counts = np.zeros( (K, 1) )
		for j in range(N):
			newmeans[codes[j,0],:] += A[j,:]
			counts[codes[j,0],0] += 1.0

		# finish calculating the means, taking into account possible zero counts
		for j in range(K):
			if counts[j,0] > 0.0:
				newmeans[j,:] /= counts[j, 0]
			else:
				newmeans[j,:] = A[random.randint(0,A.shape[0]),:]

		# test if the change is small enough
		diff = np.sum(np.square(means - newmeans))
		means = newmeans
# 		print "diff\n",diff
		if diff < MIN_CHANGE:
			break

	# call classify with the final means
	codes, errors = kmeans_classify( A, means )

	# return the means, codes, and errors
	return (means, codes, errors)

if __name__ == "__main__":
	an = Analysis()
#	data = Data("data-clean.csv")
#	print an.linear_regression(data, ["X0", "X1"], "Y")
#	
#	data = Data("data-good.csv")
#	print an.linear_regression(data, ["X0", "X1"], "Y")
#	
#	data = Data("data-noisy.csv")
#	print an.linear_regression(data, ["X0", "X1"], "Y")

	data = Data("BodyFat.csv")
	print an.linear_regression(data, ["AGE", "WEIGHT"], "BODYFAT")
	print an.normalize_columns_separately(["AGE", "WEIGHT"], data)
#	print dapp.get_data(['Age', 'Fare']).T 
#	print "Data range is\n", an.data_range(['Fare', 'Age', 'SibSp', 'Parch'], data)
#	print "Mean is\n", an.mean(['Fare', 'Age', 'SibSp', 'Parch'], data)
#	print "Standard Deviation is\n", an.stdev(['Fare', 'Age', 'SibSp', 'Parch'], data)
#	print an.normalize_columns_separately(['Fare', 'Age', 'SibSp', 'Parch'], data)
#	print an.normalize_columns_together(['Fare', 'Age', 'SibSp', 'Parch'], data)

#	print "Data range is\n", an.data_range(['thing1','thing2','thing3'], data)
#	print "Mean is\n", an.mean(['thing1','thing2','thing3'], data)
#	print "Standard Deviation is\n", an.stdev(['thing1','thing2','thing3'], data)
#	print "Normalize column separately\n", an.normalize_columns_separately(['thing3','thing2'], data)
#	print "Normalize column together\n", an.normalize_columns_together(['thing1','thing2','thing3'], data)

#	print "Normalize column separately\n", an.normalize_columns_separately(['bad','headers'], data)
