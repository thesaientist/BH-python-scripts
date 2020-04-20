# ESP_spacerOrg.py
# This script organizes the SPACER GROUP data in the ESP configurator
import xlwings as xw
import re           # regular expressions module
import configFunc as cF

# main() is the main subroutine
def main():
    # Define PumpData sheet object
    #wb = xw.Book('ESP_config.xlsm')
    wb = xw.Book.caller()
    pmpDataSht = wb.sheets["PumpData"]

    # Import SPACER data as an array (list of lists)
    rowSPC = cF.findHeader(pmpDataSht, 'SPACER GROUP')
    rowEnd = cF.findHeader(pmpDataSht, 'SHIPPING GROUP')
    colEnd = pmpDataSht[rowSPC+1,0].end('right').column
    rngSPC = pmpDataSht[rowSPC+1:rowEnd,0:colEnd].options(empty='').value

    # Determine values for necessary column
    colShaftSize = rngSPC[0].index("Shaft Size")
    colMat = rngSPC[0].index("Material")
    colItemN = rngSPC[0].index("Item Notes")
    colDesc = rngSPC[0].index("Description")

    # Useful info
    shaftList = ["5/8","11/16","1/2","7/8",".50",".62",".69",".88"]
    shaftdict = {"5/8":0.62, "11/16":0.69, "1/2":0.5, "7/8":0.88, ".50":0.5, \
                ".62": 0.62, ".69": 0.69, ".88": 0.88}
    strMaterial = ["304","N1"]

    # Main loop that populates the array (list of lists) for COM PART group data
    for rowi in range(1,len(rngSPC)):
        desc = rngSPC[rowi][colDesc]
        itemN = rngSPC[rowi][colItemN]
        spcExtDesc = desc + " " + itemN
        # Shaft size
        for siz in shaftList:
            if siz in spcExtDesc and siz in shaftdict:
                rngSPC[rowi][colShaftSize] = shaftdict[siz]
        # Material (standard is 304 going forward)
        for mat in strMaterial:
            if mat in spcExtDesc:
                rngSPC[rowi][colMat] = mat

    # Export modified O-RING GROUP data back to worksheet
    pmpDataSht[rowSPC+2,0].value = rngSPC[1:]
