# ESP_oring.py
# This script is for the O-RING GROUP BOM in the ESP configurator
import xlwings as xw
import configFunc as cF

# main() is the main subroutine
def main():
    # Define PumpData sheet object
    #wb = xw.Book('ESP_config.xlsm')
    wb = xw.Book.caller()
    pmpDataSht = wb.sheets["PumpData"]
    tmpSht = wb.sheets["TempSheet"]

    # Import H&B GROUP data as an array (list of lists)
    rowOR = cF.findHeader(pmpDataSht, 'O-RING GROUP')
    rowEnd = cF.findHeader(pmpDataSht, 'SPACER GROUP')
    colEnd = pmpDataSht[rowOR+1,0].end('right').column
    rngOR = pmpDataSht[rowOR+1:rowEnd,0:colEnd].options(empty='').value

    # Determine values for necessary column
    colSeries = rngOR[0].index("Series")
    colMat = rngOR[0].index("Material")
    colDuro = rngOR[0].index("Durometer")
    colTyp = rngOR[0].index("Type Designation")
    colApp = rngOR[0].index("Application")
    colItemN = rngOR[0].index("Item Notes")
    colDesc = rngOR[0].index("Description")
    colItemID = rngOR[0].index("Item ID")

    # Extract pump info from TempSheet and clear TempSheet
    pmpSeries = tmpSht[0,0].value
    pmpStageType = tmpSht[1,0].value
    pmpOringMaterial = tmpSht[2,0].value
    pmpDuro = tmpSht[3,0].options(numbers=int).value
    pmpApp = tmpSht[4,0].value
    tmpSht[0:4,0].value = ""

    # Type designation & App designations
    # 1. Type designation
    if pmpStageType in ["FLT","AR-FLT","AR-MDLR","Q-PLUS"]:
        strTypeDesig = "FLT"
    else:
        strTypeDesig = "CMP"
    # 2. Application type
    if pmpApp in ["UHP","XHT"]:
        strApp = pmpApp
    else:
        strApp = ""

    # Initialize the BOM elements
    strOringItemID = "NEW"
    strOringDescription = "GROUP,PMP " + pmpSeries + " O-RING " + pmpOringMaterial + \
                            " " + str(pmpDuro) + "*"
    strOringItemNotes = strTypeDesig + " " + strApp

    # Find a part number matching the O-RING group (if any existing)
    for rowi in range(1,len(rngOR)):
        if pmpSeries == rngOR[rowi][colSeries] and \
            strTypeDesig == rngOR[rowi][colTyp] and \
            pmpOringMaterial == rngOR[rowi][colMat] and \
            pmpDuro == rngOR[rowi][colDuro] and \
            strApp == rngOR[rowi][colApp]:
            strOringItemID = rngOR[rowi][colItemID]
            break

    # Write to TempSheet
    tmpSht[0,0].value = strOringItemID
    tmpSht[0,1].value = strOringDescription
    tmpSht[0,2].value = strOringItemNotes
