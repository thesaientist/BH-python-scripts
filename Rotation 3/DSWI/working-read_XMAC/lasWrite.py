################################################################################
##
##    Property of Baker Hughes, a GE Company
##    Copyright 2018
##    Author: Sai Uppati
##    saipranav.uppati@bhge.com
##
################################################################################
# function to write LAS file for radial extents and fracture intensity
def lasWrite(inputData, writeData):
    # timestr = time.strftime("%Y%m%d-%H%M%S")
    # outputFileName = 'logOutput_' + timestr +'.txt'
    logOutputID = open(inputData['log filepath'], 'w')

    # Define values needed for writing file
    companyName = inputData['company']
    wellName = inputData['well']
    fieldName = inputData['field']
    locationName = inputData['location']
    countyName = inputData['county']
    stateName = inputData['state']
    countryName = inputData['country']
    serviceCompanyName = inputData['service company']
    logDate = inputData['log date']
    apiNumber = inputData['api']
    wellID = inputData['well id']
    apiCode = inputData['api code']
    mdStep = inputData['mdStep']
    rStart = inputData['rStart']
    rStep = inputData['rStep']
    startingDepth = writeData['starting depth']
    endingDepth = writeData['ending depth']
    zData = writeData['zData']
    nDepth = zData.shape[0]
    rNeg = writeData['rNeg']
    rPos = writeData['rPos']
    rNegVert = writeData['rNegVert']
    rPosVert = writeData['rPosVert']
    intn = writeData['intn']

    # Writing out header lines of LAS file
    logOutputID.write('~Version Information\n')
    logOutputID.write(' VERS.                2.00:   CWLS log ASCII Standard -VERSION 2.00\n')
    logOutputID.write(' WRAP.                  NO:   One line per frame      \n')
    logOutputID.write('~Well Information Block\n')
    logOutputID.write('#MNEM.UNIT                  Well Data                   Data Description\n')
    logOutputID.write('#----.----   ----------------------------------------   -------------------------------\n')
    logOutputID.write(' {0:<9}   {1:>40.4f} : {2:<}\n'.format('STRT.FT', startingDepth, 'Starting Depth'))
    logOutputID.write(' {0:<9}   {1:>40.4f} : {2:<}\n'.format('STOP.FT', endingDepth, 'Ending Depth'))
    logOutputID.write(' {0:<9}   {1:>40.4f} : {2:<}\n'.format('STEP.FT', mdStep, 'Level Spacing'))
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

    return
