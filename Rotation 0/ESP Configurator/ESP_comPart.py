# ESP_comPart.py
# This script is to generate COMMON group BOM in the ESP configurator
import xlwings as xw
import re
import configFunc as cF

# main() is the main subroutine
def main():
    # Define PumpData sheet object
    wb = xw.Book.caller()
    pmpDataSht = wb.sheets["PumpData"]
    tmpSht = wb.sheets["TempSheet"]

    # Import COMMON (com parts) data as an array (list of lists)
    rowCOM = cF.findHeader(pmpDataSht, 'COMMON')
    rowEnd = cF.findHeader(pmpDataSht, 'STAGE GROUP')
    colEnd = pmpDataSht[rowCOM+1,0].end('right').column
    rngCOM = pmpDataSht[rowCOM+1:rowEnd,0:colEnd].options(empty='').value

    # Determine values for necessary column
    colSeries = rngCOM[0].index("Series")
    colStgType = rngCOM[0].index("Stage Type")
    colShaftSize = rngCOM[0].index("Shaft Size")
    colDesignation = rngCOM[0].index("Designation")
    colItemN = rngCOM[0].index("Item Notes")
    colDesc = rngCOM[0].index("Description")
    colItemID = rngCOM[0].index("Item ID")

    # Extract pump info from TempSheet and clear TempSheet
    pmpSeries = tmpSht[0,0].value
    pmpStageType = tmpSht[1,0].value
    pmpShaftSize = tmpSht[2,0].value
    pmpExternal = tmpSht[3,0].value
    pmpAppType = tmpSht[4,0].value
    tmpSht[0:5,0].value = ""

    # Stage type association for COM PART group
    if pmpStageType in ["FLT", "AR-FLT"]:
        strComStageType = "AR-FLT"
    elif pmpStageType in ["CMP", "AR-CMP"]:
        strComStageType = "AR-CMP"
    elif pmpStageType == "AR-MDLR":
        strComStageType = "AR-MDLR"
    elif pmpStageType == "Q-PLUS":
        strComStageType = "Q-PLUS"

    # Shaft size converted to a string of the correct format for COM PART group
    shaftSizeMatch = re.search("\.\d+", str(pmpShaftSize))
    strShaftSize = shaftSizeMatch.group(0)

    # Special designation based on desired pump configuration
    if pmpExternal == "NLP":
        strDesignation = "NLP"
    elif pmpAppType in ["UHP", "WAG"]:
        strDesignation = pmpAppType
    else:
        strDesignation = ""

    # Initialize the BOM elements
    strComItemID = "NEW"
    strComDescription = "COM PART,PMP " + pmpSeries + " " + strComStageType + " " + \
                        strShaftSize
    if strDesignation != "":
        strComDescription = strComDescription + "*"
    strComItemNotes = strDesignation

    # Find a part number matching the COM PART group (if any existing)
    for rowi in range(1,len(rngCOM)):
        if pmpSeries == rngCOM[rowi][colSeries] and \
            strComStageType == rngCOM[rowi][colStgType] and \
            pmpShaftSize == rngCOM[rowi][colShaftSize] and \
            strDesignation == rngCOM[rowi][colDesignation]:
            strComItemID = rngCOM[rowi][colItemID]
            break

    # Write to TempSheet
    tmpSht[0,0].value = strComItemID
    tmpSht[0,1].value = strComDescription
    tmpSht[0,2].value = strComItemNotes
