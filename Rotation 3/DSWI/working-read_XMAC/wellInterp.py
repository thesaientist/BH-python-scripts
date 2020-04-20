################################################################################
##
##    Property of Baker Hughes, a GE Company
##    Copyright 2018
##    Author: Sai Uppati
##    saipranav.uppati@bhge.com
##
################################################################################
# Define function to interpolate Easting, Northing, and TVD for a given MD, if
# well survey data with Easting, Northing, TVD and MD values are provided
def wellInterp(md, wellSurveyData):
    # Assuming columns are ordered like Easting, Northing, TVD and MD
    # find the two rows of data closest to given md for interpolation
    import numpy as np
    closestIndex = np.argmin(abs(md - wellSurveyData[:,3]))
    if wellSurveyData[closestIndex, 3] < md:
        lowerIndex = closestIndex
        upperIndex = closestIndex + 1
    else:
        lowerIndex = closestIndex - 1
        upperIndex = closestIndex

    # Endpoints to use in linear interpolation
    e0 = wellSurveyData[lowerIndex,0]
    e1 = wellSurveyData[upperIndex,0]
    n0 = wellSurveyData[lowerIndex,1]
    n1 = wellSurveyData[upperIndex,1]
    tvd0 = wellSurveyData[lowerIndex,2]
    tvd1 = wellSurveyData[upperIndex,2]
    md0 = wellSurveyData[lowerIndex,3]
    md1 = wellSurveyData[upperIndex,3]

    # linear interpolation
    Easting = (e1-e0)/(md1-md0)*(md-md0) + e0
    Northing = (n1-n0)/(md1-md0)*(md-md0) + n0
    TVD = (tvd1-tvd0)/(md1-md0)*(md-md0) + tvd0

    return Easting, Northing, TVD
