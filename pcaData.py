import numpy as np
from data import Data

class PCAData(Data):
	def __init__(self, headers, pdata, evals, evecs, means, filename = None):
		Data.__init__(self)
		self.eigenValues = evals
		self.eigenVectors = evecs
		self.dataMeans = means
		self.dataHeaders = headers
		self.matrix_data = pdata
		
		# add to raw_headers and raw data types 
		for idx in range(len(headers)):
			if idx > 9:
				self.raw_headers.append("P%d" % (idx))
			else:
				self.raw_headers.append("P0%d" % (idx))
			self.raw_types.append("numeric")
		
# 		print self.raw_headers
		# add a numpy array to raw_data 
		self.raw_data = np.squeeze(np.asarray(pdata))
		
		# add to header2raw and header2matrix
		for index in range(len(self.raw_headers)):
			self.header2raw[self.raw_headers[index]] = index
			self.header2matrix[self.raw_headers[index]] = index
		
	
	def get_eigenvalues(self):
# 		print type(self.eigenValues)
		return self.eigenValues
	
	def get_eigenvectors(self):
		return self.eigenVectors
		
	def get_data_means(self):
		return self.dataMeans
	
	def get_PCA_headers(self):
		return self.raw_headers
		
	def get_original_headers(self):
		return self.dataHeaders

if __name__ == "__main__":
	pca = PCAData()