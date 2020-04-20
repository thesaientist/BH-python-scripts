# ESP_ship.py
# This script is for the SHIPPING GROUP BOM in the ESP configurator
import xlwings as xw
import configFunc as cF

# main() is the main subroutine
def main():
    # Define PumpData sheet object
    #wb = xw.Book('ESP_config.xlsm')
    wb = xw.Book.caller()
    pmpDataSht = wb.sheets["PumpData"]
    tmpSht = wb.sheets["TempSheet"]

    # Import Shipping data as an array (list of lists)
    rowSHP = cF.findHeader(pmpDataSht, 'SHIPPING GROUP')
    rowEnd = cF.findHeader(pmpDataSht, 'COAT/PAINT GROUP')
    colEnd = pmpDataSht[rowSHP+1,0].end('right').column
    rngSHP = pmpDataSht[rowSHP+1:rowEnd,0:colEnd].options(empty='').value

    # Determine values for necessary column
    colSeries = rngSHP[0].index("Series")
    colItemN = rngSHP[0].index("Item Notes")
    colDesc = rngSHP[0].index("Description")
    colItemID = rngSHP[0].index("Item ID")

    # Extract pump info from TempSheet and clear TempSheet
    pmpSeries = tmpSht[0,0].value
    tmpSht[0,0].value = ""

    # Initialize BOM elements
    strShippingItemID = "NEW"
    strShippingDescription = "GROUP,PMP " + pmpSeries + " SHIPPING COMPONENTS"
    strShippingItemNotes = ""

    # Find a part number matching the Shipping group (if any existing)
    for rowi in range(1,len(rngSHP)):
        if pmpSeries == rngSHP[rowi][colSeries]:
            strShippingItemID = rngSHP[rowi][colItemID]
            break

    # Write to TempSheet
    tmpSht[0,0].value = strShippingItemID
    tmpSht[0,1].value = strShippingDescription
    tmpSht[0,2].value = strShippingItemNotes
