################################################################################
##
##    Property of Baker Hughes, a GE Company
##    Copyright 2018
##    Author: Sai Uppati
##    saipranav.uppati@bhge.com
##
################################################################################
# Interpolation func to convert to n times as many samples radially at all MDs
# for example 4 times, 256 samples in each of the 4 directions becomes 1021 samples in each
def interpRadial(dataXYZ, n):
	numSamples = dataXYZ.shape[1] + (dataXYZ.shape[1] - 1) * (n - 1)
	import numpy as np
	quadDataXYZ = np.zeros((dataXYZ.shape[0], numSamples))
	origSampleArray = np.arange(1,257)
	newSampleArray = np.linspace(1.0, 256.0, num=numSamples)
	for row in range(dataXYZ.shape[0]):
		quadDataXYZ[row, :] = np.interp(newSampleArray, origSampleArray, dataXYZ[row, :])

	return quadDataXYZ
