# Import required modules
import os, sys
import numpy as np
from math import pi
import matplotlib.pyplot as plt
#from scipy.signal import lfilter
#import time

# def read_XMAC(boolSuppress = False, suppressLimit = 8):
boolSuppress = False
suppressLimit = 8

# Is well trajectory data available?
boolWellSurvey = True

# XMAC txt format standards _DKA interpreted
#1)  \r\n is the delineation of a new value
#2) First line is the measured depth
#3) Next lines are 1D array given in 2D row column format

# Assign well name/API number
wellName = 'ROTHE_pre' # NOTE: input 1

# Begin reading in text files
# It's assumed that the filenames contain relative path based on the directory that this python script is in
xmac_filename = 'WIMGHH.txt'	# NOTE: input 2
xmac_filename_vert = 'WIMGVHM.txt'	# NOTE: input 3
# working_dir = os.path.dirname(sys.executable) #<-- absolute dir the script/executable is in
# TODO: revert to above working_dir definition for executable-convertable python code
working_dir = os.path.dirname('C:/Users/212566876/Box Sync/Rotation 3/DSWI/MARATHON_CHAPMAN_ROTHE_UNIT_6H_BEFORE_FRAC/read_XMAC.py')
xmac_abs_file_path = os.path.join(working_dir, xmac_filename)
xmac_vert_abs_file_path = os.path.join(working_dir, xmac_filename_vert)
logName = 'MARATHON_CHAPMAN_ROTHE_DSWI_preFrac.las' # NOTE: input 4
logFilePath = os.path.join(working_dir, logName)
logFilePath = os.path.normpath(logFilePath)
txtFileName = 'MARATHON_CHAPMAN_ROTHE_DSWI_preFrac_DFN.txt'	# NOTE: input 5
txtFilePath = os.path.join(working_dir, txtFileName)
txtFilePath = os.path.normpath(txtFilePath)
fid = open(xmac_abs_file_path)
fid_vert = open(xmac_vert_abs_file_path)
rStart = -99.80469	#i5 how many feet away from the wellbore
rStep = 0.390625	#i6 how large is an individual step
wellSurveyFileName = 'CR6H_well_trajectory.txt'
wellSurveyFilePath = os.path.join(working_dir, wellSurveyFileName)

# -----------------------------
# Read in horizontal XMAC data
# -----------------------------
data = []
dataRow = []
startingDepth = -100000	# Non-sensical depth initialized for startingDepth (as a check) to prevent reassignment after initial assignment below
# endingDepth = -100000	# Non-sensical depth initialized for endingDepth (will be continuously reassigned in loop below until loop finishes)
for line in fid:
	# If there is no data, then on next line there is a value
	if line == '' or line == '\n':
		# Store the previous row of data, if any, into the data array
		if len(dataRow) != 0:
			if dataRow[1] != -32767:
				if startingDepth == -100000:
					startingDepth = dataRow[0]	# for the first row of useful data, record the starting depth
				data.append(dataRow)
		dataRow = []
	else:
		listOfValuesInLine = [float(val) for val in line.split()]
		dataRow.extend(listOfValuesInLine)
# Store the last row of data, if last line of file is not empty	(also reassign ending depth)
if len(dataRow) != 0:
	if dataRow[1] != -32767:
		data.append(dataRow)
# Convert dynamic list of lists from horizontal XMAC file to numpy array
data = np.array(data)
endingDepth = data[-1,0]

#--DEBUG--
# print("Horizonatal portion...")
# print(data)
# print(type(data))
# print(data.shape)

# Make sure to close the open file
fid.close()

# -----------------------------
# Read in vertical XMAC data
# -----------------------------
data_vert = []
dataRow = []
startingDepth_vert = -100000	# Non-sensical depth initialized for startingDepth (as a check) to prevent reassignment after initial assignment below
# endingDepth_vert = -100000	# Non-sensical depth initialized for endingDepth (will be continuously reassigned in loop below until loop finishes)
for line in fid_vert:
	# If there is no data, then on next line there is a value
	if line == '' or line == '\n':
		# Store the previous row of data, if any into the data array
		if len(dataRow) != 0:
			if dataRow[1] != -32767:
				if startingDepth_vert == -100000:
					startingDepth_vert = dataRow[0]	# for the first row of useful data, record the starting depth (vertical slice)
				data_vert.append(dataRow)
		dataRow = []
	else:
		listOfValuesInLine = [float(val) for val in line.split()]
		dataRow.extend(listOfValuesInLine)
# Store the last row of data, if last line of file is not empty
if len(dataRow) != 0:
	if dataRow[1] != -32767:
		data_vert.append(dataRow)
# Convert dynamic list of lists from horizontal XMAC file to numpy array
data_vert = np.array(data_vert)
endingDepth_vert = data_vert[-1,0]

# --DEBUG--
# print("Vertical portion...")
# print(data_vert)
# print(type(data_vert))
# print(data_vert.shape)

# Make sure to close open file
fid_vert.close()

# If there is discrepancy between measured depths in horizontal and vertical
# slices of data, then fix if possible and throw an error if not
# starting depth index
if startingDepth != startingDepth_vert:
	if startingDepth > startingDepth_vert:
		depthStartIndex = 0
		depthStartIndex_vert = np.argwhere(data_vert[:,0] == startingDepth)[0][0]
		tempStartDepth = startingDepth
	else:
		depthStartIndex = np.argwhere(data[:,0] == startingDepth_vert)[0][0]
		depthStartIndex_vert = 0
		tempStartDepth = startingDepth_vert
# ending depth index
if endingDepth != endingDepth_vert:
	if endingDepth > endingDepth_vert:
		depthEndIndex = np.argwhere(data[:,0] == endingDepth_vert)[0][0]
		depthEndIndex_vert = -1
		tempEndDepth = endingDepth_vert
	else:
		depthEndIndex = -1
		depthEndIndex_vert = np.argwhere(data_vert[:,0] == endingDepth)[0][0]
		tempEndDepth = endingDepth
# eliminate depth measurements that are outside the mutually compatiable range
data = data[depthStartIndex:depthEndIndex,:]
data_vert = data_vert[depthStartIndex_vert:depthEndIndex_vert,:]
# exit the program if the horizontal and vertical slices don't have the same number of samples
if data.shape[0] == data_vert.shape[0]:
	startingDepth = tempStartDepth
	endingDepth = tempEndDepth
else:
	print('There was an issue! The number of measured depth samples are NOT the \
			same in the horizontal and vertical slices of provided XMAC data. \
			The program will now terminate. ')
	exit()

# Read in well trajectory data, if available
if boolWellSurvey:
	wellSurveyData = []
	wellFID = open(wellSurveyFilePath)
	# skip 3 lines to start from 4th line
	next(wellFID)
	next(wellFID)
	next(wellFID)
	for line in wellFID:
		listRow = line.split('\t')
		dataRow = []
		for i in [2, 3, 4, 7]:
			dataRow.append(float(listRow[i]))
		wellSurveyData.append(dataRow)
	wellSurveyData = np.array(wellSurveyData)


#%%

# ---------------
# MAIN ALGORITHM
# ---------------

# Suppress values in data that are less than 8 (set to 0),
if boolSuppress:
    data[np.absolute(data) < suppressLimit] = 0
    data_vert[np.absolute(data_vert) < suppressLimit] = 0

# Separate into + and - (horizontal and vertical)
zData = data[:,0]	# measured depths (MDs)
dataNeg = np.fliplr(data[:,1:257])
dataPos = data[:,257:]
zDataVert = data_vert[:,0]	# these MDs should be identical to zData, otherwise there's a mismatch between horizontal and vertical data files
dataNegVert = np.fliplr(data_vert[:,1:257])
dataPosVert = data_vert[:,257:]

# Begin estimating fracture intensity
dataNeg = np.absolute(dataNeg)
dataPos = np.absolute(dataPos)
dataNegVert = np.absolute(dataNegVert)
dataPosVert = np.absolute(dataPosVert)

#--DEBUG--
# print(dataNeg.shape)
# print(dataPos.shape)
# print(dataNegVert.shape)
# print(dataPosVert.shape)

# Overall fracture length estimation

# TODO: Problem here Sai as we do not orient
# to the fracture azimuth. Could rotate the image and find angle
# automatically; Could assume an angle of the fracture prior to measuring
# the length.

# Smoothing 7 points
dataNegSmoothed = dataNeg
dataPosSmoothed = dataPos
dataNegVertSmoothed = dataNegVert
dataPosVertSmoothed = dataPosVert
for col in range(3,dataNeg.shape[1]-3):
	dataNegSmoothed[:, col] = np.mean(dataNeg[:, col-3:col+3], axis=1)
	dataPosSmoothed[:, col] = np.mean(dataPos[:, col-3:col+3], axis=1)
	dataNegVertSmoothed[:, col] = np.mean(dataNegVert[:, col-3:col+3], axis=1)
	dataPosVertSmoothed[:, col] = np.mean(dataPosVert[:, col-3:col+3], axis=1)
dataNeg = dataNegSmoothed
dataPos = dataPosSmoothed
dataNegVert = dataNegVertSmoothed
dataPosVert = dataPosVertSmoothed

# Interpolation func to convert to four times as many samples radially at all MDs
# 256 samples in each of the 4 directions becomes 1021 samples in each
def quadrupRadial(dataXYZ):
	quadDataXYZ = np.zeros((dataXYZ.shape[0], 1021))
	origSampleArray = np.arange(1,257)
	newSampleArray = np.linspace(1.0, 256.0, num=1021)
	for row in range(dataXYZ.shape[0]):
		quadDataXYZ[row, :] = np.interp(newSampleArray, origSampleArray, dataXYZ[row, :])
	return quadDataXYZ

# Interpolate in all 4 directions
dataNInterp = quadrupRadial(dataNeg)
dataPInterp = quadrupRadial(dataPos)
dataHorizInterp = np.concatenate((np.fliplr(dataNInterp), dataPInterp), axis=1)
dataNVInterp = quadrupRadial(dataNegVert)
dataPVInterp = quadrupRadial(dataPosVert)

# for col in range(3,dataNeg.shape[1]-3):
# 	dataNeg[:, col] = np.mean(dataNeg[:, col-3:col+3], axis=1)
# 	dataPos[:, col] = np.mean(dataPos[:, col-3:col+3], axis=1)
# 	dataNegVert[:, col] = np.mean(dataNegVert[:, col-3:col+3], axis=1)
# 	dataPosVert[:, col] = np.mean(dataPosVert[:, col-3:col+3], axis=1)


#--DEBUG--
# print(dataNeg.shape)
# print(dataPos.shape)
# print(dataNegVert.shape)
# print(dataPosVert.shape)
# i = 2703
# plt.figure(1)
# plt.plot(range(1,257), dataNegVert[i,:], 'r.')
# plt.xlabel("radial sample #")
# plt.ylabel("dataNegVert reflectivity")
# plt.title("MD: {0} ft".format(zData[i]))
#
# plt.figure(2)
# plt.plot(range(1,1022), dataNVInterp[i,:], 'b.')
# plt.xlabel("radial sample #")
# plt.ylabel("dataNegVert interpolated reflectivity")
# plt.title("MD: {0} ft".format(zData[i]))




# Find cumulative fracture intensity

# (is it a single small and long fracture
# or is it many fractures far from the wellbore?)

normNeg = np.sum(dataNeg, axis=1)
normPos = np.sum(dataPos, axis=1)
normNegVert = np.sum(dataNegVert, axis=1)
normPosVert = np.sum(dataPosVert, axis=1)
intn = normNeg + normPos + normNegVert + normPosVert

#--DEBUG--
# Check for zeros and NaN elements
# print("Check for zeros and NaN elements in norm arrays...")
# if np.count_nonzero(normNeg) < normNeg.shape[0]:
# 	print("Way 1: normNeg has {0} zeros".format(normNeg.shape[0]-np.count_nonzero(normNeg)))
# 	print("Way 2: normNeg has {0} zeros".format(np.count_nonzero(normNeg==0)))
# if np.count_nonzero(normPos) < normPos.shape[0]:
# 	print("Way 1: normPos has {0} zeros".format(normPos.shape[0]-np.count_nonzero(normPos)))
# 	print("Way 2: normPos has {0} zeros".format(np.count_nonzero(normPos==0)))
# if np.count_nonzero(normNegVert) < normNegVert.shape[0]:
# 	print("Way 1: normNegVert has {0} zeros".format(normNegVert.shape[0]-np.count_nonzero(normNegVert)))
# 	print("Way 2: normNegVert has {0} zeros".format(np.count_nonzero(normNegVert==0)))
# if np.count_nonzero(normPosVert) < normPosVert.shape[0]:
# 	print("Way 1: normPosVert has {0} zeros".format(normPosVert.shape[0]-np.count_nonzero(normPosVert)))
# 	print("Way 2: normPosVert has {0} zeros".format(np.count_nonzero(normPosVert==0)))
# print("normNeg")
# print("num elements: {0}".format(normNeg.shape[0]))
# print("num NaN elements: {0}".format(np.count_nonzero(np.isnan(normNeg))))
# print("normPos")
# print("num elements: {0}".format(normPos.shape[0]))
# print("num NaN elements: {0}".format(np.count_nonzero(np.isnan(normPos))))
# print("normNegVert")
# print("num elements: {0}".format(normNegVert.shape[0]))
# print("num NaN elements: {0}".format(np.count_nonzero(np.isnan(normNegVert))))
# print("normPosVert")
# print("num elements: {0}".format(normPosVert.shape[0]))
# print("num NaN elements: {0}".format(np.count_nonzero(np.isnan(normPosVert))))
# normNeg[normNeg==0] = 1
# normPos[normPos==0] = 1
# normNegVert[normNegVert==0] = 1
# normPosVert[normPosVert==0] = 1

# Cumulative sum, ignoring the division by zero warnings (which will later be replaced by 1's)
with np.errstate(invalid = 'ignore'):
	cumSumNormNeg = np.divide(np.cumsum(dataNeg, axis=1), normNeg[:,None])
	cumSumNormPos = np.divide(np.cumsum(dataPos, axis=1), normPos[:,None])
	cumSumNormNegVert = np.divide(np.cumsum(dataNegVert, axis=1), normNegVert[:,None])
	cumSumNormPosVert = np.divide(np.cumsum(dataPosVert, axis=1), normPosVert[:,None])

#--DEBUG--
# print(cumSumNormNeg.shape)
# print(cumSumNormPos.shape)
# print(cumSumNormNegVert.shape)
# print(cumSumNormPosVert.shape)
# print("BEFORE...")
# print("cumSumNormNeg")
# print("num elements: {0}".format(cumSumNormNeg.shape[0]*cumSumNormNeg.shape[1]))
# print("num NaN elements: {0}".format(np.count_nonzero(np.isnan(cumSumNormNeg))))
# print("cumSumNormPos")
# print("num elements: {0}".format(cumSumNormPos.shape[0]*cumSumNormPos.shape[1]))
# print("num NaN elements: {0}".format(np.count_nonzero(np.isnan(cumSumNormPos))))
# print("cumSumNormNegVert")
# print("num elements: {0}".format(cumSumNormNegVert.shape[0]*cumSumNormNegVert.shape[1]))
# print("num NaN elements: {0}".format(np.count_nonzero(np.isnan(cumSumNormNegVert))))
# print("cumSumNormPosVert")
# print("num elements: {0}".format(cumSumNormPosVert.shape[0]*cumSumNormPosVert.shape[1]))
# print("num NaN elements: {0}".format(np.count_nonzero(np.isnan(cumSumNormPosVert))))


# Finding the lathe plot
integral = 0.8
nDepth = dataNeg.shape[0]
rNeg = np.zeros((nDepth,))
rPos = np.zeros((nDepth,))
rNegVert = np.zeros((nDepth,))
rPosVert = np.zeros((nDepth,))
cumSumNormNeg[np.where(np.isnan(cumSumNormNeg))] = 1
cumSumNormPos[np.where(np.isnan(cumSumNormPos))] = 1
cumSumNormNegVert[np.where(np.isnan(cumSumNormNegVert))] = 1
cumSumNormPosVert[np.where(np.isnan(cumSumNormPosVert))] = 1

#--DEBUG--
# print("AFTER...")
# print("cumSumNormNeg")
# print("num elements: {0}".format(cumSumNormNeg.shape[0]*cumSumNormNeg.shape[1]))
# print("num NaN elements: {0}".format(np.count_nonzero(np.isnan(cumSumNormNeg))))
# print("cumSumNormPos")
# print("num elements: {0}".format(cumSumNormPos.shape[0]*cumSumNormPos.shape[1]))
# print("num NaN elements: {0}".format(np.count_nonzero(np.isnan(cumSumNormPos))))
# print("cumSumNormNegVert")
# print("num elements: {0}".format(cumSumNormNegVert.shape[0]*cumSumNormNegVert.shape[1]))
# print("num NaN elements: {0}".format(np.count_nonzero(np.isnan(cumSumNormNegVert))))
# print("cumSumNormPosVert")
# print("num elements: {0}".format(cumSumNormPosVert.shape[0]*cumSumNormPosVert.shape[1]))
# print("num NaN elements: {0}".format(np.count_nonzero(np.isnan(cumSumNormPosVert))))

# At each MD, find the first of the 256 distances in each direction at which the cumulative sum norm exceeds the threshold integral value
for row in range(nDepth):
	rNeg[row] = np.argmax(cumSumNormNeg[row,:] > integral) + 1
	rPos[row] = np.argmax(cumSumNormPos[row,:] > integral) + 1
	rNegVert[row] = np.argmax(cumSumNormNegVert[row,:] > integral) + 1
	rPosVert[row] = np.argmax(cumSumNormPosVert[row,:] > integral) + 1

# Smoothing in depth (both radial extent and intensity)
# 1. Radii
rNegSmoothed = rNeg
rPosSmoothed = rPos
rNegVertSmoothed = rNegVert
rPosVertSmoothed = rPosVert
# filterDef = np.concatenate((np.arange(1,5), np.arange(3,0,-1))) / 16
filterDef = np.concatenate((np.arange(1,8), np.arange(6,0,-1))) / 49
for i in range(6, rNeg.shape[0]-7):
	rNegSmoothed[i] = np.dot(rNeg[i-6:i+7], filterDef)
	rPosSmoothed[i] = np.dot(rPos[i-6:i+7], filterDef)
	rNegVertSmoothed[i] = np.dot(rNegVert[i-6:i+7], filterDef)
	rPosVertSmoothed[i] = np.dot(rPosVert[i-6:i+7], filterDef)
rNeg = rNegSmoothed
rPos = rPosSmoothed
rNegVert = rNegVertSmoothed
rPosVert = rPosVertSmoothed
# 2. Intensity
intnSmoothed = intn
for i in range(6, intn.shape[0]-7):
    intnSmoothed[i] = np.dot(intn[i-6:i+7], filterDef)
intn = intnSmoothed

# Alternative IDEA: filtering/smoothing using lfilter from SCIPY
# rNeg = np.roll(rNeg, -6)
# rPos = np.roll(rPos, 6)
# rNeg = lfilter(filterDef, 1, rNeg)
# rPos = lfilter(filterDef, 1, rPos)
# rNegVert = np.roll(rNegVert, -6)
# rPosVert = np.roll(rPosVert, 6)
# rNegVert = lfilter(filterDef, 1, rNegVert)
# rPosVert = lfilter(filterDef, 1, rPosVert)


# --------------------------
# DETERMINE FRACTURE PLANES (AT WHICH MD AND GEOMETRY) FOR DISCRETE FRACTURE NETWORK (DFN)
# --------------------------

# Based on threshold approach, intensity values below set threshold
# will not be considered for visualization
thresh = 3000
isGood = intn > thresh
zDataAbove = zData[isGood]
nDepthsAbove = zDataAbove.shape[0]
intnAbove = intn[isGood]
rNegAbove = rNeg[isGood]
rPosAbove = rPos[isGood]
rNegVertAbove = rNegVert[isGood]
rPosVertAbove = rPosVert[isGood]

# Determine curvature change for finding local maxima, which
# will serve as locations of fractures along MD
max = 0
iDepth = 0
zDataDFN = []
intnDFN = []
rnDFN = []
rpDFN = []
rnvDFN = []
rpvDFN = []
while iDepth <= nDepthsAbove-1:
    skip = 0
    # Ascending
    while intnAbove[iDepth + skip] >= max:
        max = intnAbove[iDepth + skip]
        skip += 1
        if iDepth + skip >= nDepthsAbove:
            break
    # Local maximum found
    intnDFN.append(max)
    zDataDFN.append(zDataAbove[iDepth + skip - 1])
    rnDFN.append(rNegAbove[iDepth + skip - 1])
    rpDFN.append(rPosAbove[iDepth + skip - 1])
    rnvDFN.append(rNegVertAbove[iDepth + skip - 1])
    rpvDFN.append(rPosVertAbove[iDepth + skip - 1])
    iDepth += skip
    skip = 0
    # Descending
    if iDepth + 1 >= nDepthsAbove:
        break
    while intnAbove[iDepth + skip + 1] <= intnAbove[iDepth + skip]:
        skip += 1
        if iDepth + skip + 1 >= nDepthsAbove:
            break
    # Skip checking when last data point is reached
    if iDepth + skip + 1 >= nDepthsAbove:
        break
    # Local minimum found
    iDepth += skip
    max = 0 # reset max

# Convert to numpy arrays for DFN data currently in list form
intnDFN = np.array(intnDFN)
zDataDFN = np.array(zDataDFN)
print('{} fracs in DFN'.format(zDataDFN.shape[0]))
# print(np.argmin(np.absolute(zDataDFN-12500)))
rnDFN = np.array(rnDFN)
rpDFN = np.array(rpDFN)
rnvDFN = np.array(rnvDFN)
rpvDFN = np.array(rpvDFN)

# Define function to interpolate Easting, Northing, and TVD for a given MD, if
# well survey data with Easting, Northing, TVD and MD values are provided
def wellInterp(md, wellSurveyData):
	# Assuming columns are ordered like Easing, Northing, TVD and MD
	closestIndex = np.argmin(abs(md - wellSurveyData[:,3]))
	if wellSurveyData[closestIndex, 3] < md:
		lowerIndex = closestIndex
		upperIndex = closestIndex + 1
	else:
		lowerIndex = closestIndex - 1
		upperIndex = closestIndex
	e0 = wellSurveyData[lowerIndex,0]
	e1 = wellSurveyData[upperIndex,0]
	n0 = wellSurveyData[lowerIndex,1]
	n1 = wellSurveyData[upperIndex,1]
	tvd0 = wellSurveyData[lowerIndex,2]
	tvd1 = wellSurveyData[upperIndex,2]
	md0 = wellSurveyData[lowerIndex,3]
	md1 = wellSurveyData[upperIndex,3]
	Easting = (e1-e0)/(md1-md0)*(md-md0) + e0
	Northing = (n1-n0)/(md1-md0)*(md-md0) + n0
	TVD = (tvd1-tvd0)/(md1-md0)*(md-md0) + tvd0
	return Easting, Northing, TVD

# Calculate Easting, Northing and TVD for DFN measured depths for writing to file
# if well survey file is not provided, then assign null values -9999
eastingDFN = np.zeros(zDataDFN.shape)
northingDFN = np.zeros(zDataDFN.shape)
tvdDFN = np.zeros(zDataDFN.shape)
for i in range(zDataDFN.shape[0]):
	if boolWellSurvey:
		eastingDFN[i], northingDFN[i], tvdDFN[i] = wellInterp(zDataDFN[i], wellSurveyData)
	else:
		eastingDFN[i] = -9999
		northingDFN[i] = -9999
		tvdDFN[i] = -9999



# Define function to determine stacking of reflectivity signal traces at a given angle
# for the fracture (plane) selected at a certain MD in above DFN Selection and return
# the metric for how good the traces stack (standard deviation: high - poor stacking,
# low - good stacking)
def reflStack(angle, measDepth, zData, rStep, dataHorizInterp):
	# Define vertical shift array (15 samples on either side) for trace shift as empty list
	vsArray = []
	for i in range(1,16):
		hs = i*0.5
		vs = np.absolute(np.tan(angle*pi/180) * hs)
		vs = np.rint(vs / (rStep/4))	# vertical shift by this many radial samples
		vsArray.append(vs)
	# DEBUG:--
	# print(vsArray)
	# --
	# Find the index of current measured depth in zData
	depthRow = np.argwhere(zData == measDepth)[0][0]
	# Obtain the reflectivity data, apply vertical shift (circularly), at relevant measured depths
	reflData = np.zeros((31,2042))
	#DEBUG:--
	zDataRefl = np.zeros((31,1))
	originalTraceData = []
	shiftedTraceData = []
	for i in range(-15, 16):
		#DEBUG:--
		zDataRefl[i+15,0] = zData[depthRow + i]
		originalTraceData.append(dataHorizInterp[depthRow + i, :])
		# plt.figure()
		# plt.plot(range(2042), dataHorizInterp[depthRow + i,:])
		# plt.xlabel("radial space")
		# plt.ylabel("reflectivity")
		# plt.title("trace @ md = {}".format(zData[depthRow + i]))
		# plt.show()
		#--
		if i<0:
			if angle>=0:
				reflData[i+15, :] = np.roll(dataHorizInterp[depthRow + i, :], int(-1*vsArray[-i-1]))
			else:
				reflData[i+15, :] = np.roll(dataHorizInterp[depthRow + i, :], int(vsArray[-i-1]))

		elif i>0:
			if angle>=0:
				reflData[i+15, :] = np.roll(dataHorizInterp[depthRow + i, :], int(vsArray[i-1]))
			else:
				reflData[i+15, :] = np.roll(dataHorizInterp[depthRow + i, :], int(-1*vsArray[i-1]))
		else:
			reflData[i+15, :] = dataHorizInterp[depthRow + i, :]
		#DEBUG:--
		shiftedTraceData.append(reflData[i+15, :])
		#--
	#DEBUG:--
	originalTraceData = np.asarray(originalTraceData)
	originalTraceData = np.concatenate((zDataRefl, originalTraceData), axis=1)
	shiftedTraceData = np.asarray(shiftedTraceData)
	shiftedTraceData = np.concatenate((zDataRefl, shiftedTraceData), axis=1)
	#--
	# Sum all the shifted traces at the 31 MDs to get a resultant stacked trace
	sumReflData = np.sum(reflData, axis=0)
	# DEBUG:--
	# plt.figure()
	# plt.plot(range(2042), sumReflData)
	# plt.xlabel("radial space")
	# plt.ylabel("reflectivity")
	# plt.title("Stacked reflectivity with angle = {} @ MD = {}".format(angle, measDepth))
	# plt.show()
	#--
	# Get standard deviation of resultant trace
	stdReflData = np.std(sumReflData)
	return stdReflData, originalTraceData, shiftedTraceData, sumReflData

# Define a function that compares the output (standard deviation) from reflStack function
# for various angles and picks the best angle
def bestAzimuth(measDepth, zData, rStep, dataHorizInterp):
	trialAnglesPos = np.linspace(1, 89, 89)
	trialAnglesNeg = np.linspace(-1, -89, 89)
	trialAngles = np.concatenate((trialAnglesPos, trialAnglesNeg))
	stdAngles = np.zeros(trialAngles.shape)
	# Compute standard deviation of stacked reflectivity trace for all trial angles
	#DEBUG:--
	# traceFile = open('traceStacking.txt', 'w')
	# traceFile.write("Original Trace Data for Fracture Plane @ MD = {}\n".format(measDepth))
	#--
	# plt.figure()
	for i in range(trialAngles.shape[0]):
		depthRow = np.argwhere(zData == measDepth)[0][0]
		if depthRow + 15 > zData.shape[0]-1:
			stdAngles[i] = 0
			break
		stdAngles[i], originalTraceData, shiftedTraceData, sumReflData = reflStack(trialAngles[i], measDepth, zData, rStep, dataHorizInterp)
		#DEBUG: --
		# FIRST TIME, write original trace data
		# if i==0:
		# 	for row in range(originalTraceData.shape[0]):
		# 		for col in range(originalTraceData[row].shape[0]):
		# 			if col==0:
		# 				traceFile.write(str(originalTraceData[row, col]) + "\t")
		# 			elif col % 10 == 0:
		# 				traceFile.write(str(originalTraceData[row, col]) + "\t")
		# 		traceFile.write("\n")
		# 	traceFile.write('\n')
		# 	traceFile.write('\n')
		# # FOR EVERY TRIAL ANGLE, write shifted trace data
		# traceFile.write('Trial Angle = {}\n'.format(trialAngles[i]))
		# for row in range(shiftedTraceData.shape[0]):
		# 	for col in range(shiftedTraceData[row].shape[0]):
		# 		if col==0:
		# 			traceFile.write(str(shiftedTraceData[row, col]) + "\t")
		# 		elif col % 10 == 0:
		# 			traceFile.write(str(shiftedTraceData[row, col]) + "\t")
		# 	traceFile.write("\n")
		# traceFile.write("For angle {}, standard deviation is {}.".format(trialAngles[i], stdAngles[i]))
		# traceFile.write('\n')
		# traceFile.write('\n')
		# print("For angle {}, standard deviation is {}.".format(trialAngles[i], stdAngles[i]))
		# plt.cla()
		# plt.plot(range(2042), sumReflData)
		# plt.xlabel("radial space")
		# plt.ylabel("reflectivity")
		# plt.title("Stacked reflectivity with angle = {} @ MD = {}".format(trialAngles[i], measDepth))
		# plt.pause(0.3)
		#--
	# plt.show()
	# traceFile.close()

	# DEBUG: plot standard deviation vs angle
	# plt.figure()
	# plt.plot(stdAngles, trialAngles, 'b.')
	# plt.xlabel('standard deviation')
	# plt.ylabel('angle')
	# plt.title('angle vs. stdev')
	# plt.show()

	# Pick the angle that corresponds to the largest standard deviation
	indLowestStd = np.argmax(stdAngles)
	bestAngle = trialAngles[indLowestStd]
	return bestAngle

# Using bestAzimuth and reflStack functions defined above, generate azimuth angles
# for all the fracture planes selected in the DFN
azimuthDFN = np.zeros(zDataDFN.shape)
for i in range(zDataDFN.shape[0]):
	azimuthDFN[i] = bestAzimuth(zDataDFN[i], zData, rStep, dataHorizInterp)
# azimuthDFN[41] = bestAzimuth(zDataDFN[41], zData, rStep, dataHorizInterp)

# Convert radial positions (indices) to distances
for i in range(rpDFN.shape[0]):
    rpDFN[i] = rStart+rStep*(256+rpDFN[i])
    rnDFN[i] = rStart+rStep*(256-rnDFN[i])
    rpvDFN[i] = rStart+rStep*(256+rpvDFN[i])
    rnvDFN[i] = rStart+rStep*(256-rnvDFN[i])

# TEMP: PLOTTING TO CHECK VISUALIZATION
# plt.figure(1)
# plt.plot(azimuthDFN, np.arange(1, zDataDFN.shape[0]+1),'r.')
# # plt.ylim(zData[-1], zData[0])
# # plt.ylim(zDataDFN[-1], zDataDFN[0])
# plt.ylabel('Fracture Index')
# plt.xlabel('Fracture Angle')
# # plt.title('Azimuth Variation for Planes in DFN')
# plt.show()

plt.figure(2)
plt.plot(intn, zData, 'r-')
# plt.plot(intnDFN*3, zDataDFN,'b.')
#plt.ylim(zDataAbove[-1], zDataAbove[0])   # invert MD axis for standard log type presentation
plt.ylim(zData[-1], zData[0])
# plt.ylim(zDataDFN[-1], zDataDFN[0])
# plt.ylabel('Fracture Index')
# plt.xlabel('Fracture Angle')
plt.ylabel('measured depth (ft)')
plt.xlabel('intensity')
# plt.title('Azimuth Variation for Planes in DFN')
plt.show()



# ------------------
# FORMATTING OUTPUT (NOTE: NEEDS DECISION BY VISUALIZATION SOFTWARE/DFN MODELLER)
# ------------------

# 1. LOG
# timestr = time.strftime("%Y%m%d-%H%M%S")
# outputFileName = 'logOutput_' + timestr +'.txt'
logOutputID = open(logFilePath, 'w')

# Writing out header lines of LAS file (NOTE: change fields as necessary here)
companyName = 'Marathon Oil'
# wellName = 'DE-03H' # NOTE: already assigned above as input (CHECK)
fieldName = 'Field XYZ'
locationName = 'Location XYZ'
countyName = 'County XYZ'
stateName = 'State XYZ'
countryName = 'Country XYZ'
serviceCompanyName = 'Baker Hughes'
logDate = 'Date XYZ'
apiNumber = 'API ###'
wellID = 'well ###'
apiCode = '99 995 99  1'
logOutputID.write('~Version Information\n')
logOutputID.write(' VERS.                2.00:   CWLS log ASCII Standard -VERSION 2.00\n')
logOutputID.write(' WRAP.                  NO:   One line per frame      \n')
logOutputID.write('~Well Information Block\n')
logOutputID.write('#MNEM.UNIT                  Well Data                   Data Description\n')
logOutputID.write('#----.----   ----------------------------------------   -------------------------------\n')
logOutputID.write(' {0:<9}   {1:>40.4f} : {2:<}\n'.format('STRT.FT', startingDepth, 'Starting Depth'))
logOutputID.write(' {0:<9}   {1:>40.4f} : {2:<}\n'.format('STOP.FT', endingDepth, 'Ending Depth'))
logOutputID.write(' {0:<9}   {1:>40.4f} : {2:<}\n'.format('STEP.FT', 0.5, 'Level Spacing'))
logOutputID.write(' {0:<9}   {1:>40.4f} : {2:<}\n'.format('NULL.', -9999, 'Absent Value'))
logOutputID.write(' {0:<9}   {1:<40} : {2:<}\n'.format('COMP.', companyName, 'Company'))
logOutputID.write(' {0:<9}   {1:<40} : {2:<}\n'.format('WELL.', wellName, 'Well'))
logOutputID.write(' {0:<9}   {1:<40} : {2:<}\n'.format('FLD .', fieldName, 'Field'))
logOutputID.write(' {0:<9}   {1:<40} : {2:<}\n'.format('LOC .', locationName, 'Location'))
logOutputID.write(' {0:<9}   {1:<40} : {2:<}\n'.format('CNTY.', countyName, 'County'))
logOutputID.write(' {0:<9}   {1:<40} : {2:<}\n'.format('STAT.', stateName, 'State'))
logOutputID.write(' {0:<9}   {1:<40} : {2:<}\n'.format('CTRY.', countryName, 'Country'))
logOutputID.write(' {0:<9}   {1:<40} : {2:<}\n'.format('SRVC.', serviceCompanyName, 'Service Company'))
logOutputID.write(' {0:<9}   {1:<40} : {2:<}\n'.format('DATE.', logDate, 'Log Date'))
logOutputID.write(' {0:<9}   {1:<40} : {2:<}\n'.format('API .', apiNumber, 'API Number'))
logOutputID.write(' {0:<9}   {1:<40} : {2:<}\n'.format('UWI .', wellID, 'Unique Well ID'))
logOutputID.write('~Curve Information Block\n')
logOutputID.write('#MNEM    .UNIT        API Codes     Curve Description\n')
logOutputID.write('#--------.--------   ------------   ---------------------------------------------------\n')
logOutputID.write(' {0:<8}.{1:<8}   {2:<12} : {3:<}\n'.format('DEPT', 'FT', apiCode, 'DEPTH'))
logOutputID.write(' {0:<8}.{1:<8}   {2:<12} : {3:<}\n'.format('HZUP', 'FT', apiCode, 'DSWI_HZ_Contour_+'))
logOutputID.write(' {0:<8}.{1:<8}   {2:<12} : {3:<}\n'.format('HZDN', 'FT', apiCode, 'DSWI_HZ_Contour_-'))
logOutputID.write(' {0:<8}.{1:<8}   {2:<12} : {3:<}\n'.format('VTDN', 'FT', apiCode, 'DSWI_VT_Contour_+'))
logOutputID.write(' {0:<8}.{1:<8}   {2:<12} : {3:<}\n'.format('VTUP', 'FT', apiCode, 'DSWI_VT_Contour_-'))
logOutputID.write(' {0:<8}.{1:<8}   {2:<12} : {3:<}\n'.format('INTN', '', apiCode, 'DSWI_TotalFractureIntensity'))

# Writing out log data
logOutputID.write('#  Curve Data\n')
logOutputID.write('~A   DEPT       HZUP      HZDN      VTDN      VTUP      INTN\n')
# All the depths with null intensity values at the beginning until the first MD with usable values
if zData[0] != startingDepth:
	depthIncrementCount = 0
	while startingDepth + 0.5*depthIncrementCount < zData[0]:
		logOutputID.write(' {0:>9.2f} {1:>9.2f} {2:>9.2f} {3:>9.2f} {4:>9.2f} {5:>9.2f}\n'.format(startingDepth + 0.5*depthIncrementCount,
																							-9999,
																							-9999,
																							-9999,
																							-9999,
																							-9999))
		depthIncrementCount += 1
# First MD with usable values
logOutputID.write(' {0:>9.2f} {1:>9.2f} {2:>9.2f} {3:>9.2f} {4:>9.2f} {5:>9.2f}\n'.format(zData[0],
																							rStart+rStep*(256+rPos[0]),
																							rStart+rStep*(256-rNeg[0]),
																							rStart+rStep*(256+rPosVert[0]),
																							rStart+rStep*(256-rNegVert[0]),
																							intn[0]))
# Loop through MDs, adding MDs with null intensity values where MD increment(s) are missing
for iDepth in range(1, nDepth):
	# Recording the missing MDs with null intensity
	if zData[iDepth] - zData[iDepth-1] != 0.5:
		depthIncrementCount = 1
		while zData[iDepth-1] + 0.5*depthIncrementCount < zData[iDepth]:
			logOutputID.write(' {0:>9.2f} {1:>9.2f} {2:>9.2f} {3:>9.2f} {4:>9.2f} {5:>9.2f}\n'.format(zData[iDepth-1] + 0.5*depthIncrementCount,
																							-9999,
																							-9999,
																							-9999,
																							-9999,
																							-9999))
			depthIncrementCount += 1
	# Recording the accounted for MDs with calculated intensity values
	logOutputID.write(' {0:>9.2f} {1:>9.2f} {2:>9.2f} {3:>9.2f} {4:>9.2f} {5:>9.2f}\n'.format(zData[iDepth],
																							rStart+rStep*(256+rPos[iDepth]),
																							rStart+rStep*(256-rNeg[iDepth]),
																							rStart+rStep*(256+rPosVert[iDepth]),
																							rStart+rStep*(256-rNegVert[iDepth]),
																							intn[iDepth]))
# All the depths (if any) with null values after the final MD through the above loop, until the ending depth is reached
if zData[-1] != endingDepth:
	depthIncrementCount = 1
	while zData[-1] + 0.5*depthIncrementCount <= endingDepth:
		logOutputID.write(' {0:>9.2f} {1:>9.2f} {2:>9.2f} {3:>9.2f} {4:>9.2f} {5:>9.2f}\n'.format(zData[-1] + 0.5*depthIncrementCount,
																							-9999,
																							-9999,
																							-9999,
																							-9999,
																							-9999))
		depthIncrementCount += 1
# Close log write file
logOutputID.close()

# 2. TXT output for DFN (TODO: calculate correct values for Easting, Northing TVDSS, Dip and Azimuth; right now only null values given)
dfnOutput = open(txtFilePath, 'w')
dfnOutput.write("MD Easting Northing TVDSS StructureDip StructureAzimuth FracLength FracHeight Area\n")
dfnOutput.write("ft ft ft ft deg deg ft ft sqft\n")
for i in range(zDataDFN.shape[0]):
    dfnOutput.write("{0} {1} {2} {3} {4} {5} {6} {7} {8}\n".format(zDataDFN[i],
                                                            eastingDFN[i],
                                                            northingDFN[i],
                                                            tvdDFN[i],
                                                            90,
															azimuthDFN[i],
															rpDFN[i]-rnDFN[i],
															rpvDFN[i]-rnvDFN[i],
                                                            (rpDFN[i]-rnDFN[i])*(rpvDFN[i]-rnvDFN[i])))
dfnOutput.close()

# return logFilePath

# Run the function defined above
print('Running the read_XMAC.exe program...')
print('...')
# print('From the input data, small magnitude values may be suppressed (read in as 0), which may help with reducing noise in the output log.')
# boolSuppress = input('Is suppressing values desired (y/n)? ')
# if boolSuppress in 'yes':
#     boolSuppress = True
#     print('...')
#     suppressLimit = float(input('Please enter the magnitude threshold below which values should be suppressed? '))
# else:
#     boolSuppress = False
#     suppressLimit = float(8)
print('...')
print('...Generating the log and text file...')
# logFilePath = read_XMAC(boolSuppress, suppressLimit)
print('The log and text file output have been successfully generated. The absolute path of the output log file is {}. The associated text file path is {}.'.format(logFilePath, txtFilePath))
print('\n')
print('The program read_XMAC.exe run was successful.')
print('\n')
endProgram = input('Press RETURN to exit the console...')
