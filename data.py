# Tatsuya Yokota
# data.py

import csv
import numpy as np
import time
import datetime
import xlrd

class Data():
	def __init__(self, filename = None):
		# create and initialize fields for the class
		self.raw_headers = [] # list of headers
		self.raw_types = [] # list of data types 
		self.raw_data = [] # list of list of all data
		self.header2raw = {} # dictionary that maps each header (key) to a column index number (value)
		self.numericalConvertedData = []
		self.matrix_data = np.matrix([]) # matrix of numeric data
		self.header2matrix = {} # dictionary mapping header string to index of column in matrix data
		self.enumHeaders = [] # header name of the enum columns
		self.enum2numeric = {} # dictionary mapping enum string to its unique value
		
		if filename != None:
			self.read(filename)
	
	# helper method to convert xls or xlsx files into csv
	def xls_to_csv(self, filename):
		
		wb = xlrd.open_workbook(filename)
		sh = wb.sheet_by_name('Sheet1')
		csvFile = open(filename.split('.')[0]+'.csv', 'wb')
		wr = csv.writer(csvFile, quoting=csv.QUOTE_ALL)

		for rownum in xrange(sh.nrows):
			wr.writerow(sh.row_values(rownum))

		csvFile.close()
	
	# creates the raw_data 2D list and numeric data matrix, takes in csv, xls, or xlsx files
	def read(self, filename):
		if filename.split('.')[1] == "xls" or filename.split('.')[1] == "xlsx":
			self.xls_to_csv(filename)
			filename = filename.split('.')[0]+'.csv'
		
		with open(filename, 'rU') as csvfile:
			fileReader = csv.reader(csvfile, dialect=csv.excel)
			count = 0
			
		# read each row of the csv file, the first and second rows are 
		# headers and types respectively
			for row in fileReader:
				if count == 0:
					for header in row: 
						self.raw_headers.append(header.strip()) # get rid of whitespace
					# print self.raw_headers
				elif count == 1:
					for type in row:
						self.raw_types.append(type.strip()) # get rid of whitespace
					# print self.raw_types
				else:
					# print row
					self.raw_data.append(row)
				count += 1
			#print self.raw_data
			
		# map index number to each header string
			for index in range(len(self.raw_headers)):
				self.header2raw[self.raw_headers[index]] = index
			#print self.header2raw
			
			key = -1
			for colIndex in range(len(self.raw_headers)):
				if self.raw_types[colIndex] == "enum":
					for rowIndex in range(self.get_raw_num_rows()):
						if self.enum2numeric.get(self.get_raw_value(rowIndex, self.raw_headers[colIndex])) == None:
							key += 1
							self.enum2numeric[self.get_raw_value(rowIndex, self.raw_headers[colIndex])] = key
					key = -1
			#print self.enum2numeric
							
			
		# convert string data to numeric form in the numeric data set and store in np matrix 
		# also map header string to index of column in matrix data
			ret = []
			matrixIndex = 0
			# loop through all columns
			for colIndex in range(self.get_raw_num_columns()):
				# check if column type is numeric
				if self.raw_types[colIndex] == "numeric":
					col = []
					# loop through all rows in numeric column
					for rowIndex in range(self.get_raw_num_rows()):
						# check and add value to temporary list
						if not self.check_if_numeric(self.get_raw_value(rowIndex, self.raw_headers[colIndex])):
# 							print self.get_raw_value(rowIndex, self.raw_headers[colIndex])
# 							print self.raw_headers[colIndex]
							col.append(float("NaN"))
						else:
							#print self.raw_headers[colIndex]
							col.append(float(self.get_raw_value(rowIndex, self.raw_headers[colIndex])))
					ret.append(col)
					
					# map header to matrix column index
					self.header2matrix[self.raw_headers[colIndex]] = matrixIndex
					# print ret
					matrixIndex += 1
					
# 				convert date into numeric data
				elif self.raw_types[colIndex] == "date":
					col = []
# 					loop through all rows in date column
					for rowIndex in range(self.get_raw_num_rows()):
						date = self.convert_date(self.get_raw_value(rowIndex, self.raw_headers[colIndex]))
						dt = datetime.datetime.strptime(date, "%m/%d/%Y")
						col.append(time.mktime(dt.timetuple()))
					ret.append(col)
					
					self.header2matrix[self.raw_headers[colIndex]] = matrixIndex
					
					matrixIndex += 1
				# convert enum into numeric data
				elif self.raw_types[colIndex] == "enum":
					self.enumHeaders.append(self.raw_headers[colIndex])
					col = []
					for rowIndex in range(self.get_raw_num_rows()):
						col.append(self.enum2numeric.get(self.get_raw_value(rowIndex, self.raw_headers[colIndex])))
					ret.append(col)
					
					self.header2matrix[self.raw_headers[colIndex]] = matrixIndex
										
					matrixIndex += 1
				
			# take transpose to make it into columns and convert elements into float
			self.matrix_data = np.matrix(ret).T.astype(np.float)
			
			# print self.raw_headers
# 			print self.raw_types
# 			
# 			print self.header2raw
# 			print self.numericalConvertedData
# 			print self.enum2numeric
# 			print "Raw Data 2D List\n", self.raw_data, "\n"
# 			print "Header to matrix dictionary\n", self.header2matrix, "\n"
# 			print "Numeric Data Matrix", self.matrix_data, "\n"
			

################## READ METHOD HELPER METHODS ############################################

	# use to check if data point is numeric
	def check_if_numeric(self, string):
		try:
			float(string)
			return True
		except ValueError:
			return False

	# convert 'month/day/year(2 digit)' to 'month/day/year(4 digit)'
	def convert_date(self, date):
		splitDate = date.split('/')
		if int(splitDate[2]) <= 17:
			splitDate[2] = "20" + splitDate[2]
		elif int(splitDate[2]) > 17:
			splitDate[2] = "19" + splitDate[2]
		return splitDate[0] + "/" + splitDate[1] + "/" + splitDate[2]
		

############## RAW DATA METHODS ##########################################################

	# returns a list of header strings
	def get_raw_headers(self):
		return self.raw_headers
	
	# returns a list of data types of each column
	def get_raw_types(self):
		return self.raw_types
	
	# returns number of columns
	def get_raw_num_columns(self):
		return len(self.raw_headers)
		
	# returns number of rows in the raw data set
	def get_raw_num_rows(self):
		return len(self.raw_data)
	
	# returns a row of data (the type is list) given a row index (int)
	def get_raw_row(self, rowIndex):
		return self.raw_data[rowIndex]
	
	# takes a row index (an int) and column header (a string) and returns the raw data at 
	# that location. (The return type will be a string) 
	def get_raw_value(self, rowIndex, colHeader):
		return self.raw_data[rowIndex][self.header2raw.get(colHeader)]

	# prints out all accessor methods for raw data
	def print_raw_data_info(self, row=0, colHeader="Age"):
		print "List of header strings:\n", self.get_raw_headers()
		print "List of data types:\n", self.get_raw_types()
		print "Number of columns:\n", self.get_raw_num_columns()
		print "Number of rows in data set:\n", self.get_raw_num_rows()
		print "Row data at row %d:\n" % (row+1), self.get_raw_row(row)
		print "Raw data at row ", row, " at ", colHeader, ":\n", self.get_raw_value(13, colHeader)

############## NUMERIC DATA METHODS ######################################################

	# returns list of headers of columns with numeric data
	def get_headers(self):
		ret = []
		for key in sorted(self.header2matrix, key=self.header2matrix.get): # need to sort the dictionary by the col index (value)
			ret.append(key)
		return ret
	
	# returns list of headers that are enums
	def get_enums(self):
		ret = []
		for key in sorted(self.enum2numeric, key=self.enum2numeric.get):
			ret.append(key)
		return ret
	
	# returns the number of columns of numeric data
	def get_num_columns(self):
		return len(self.header2matrix)
	
	# returns a row of numeric data given a row index 
	def get_row(self, rowIndex):
		return self.matrix_data[rowIndex, :]
	
	# returns the data in the numeric matrix given a row index (int) and column header (string)
	def get_value(self, rowIndex, colHeader):
		return self.matrix_data[rowIndex, self.header2matrix.get(colHeader)]
	
	# returns a matrix with the data for all rows but just the specified columns given a list of columns headers
	def get_data(self, colHeaders):
		cols = []
		for header in colHeaders:
			cols.append(self.header2matrix.get(header))
		return self.matrix_data[:, cols]

	# prints out all accessor methods for numeric data
	def print_numeric_data_info(self, rowIndex=5, colHeader="Age", colHeaders=["Age"]):
		print "List of headers of columns with numeric data:\n", self.get_headers()
		print "Number of columns of numeric data:\n", self.get_num_columns()
		print "Row of numeric data at row %d\n" % (rowIndex), self.get_row(rowIndex)
		print "Data in the numeric matrix at row ", (rowIndex), " and ", colHeader, "\n", self.get_value(rowIndex, colHeader) 
		print "Matrix with the data for all rows but columns of ", colHeaders, "\n",self.get_data(colHeaders)
		
##########################################################################################
	
	# add an additional column to raw data and if the type is numeric, also to numeric data matrix
	def addColumn(self, dataColumn):
		count = 0
		data = []
		duplicate = False
		header = ""
		for row in dataColumn:
			if count == 0:
				if row in self.raw_headers:
					header = row
					duplicate = True
				else:
					self.raw_headers.append(row.strip())
					self.header2raw[row.strip()] = len(self.raw_headers) - 1
			elif count == 1:
				if duplicate:
					self.raw_types[self.header2raw.get(header)] = row.strip()
				else:
					self.raw_types.append(row.strip())
			else:
				if duplicate:
					self.raw_data[self.header2raw.get(header)] = row
				else:
					self.raw_data[count - 2].append(row)
			count += 1
# 		print self.raw_data
# 		print self.header2raw
		# if type is numeric, add to numeric data matrix
		if dataColumn[1] == "numeric":
			if duplicate:
				return 
			ret = []
			col = []
			for rowIndex in range(self.get_raw_num_rows()):
				# check and add value to temporary list
				if not self.check_if_numeric(self.get_raw_value(rowIndex, dataColumn[0])):
					col.append(float("NaN"))
				else:
					col.append(float(self.get_raw_value(rowIndex, dataColumn[0])))
			ret.append(col)
				
				# map header to matrix column index
			self.header2matrix[dataColumn[0]] = self.matrix_data.shape[1]
				# print ret
			newColumn = np.matrix(ret).T.astype(np.float)
			self.matrix_data = np.hstack([self.matrix_data, newColumn])
			
# 		print self.matrix_data 
# 		print self.header2matrix


	def writeToCSV(self, filename, headers):
		with open(filename+'.csv', "wb") as csv_file:
			writer = csv.writer(csv_file, delimiter=',')
			
			writer.writerow(headers)
			
			for row in range(self.matrix_data.shape[0]):
				writer.writerow(self.matrix_data[row,:].tolist()[0])
			
			
		
if __name__ == "__main__":
	dapp = Data("AustraliaCoast.csv")
	dapp.writeToCSV("hey", ["jhaha","jaja"])
	
# 	print dapp.matrix_data
# 	print dapp.enumHeaders
# 	print dapp.get_data(dapp.enumHeaders)
#	dapp.addColumn(["thing4", "numeric", "96","48","16","26","14","11","43","24.5","-3", "23","445","21","34", "12"])
# 	dapp.print_raw_data_info()
# 	dapp.print_numeric_data_info()

	# print dapp.get_headers()
#	print dapp.get_num_columns()
#	print dapp.get_row(0) 
#	print dapp.get_value(0, 'numberstuff') 
#	print dapp.get_data(['numberstuff', 'datestuff'])
