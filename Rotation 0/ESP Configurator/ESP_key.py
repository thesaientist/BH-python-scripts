# ESP_key.py
# This script is for the KEYSTOCK BOM in the ESP configurator
import xlwings as xw
import re           # regular expressions module
import configFunc as cF
from math import ceil

# main() is the main subroutine
def main():
    # Define PumpData sheet object
    wb = xw.Book.caller()
    pmpDataSht = wb.sheets["PumpData"]
    tmpSht = wb.sheets["TempSheet"]
    keySht = wb.sheets["KeystockTable"]

    # Import KEYSTOCK data as an array (list of lists)
    rowKEY = cF.findHeader(pmpDataSht, 'KEYSTOCK')
    rowEnd = cF.findHeader(pmpDataSht, 'COUPLING')
    colEnd = pmpDataSht[rowKEY+1,0].end('right').column
    rngKEY = pmpDataSht[rowKEY+1:rowEnd,0:colEnd].value

    # Determine values for necessary column
    colMat = rngKEY[0].index("Material")
    colItemID = rngKEY[0].index("Item ID")

    # Extract pump info from TempSheet and clear TempSheet
    pmpSeries = tmpSht[0,0].value
    pmpStageType = tmpSht[1,0].value
    pmpHousingNum = tmpSht[2,0].options(numbers=int).value
    pmpShaftSize = tmpSht[3,0].value
    pmpAppType = tmpSht[4,0].value
    tmpSht[0:5,0].value = ""

    # Useful associations
    # 1. Keystock Material
    if pmpStageType in ["AR-MDLR", "Q-PLUS"]:
        strMat = "INC"
    elif pmpAppType in ["UHP","XHT"]:
        strMat = "INC"
    else:
        strMat = "MNL"
    # 2. Keystock length tables
    lrow = keySht[0,0].end('down').row
    lcol = keySht[0,0].end('right').column
    rngTAB = keySht[0:lrow,0:lcol].value
    colSeries = rngTAB[0].index("Series")
    colType = rngTAB[0].index("Type")
    colSize = rngTAB[0].index("Size")
    colHsgNum = rngTAB[0].index("Hsg Num")
    colAval = rngTAB[0].index("A value")
    if pmpSeries == "TA":
        if pmpStageType in ["FLT","AR-FLT","AR-MDLR","Q-PLUS"]:
            strType = "FLT"
            if pmpShaftSize == 0.62:
                subtract_len = 2.028 + 2.580
            else:
                subtract_len = 2.225 + 2.830
        else:
            strType = "CMP"
            if pmpShaftSize == 0.62:
                subtract_len = 1.69 + 0.255 + 0.382 + 2.179
            else:
                subtract_len = 1.69 + 0.382 + 0.382 + 2.142
    # FIX THIS!!!! (JUST TEMPORARY TO AVOID PYTHON ERRORS)
    else:
        subtract_len = 5


    # Calculate keystock quantity
    Aval = 10000    # default value for distinction

    for rowi in range(1,len(rngTAB)):
        if pmpSeries == rngTAB[rowi][colSeries] and \
            strType == rngTAB[rowi][colType] and \
            pmpHousingNum == rngTAB[rowi][colHsgNum] and \
            pmpShaftSize == rngTAB[rowi][colSize]:
            Aval = rngTAB[rowi][colAval]
            break

    intKeystockQuantity = ceil(Aval - subtract_len)

    # Initialize BOM elements
    strKeystockItemID = "NEW"
    strKeystockDescription = "KEYSTOCK," + strMat + " 0.062 SQ (PMP)"
    strKeystockItemNotes = ""

    # Find a part number for KEYSTOCK data (if any existing)
    for rowi in range(1,len(rngKEY)):
        if strMat == rngKEY[rowi][colMat]:
            strKeystockItemID = rngKEY[rowi][colItemID]

    # Write to TempSheet
    tmpSht[0,0].value = strKeystockItemID
    tmpSht[0,1].value = strKeystockDescription
    tmpSht[0,2].value = strKeystockItemNotes
    tmpSht[0,3].value = intKeystockQuantity
