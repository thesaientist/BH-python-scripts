# ESP_ldf.py
# This script is for the LOWER DIFFUSER BOM in the ESP configurator
import xlwings as xw
import re           # regular expressions module
import configFunc as cF

# main() is the main subroutine
def main():
    # Define PumpData sheet object
    wb = xw.Book.caller()
    pmpDataSht = wb.sheets["PumpData"]
    tmpSht = wb.sheets["TempSheet"]

    # Import LOWER DIFFUSER data as an array (list of lists)
    rowLDF = cF.findHeader(pmpDataSht, 'LOWER DIFFUSER')
    rowEnd = cF.findHeader(pmpDataSht, 'KEYSTOCK')
    colEnd = pmpDataSht[rowLDF+1,0].end('right').column
    rngLDF = pmpDataSht[rowLDF+1:rowEnd,0:colEnd].value

    # Determine values for necessary column
    colSeries = rngLDF[0].index("Series")
    colBPD = rngLDF[0].index("BPD")
    colType1= rngLDF[0].index("Type 1")
    colType2= rngLDF[0].index("Type 2")
    colMat = rngLDF[0].index("Material")
    colCoat = rngLDF[0].index("Coating Material")
    colMS = rngLDF[0].index("MS")
    colItemN = rngLDF[0].index("Item Notes")
    colDesc = rngLDF[0].index("Description")
    colItemID = rngLDF[0].index("Item ID")

    # Extract pump info from TempSheet and clear TempSheet
    pmpSeries = tmpSht[0,0].value
    pmpCapacity = str(tmpSht[1,0].options(numbers=int).value)
    pmpStageType = tmpSht[2,0].value
    pmpStagesMaterial = tmpSht[3,0].value
    pmpCoatingMaterial = tmpSht[4,0].value
    tmpSht[0:5,0].value = ""

    # Other useful associations
    # 1. Stage type
    if pmpStageType in ["FLT","AR-FLT","AR-MDLR"]:
        strStageType = "FLT"
    else:
        strStageType = "CMP"
    # 2. Coating type (if applicable)
    if pmpCoatingMaterial != "N/A":
        boolCoat = True
        strCoating = pmpCoatingMaterial
    else:
        boolCoat = False
        strCoating = None

    # Initialize BOM elements
    strLowerDiffuserItemID = "NEW"
    strLowerDiffuserDescription = "DIFFUSER, LWR " + pmpSeries + pmpCapacity + \
                                    " " + strStageType + " Type2 " + pmpStagesMaterial + "*"
    if boolCoat:
        strLowerDiffuserItemNotes = strCoating
    else:
        strLowerDiffuserItemNotes = ""

    # Find a part number for LOWER DIFFUSER data (if any existing)
    for rowi in range(1,len(rngLDF)):
        if pmpSeries == rngLDF[rowi][colSeries] and \
            pmpCapacity in rngLDF[rowi][colBPD] and \
            strStageType in rngLDF[rowi][colType1] and \
            pmpStagesMaterial == rngLDF[rowi][colMat] and \
            strCoating == rngLDF[rowi][colCoat]:
            strLowerDiffuserItemID = rngLDF[rowi][colItemID]
            strLowerDiffuserDescription = strLowerDiffuserDescription.replace(\
                                        pmpCapacity, rngLDF[rowi][colBPD])
            oldStgType = rngLDF[rowi][colType1]
            if oldStgType == "CMP/FLT":
                newStgType = "C/F"
                strLowerDiffuserDescription = strLowerDiffuserDescription.replace(\
                                            strStageType, newStgType)
            type2Val = rngLDF[rowi][colType2]
            if type2Val != None:
                strLowerDiffuserDescription = strLowerDiffuserDescription.replace(\
                                            "Type2", type2Val)
            break
    # If no part number found, replace Type2 in description with appropriate Type 2 value
    if strLowerDiffuserItemID == "NEW":
        if boolCoat and strCoating != "NDP":
            strLowerDiffuserDescription = strLowerDiffuserDescription.replace(\
                                        "Type2", "P-MACH")
        else:
            strLowerDiffuserDescription = strLowerDiffuserDescription.replace(\
                                        "Type2", "MACH")


    # Write to TempSheet
    tmpSht[0,0].value = strLowerDiffuserItemID
    tmpSht[0,1].value = strLowerDiffuserDescription
    tmpSht[0,2].value = strLowerDiffuserItemNotes
