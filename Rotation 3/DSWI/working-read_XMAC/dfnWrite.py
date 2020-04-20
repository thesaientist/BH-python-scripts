################################################################################
##
##    Property of Baker Hughes, a GE Company
##    Copyright 2018
##    Author: Sai Uppati
##    saipranav.uppati@bhge.com
##
################################################################################
# function to write the DFN text file with a point set of all the selected fracture planes,
# their respective coordinates and properties
def dfnWrite(inputData, writeData):
    # Define values needed for write point set text file
    zDataDFN = writeData['zDataDFN']
    eastingDFN = writeData['eastingDFN']
    northingDFN = writeData['northingDFN']
    tvdDFN = writeData['tvdDFN']
    azimuthDFN = writeData['azimuthDFN']
    rpDFN = writeData['rpDFN']
    rnDFN = writeData['rnDFN']
    rpvDFN = writeData['rpvDFN']
    rnvDFN = writeData['rnvDFN']

    # Write file
    dfnOutput = open(inputData['text filepath'], 'w')
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

    return
