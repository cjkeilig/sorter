#
# This program will sort OCR'ed pdfs by rules in config file
#

from whoosh.index import create_in
from whoosh.fields import *
from whoosh.qparser import QueryParser
from subprocess import call
import time
import shutil
import os

#Moving files, includes duplicating checking behavior
def move(fName, start, end):
    if fName in os.listdir(end):
        fNameOld = fName
        fName = fName.replace(".pdf", "_"+str(time.clock())+".pdf")
        os.rename(fNameOld, fName)
    shutil.move(start+fName, end)

    
    """
    if fName in os.listdir(end) and os.access(start+fNameOld, os.W_OK):
        os.rename(start+fNameOld, start+fName)
        shutil.move(start+fName, end)
    elif fName in os.listdir(end) and os.access(start+fNameOld, os.W_OK) == False :
        print("No rights to access file, skipping the file")
    else:
        print("no instructions for handling.")
    """


#Parses a variable inside config file
def parseConfigLoc(doc, var):
    docT = doc.read()
    varLoc = docT.find(var)
    if(varLoc == -1):
        print("Error!")
        print("Unable to find variable " + var + " in config.")
        print("""Refer to the list 
            of config variables that must be set in the configlist
            document
            """)
        exit()
        
    value = docT[varLoc+len(var):docT.find("\n", varLoc+1)]
    return value

#Parses move rules inside config file
def parseConfigMoveRules():
    #Get rules from config
    #tuple[0] = comparison word, tuple[1] = file location
    rules = []
    configF = open("config.txt")
    for ln in configF:
        if "MOVE:" in ln:
                colonOneLoc = ln.find(":")
                colonTwoLoc = ln.find(":", colonOneLoc + 1)
                colonThreeLoc = ln.rfind(":")
                rules.append((ln[colonOneLoc+1:colonTwoLoc],
                              ln[colonTwoLoc+1:colonThreeLoc])) 
    return rules

#Pares rename rules inside config
def parseConfigRenameRules():
    #Get rules from config
    #tuple[0] = comparison word, tuple[1] = file location
    rules = []
    configF = open("config.txt")
    for ln in configF:
        if "NAME:" in ln:
                colonOneLoc = ln.find(":")
                colonTwoLoc = ln.find(":", colonOneLoc + 1)
                colonThreeLoc = ln.rfind(":")
                rules.append((ln[colonOneLoc+1:colonTwoLoc],
                              ln[colonTwoLoc+1:colonThreeLoc]))
    return rules

#Creates index & loads it with files
def makeIndex(inDir):
    #Make sure file structure is acceptable
    #Delete old file structure
    if "indexdir" in os.listdir(os.curdir):
        shutil.rmtree("indexdir")

    #Create file structure
    os.mkdir("indexdir")

    #Create index
    ix = create_in("indexdir", schema)

    #Load files into schema
    loc = os.listdir(inDir)
    writer = ix.writer()
    for x in loc:
        call("pdftotext \"" + inDir+ "//" + x + "\" tmp.txt")
        f = open("tmp.txt", "r")
        fText = f.read()
        writer.add_document(fileName=x, content=fText)
        f.close()
    writer.commit()

    return ix
    
#Start of main
print("Running fax sorting program.")

def SortFaxes():
    #Run OCR
    #call("runOCR.exe")

    #Get input location of original pdfs from config
    origInDir = parseConfigLoc(open("config.txt"), "POI=")
    #print("Original PDF input Directory: " + origInDir)

    #Get location of OCR'ed pdfs from config
    inDir = parseConfigLoc(open("config.txt"), "OID=")
    #print("OCR Input Directory: " + inDir)

    #Get output location for original outputs from config
    origOutDir = parseConfigLoc(open("config.txt"), "POD=")
    #print("Original PDF output Directory: " + origOutDi
	
    print("Before loading index.")
    
    #
    # Rename files
    #
    ix = makeIndex(inDir)

    #Read in rules
    nRules = parseConfigRenameRules()

    #Apply rules
    for r in nRules:
        search = ix.searcher()
        result = search.find("content", r[0])
        for u in result:
            w = ix.writer()
            #print("Renaming " + u['fileName'])
            t = str(time.clock()).replace(".", "")
            os.rename(inDir+u['fileName'], inDir+r[1]+"_"+t+"_"+"ocr.pdf")
            os.rename(origInDir+ ("" + u['fileName']).replace("_ocr", ""),
                  origInDir+r[1]+"_"+t+".pdf")
            w.delete_by_term('fileName', u['fileName'])
            w.commit()
        search.close()
    ix.close()

    print("After loading rules.")

    #
    # Move files
    #
    ix = makeIndex(inDir)

    #read in rules
    mRules = parseConfigMoveRules()

    #Apply rules
    for r in mRules:
        search = ix.searcher()
        result = search.find("content", r[0])
		#make the new sort folder above the app folder
        for u in result:
            if r[1] not in os.listdir("../"):
                os.mkdir("../"+r[1])
            w = ix.writer()

            #Move OCR'd file
            try:
                shutil.move(inDir+"\/" + u['fileName'], "../"+r[1]+"/")
            except shutil.Error as e:
                print(e)
                if "already exists" in e:
                    os.remove(inDir+u['fileName'])

            #Move Pre OCR file
            #try:
             #   shutil.move(origInDir+ u['fileName'].replace("_ocr", ""), origOutDir)
            #except shutil.Error:
             #   print(e)
             #   if "already exists" in e:
             #       os.remove(origInDir+ u['fileName'].replace("_ocr", ""))
                

            #Clean up Indexing
            w.delete_by_term('fileName', u['fileName'])
            w.commit()
        search.close()
    ix.close()

    print("Post move rules.")

    if not os.path.exists("../Unsorted"):
        os.mkdir("../Unsorted") 

    for pdf in os.listdir(inDir):
        move(pdf, inDir, "../Unsorted/")
        #move(pdf.replace("_ocr", ""), origInDir, origOutDir)

    #print("Done!")
#
# Main Loop
#

#Load schema, guess it has to be done globallyf
schema = Schema(fileName=TEXT(stored=True), content=TEXT)

print("Press CTRL+C a couple of times to exit program.")

#Get input location of original pdfs from config
origInDir = parseConfigLoc(open("config.txt"), "POI=")
#print("Original PDF input Directory: " + origInDir)

ignore = []

#Move incoming PDFs to incoming fax folder
#print(os.listdir("../"))
#for f in os.listdir("../"):
#    if ".pdf" in f and f not in os.listdir(origInDir):
#        print("moving " + f)
#        shutil.move("../"+f, origInDir)

#Decide if SortFaxes program needs to be run
#shouldRun = False
#for f in os.listdir(origInDir):
    #print(f)
#    if ".pdf" in f and f not in ignore:
#        shouldRun = True
#        break
#if shouldRun == True:
    #Need to sort

    #Call OCR
SortFaxes()

#for e in os.listdir(origInDir):
    #print("hmm" + e)
#print(ignore)
