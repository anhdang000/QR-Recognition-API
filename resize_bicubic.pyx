# import modules
import cv2
import numpy as np
cimport numpy as np
import math
import sys
import time

DTYPE = np.int
ctypedef np.int_t DTYPE_t

# Interpolation kernel
cpdef float u(float s, float a):
	if (abs(s) >= 0) & (abs(s) <= 1):
		return (a+2)*(abs(s)**3)-(a+3)*(abs(s)**2)+1
	elif (abs(s) > 1) & (abs(s) <= 2):
		return a*(abs(s)**3)-(5*a)*(abs(s)**2)+(8*a)*abs(s)-4*a
	return 0


# Padding
cpdef np.ndarray padding(np.ndarray img, int H, int W, int C):
	cdef np.ndarray zimg = np.zeros((H+4, W+4, C), dtype=DTYPE)

	zimg[2:H+2, 2:W+2, :C] = img
	
	# Pad the first/last two col and row
	zimg[2:H+2, 0:2, :C] = img[:, 0:1, :C]
	zimg[H+2:H+4, 2:W+2, :] = img[H-1:H, :, :]
	zimg[2:H+2, W+2:W+4, :] = img[:, W-1:W, :]
	zimg[0:2, 2:W+2, :C] = img[0:1, :, :C]
	
	# Pad the missing eight points
	zimg[0:2, 0:2, :C] = img[0, 0, :C]
	zimg[H+2:H+4, 0:2, :C] = img[H-1, 0, :C]
	zimg[H+2:H+4, W+2:W+4, :C] = img[H-1, W-1, :C]
	zimg[0:2, W+2:W+4, :C] = img[0, W-1, :C]
	return zimg


# Bicubic operation
cpdef np.ndarray bicubic(np.ndarray img, float ratio, float a):
	cdef H = img.shape[0]
	cdef W = img.shape[1]
	cdef C = img.shape[2]
	
	# Here H = Height, W = weight,
	# C = Number of channels if the
	# image is coloured.
	img = padding(img, H, W, C)
	
	# Create new image
	cdef int dH = math.floor(H*ratio)
	cdef int dW = math.floor(W*ratio)

	# Converting into matrix
	cdef np.ndarray dst = np.zeros((dH, dW, 3))
	# np.zeroes generates a matrix
	# consisting only of zeroes
	# Here we initialize our answer
	# (dst) as zero

	cdef float h = 1 / ratio
	cdef int c, j, i
	cdef float x, y, x1, x2, x3, x4, y1, y2, y3, y4
	cdef np.ndarray mat_l, mat_m, mat_r
	for c in range(C):
		for j in range(dH):
			for i in range(dW):
				# Getting the coordinates of the
				# nearby values
				x, y = i * h + 2, j * h + 2

				x1 = 1 + x - math.floor(x)
				x2 = x - math.floor(x)
				x3 = math.floor(x) + 1 - x
				x4 = math.floor(x) + 2 - x

				y1 = 1 + y - math.floor(y)
				y2 = y - math.floor(y)
				y3 = math.floor(y) + 1 - y
				y4 = math.floor(y) + 2 - y
				
				# Considering all nearby 16 values
				mat_l = np.matrix([[u(x1, a), u(x2, a), u(x3, a), u(x4, a)]])
				mat_m = np.matrix([[img[int(y-y1), int(x-x1), c],
									img[int(y-y2), int(x-x1), c],
									img[int(y+y3), int(x-x1), c],
									img[int(y+y4), int(x-x1), c]],
								[img[int(y-y1), int(x-x2), c],
									img[int(y-y2), int(x-x2), c],
									img[int(y+y3), int(x-x2), c],
									img[int(y+y4), int(x-x2), c]],
								[img[int(y-y1), int(x+x3), c],
									img[int(y-y2), int(x+x3), c],
									img[int(y+y3), int(x+x3), c],
									img[int(y+y4), int(x+x3), c]],
								[img[int(y-y1), int(x+x4), c],
									img[int(y-y2), int(x+x4), c],
									img[int(y+y3), int(x+x4), c],
									img[int(y+y4), int(x+x4), c]]])
				mat_r = np.matrix(
					[[u(y1, a)], [u(y2, a)], [u(y3, a)], [u(y4, a)]])
				
				# Here the dot function is used to get
				# the dot product of 2 matrices
				dst[j, i, c] = np.dot(np.dot(mat_l, mat_m), mat_r)
	return dst

if __name__ == "__main__":
	# Read image
	# You can put your input image over
	# here to run bicubic interpolation
	# The read function of Open CV is used
	# for this task
	img = cv2.imread('ret.jpg')

	# Scale factor
	ratio = 4
	# Coefficient
	a = -1/2

	# Passing the input image in the
	# bicubic function
	dst = bicubic(img, ratio, a)
	print('Completed!')

	# Saving the output image
	cv2.imwrite('bicubic.png', dst)
	bicubicImg = cv2.imread('bicubic.png')

	# display shapes of both images
	print('Original Image Shape:', img.shape)
	print('Generated Bicubic Image Shape:', bicubicImg.shape)
