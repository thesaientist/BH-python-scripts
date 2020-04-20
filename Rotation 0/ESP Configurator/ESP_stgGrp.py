# ESP_stgGrp.py
# This script is for the STAGE GROUP BOM in the ESP configurator
import xlwings as xw
import configFunc as cF

# main() is the main subroutine
def main():
    # Define PumpData sheet object
    wb = xw.Book.caller()
    #wb = xw.Book("ESP_config.xlsm")
    pmpDataSht = wb.sheets["PumpData"]
    tmpSht = wb.sheets["TempSheet"]

    # Import STAGE GROUP data as an array (list of lists)
    rowSTG = cF.findHeader(pmpDataSht, 'STAGE GROUP')
    rowEnd = cF.findHeader(pmpDataSht, 'H&B GROUP')
    colEnd = pmpDataSht[rowSTG+1,0].end('right').column
    rngSTG = pmpDataSht[rowSTG+1:rowEnd,0:colEnd].options(empty='').value

    # Determine values for necessary column
    colSeries = rngSTG[0].index("Series")
    colBPD = rngSTG[0].index("BPD")
    colStgType = rngSTG[0].index("Stage Type")
    colTemp = rngSTG[0].index("Temperature")
    colUPR = rngSTG[0].index("UPR")
    colOring = rngSTG[0].index("O-Ring Material")
    colMat = rngSTG[0].index("Material")
    colCoat = rngSTG[0].index("Coating Type")
    colItemN = rngSTG[0].index("Item Notes")
    colDesc = rngSTG[0].index("Description")
    colItemID = rngSTG[0].index("Item ID")

    # Extract pump info from TempSheet and clear TempSheet
    pmpSeries = tmpSht[0,0].value
    pmpCapacity = tmpSht[1,0].options(numbers=int).value
    pmpStageType = tmpSht[2,0].value
    pmpStageCount = tmpSht[3,0].options(numbers=int).value
    if "AR" in pmpStageType or "Q" in pmpStageType:
        pmpBearingCount = tmpSht[4,0].options(numbers=int).value
    pmpStagesMaterial = tmpSht[5,0].value
    pmpOringMaterial = tmpSht[6,0].value
    pmpCoatingMaterial = tmpSht[7,0].value
    pmpAppType = tmpSht[8,0].value
    tmpSht[0:9,0].value = ""

    # Other useful info
    noOringList = ["TA400","TA550","TA900","TA1200","TA1500"]

    # -------------------------------------------------------------------------
    # Initialize REGULAR stage group (for both AR and non-AR pumps)
    # -------------------------------------------------------------------------

    # Item ID initialized as "NEW"
    strStgGrpItemID = "NEW"

    # REGULAR stage group description
    strStgGrpDescription = "GROUP,STAGE " + pmpSeries + str(pmpCapacity)
    # Check whether pump configuration is AR/Q-plus, which then requires modification
    # in the REGULAR stage group description of stage type
    if "AR" in pmpStageType:
        strStgGrpDescription = strStgGrpDescription + " " + pmpStageType[3:]
        strStgType = pmpStageType[3:]      # For use when matching part numbers
    elif "Q" in pmpStageType:
        strStgGrpDescription = strStgGrpDescription + " " + "MDLR"
        strStgType = "MDLR"
    else:
        strStgGrpDescription = strStgGrpDescription + " " + pmpStageType
        strStgType = pmpStageType
    # Add O-ring material to description if not in the noOringList
    # ****************EXCEPTIONS: pumps with Quad Rings****************
    if pmpSeries == "TA":
        if pmpSeries+str(pmpCapacity) in noOringList:
            strStgGrpDescription = strStgGrpDescription + "*"
            strOring = ""             # For use when matching part numbers
        else:
            strStgGrpDescription = strStgGrpDescription + " " + pmpOringMaterial + "*"
            strOring = pmpOringMaterial
    elif pmpSeries == "TD":
        strStgGrpDescription = strStgGrpDescription + " EPDM*"
        strOring = "EPDM"

    # Item notes
    strStgGrpItemNotes = pmpStagesMaterial
    strCoating = ""               # For use when matching part numbers
    # Add coating material to item notes if applicable
    if pmpCoatingMaterial != "N/A":
        strStgGrpItemNotes = strStgGrpItemNotes + " " + pmpCoatingMaterial
        strCoating = pmpCoatingMaterial

    #--------------------------------O-----------------------------------------

    # Determine REGULAR and AR (bearing) stage counts (if any)
    if "AR" in pmpStageType:
        strStgCount = pmpStageCount - pmpBearingCount + 2
        strARStgCount = pmpBearingCount - 2
    elif "Q" in pmpStageType:
        strStgCount = pmpStageCount - pmpBearingCount + 2
        strQpStgCount = pmpBearingCount - 3
        strQpUPRStgCount = 1
    else:
        strStgCount = pmpStageCount

    # -------------------------------------------------------------------------
    # Initialize AR stage group (ONLY for AR pumps)
    # -------------------------------------------------------------------------

    if "AR" in pmpStageType:
        # Item ID initialized as "NEW"
        strARStgGrpItemID = "NEW"

        # AR stage group description
        strARStgGrpDescription = "GROUP,STAGE " + pmpSeries + str(pmpCapacity) + " " \
                                + pmpStageType
        # Add O-ring material to description if not in the noOringList
        # ****************EXCEPTIONS: pumps with Quad Rings****************
        if pmpSeries == "TA":
            if pmpSeries+str(pmpCapacity) in noOringList:
                strARStgGrpDescription = strARStgGrpDescription + "*"
                strAROring = ""             # For use when matching part numbers
            else:
                strARStgGrpDescription = strARStgGrpDescription + " " + pmpOringMaterial + "*"
                strAROring = pmpOringMaterial
        elif pmpSeries == "TD":
            strARStgGrpDescription = strARStgGrpDescription + " EPDM*"
            strAROring = "EPDM"

        # Item notes
        strARStgGrpItemNotes = pmpStagesMaterial
        strARCoating = ""             # For use when matching part numbers
        # Add coating material to item notes if applicable
        if pmpCoatingMaterial != "N/A":
            strARStgGrpItemNotes = strARStgGrpItemNotes + " " + pmpCoatingMaterial
            strARCoating = pmpCoatingMaterial

    # -------------------------------------------------------------------------
    # Initialize Q+ & Q+ UPR stage group (ONLY for Q+ pumps)
    # -------------------------------------------------------------------------

    if "Q" in pmpStageType:
        # Item ID initialized as "NEW"
        strQpStgGrpItemID = "NEW"

        # Q+ stage group description
        strQpStgGrpDescription = "GROUP,STAGE " + pmpSeries + str(pmpCapacity) + " " \
                                + pmpStageType
        # Add O-ring material to description if not in the noOringList
        # ****************EXCEPTIONS: pumps with Quad Rings****************
        if pmpSeries == "TA":
            if pmpSeries+str(pmpCapacity) in noOringList:
                strQpStgGrpDescription = strQpStgGrpDescription + "*"
                strQpOring = ""             # For use when matching part numbers
            else:
                strQpStgGrpDescription = strQpStgGrpDescription + " " + pmpOringMaterial + "*"
                strQpOring = pmpOringMaterial
        elif pmpSeries == "TD":
            strQpStgGrpDescription = strQpStgGrpDescription + " EPDM*"
            strQpOring = "EPDM"

        # Item notes
        strQpStgGrpItemNotes = pmpStagesMaterial
        strQpCoating = ""             # For use when matching part numbers
        # Add coating material to item notes if applicable
        if pmpCoatingMaterial != "N/A":
            strQpStgGrpItemNotes = strQpStgGrpItemNotes + " " + pmpCoatingMaterial
            strQpCoating = pmpCoatingMaterial

        # Q+ UPR stage Item ID initialized as "NEW"
        strQpUPRStgGrpItemID = "NEW"

        # Q+ UPRstage group description
        strQpUPRStgGrpDescription = "GROUP,STAGE " + pmpSeries + str(pmpCapacity) + " " \
                                + pmpStageType + "-UPR"
        # Add O-ring material to description if not in the noOringList
        # ****************EXCEPTIONS: pumps with Quad Rings****************
        if pmpSeries == "TA":
            if pmpSeries+str(pmpCapacity) in noOringList:
                strQpUPRStgGrpDescription = strQpUPRStgGrpDescription + "*"
                strQpUPROring = ""             # For use when matching part numbers
            else:
                strQpUPRStgGrpDescription = strQpUPRStgGrpDescription + " " + pmpOringMaterial + "*"
                strQpUPROring = pmpOringMaterial
        elif pmpSeries == "TD":
            strQpUPRStgGrpDescription = strQpUPRStgGrpDescription + " EPDM*"
            strQpUPROring = "EPDM"

        # Item notes
        strQpUPRStgGrpItemNotes = pmpStagesMaterial
        strQpUPRCoating = ""             # For use when matching part numbers
        # Add coating material to item notes if applicable
        if pmpCoatingMaterial != "N/A":
            strQpUPRStgGrpItemNotes = strQpUPRStgGrpItemNotes + " " + pmpCoatingMaterial
            strQpUPRCoating = pmpCoatingMaterial

    # Application type designation
    if pmpAppType == "XHT":
        strApp = "XHT"
    else:
        strApp = ""

    #--------------------------------O-----------------------------------------

    # Find a part number for REGULAR stage group matching the STAGE GROUP data (if any existing)
    for rowi in range(1,len(rngSTG)):
        if pmpSeries == rngSTG[rowi][colSeries] and \
            pmpCapacity == rngSTG[rowi][colBPD] and \
            strStgType in rngSTG[rowi][colStgType] and \
            "AR" not in rngSTG[rowi][colStgType] and \
            "Q" not in rngSTG[rowi][colStgType] and \
            strOring == rngSTG[rowi][colOring] and \
            pmpStagesMaterial == rngSTG[rowi][colMat] and \
            strCoating == rngSTG[rowi][colCoat] and \
            strApp == rngSTG[rowi][colTemp]:
            strStgGrpItemID = rngSTG[rowi][colItemID]
            oldStgType = rngSTG[rowi][colStgType]
            if oldStgType == "CMP/MDLR":
                newStgType = "C/MDLR"
                strStgGrpDescription = strStgGrpDescription.replace(strStgType,\
                                        newStgType)
            elif oldStgType == "CMP/FLT":
                newStgType = "C/F"
                strStgGrpDescription = strStgGrpDescription.replace(strStgType,\
                                    newStgType)
            break

    # If no matching part number found and if pump type is a TA series AR-MDLR,
    # try to find a match with CMP stage type (done CURRENTLY for TA550, TA900
    # and TA1200)
    if pmpSeries == "TA" and pmpStageType == "AR-MDLR" and strStgGrpItemID == "NEW":
        for rowi in range(1,len(rngSTG)):
            if pmpSeries == rngSTG[rowi][colSeries] and \
                pmpCapacity == rngSTG[rowi][colBPD] and \
                "CMP" == rngSTG[rowi][colStgType] and \
                strOring == rngSTG[rowi][colOring] and \
                pmpStagesMaterial == rngSTG[rowi][colMat] and \
                strCoating == rngSTG[rowi][colCoat] and \
                strApp == rngSTG[rowi][colTemp]:
                strStgGrpItemID = rngSTG[rowi][colItemID]
                strStgGrpDescription = strStgGrpDescription.replace("MDLR","CMP")
                break

    # Find a part number for AR stage group matching the STAGE GROUP data (if any existing)
    if "AR" in pmpStageType:
        for rowi in range(1,len(rngSTG)):
            if pmpSeries == rngSTG[rowi][colSeries] and \
                pmpCapacity == rngSTG[rowi][colBPD] and \
                pmpStageType[3:] in rngSTG[rowi][colStgType] and \
                "AR" in rngSTG[rowi][colStgType] and \
                strAROring == rngSTG[rowi][colOring] and \
                pmpStagesMaterial == rngSTG[rowi][colMat] and \
                strARCoating == rngSTG[rowi][colCoat] and \
                strApp == rngSTG[rowi][colTemp]:
                strARStgGrpItemID = rngSTG[rowi][colItemID]
                oldStgType = rngSTG[rowi][colStgType]
                if oldStgType == "AR-CMP/FLT":
                    newStgType = "AR-C/F"
                    strStgGrpDescription = strStgGrpDescription.replace(pmpStageType,\
                                        newStgType)
                break

    # Find a part number for Q+ stage group matching the STAGE GROUP data (if any existing)
    if "Q" in pmpStageType:
        # For Q+ stage
        for rowi in range(1,len(rngSTG)):
            if pmpSeries == rngSTG[rowi][colSeries] and \
                pmpCapacity == rngSTG[rowi][colBPD] and \
                "Q-PLUS" == rngSTG[rowi][colStgType] and \
                "" == rngSTG[rowi][colUPR] and \
                strQpOring == rngSTG[rowi][colOring] and \
                pmpStagesMaterial == rngSTG[rowi][colMat] and \
                strQpCoating == rngSTG[rowi][colCoat] and \
                strApp == rngSTG[rowi][colTemp]:
                strQpStgGrpItemID = rngSTG[rowi][colItemID]
                break
        # For Q+ UPR stage
        for rowi in range(1,len(rngSTG)):
            if pmpSeries == rngSTG[rowi][colSeries] and \
                pmpCapacity == rngSTG[rowi][colBPD] and \
                "Q-PLUS" == rngSTG[rowi][colStgType] and \
                "UPR" == rngSTG[rowi][colUPR] and \
                strQpUPROring == rngSTG[rowi][colOring] and \
                pmpStagesMaterial == rngSTG[rowi][colMat] and \
                strQpUPRCoating == rngSTG[rowi][colCoat] and \
                strApp == rngSTG[rowi][colTemp]:
                strQpUPRStgGrpItemID = rngSTG[rowi][colItemID]
                break

    # Write to TempSheet
    tmpSht[0,0].value = strStgGrpItemID
    tmpSht[0,1].value = strStgCount
    tmpSht[0,2].value = strStgGrpDescription
    tmpSht[0,3].value = strStgGrpItemNotes
    if "AR" in pmpStageType:
        tmpSht[1,0].value = strARStgGrpItemID
        tmpSht[1,1].value = strARStgCount
        tmpSht[1,2].value = strARStgGrpDescription
        tmpSht[1,3].value = strARStgGrpItemNotes
    elif "Q" in pmpStageType:
        tmpSht[1,0].value = strQpStgGrpItemID
        tmpSht[1,1].value = strQpStgCount
        tmpSht[1,2].value = strQpStgGrpDescription
        tmpSht[1,3].value = strQpStgGrpItemNotes
        tmpSht[2,0].value = strQpUPRStgGrpItemID
        tmpSht[2,1].value = strQpUPRStgCount
        tmpSht[2,2].value = strQpUPRStgGrpDescription
        tmpSht[2,3].value = strQpUPRStgGrpItemNotes
