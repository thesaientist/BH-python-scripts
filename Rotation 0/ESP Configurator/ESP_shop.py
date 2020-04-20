# ESP_shop.py
# This script is for the SHOP GROUP BOM in the ESP configurator
import xlwings as xw
import configFunc as cF

# main() is the main subroutine
def main():
    # Define PumpData sheet object
    #wb = xw.Book('ESP_config.xlsm')
    wb = xw.Book.caller()
    pmpDataSht = wb.sheets["PumpData"]
    tmpSht = wb.sheets["TempSheet"]

    # Import Shop data as an array (list of lists)
    rowSHO = cF.findHeader(pmpDataSht, 'SHOP GROUP')
    rowEnd = cF.findHeader(pmpDataSht, 'SHAFT')
    colEnd = pmpDataSht[rowSHO+1,0].end('right').column
    rngSHO = pmpDataSht[rowSHO+1:rowEnd,0:colEnd].value

    # Determine values for necessary column
    colItemN = rngSHO[0].index("Item Notes")
    colDesc = rngSHO[0].index("Description")
    colItemID = rngSHO[0].index("Item ID")

    # Build BOM elements
    strShopItemID = rngSHO[1][colItemID]
    strShopDescription = rngSHO[1][colDesc]
    strShopItemNotes = rngSHO[1][colItemN]

    # Write to TempSheet
    tmpSht[0,0].value = strShopItemID
    tmpSht[0,1].value = strShopDescription
    tmpSht[0,2].value = strShopItemNotes
