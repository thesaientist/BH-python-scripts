################################################################################
##
##    Property of Baker Hughes, a GE Company
##    Copyright 2018
##    Author: Sai Uppati
##    saipranav.uppati@bhge.com
##
################################################################################
# function to determine cumulative intensity and radial extent based on integral threshold
def radialExtent(integral, dataNeg, dataPos, dataNegVert, dataPosVert, \
                    normNeg, normPos, normNegVert, normPosVert):
    import numpy as np
    # Cumulative sum, ignoring the division by zero warnings (which will later be replaced by 1's)
    with np.errstate(invalid = 'ignore'):
    	cumSumNormNeg = np.divide(np.cumsum(dataNeg, axis=1), normNeg[:,None])
    	cumSumNormPos = np.divide(np.cumsum(dataPos, axis=1), normPos[:,None])
    	cumSumNormNegVert = np.divide(np.cumsum(dataNegVert, axis=1), normNegVert[:,None])
    	cumSumNormPosVert = np.divide(np.cumsum(dataPosVert, axis=1), normPosVert[:,None])
    cumSumNormNeg[np.where(np.isnan(cumSumNormNeg))] = 1
    cumSumNormPos[np.where(np.isnan(cumSumNormPos))] = 1
    cumSumNormNegVert[np.where(np.isnan(cumSumNormNegVert))] = 1
    cumSumNormPosVert[np.where(np.isnan(cumSumNormPosVert))] = 1
    # Radial extent based on reaching threshold integral value for cumul. frac intensity
    nDepth = dataNeg.shape[0]
    rNeg = np.zeros((nDepth,))
    rPos = np.zeros((nDepth,))
    rNegVert = np.zeros((nDepth,))
    rPosVert = np.zeros((nDepth,))
    for row in range(nDepth):
    	rNeg[row] = np.argmax(cumSumNormNeg[row,:] > integral) + 1
    	rPos[row] = np.argmax(cumSumNormPos[row,:] > integral) + 1
    	rNegVert[row] = np.argmax(cumSumNormNegVert[row,:] > integral) + 1
    	rPosVert[row] = np.argmax(cumSumNormPosVert[row,:] > integral) + 1

    return rNeg, rPos, rNegVert, rPosVert
