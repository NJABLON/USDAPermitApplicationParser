from tabula import wrapper
import pandas as pd
import numpy as np
import csv, sys, os, glob
from tika import parser
from datetime import datetime

def read_pdf(filename): 
    organismList = []
    organismSection = True
    shippedFromCheck = False
    destinationSection = False
    intendedUseSection = False
    organism = '' 

    raw = parser.from_file(filename)
    pdfstring = raw['content'].replace('\n\n', '\n').replace('\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n', '')

    pdfline = pdfstring.splitlines()    

    for line in pdfline:
        if 'Application Number' in line.strip() or 'APPLICATIONNUMBER:' in line.strip():
            lineSplit = line.strip().split(' ')
            appNumber = lineSplit[-1]
            continue
        if 'DESTINATION' in line.strip():
            destinationSection = True
        if destinationSection:
            if line.strip() == 'Address:':
                addressIndex = pdfline.index(line)
                state = pdfline[addressIndex+1].strip()
                destinationSection = False
                #break
            if 'Street Address:' in line.strip():
                addressSplit = line.strip().split(' ')
                state = addressSplit[-1]
                destinationSection = False
                #break
        if 'DATE' in line.strip() and not 'DATE(S)' in line.strip():
            applicationDate = pdfline[pdfline.index(line) + 1].strip().replace(',', '')
            datetime_object = datetime.strptime(applicationDate, '%b %d %Y')
            appDate = datetime_object.strftime('%m/%d/%Y')
            break            
    
    df = wrapper.read_pdf(filename, pages = "all", multiple_tables= True, lattice=True)

    clean_df = [item.replace('\r',' ', regex=True) for item in df]

    for table in clean_df:    
        for index, row in table.iterrows():
            col1 = row[0]
            col2 = row[1]

            if organismSection:
                organism = row[0]
                classification = row[1]
                shippedFrom = row[4]

            if organism == 'Article':
                organismSection = False
                # break

            if intendedUseSection:
                intendedUse = col2
                break

            if col1 == 'Article' and col2 == 'Intended Use':
                intendedUseSection = True
                continue
            
            if pd.isna(organism) or (not pd.isna(classification) and classification in organism):
               organism = row[1]

            if 'Scientific Names' not in organism and organismSection and 'Article' not in organism:
                organismList.append(organism)

                if not shippedFromCheck:
                    shippedFromInfo = shippedFrom
                    shippedFromCheck = True
        else:
            continue
        break
    
    # need this format to have multiple associations in upload file
    appliedOrganisms = "\"," + ','.join(organismList) + ",\""

    dataList = ['PERMIT', '', '', appNumber, appliedOrganisms, state, shippedFromInfo, appDate, intendedUse]
    csvData.append(dataList)

def create_csv():
    
    with open(pathname + "\\permitApplicationUpload.csv", 'w', newline='') as csvfile:
        filewriter = csv.writer(csvfile)
        filewriter.writerows(csvData)

def main():
	files = glob.glob(pathname + "\\*.pdf")
	print(files)

	for file in files:
	    print("Parsing: " + file)
	    read_pdf(file)
	    
	create_csv()

if __name__ == '__main__': 
    pathname = os.path.dirname(sys.argv[0])

    csvData = []
    csvData.append(['ENTITY TYPE', 'BARCODE', 'Name', 'ApplicationNumber', 'APPLIEDTAXONOMY', 'State', 'ShippedFrom', 'ApplicationDate', 'IntendedUse'])

    main() 