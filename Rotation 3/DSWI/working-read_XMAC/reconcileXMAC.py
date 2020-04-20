################################################################################
##
##    Property of Baker Hughes, a GE Company
##    Copyright 2018
##    Author: Sai Uppati
##    saipranav.uppati@bhge.com
##
################################################################################
# function to reconcile differences between horizontal and vertical XMAC data
def reconcileXMAC(startingDepth, startingDepth_vert, \
                    endingDepth, endingDepth_vert, \
                    data, data_vert):
    # If there is discrepancy between measured depths in horizontal and vertical
    # slices of data, then fix if possible and throw an error if not
    # starting depth index
    import numpy as np
    depthStartIndex = 0
    depthStartIndex_vert = 0
    tempStartDepth = startingDepth
    if startingDepth != startingDepth_vert:
    	if startingDepth > startingDepth_vert:
    		depthStartIndex_vert = np.argwhere(data_vert[:,0] == startingDepth)[0][0]
    	else:
    		depthStartIndex = np.argwhere(data[:,0] == startingDepth_vert)[0][0]
    		tempStartDepth = startingDepth_vert
    # ending depth index
    depthEndIndex = -1
    depthEndIndex_vert = -1
    tempEndDepth = endingDepth
    if endingDepth != endingDepth_vert:
    	if endingDepth > endingDepth_vert:
    		depthEndIndex = np.argwhere(data[:,0] == endingDepth_vert)[0][0]
    		tempEndDepth = endingDepth_vert
    	else:
    		depthEndIndex_vert = np.argwhere(data_vert[:,0] == endingDepth)[0][0]
    # eliminate depth measurements that are outside the mutually compatiable range
    data = data[depthStartIndex:depthEndIndex,:]
    data_vert = data_vert[depthStartIndex_vert:depthEndIndex_vert,:]
    # exit the program if the horizontal and vertical slices don't have the same number of samples
    if data.shape[0] == data_vert.shape[0]:
        startingDepth = tempStartDepth
        endingDepth = tempEndDepth
        isMismatch = False
    else:
        isMismatch = True

    return data, data_vert, startingDepth, endingDepth, isMismatch
