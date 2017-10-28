# Tatsuya Yokota
# view.py

import numpy as np
import math

class view():
	def __init__(self):
		self.reset()

	def reset(self):
		self.vrp = np.matrix([[0.5, 0.5, 1]])
		self.vpn = np.matrix([[0, 0, -1]])
		self.vup = np.matrix([[0, 1, 0]])
		self.u = np.matrix([[-1, 0, 0]])
		self.extent = np.matrix([[1, 1, 1]])
		self.screen = np.matrix([[400, 400]])
		self.offset = np.matrix([[20, 20]])

	def build(self):
		# 4x4 identity matrix, basis for the view matrix
		vtm = np.identity(4, float)

		# translation matrix, move VRP to the origin
		t1 = np.matrix([[1, 0, 0, -self.vrp[0, 0]],
						   [0, 1, 0, -self.vrp[0, 1]],
						   [0, 0, 1, -self.vrp[0, 2]],
						   [0, 0, 0, 1]])

		vtm = t1 * vtm

		# cross product of vup and vpn
		tu = np.cross(self.vup, self.vpn)
		tvup = np.cross(self.vpn, tu)
		tvpn = self.vpn.copy()

		# normalize the orthogonal matrices
		self.u = self.normalize(tu)
		self.vup = self.normalize(tvup)
		self.vpn = self.normalize(tvpn)

		# align the axes with rotation
		r1 = np.matrix([[self.u[0, 0], self.u[0, 1], self.u[0, 2], 0.0],
						   [self.vup[0, 0], self.vup[0, 1], self.vup[0, 2], 0.0],
						   [self.vpn[0, 0], self.vpn[0, 1], self.vpn[0, 2], 0.0],
						   [0.0, 0.0, 0.0, 1.0]])

		vtm = r1 * vtm

		# Translate the lower left corner of the view space to the origin
		t2 = np.matrix([[1, 0, 0, 0.5*self.extent[0,0]],
					   [0, 1, 0, 0.5*self.extent[0,1]],
					   [0, 0, 1, 0],
					   [0, 0, 0, 1]])

		vtm = t2 * vtm


		s1 = np.matrix([[ -self.screen[0,0] / self.extent[0,0], 0, 0, 0],
					   [0, -self.screen[0,1] / self.extent[0,1], 0, 0],
					   [0, 0, 1.0 / self.extent[0,2], 0],
					   [0, 0, 0, 1]])
		vtm = s1 * vtm

		t3 = np.matrix([[1, 0, 0, self.screen[0,0] + self.offset[0,0]],
					   [0, 1, 0, self.screen[0,1] + self.offset[0,1]],
					   [0, 0, 1, 0],
					   [0, 0, 0, 1]])
		vtm = t3 * vtm

		return vtm


	def normalize(self, vector):
		length = np.linalg.norm(vector)
		return vector / length

	def clone(self):
		copy = view()
		copy.vrp = self.vrp.copy()
		copy.vpn = self.vpn.copy()
		copy.vup = self.vup.copy()
		copy.u = self.u.copy()
		copy.extent = self.extent.copy()
		copy.screen = self.screen.copy()
		copy.offset = self.offset.copy()
		return copy
	
	def rotateVRC(self, vupAngle, uAngle):
		# Make a translation matrix to move the point ( VRP + VPN * extent[Z] * 0.5 ) to the origin
		t1 = np.matrix([[1, 0, 0, -(self.vrp[0, 0] + self.vpn[0,0]*self.extent[0,2]*0.5)],
						   [0, 1, 0, -(self.vrp[0, 1] + self.vpn[0,1]*self.extent[0,2]*0.5)],
						   [0, 0, 1, -(self.vrp[0, 2] + self.vpn[0,2]*self.extent[0,2]*0.5)],
						   [0, 0, 0, 1]])
	
		# Make an axis alignment matrix Rxyz using u, vup and vpn.
		Rxyz = np.matrix([[self.u[0, 0], self.u[0, 1], self.u[0, 2], 0.0],
						   [self.vup[0, 0], self.vup[0, 1], self.vup[0, 2], 0.0],
						   [self.vpn[0, 0], self.vpn[0, 1], self.vpn[0, 2], 0.0],
						   [0.0, 0.0, 0.0, 1.0]])
						   
		# Make a rotation matrix about the Y axis by the VUP angle.
		r1 = np.matrix([[math.cos(vupAngle), 0, math.sin(vupAngle), 0],
						[0, 1, 0, 0],
						[-math.sin(vupAngle), 0, math.cos(vupAngle), 0],
						[0, 0, 0, 1]])
		
		# Make a rotation matrix about the X axis by the U angle.
		r2 = np.matrix([[1, 0, 0, 0],
						[0, math.cos(uAngle), -math.sin(uAngle), 0],
						[0, math.sin(uAngle), math.cos(uAngle), 0],
						[0, 0, 0, 1]])
						
		# Make a translation matrix that has the opposite translation from t1.
		t2 = np.matrix([[1, 0, 0, self.vrp[0, 0] + self.vpn[0,0]*self.extent[0,2]*0.5],
					   [0, 1, 0, self.vrp[0, 1] + self.vpn[0,1]*self.extent[0,2]*0.5],
					   [0, 0, 1, self.vrp[0, 2] + self.vpn[0,2]*self.extent[0,2]*0.5],
					   [0, 0, 0, 1]])
	
		# Make a matrix where the VRP is on the first row, with a 1 in the homogeneous coordinate,
		# and u, vup, and vpn are the next three rows, with a 0 in the homogeneous coordinate.
		tvrc = np.hstack([np.vstack([self.vrp, self.u, self.vup, self.vpn]), np.matrix([1,0,0,0]).T])
		
		# apply translations and rotations to tvrc
		tvrc = (t2*Rxyz.T*r2*r1*Rxyz*t1*tvrc.T).T
		
		# reassign everything and normalize vectors
		self.vrp = tvrc[0, :3]
		self.u = self.normalize(tvrc[1, :3])
		self.vup = self.normalize(tvrc[2, :3])
		self.vpn = self.normalize(tvrc[3, :3])
	
# 	def getExtent(self):
# 		return self.extent
# 	
# 	def getVRP(self):
# 		return self.vrp
# 	
# 	def getU(self):
# 		return self.u
# 		
# 	def setVRP(self, newvrp):
# 		self.vrp = newvrp
			
		
if __name__ == '__main__':
	view = view()
	print view.build()