# Tatsuya Yokota
# display.py
# A GUI made by using Tkinter

import Tkinter as tk
import tkFont as tkf
import tkSimpleDialog
import tkFileDialog
import subprocess
import os
import math
import random
import numpy as np
import scipy.stats
import Dialog as Dialog
from view import view
from data import Data
import analysis
import time
import csv

# create a class to build and manage the display
class DisplayApp():

	def __init__(self, width, height):
		self.view = view()
		
		# create axis by making two end points for each axes
		self.x1 = np.matrix([[0, 0, 0, 1]])
		self.x2 = np.matrix([[1, 0, 0, 1]])
		self.y1 = np.matrix([[0, 0, 0, 1]])
		self.y2 = np.matrix([[0, 1, 0, 1]])
		self.z1 = np.matrix([[0, 0, 0, 1]])
		self.z2 = np.matrix([[0, 0, 1, 1]])
		
		self.rotX = 0
		self.rotY = 0
		
		# graphical objects associated with a linear regression
		self.linRegObjs = []
		
		# independent and dependent variables for linear regression
		self.indepVar = None
		self.depVar = None
		
		# endpoints of the regression line in normalized data space
		self.linRegEndPoints = None
		
		# dictionary to store all PCA 
		self.PCA = {}
		
		# list to hold the actual graphics line objects that instantiate on the screen
		self.graphicLineObjs = []
		
		# create a tk object, which is the root window
		self.root = tk.Tk()

		# width and height of the window
		self.initDx = width
		self.initDy = height
		
		# optionMenu var reference
		self.var = ''
		
		self.distribution = ''
		
		# mouse position variables
		self.xPos = None 
		self.yPos = None
		self.mousePos = ''
		
		# data point size
		self.dx = 2
		self.dy = 2
		
		self.colors = []
		# set up the geometry for the window
		self.root.geometry( "%dx%d+50+30" % (self.initDx, self.initDy) )

		# set the title of the window
		self.root.title("FETA")

		# set the maximum size of the window for resizing
		self.root.maxsize( 1600, 900 )

		# setup the menus
		self.buildMenus()

		# build the controls
		self.buildDataControls()
		self.buildControls()
		
		# build the Canvas
		self.buildCanvas()

		# bring the window to the front
		self.root.lift()

		# - do idle events here to get actual canvas size
		self.root.update_idletasks()

		# now we can ask the size of the canvas
# 		print self.canvas.winfo_geometry()

		# set up the key bindings
		self.setBindings()

		# set up the application state
		self.objects = [] # list of data objects that will be drawn in the canvas
		self.data = None # will hold the raw data someday.
		self.baseClick = None # used to keep track of mouse movement
		self.baseClick2 = None
		
		self.numDataPoints = 100
		
		self.number = ""
		
		self.gaussPoint = [0,0]
		
		self.data = None
		self.dataMatrix = None
		
		# axes labels
		self.xName = "X"
		self.yName = "Y"
		self.zName = "Z"
		
		self.buildAxes()
		self.updateAxes()
		
	
	# creates three line objects, using the vtm
	def buildAxes(self):
		vtm = self.view.build()
		
		# set end points using vtm
		x1pt = (vtm * self.x1.T).T
		x2pt = (vtm * self.x2.T).T
		y1pt = (vtm * self.y1.T).T
		y2pt = (vtm * self.y2.T).T
		z1pt = (vtm * self.z1.T).T
		z2pt = (vtm * self.z2.T).T
		
		# create label objects for the axes
		self.xLabel = tk.Label(self.canvas, text=self.xName)
		self.yLabel = tk.Label(self.canvas, text=self.yName)
		self.zLabel = tk.Label(self.canvas, text=self.zName)
		
		# place the label objects at the second end point of each axes
		self.xLabel.place(x=x2pt[0,0], y=x2pt[0,1]) 
		self.yLabel.place(x=y2pt[0,0], y=y2pt[0,1]) 
		self.zLabel.place(x=z2pt[0,0], y=z2pt[0,1]) 
		
# 		print "x1pt is ", x1pt
# 		print "x2pt is ", x2pt
# 		print "y1pt is ", y1pt
# 		print "y2pt is ", y2pt
# 		print "z1pt is ", z1pt
# 		print "z2pt is ", z2pt
		
		# create three new line objects, one for each axis
		xAxis = self.canvas.create_line(x1pt[0,0], x1pt[0,1], x2pt[0,0], x2pt[0,1], tags=("x"), fill='green')
		yAxis = self.canvas.create_line(y1pt[0,0], y1pt[0,1], y2pt[0,0], y2pt[0,1], tags=("y"), fill='red')
		zAxis = self.canvas.create_line(z1pt[0,0], z1pt[0,1], z2pt[0,0], z2pt[0,1], tags=("z"), fill='blue')
		
		self.objects.append(xAxis)
		self.objects.append(yAxis)
		self.objects.append(zAxis)
	
	def buildPoints(self, headerList):
		# delete any canvas objects that represent data
		for dataPoint in self.canvas.find_withtag("dataPoint"):
			self.canvas.delete(dataPoint)
		
		# build vtm
		vtm = self.view.build()
		
		# get the color axis
		colorAxis = self.colorAxis.get()
		
		# get the size axis
		sizeAxis = self.sizeAxis.get()
		
		# get the shape axis
		shapeAxis = self.shapeAxis.get()
		
		#  normalize the data
		self.dataMatrix = analysis.normalize_columns_separately(headerList, self.data)
		
		# normalize the color Axis
		if colorAxis != "":
			if len(self.colors) != 0:
				colorVals = self.colors
			else:
				colorVals =	 analysis.normalize_columns_separately([colorAxis], self.data)
		

			
		
		# normalize the size axis
		if sizeAxis != "":
			sizeVals =	analysis.normalize_columns_separately([sizeAxis], self.data)
		
#		get the shape axis values
		if shapeAxis != "":
			shapeVals = self.data.get_data([shapeAxis])
#		
# 		print self.dataMatrix
		
		
		# Get the spatial (x, y, z) columns specified by the argument headers to plot.
		if len(headerList) == 2:
			zeroCol = np.asmatrix(np.zeros(self.dataMatrix.shape[0])).T
			oneCol = np.asmatrix(np.ones(self.dataMatrix.shape[0])).T
			self.dataMatrix = np.hstack([self.dataMatrix, zeroCol])
			self.dataMatrix = np.hstack([self.dataMatrix, oneCol])
		if len(headerList) == 3:
			oneCol = np.asmatrix(np.ones(self.dataMatrix.shape[0])).T
			self.dataMatrix = np.hstack([self.dataMatrix, oneCol])
		
		
# 		print self.dataMatrix
		
		self.sizeList = []
		self.triangleIndices = []
		for i in range(self.dataMatrix.shape[0]):
			point = (vtm * self.dataMatrix[i,:].T).T
			
			# set the color
			if colorAxis != "":
				# r = 255*(1-dtpoint), g = 255*dtpoint, b = 255*(1 - dtpoint)
				tk_rgb = "#%02x%02x%02x" % (255*(1- colorVals[i]), 255*colorVals[i], 255*(1 - colorVals[i]))
			else:
				tk_rgb = "#%02x%02x%02x" % (0,0,0)
			
			# set the size
			if sizeAxis != "":
				dif = int(sizeVals[i] * 5 + 5)
				self.sizeList.append(dif)
			else:
				dif = 5
				self.sizeList.append(dif)
			
			# create the dataPoint obj.
			if shapeAxis != "":
				if shapeVals[i] == 0:
					dataPoint = self.canvas.create_oval(point[0,0] - dif, point[0,1] - dif, point[0,0] + dif, point[0,1] + dif, 
											fill=tk_rgb, tags=("dataPoint"))
				elif shapeVals[i] == 1:
					dataPoint = self.canvas.create_rectangle(point[0,0] - dif, point[0,1] - dif, point[0,0] + dif, point[0,1] + dif, 
											fill=tk_rgb, tags=("dataPoint"))
				else:
					dataPoint = self.canvas.create_polygon(point[0,0] - dif, point[0,1], point[0,0] + dif, point[0,1], 
											point[0,0], point[0,1]+math.sqrt((2*dif)**2-(dif)**2),fill=tk_rgb, tags=("dataPoint"))
					self.triangleIndices.append(i)
#			x, y-3.4, x-dx, y, x+dx, y,
			else:
				if len(self.colors) != 0:
					clusterid = int(self.data.get_data(["cluster"])[i])
# 					print "cluster",clusterid
# 					print len(self.colors)
					dataPoint = self.canvas.create_oval(point[0,0] - dif, point[0,1] - dif, point[0,0] + dif, point[0,1] + dif, 
													fill=self.colors[clusterid], tags=("dataPoint"))
				else:
					dataPoint = self.canvas.create_oval(point[0,0] - dif, point[0,1] - dif, point[0,0] + dif, point[0,1] + dif, 
													fill=tk_rgb, tags=("dataPoint"))
			
			self.objects.append(dataPoint)
	
	def buildLinearRegression(self):
		yDataHeader = self.depVar	
		xDataHeader = self.indepVar
		
# 		print "x: ", xDataHeader 
# 		print "y: ", yDataHeader
		
		self.xLabel.config(text=xDataHeader)
		self.yLabel.config(text=yDataHeader)
			
		self.buildPoints([xDataHeader, yDataHeader])
		
		vtm = self.view.build()
		
		# make each column a numpy array 
		xCol = np.squeeze(np.asarray(self.data.get_data([xDataHeader])))
		yCol = np.squeeze(np.asarray(self.data.get_data([yDataHeader])))
		
# 		print xCol
# 		print yCol
		
		self.slope, self.intercept, self.r_value, self.p_value, self.std_err = scipy.stats.linregress(xCol, yCol)
# 		print self.slope
# 		print self.intercept
# 		print self.r_value
# 		print self.p_value
# 		print self.std_err
		
		# get the range 
		self.range = analysis.data_range([xDataHeader, yDataHeader], self.data)
		self.xMin = self.range[0,0]
		self.xMax = self.range[0,1]
		self.yMin = self.range[1,0]
		self.yMax = self.range[1,1]
# 		print self.range
		
		# create endpoints
		self.fitPoint1 = np.matrix([[0.0, ((self.xMin * self.slope + self.intercept) - self.yMin)/(self.yMax - self.yMin),
								0,1]])
	
		self.fitPoint2 = np.matrix([[1.0, ((self.xMax * self.slope + self.intercept) - self.yMin)/(self.yMax - self.yMin),
								0,1]])

		linPoint1 = (vtm * self.fitPoint1.T).T
		linPoint2 = (vtm * self.fitPoint2.T).T
		
		# draw the line
		linRegLine = self.canvas.create_line(linPoint1[0,0], linPoint1[0,1], linPoint2[0,0], linPoint2[0,1],
											fill="red", tags=("regressionLine"))
		

	def updatePoints(self):
		# do nothing if there are no data point objects
		if len(self.canvas.find_withtag("dataPoint")) == 0:
			return
		
		vtm = self.view.build()
		
# 		print self.dataMatrix.shape[0]
# 		print len(self.canvas.find_withtag("dataPoint"))
		
		for i in range(self.dataMatrix.shape[0]):
			point = (vtm * self.dataMatrix[i].T).T
			dif = self.sizeList[i]
			if i in self.triangleIndices:
				self.canvas.coords( self.canvas.find_withtag("dataPoint")[i],
								point[0,0] - dif, point[0,1], point[0,0] + dif, point[0,1], 
											point[0,0], point[0,1]+math.sqrt((2*dif)**2-(dif)**2))
			else: 
				self.canvas.coords( self.canvas.find_withtag("dataPoint")[i],
								point[0,0] - dif, point[0,1] - dif, point[0,0] + dif, point[0,1] + dif)
		
	
	def updateAxes(self):
		# build the VTM
		vtm = self.view.build()
		
		# multiply the axis endpoints by the VTM
		x1pt = (vtm * self.x1.T).T
		x2pt = (vtm * self.x2.T).T
		y1pt = (vtm * self.y1.T).T
		y2pt = (vtm * self.y2.T).T
		z1pt = (vtm * self.z1.T).T
		z2pt = (vtm * self.z2.T).T
		
		self.xLabel.place(x=x2pt[0,0], y=x2pt[0,1]) 
		self.yLabel.place(x=y2pt[0,0], y=y2pt[0,1]) 
		self.zLabel.place(x=z2pt[0,0], y=z2pt[0,1]) 
		
		# for each line object
		# update the coordinates of the object
		xAxis = self.canvas.find_withtag("x")[0]
		yAxis = self.canvas.find_withtag("y")[0]
		zAxis = self.canvas.find_withtag("z")[0]
		 
		self.canvas.coords( xAxis, 
			  x1pt[0,0], 
			  x1pt[0,1], 
			  x2pt[0,0], 
			  x2pt[0,1])
		self.canvas.coords( yAxis, 
			  y1pt[0,0], 
			  y1pt[0,1], 
			  y2pt[0,0], 
			  y2pt[0,1])
		self.canvas.coords( zAxis, 
			  z1pt[0,0], 
			  z1pt[0,1], 
			  z2pt[0,0], 
			  z2pt[0,1])
		
#		print "x1pt is ", x1pt
#		print "x2pt is ", x2pt
#		print "y1pt is ", y1pt
#		print "y2pt is ", y2pt
#		print "z1pt is ", z1pt
#		print "z2pt is ", z2pt
	
	def updateFits(self):
		# do nothing if there are no data point objects
		if len(self.canvas.find_withtag("regressionLine")) == 0:
			return
		
		# build the VTM
		vtm = self.view.build()
		
		linPoint1 = (vtm * self.fitPoint1.T).T
		linPoint2 = (vtm * self.fitPoint2.T).T
		
		fitLine = self.canvas.find_withtag("regressionLine")[0]
		
		self.canvas.coords( fitLine, 
			  linPoint1[0,0], 
			  linPoint1[0,1], 
			  linPoint2[0,0], 
			  linPoint2[0,1])
	
	def buildMenus(self):
		
		# create a new menu
		menu = tk.Menu(self.root)

		# set the root menu to our new menu
		self.root.config(menu = menu)

		# create a variable to hold the individual menus
		menulist = []

		# create a file menu
		filemenu = tk.Menu( menu )
		menu.add_cascade( label = "File", menu = filemenu )
		menulist.append(filemenu)

		# create another menu for kicks
		cmdmenu = tk.Menu( menu )
		menu.add_cascade( label = "Command", menu = cmdmenu )
		menulist.append(cmdmenu)

		# menu text for the elements
		# the first sublist is the set of items for the file menu
		# the second sublist is the set of items for the option menu
		menutext = [ [ 'Open New Window \xE2\x8C\x98-N', 'Open File \xE2\x8C\x98-O', 'Quit	\xE2\x8C\x98-Q'],
					 [ 'Plot Linear Regression \xE2\x8C\x98-L', 'PCA \xE2\x8C\x98-P', 'Cluster \xE2\x8C\x98-K','Screenshot of Plot \xE2\x8C\x98-I' ] ]

		# menu callback functions (note that some are left blank,
		# so that you can add functions there if you want).
		# the first sublist is the set of callback functions for the file menu
		# the second sublist is the set of callback functions for the option menu
		menucmd = [ [self.handleOpenNewWindow, self.handleOpen, self.handleQuit],
					[ self.handleLinearRegression, self.handlePCA, self.handleCluster, self.generate_pdf] ]
		
		# build the menu elements and callbacks
		for i in range( len( menulist ) ):
			for j in range( len( menutext[i]) ):
				if menutext[i][j] != '-':
					menulist[i].add_command( label = menutext[i][j], command=menucmd[i][j] )
				else:
					menulist[i].add_separator()

	# create the canvas object
	def buildCanvas(self):
		self.canvas = tk.Canvas( self.root, width=self.initDx, height=self.initDy )
		self.canvas.pack( expand=tk.YES, fill=tk.BOTH )
		return

	# build a frame and put controls in it
	def buildControls(self):

		### Control ###
		# make a control frame on the right
		rightcntlframe = tk.Frame(self.root)
		rightcntlframe.pack(side=tk.RIGHT, padx=2, pady=2, fill=tk.Y)

		# make a separator frame
		sep = tk.Frame( self.root, height=self.initDy, width=2, bd=1, relief=tk.SUNKEN )
		sep.pack( side=tk.RIGHT, padx = 2, pady = 2, fill=tk.Y)

		# use a label to set the size of the right panel
		label = tk.Label( rightcntlframe, text="Control Panel", width=20 )
		label.pack( side=tk.TOP, pady=10 )
		
		label = tk.Label( rightcntlframe, text="Translation Speed", width=20 )
		label.pack( side=tk.TOP, pady=10 )
		
		# option menu for setting the translation constant
		self.transConst = tk.StringVar(rightcntlframe)
		self.transConst.set("normal")
		transConstOption = tk.OptionMenu(rightcntlframe, self.transConst, "slow", "normal", "fast")
		transConstOption.pack(side=tk.TOP)
		
		label = tk.Label( rightcntlframe, text="Rotation Speed", width=20 )
		label.pack( side=tk.TOP, pady=10 )
		
		# option menu for setting the rotation constant
		self.rotConst = tk.StringVar(rightcntlframe)
		self.rotConst.set("normal")
		rotConstOption = tk.OptionMenu(rightcntlframe, self.rotConst, "slow", "normal", "fast")
		rotConstOption.pack(side=tk.TOP)
		
		
		xLabel = tk.Label( rightcntlframe, text="X-Axis", width=20 )
		xLabel.pack( side=tk.TOP, pady=2 )
		
		# option menu for setting the x-Axis selection
		self.xAxis = tk.StringVar(rightcntlframe)
		self.xAxisOption = tk.OptionMenu(rightcntlframe, self.xAxis, "")
		self.xAxisOption.config(width=15)
		self.xAxisOption.pack(side=tk.TOP)
		
		yLabel = tk.Label( rightcntlframe, text="Y-Axis", width=20 )
		yLabel.pack( side=tk.TOP, pady=2 )
		
		# option menu for setting the y-Axis selection
		self.yAxis = tk.StringVar(rightcntlframe)
		self.yAxisOption = tk.OptionMenu(rightcntlframe, self.yAxis, "")
		self.yAxisOption.config(width=15)
		self.yAxisOption.pack(side=tk.TOP)
		
		zLabel = tk.Label( rightcntlframe, text="Z-Axis", width=20 )
		zLabel.pack( side=tk.TOP, pady=2 )
		
		# option menu for setting the z-Axis selection
		self.zAxis = tk.StringVar(rightcntlframe)
		self.zAxisOption = tk.OptionMenu(rightcntlframe, self.zAxis, "")
		self.zAxisOption.config(width=15)
		self.zAxisOption.pack(side=tk.TOP)
		
		colorLabel = tk.Label( rightcntlframe, text="Color Axis", width=20 )
		colorLabel.pack( side=tk.TOP, pady=2 )
		
		# option menu for setting the color-Axis selection
		self.colorAxis = tk.StringVar(rightcntlframe)
		self.colorAxisOption = tk.OptionMenu(rightcntlframe, self.colorAxis, "")
		self.colorAxisOption.config(width=15)
		self.colorAxisOption.pack(side=tk.TOP)
		
		sizeLabel = tk.Label( rightcntlframe, text="Size Axis", width=20 )
		sizeLabel.pack( side=tk.TOP, pady=2 )
		
		# option menu for setting the size-Axis selection
		self.sizeAxis = tk.StringVar(rightcntlframe)
		self.sizeAxisOption = tk.OptionMenu(rightcntlframe, self.sizeAxis, "")
		self.sizeAxisOption.config(width=15)
		self.sizeAxisOption.pack(side=tk.TOP)
		
		shapeLabel = tk.Label( rightcntlframe, text="Shape Axis", width=20 )
		shapeLabel.pack( side=tk.TOP, pady=2 )
		
		# option menu for setting the size-Axis selection
		self.shapeAxis = tk.StringVar(rightcntlframe)
		self.shapeAxisOption = tk.OptionMenu(rightcntlframe, self.shapeAxis, "")
		self.shapeAxisOption.config(width=15)
		self.shapeAxisOption.pack(side=tk.TOP)
		
		plotDataButton = tk.Button( rightcntlframe, text="Plot Data", 
							   command=self.handlePlotData )
		plotDataButton.pack(side=tk.TOP)
		
		self.mousePos = tk.StringVar(rightcntlframe)
		
# 		self.dataPointLabel = tk.Label( rightcntlframe, text="Data Point: ", width=10 )
# 		self.dataPointLabel.pack( side=tk.TOP, pady=10 )
		
		
		return
		
	# build a frame and put controls in it
	def buildDataControls(self):

		### Control ###
		# make a control frame on the right
		cntlframe = tk.Frame(self.root)
		cntlframe.pack(side=tk.RIGHT, padx=2, pady=2, fill=tk.Y)

		# make a separator frame
		sep = tk.Frame( self.root, height=self.initDy, width=2, bd=1, relief=tk.SUNKEN )
		sep.pack( side=tk.RIGHT, padx = 2, pady = 2, fill=tk.Y)

		# use a label to set the size of the right panel
		label = tk.Label( cntlframe, text="Data Control Panel", width=20 )
		label.pack( side=tk.TOP, pady=10 )
		
		label = tk.Label( cntlframe, text="PCA", width=20 )
		label.pack( side=tk.TOP, pady=10 )
		
		self.pcaList = tk.Listbox(cntlframe, selectmode=tk.SINGLE, exportselection=0)
		self.pcaList.pack(side=tk.TOP, padx=5, pady=5)
		
		delete = tk.Button(cntlframe, text="Delete", width=10, command=lambda lb=self.pcaList: lb.delete(tk.ANCHOR))
		delete.pack(side=tk.TOP, padx=5, pady=5)
		
		selectPCA = tk.Button(cntlframe, text="Select PCA", width=10, command=self.showPCAData)
		selectPCA.pack(side=tk.TOP, padx=5, pady=5)
		
		plotPCA = tk.Button(cntlframe, text="Spatial Plot", width=10, command=self.plotPCA)
		plotPCA.pack(side=tk.TOP, padx=5, pady=5)
		
		exportPCA = tk.Button(cntlframe, text="Export to CSV", width=10, command=self.exportPCA)
		exportPCA.pack(side=tk.TOP, padx=5, pady=5)
		
	def setBindings(self):
		# bind mouse motions to the canvas
		self.canvas.bind( '<Button-1>', self.handleMouseButton1 )
		self.canvas.bind( '<Control-Button-1>', self.handleMouseButton2 )
		self.canvas.bind( '<Shift-Button-1>', self.handleMouseButton3 )
		self.canvas.bind( '<Button-2>', self.handleMouseButton2 )
		self.canvas.bind( '<Motion>', self.handleMouseMotion )
		self.canvas.bind( '<B1-Motion>', self.handleMouseButton1Motion )
		self.canvas.bind( '<B2-Motion>', self.handleMouseButton2Motion )
		self.canvas.bind( '<Control-B1-Motion>', self.handleMouseButton2Motion )
		self.canvas.bind( '<Shift-B1-Motion>', self.handleMouseButton3Motion )

		# bind command sequences to the root window
		self.root.bind( '<Command-q>', self.handleQuit )
		self.root.bind( '<Command-r>', self.handleResetToDefault )
		self.root.bind( '<Command-o>', self.handleOpen )
		self.root.bind( '<Command-n>', self.handleOpenNewWindow )
		self.root.bind( '<Command-i>', self.generate_pdf )
		self.root.bind( '<Command-l>', self.handleLinearRegression )
		self.root.bind( '<Command-p>', self.handlePCA )
		self.root.bind( '<Command-k>', self.handleCluster )

	def handleQuit(self, event=None):
		print 'Terminating'
		self.root.destroy()
		
	def handleResetToDefault(self, event=None):
		self.view.reset()
		self.updateAxes()
		self.updatePoints()
		self.updateFits()

	def handleButton1(self):
		for obj in self.objects:
			self.canvas.itemconfig(obj, fill=self.colorOption.get() )
# 		print 'handling command button:', self.colorOption.get()
	
	def handleXRot(self):
		self.view = self.viewCopy
		
		self.view.rotateVRC(0, math.pi/2)
		
		self.updateAxes()
		self.updatePoints()
		self.updateFits()
	
	def handleYRot(self):
		self.view = self.viewCopy
		
		self.view.rotateVRC(math.pi/2, 0)
		
		self.updateAxes()
		self.updatePoints()
		self.updateFits()
		
	def handleButton3(self):
		self.clearData(self)

	def handleMouseButton1(self, event):
		self.viewCopy = self.view.clone()
		self.baseClick = (event.x, event.y)

	def handleMouseButton2(self, event):
		self.baseClick = (event.x, event.y)
		self.extentCopy = self.view.clone().extent

	
	def handleMouseButton3(self, event):
		self.baseClick2 = (event.x, event.y)
		self.viewCopy = self.view.clone()
				
	
	def handleMouseMotion(self, event):
		self.xPos, self.yPos = event.x, event.y
		for pt in self.objects:
			# conditional assignment to solve the if statement check issue below
			loc = self.canvas.coords(pt) if self.canvas.coords(pt) != [] else None
			if loc != None and self.xPos >= loc[0] and self.yPos >= loc[1] and self.xPos <= loc[2] and self.yPos <= loc[3]:
				self.mousePos.set(str(loc[0]+self.dx) + ', ' + str(loc[1]+self.dy))
# 				self.dataPointLabel.config(text="Data Point: "+str(loc[0]+self.dx) + ', ' + str(loc[1]+self.dy), width=20)
#				print self.mousePos.get()
	
	# This is called if the first mouse button is being moved
	def handleMouseButton1Motion(self, event):
		# Calculate the differential motion since the last time the function was called
		diff = ( float(event.x - self.baseClick[0]), float(event.y - self.baseClick[1]) )
		
		# Divide the differential motion (dx, dy) by the screen size (view X, view Y)
		diff = (diff[0]/float(self.canvas.winfo_width()), diff[1]/float(self.canvas.winfo_height()))
		
		# check the option menu and set translation constant
		if self.transConst.get() == "slow":
			transConst = 100
		elif self.transConst.get() == "normal":
			transConst = 10
		elif self.transConst.get() == "fast":
			transConst = 5
		
		# Multiply the horizontal and vertical motion by the horizontal and vertical extents.
		# Put the result in delta0 and delta1
		delta0 = diff[0] * self.view.extent[0, 0]
		delta1 = diff[1] * self.view.extent[0, 1]
		
		
		# The VRP should be updated by delta0 * U + delta1 * VUP (this is a vector equation)
		# call updateAxes()
#		self.view = self.viewCopy
		
		self.view.vrp += delta0 * self.view.u + delta1 * self.view.vup
		self.updateAxes()
		self.updatePoints()
		self.updateFits()
		
		self.baseClick = (event.x, event.y)
		
		# print "this is the window size"
#		print self.canvas.winfo_height()
#		print self.canvas.winfo_width()
		
#		print 'handle button1 motion %d %d' % (diff[0], diff[1])

			
	# This is called if the second button of a real mouse has been pressed
	# and the mouse is moving. Or if the control key is held down while
	# a person moves their finger on the track pad.
	def handleMouseButton2Motion(self, event):
		yPercentage = (float(event.y) - float(self.baseClick[1]))/self.canvas.winfo_height()
		
		# when mouse is below original point, scale between 0.1 and 1.0
		if yPercentage >= 0:
			if yPercentage > 1.0:
				scalingFactor = 0.1
			else:
				scalingFactor = -0.9*yPercentage + 1.0
		# when mouse is above original point, scale between 1.0 and 3.0
		elif yPercentage < 0:
			if yPercentage < -1.0:
				scalingFactor = 3.0
			else:
				scalingFactor = -2.0*yPercentage + 1.0
# 		print yPercentage
# 		print scalingFactor 
		
		self.view.extent = self.extentCopy * scalingFactor
# 		print self.view.extent
		self.updateAxes()
		self.updatePoints()
		self.updateFits()
		# print yPercentage
#		print "scaling factor ", scalingFactor

	
	def handleMouseButton3Motion(self, event):
		# check the option menu and set rotation constant
		if self.rotConst.get() == "slow":
			rotConst = 300
		elif self.rotConst.get() == "normal":
			rotConst = 200
		elif self.rotConst.get() == "fast":
			rotConst = 100
		
		delta0 = float(event.x - self.baseClick2[0])/(0.5*self.canvas.winfo_width())*math.pi
		delta1 = float(event.y - self.baseClick2[1])/(0.5*self.canvas.winfo_width())*math.pi
		
		
		self.rotX += delta0
		self.rotY += delta1
		
# 		print delta0
# 		print delta1
		
		self.view = self.viewCopy.clone()
		
		self.view.rotateVRC(delta0, delta1)
		
		self.updateAxes()
		self.updatePoints()
		self.updateFits()
	
	def createRandomDataPoints( self, event=None ):
		
		for i in range(self.numDataPoints):
			# random uniform distribution
#			print self.distribution.get()
			if self.distribution.get() == "Uniform":
				x = random.randint(0, 1200)
				y = random.randint(0, 675)
			elif self.distribution.get() == "Gaussian":
				x = round(np.random.normal(self.gaussPoint[0], 50),0)
				y = round(np.random.normal(self.gaussPoint[1], 50),0)
			dx = self.dx
			dy = self.dy
			option = self.var.get()
			pt = None
			if option == "circle":
				pt = self.canvas.create_oval( x-dx, y-dx, x+dx, y+dx,
										fill=self.colorOption.get(), outline='' )
			elif option == "square":
				pt = self.canvas.create_rectangle( x-dx, y-dx, x+dx, y+dx,
										fill=self.colorOption.get(), outline='' )
			elif option == "triangle":
				pt = self.canvas.create_polygon( x, y-3.4, x-dx, y, x+dx, y,
										fill=self.colorOption.get(), outline='' )
			self.objects.append(pt)
	
	def handleSetGaussianPoint(self, event):
		self.gaussPoint[0], self.gaussPoint[1] = event.x, event.y
		self.gaussPointLabel.config(text="Gauss. Mean Point: "+str(self.gaussPoint[0]) + ', ' + str(self.gaussPoint[1]), width=20)
#		print self.gaussPoint
	
	# use the tkFileDialog module to let the user select the csv file they want to open
	def handleOpen(self, event=None):
		fn = tkFileDialog.askopenfilename( parent=self.root,
											title='Choose a data file', initialdir='.' )
		self.data = Data(fn)
		self.headers = self.data.get_headers()
		
		# do not want to use shapes other than square, circle, and triangle because it gets 
		# hard to differentiate after a certain point, thus, limiting the enums that the 
		# user can choose 
		self.enumHeaders = []
		for header in self.data.enumHeaders:
# 			print self.data.get_data([header]).max()
			if self.data.get_data([header]).max() <= 3:
				self.enumHeaders.append(header)
		self.handleChooseAxes()
		# set the option menu to the first header col. when opening a file
		self.xAxis.set("")
		self.yAxis.set("")
		self.zAxis.set("")
		self.colorAxis.set("")
	
	def handleOpenNewWindow(self, event=None):
		dapp = DisplayApp(1200, 675)
		dapp.handleOpen()
		dapp.main()
	
	def handlePlotData(self, event=None):
# 		print "handling"
		# z-axes is optional 
		if	self.zAxis.get() == "":
			axes = [self.xAxis.get(), self.yAxis.get()]
			self.xLabel.config(text=axes[0])
			self.yLabel.config(text=axes[1])
		else:
			axes = [self.xAxis.get(), self.yAxis.get(), self.zAxis.get()]
			self.xLabel.config(text=axes[0])
			self.yLabel.config(text=axes[1])
			self.zLabel.config(text=axes[2])
# 		print axes
		
		self.gradLabel = tk.Label(self.canvas, text="Color Axis Measure")
		self.minLabel = tk.Label(self.canvas, text="0")
		self.maxLabel = tk.Label(self.canvas, text="1")
		
		if self.colorAxis.get() != "":
			self.drawGradient( self.canvas, self.canvas.winfo_width() - 150, 35, 100, 50 )
			self.gradLabel.place(x=self.canvas.winfo_width() - 155, y=12) 
			self.minLabel.place(x=self.canvas.winfo_width() - 155, y=87) 
			self.maxLabel.place(x=self.canvas.winfo_width() - 55, y=87)
		else:
			for gradLine in self.canvas.find_withtag("gradient"):
				self.canvas.delete(gradLine)
# 			print self.canvas.find_withtag("gradient")
			self.gradLabel.pack_forget()
			self.minLabel.pack_forget()
			self.maxLabel.pack_forget()
		
		self.canvas.delete("regressionLine")
		self.buildPoints(axes)
	
	# helper function to draw gradient line
	def drawGradient(self, canvas, x, y, w, h):
		w = float(w)
		for offset in range(0, int(w)):
			gradColor = '#%02x%02x%02x' % (int((w-offset)/w*255), int(offset/w*255), int((w-offset)/w*255))
			canvas.create_line(x + offset, y, x + offset, y + h, fill=gradColor, tags="gradient")
	
	def handleChooseAxes(self, event=None):
		ret = []
		# for header in self.data.get_headers():
#			if len(ret) == 3:
#				break
#			ret.append(header)
#		print ret
#		self.headers = ret


		self.xAxisOption['menu'].delete(0, "end")
		self.yAxisOption['menu'].delete(0, "end")
		self.zAxisOption['menu'].delete(0, "end")
		self.colorAxisOption['menu'].delete(0, "end")
		self.sizeAxisOption['menu'].delete(0, "end")
		self.shapeAxisOption['menu'].delete(0, "end")
		
		for header in self.headers:
			self.xAxisOption['menu'].add_command(label=header, command=lambda col=header: self.xAxis.set(col))
			self.yAxisOption['menu'].add_command(label=header, command=lambda col=header: self.yAxis.set(col))
			self.zAxisOption['menu'].add_command(label=header, command=lambda col=header: self.zAxis.set(col))
			self.colorAxisOption['menu'].add_command(label=header, command=lambda col=header: self.colorAxis.set(col))
			self.sizeAxisOption['menu'].add_command(label=header, command=lambda col=header: self.sizeAxis.set(col))
		self.zAxisOption['menu'].add_command(label="", command=lambda col="": self.zAxis.set(col))
		self.colorAxisOption['menu'].add_command(label="", command=lambda col="": self.colorAxis.set(col))
		self.sizeAxisOption['menu'].add_command(label="", command=lambda col="": self.sizeAxis.set(col))
		
		for header in self.enumHeaders:
			self.shapeAxisOption['menu'].add_command(label=header, command=lambda col=header: self.shapeAxis.set(col))
		self.shapeAxisOption['menu'].add_command(label="", command=lambda col="": self.shapeAxis.set(col))
		return ret
	
	def handleLinearRegression(self, event=None):
		dBox = DBox(self.root, self.headers)
		if dBox.canceled:
			return
		
		self.indepVar = self.headers[dBox.currentIndep[0]]
		self.depVar = self.headers[dBox.currentDep[0]]
		
		self.canvas.delete("dataPoint")
		self.canvas.delete("regressionLine")
		
		self.handleResetToDefault()
		
		self.buildLinearRegression()
		
# 		print self.indepVar
# 		print self.depVar
	
	def generate_pdf(self, event=None):
		# need to find current x position of origin
		vtm = self.view.build()
		x1pt = (vtm * self.x1.T).T[0,0]
		
		self.canvas.postscript(file="tmp.ps", colormode='color', x=x1pt-200)
		
		# run command line argument to convert ps to pdf
		process = subprocess.Popen(["ps2pdf13 tmp.ps result.pdf"], shell=True)

	def handlePCA(self, event=None):
		pBox = PCABox(self.root, self.headers)
		if pBox.canceled:
			return
		
		pcaVars = []
		for index in pBox.current:
# 			print index
			pcaVars.append(self.headers[index])
		
		if pBox.listName == '':
			pBox.listName = str(int(time.time()))
		
		self.PCA[pBox.listName] = analysis.pca(self.data, pcaVars)
		
		self.pcaList.insert(tk.END, pBox.listName)
		
# 		print self.PCA
		
		
	def showPCAData(self,event=None):
# 		print self.pcaList.get(tk.ACTIVE)
		pcaBox = PCADataBox(self.root, self.PCA.get(self.pcaList.get(tk.ACTIVE)))
		if pcaBox.canceled:
			return
	
	def plotPCA(self,event=None):
		# delete any canvas objects that represent data
		for dataPoint in self.canvas.find_withtag("dataPoint"):
			self.canvas.delete(dataPoint)
		
		self.data = self.PCA.get(self.pcaList.get(tk.ACTIVE))
		
		
		vtm = self.view.build()
		
		# get the color axis
		colorAxis = self.colorAxis.get()
		
		# get the size axis
		sizeAxis = self.sizeAxis.get()
		
		# get the shape axis
		shapeAxis = self.shapeAxis.get()
		
		# normalize the color Axis
		if colorAxis != "":
			colorVals =	 analysis.normalize_columns_separately([colorAxis], self.data)
			
		
		# normalize the size axis
		if sizeAxis != "":
			sizeVals =	analysis.normalize_columns_separately([sizeAxis], self.data)
		
#		get the shape axis values
		if shapeAxis != "":
			shapeVals = self.data.get_data([shapeAxis])
		
# 		print "headers"
# 		print self.data.get_PCA_headers()[:3]
		
		# normalize data
		self.dataMatrix = analysis.normalize_columns_separately(self.data.get_PCA_headers()[:3], self.data)
		
# 		print self.data.get_PCA_headers()[:3]
		
# 		print self.dataMatrix
		
		oneCol = np.asmatrix(np.ones(self.dataMatrix.shape[0])).T
		self.dataMatrix = np.hstack([self.dataMatrix, oneCol])
		
# 		print self.dataMatrix
		
		self.sizeList = []
		self.triangleIndices = []
		for i in range(self.dataMatrix.shape[0]):
			point = (vtm * self.dataMatrix[i,:].T).T
			
			# set the color
			if colorAxis != "":
				# r = 255*(1-dtpoint), g = 255*dtpoint, b = 255*(1 - dtpoint)
				tk_rgb = "#%02x%02x%02x" % (255*(1- colorVals[i]), 255*colorVals[i], 255*(1 - colorVals[i]))
			else:
				tk_rgb = "#%02x%02x%02x" % (0,0,0)
			
			# set the size
			if sizeAxis != "":
				dif = int(sizeVals[i] * 5 + 5)
				self.sizeList.append(dif)
			else:
				dif = 5
				self.sizeList.append(dif)
			
			# create the dataPoint obj.
			if shapeAxis != "":
				if shapeVals[i] == 0:
					dataPoint = self.canvas.create_oval(point[0,0] - dif, point[0,1] - dif, point[0,0] + dif, point[0,1] + dif, 
											fill=tk_rgb, tags=("dataPoint"))
				elif shapeVals[i] == 1:
					dataPoint = self.canvas.create_rectangle(point[0,0] - dif, point[0,1] - dif, point[0,0] + dif, point[0,1] + dif, 
											fill=tk_rgb, tags=("dataPoint"))
				else:
					dataPoint = self.canvas.create_polygon(point[0,0] - dif, point[0,1], point[0,0] + dif, point[0,1], 
											point[0,0], point[0,1]+math.sqrt((2*dif)**2-(dif)**2),fill=tk_rgb, tags=("dataPoint"))
					self.triangleIndices.append(i)
#			x, y-3.4, x-dx, y, x+dx, y,
			else:
				dataPoint = self.canvas.create_oval(point[0,0] - dif, point[0,1] - dif, point[0,0] + dif, point[0,1] + dif, 
												fill=tk_rgb, tags=("dataPoint"))
			
			self.objects.append(dataPoint)
	
	def exportPCA(self):
# 		print self.pcaList.get(tk.ACTIVE)
		
		pcaData = self.PCA[self.pcaList.get(tk.ACTIVE)]
		
		eVals = pcaData.get_eigenvalues()
		eVecs = pcaData.get_eigenvectors()
		PCAheaders = pcaData.get_PCA_headers()
		headers = pcaData.get_original_headers()
		
		with open(self.pcaList.get(tk.ACTIVE)+'.csv', 'wb') as csvfile:
			writer = csv.writer(csvfile, delimiter=',')
			
			pcaHeaderList = []
			evalList = []
			reverseList = [pcaHeaderList, evalList]
			
			for i in range(eVecs.shape[1]):
				reverseList.append([])
			
			for col in range(len(PCAheaders)):
				if col == 0:
					for header in PCAheaders:
						reverseList[col].append(header)
				
				for row in range(eVals.shape[0]):
					if col == 1:
						reverseList[col].append(eVals[row])
# 					print eVecs[row,col-2]
# 					print eVecs[row,col]
					reverseList[col+2].append(eVecs[row,col])
			
# 			print reverseList
			
			for e in range(len(reverseList)):
				reverseList[e] = tuple(reverseList[e])
			
# 			print reverseList
			
			reverseList = zip(*reverseList)
			
# 			print reverseList
			
			writer.writerow(["E-vec", "E-val"]+headers)
			
			for i in range(len(reverseList)):
				writer.writerow(reverseList[i])
	
	def handleCluster(self,event=None):
		# ask user for headers and K
		clusterBox = ClusterBox(self.root, self.headers)
		if clusterBox.canceled:
			return 
		
		if clusterBox.var.get() == 0:
			whiten = False
		else:
			whiten = True
		
		try:
# 			print clusterBox.numClusters
			K = int(clusterBox.numClusters)
		except:
			print "Not a number"
			return
		
		clusterVars = []
		for index in clusterBox.current:
# 			print index
			clusterVars.append(self.headers[index])
		
		codebook, codes, errors = analysis.kmeans(self.data, clusterVars, K, whiten)		
		
		if self.data.get_headers()[-1] == "cluster":
			print "overwriting clusters"
			self.data.removeLastColumn()
		
# 		print codes
		
		self.data.addColumn(["cluster", "numeric"]+codes.T.tolist()[0])
		
# 		print "this is the new cluster",self.data.get_data(["cluster"])
		
		self.handleClusterColor()	
		
	def handleClusterColor(self):
		# build the points
		# color according to cluster id
		colors = ["red", "pink", "blue", "orange", "yellow", "green", "bisque", "dark slate blue", "dark turquoise", "olive drab", "purple"]
		maxid = int(max(self.data.get_data(["cluster"]).T.tolist()[0]))
#		for id in range(max(self.data.get_data(["cluster"]).T.tolist()))
# 		print "maxid",maxid
		if len(self.colors)-1 <= maxid:
			self.colors = colors[:maxid+1]
		else:
			pass
#			for i in range(int(maxid - len(colors)-1)):
#				colors.append('#%02x%02x%02x' % (i*255, *255, *255))

			
	def main(self):
		print 'Entering main loop'
		self.root.mainloop()


################## Dialog Box instance ###################################################

class DBox(tkSimpleDialog.Dialog):
	def __init__(self, parent, variables, title = None):
		self.variables = variables
		tkSimpleDialog.Dialog.__init__(self, parent)
# 		print self.canceled
		
	def body(self, master):
		self.box = tk.Frame(self)
		self.indepListbox = tk.Listbox(self.box, selectmode=tk.SINGLE, exportselection=0)
		self.depListbox = tk.Listbox(self.box, selectmode=tk.SINGLE, exportselection=0)
		
		self.currentIndep = None
		self.currentDep = None
		self.poll()
		
		return self.indepListbox # initial focus
	
	
	def poll(self):
		indepNow = self.indepListbox.curselection()
		depNow = self.depListbox.curselection()
		if indepNow != self.currentIndep:
			self.list_has_changed(indepNow)
			self.currentIndep = indepNow
		if depNow != self.currentDep:
			self.list_has_changed(depNow)
			self.currentDep = depNow
		self.after(250, self.poll)

	def list_has_changed(self, selection):
		print "selection is", selection

	def buttonbox(self):
		# add standard button box. override if you don't want the
		# standard buttons
	
		label = tk.Label( self.box, text="Independent Variable", width=20 )
		label.pack( side=tk.TOP,padx=10 , pady=10 )
		
		self.indepListbox.pack(side=tk.TOP, padx=5, pady=5)
		
		label = tk.Label( self.box, text="Dependent Variable", width=20 )
		label.pack( side=tk.TOP,padx=10 , pady=10 )
		
		self.depListbox.pack(side=tk.TOP, padx=5, pady=5)

		for item in self.variables:
			self.indepListbox.insert(tk.END, item)
			self.depListbox.insert(tk.END, item)
	
	
		w = tk.Button(self.box, text="OK", width=10, command=self.ok, default=tk.ACTIVE)
		w.pack(side=tk.LEFT, padx=5, pady=5)
		w = tk.Button(self.box, text="Cancel", width=10, command=self.cancel)
		w.pack(side=tk.LEFT, padx=5, pady=5)

		self.bind("<Return>", self.ok)
		self.bind("<Escape>", self.cancel)
	
		self.box.pack()
	
	def ok(self, event=None):
		self.canceled = False
		
		if not self.validate():
			self.initial_focus.focus_set() # put focus back
			return

		self.withdraw()
		self.update_idletasks()

		self.apply()
		
		self.parent.focus_set()
		self.destroy()

	def cancel(self, event=None):
		self.canceled = True
		
		# put focus back to the parent window
		self.parent.focus_set()
		self.destroy()


class PCABox(tkSimpleDialog.Dialog):
	def __init__(self, parent, variables, title = None):
		self.variables = variables
		tkSimpleDialog.Dialog.__init__(self, parent)
# 		print self.canceled
		
	def body(self, master):
		self.box = tk.Frame(self)
		self.colsListbox = tk.Listbox(self.box, selectmode=tk.MULTIPLE, exportselection=0)
		
		self.current = None
		self.poll()
		
		return self.colsListbox # initial focus
	
	
	def poll(self):
		now = self.colsListbox.curselection()
		if now != self.current:
			self.list_has_changed(now)
			self.current = now
		self.after(250, self.poll)

	def list_has_changed(self, selection):
		print "selection is", selection

	def buttonbox(self):
		# add standard button box. override if you don't want the
		# standard buttons
	
		label = tk.Label( self.box, text="Independent Variable", width=20 )
		label.pack( side=tk.TOP,padx=10 , pady=10 )
		
		self.colsListbox.pack(side=tk.TOP, padx=5, pady=5)
		
		for item in self.variables:
			self.colsListbox.insert(tk.END, item)
		
		self.e = tk.Entry(self.box)
		self.e.pack()
		
		w = tk.Button(self.box, text="OK", width=10, command=self.ok, default=tk.ACTIVE)
		w.pack(side=tk.LEFT, padx=5, pady=5)
		w = tk.Button(self.box, text="Cancel", width=10, command=self.cancel)
		w.pack(side=tk.LEFT, padx=5, pady=5)

		self.bind("<Return>", self.ok)
		self.bind("<Escape>", self.cancel)
	
		self.box.pack()
	
	def ok(self, event=None):
		self.listName = self.e.get().replace(" ","")
		self.canceled = False
		
		if not self.validate():
			self.initial_focus.focus_set() # put focus back
			return

		self.withdraw()
		self.update_idletasks()

		self.apply()
		
		self.parent.focus_set()
		self.destroy()
	
	def setName(self, name):
		self.listName = name
	
	def cancel(self, event=None):
		self.canceled = True
		
		# put focus back to the parent window
		self.parent.focus_set()
		self.destroy()

class PCADataBox(tkSimpleDialog.Dialog):
	def __init__(self, parent, pcaData, title = None):
		self.eVals = pcaData.get_eigenvalues()
		self.eVecs = pcaData.get_eigenvectors()
		self.PCAheaders = pcaData.get_PCA_headers()
		self.headers = pcaData.get_original_headers()
		self.totalEVal = sum(self.eVals)
		
		tkSimpleDialog.Dialog.__init__(self, parent)
# 		print self.canceled
		
	def body(self, master):
		self.box = tk.Frame(self)
		self.box.pack() 		


	def buttonbox(self):
		# label = tk.Label(self.box, text="PCA Values", width=20 )
# 		label.grid(row=0,column=0)

		evec = tk.Label(self.box, text="E-vec", width=10 )
		evec.grid(row=0, column=0)
		eval = tk.Label( self.box, text="E-val", width=10 )
		eval.grid(row=0, column=1)
		
		cumulative = tk.Label( self.box, text="Cumulative", width=10 )
		cumulative.grid(row=0, column=2)
		
		for col in range(len(self.PCAheaders)):
			# PCA headers
			tk.Label(self.box, text=self.PCAheaders[col], width=10 ).grid(row=col+1, column=0) # PCA header label
			tk.Label(self.box, text=self.headers[col], width=10 ).grid(row=0, column=col+3) # header name
			for row in range(self.eVals.shape[0]):
				cumulative = round(self.eVals[row]/self.totalEVal, 4)
				tk.Label(self.box, text=self.eVals[row], width=10 ).grid(row=row+1, column=1) # E-Vals
				tk.Label(self.box, text=cumulative, width=10 ).grid(row=row+1, column=2) # cumulative percentage
				tk.Label(self.box, text=self.eVecs[row,col], width=10 ).grid(row=row+1, column=col+3) # E-Vecs

		
		w = tk.Button(self.box, text="OK", width=10, command=self.ok, default=tk.ACTIVE)
		w.grid(row=row+2, column=(col+4)/2)

		self.bind("<Return>", self.ok)
	
	
	def ok(self, event=None):
		self.canceled = False
		
		if not self.validate():
			self.initial_focus.focus_set() # put focus back
			return

		self.withdraw()
		self.update_idletasks()

		self.apply()
		
		self.parent.focus_set()
		self.destroy()

	def cancel(self, event=None):
		self.canceled = True
		
		# put focus back to the parent window
		self.parent.focus_set()
		self.destroy()

class ClusterBox(tkSimpleDialog.Dialog):
	def __init__(self, parent, variables, title = None):
		self.variables = variables
		tkSimpleDialog.Dialog.__init__(self, parent)
# 		print self.canceled
		
	def body(self, master):
		self.box = tk.Frame(self)
		self.colsListbox = tk.Listbox(self.box, selectmode=tk.MULTIPLE, exportselection=0)
		
		self.current = None
		self.poll()
		
		return self.colsListbox # initial focus
	
	
	def poll(self):
		now = self.colsListbox.curselection()
		if now != self.current:
			self.list_has_changed(now)
			self.current = now
		self.after(250, self.poll)

	def list_has_changed(self, selection):
		print "selection is", selection

	def buttonbox(self):
		# add standard button box. override if you don't want the
		# standard buttons
	
		label = tk.Label( self.box, text="Headers to Cluster", width=20 )
		label.pack( side=tk.TOP,padx=10 , pady=10 )
		
		self.colsListbox.pack(side=tk.TOP, padx=5, pady=5)
		
		for item in self.variables:
			self.colsListbox.insert(tk.END, item)
		
		label = tk.Label( self.box, text="Number of Clusters", width=20 )
		label.pack( side=tk.TOP,padx=10 , pady=10 )
		
		self.e = tk.Entry(self.box)
		self.e.pack()
		
		self.var = tk.IntVar()
		self.c = tk.Checkbutton(self.box, text="Whiten Data", variable=self.var)
		self.c.pack()
		
		w = tk.Button(self.box, text="OK", width=10, command=self.ok, default=tk.ACTIVE)
		w.pack(side=tk.LEFT, padx=5, pady=5)
		w = tk.Button(self.box, text="Cancel", width=10, command=self.cancel)
		w.pack(side=tk.LEFT, padx=5, pady=5)

		self.bind("<Return>", self.ok)
		self.bind("<Escape>", self.cancel)
	
		self.box.pack()
	
	def ok(self, event=None):
		self.numClusters = self.e.get().replace(" ","")
		self.canceled = False
		
		if not self.validate():
			self.initial_focus.focus_set() # put focus back
			return

		self.withdraw()
		self.update_idletasks()

		self.apply()
		
		self.parent.focus_set()
		self.destroy()
	
	def setName(self, name):
		self.numClusters = name
	
	def cancel(self, event=None):
		self.canceled = True
		
		# put focus back to the parent window
		self.parent.focus_set()
		self.destroy()



############################## DIALOG BOX CLASS ##########################################

class Dialog(tk.Toplevel):

	def __init__(self, parent, variables, title = None):

		tk.Toplevel.__init__(self, parent)
		self.transient(parent)

		if title:
			self.title(title)

		self.parent = parent
		self.result = None

		body = tk.Frame(self)
		self.initial_focus = self.body(body)
		body.pack(padx=5, pady=5)

#		self.buttonbox()

		self.grab_set()

		if not self.initial_focus:
			self.initial_focus = self

		self.protocol("WM_DELETE_WINDOW", self.cancel)

		self.geometry("+%d+%d" % (parent.winfo_rootx()+50,
								  parent.winfo_rooty()+50))

		self.initial_focus.focus_set()

		self.wait_window(self)

	#
	# construction hooks

	def body(self, master):
		# create dialog body.  return widget that should have
		# initial focus.  this method should be overridden

		pass

	def buttonbox(self):
		# add standard button box. override if you don't want the
		# standard buttons

		box = Frame(self)

		w = tk.Button(box, text="OK", width=10, command=self.ok, default=tk.ACTIVE)
		w.pack(side=tk.LEFT, padx=5, pady=5)
		w = tk.Button(box, text="Cancel", width=10, command=self.cancel)
		w.pack(side=tk.LEFT, padx=5, pady=5)

		self.bind("<Return>", self.ok)
		self.bind("<Escape>", self.cancel)

		box.pack()

	#
	# standard button semantics

	def ok(self, event=None):
#		self.canceled = False
		
		if not self.validate():
			self.initial_focus.focus_set() # put focus back
			return

		self.withdraw()
		self.update_idletasks()

		self.apply()
		
		self.parent.focus_set()
		self.destroy()

	def cancel(self, event=None):
#		self.canceled = True
		
		# put focus back to the parent window
		self.parent.focus_set()
		self.destroy()

	#
	# command hooks

	def validate(self):

		return 1 # override

	def apply(self):

		pass # override

if __name__ == "__main__":
	dapp = DisplayApp(1200, 675)
	# print dapp
	dapp.main()
	


