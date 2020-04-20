# ESP_spacer.py
# This script is for SPACER GROUP BOM in the ESP configurator
import xlwings as xw
import configFunc as cF

# main() is the main subroutine
def main():
    # Define PumpData sheet object
    #wb = xw.Book('ESP_config.xlsm')
    wb = xw.Book.caller()
    pmpDataSht = wb.sheets["PumpData"]
    tmpSht = wb.sheets["TempSheet"]

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
    colItemID = rngSPC[0].index("Item ID")

    # Extract pump info from TempSheet and clear TempSheet
    pmpShaftSize = tmpSht[0,0].value
    tmpSht[0,0].value = ""

    # Material for SPACER (304 is standard going forward)
    if pmpShaftSize == 0.50:
        strMat = "N1"
    elif pmpShaftSize in [0.62, 0.69, 0.88]:
        strMat = "304"

    # Shaft size association to fraction
    if pmpShaftSize == 0.62:
        strShaftSize = "5/8"
    elif pmpShaftSize == 0.69:
        strShaftSize = "11/16"
    elif pmpShaftSize == 0.5:
        strShaftSize = "1/2"
    elif pmpShaftSize == 0.88:
        strShaftSize = "7/8"

    # Initialize the BOM elements
    strSpacerItemID = "NEW"
    strSpacerDescription = "GROUP,SPACER IMPELLER " + strShaftSize + " " + \
                            strMat
    strSpacerItemNotes = ""

    # Find a part number matching the SPACER group (if any existing)
    for rowi in range(1,len(rngSPC)):
        if pmpShaftSize == rngSPC[rowi][colShaftSize]:
            dataMat = rngSPC[rowi][colMat]
            if str(int(dataMat)) == "304":
                compDataMat = "304"
            else:
                compDataMat = dataMat
            if strMat == compDataMat:
                strSpacerItemID = rngSPC[rowi][colItemID]
                break

    # Write to TempSheet
    tmpSht[0,0].value = strSpacerItemID
    tmpSht[0,1].value = strSpacerDescription
    tmpSht[0,2].value = strSpacerItemNotes
