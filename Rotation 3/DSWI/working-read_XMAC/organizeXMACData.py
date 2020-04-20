################################################################################
##
##    Property of Baker Hughes, a GE Company
##    Copyright 2018
##    Author: Sai Uppati
##    saipranav.uppati@bhge.com
##
################################################################################
# reorganize parsed XMAC data to define useful arrays for tracking measured depth
# and reflectivity data
def organizeXMACData(data, data_vert, boolSuppress, suppressLimit):
    import numpy as np
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

    #--DEBUG--
    # from random import randint
    # i = randint(0, zData.shape[0]-1)
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

    return zData, dataNeg, dataPos, dataNegVert, dataPosVert
