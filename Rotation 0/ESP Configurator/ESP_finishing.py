# ESP_finishing.py
# This script is for the COAT/PAINT GROUP BOM in the ESP configurator
import xlwings as xw
import configFunc as cF

# main() is the main subroutine
def main():
    # Define PumpData sheet object
    #wb = xw.Book('ESP_config.xlsm')
    wb = xw.Book.caller()
    pmpDataSht = wb.sheets["PumpData"]
    tmpSht = wb.sheets["TempSheet"]

    # Import Coat/paint data as an array (list of lists)
    rowFIN = cF.findHeader(pmpDataSht, 'COAT/PAINT GROUP')
    rowEnd = cF.findHeader(pmpDataSht, 'SHOP GROUP')
    colEnd = pmpDataSht[rowFIN+1,0].end('right').column
    rngFIN = pmpDataSht[rowFIN+1:rowEnd,0:colEnd].value

    # Determine values for necessary column
    colType = rngFIN[0].index("Category")
    colItemN = rngFIN[0].index("Item Notes")
    colDesc = rngFIN[0].index("Description")
    colItemID = rngFIN[0].index("Item ID")

    # Extract pump info from TempSheet and clear TempSheet
    pmpFinish = tmpSht[0,0].value
    tmpSht[0,0].value = ""

    # Finish type designation
    if pmpFinish == "Paint":
        strFinishType = "PAINT"
    elif pmpFinish == "Monel Coating":
        strFinishType = "COAT"

    # Initialize BOM elements
    strFinishItemID = "NEW"
    strFinishDescription = strFinishType
    strFinishItemNotes = ""

    # Find a part number matching the coat/paint group (if any existing)
    for rowi in range(1,len(rngFIN)):
        if strFinishType == rngFIN[rowi][colType]:
            strFinishItemID = rngFIN[rowi][colItemID]
            strFinishDescription = rngFIN[rowi][colDesc]
            strFinishItemNotes = rngFIN[rowi][colItemN]
            break

    # Write to TempSheet
    tmpSht[0,0].value = strFinishItemID
    tmpSht[0,1].value = strFinishDescription
    tmpSht[0,2].value = strFinishItemNotes
