################################################################################
##
##    Property of Baker Hughes, a GE Company
##    Copyright 2018
##    Author: Sai Uppati
##    saipranav.uppati@bhge.com
##
################################################################################
# function to smooth the reflectivity data radially over 7 points at a time
def radialXMACSmoothing(dataNeg, dataPos, dataNegVert, dataPosVert, zData):
    # Smoothing 7 points
    dataNegSmoothed = dataNeg
    dataPosSmoothed = dataPos
    dataNegVertSmoothed = dataNegVert
    dataPosVertSmoothed = dataPosVert
    import numpy as np
    for col in range(3,dataNeg.shape[1]-3):
    	dataNegSmoothed[:, col] = np.mean(dataNeg[:, col-3:col+3], axis=1)
    	dataPosSmoothed[:, col] = np.mean(dataPos[:, col-3:col+3], axis=1)
    	dataNegVertSmoothed[:, col] = np.mean(dataNegVert[:, col-3:col+3], axis=1)
    	dataPosVertSmoothed[:, col] = np.mean(dataPosVert[:, col-3:col+3], axis=1)
    dataNeg = dataNegSmoothed
    dataPos = dataPosSmoothed
    dataNegVert = dataNegVertSmoothed
    dataPosVert = dataPosVertSmoothed

    #--DEBUG--
    # import matplotlib.pyplot as plt
    # plt.figure()
    # plt.subplot(2,2,1)
    # plt.plot(np.arange(1,257), dataNeg[i, :])
    # plt.xlabel('radial space')
    # plt.ylabel('reflectivity')
    # plt.title('dataNeg @ MD {}'.format(zData[i]))
    # plt.subplot(2,2,2)
    # plt.plot(np.arange(1,257), dataPos[i, :])
    # plt.xlabel('radial space')
    # plt.ylabel('reflectivity')
    # plt.title('dataPos @ MD {}'.format(zData[i]))
    # plt.subplot(2,2,3)
    # plt.plot(np.arange(1,257), dataNegVert[i, :])
    # plt.xlabel('radial space')
    # plt.ylabel('reflectivity')
    # plt.title('dataNegVert @ MD {}'.format(zData[i]))
    # plt.subplot(2,2,4)
    # plt.plot(np.arange(1,257), dataPosVert[i, :])
    # plt.xlabel('radial space')
    # plt.ylabel('reflectivity')
    # plt.title('dataPosVert @ MD {}'.format(zData[i]))
    # plt.show()

    return dataNeg, dataPos, dataNegVert, dataPosVert

# function to smooth the fracture radial extent and fracture intensity in depth
# with a weighted filter
def depthXMACSmoothing(rNeg, rPos, rNegVert, rPosVert, intn):
    # Smoothing in depth (both radial extent and intensity)
    # 1. Radii
    rNegSmoothed = rNeg
    rPosSmoothed = rPos
    rNegVertSmoothed = rNegVert
    rPosVertSmoothed = rPosVert
    import numpy as np
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

    return rNeg, rPos, rNegVert, rPosVert, intn
