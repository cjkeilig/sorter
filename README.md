#Welcome to my Fax Sorting Application
This Python3 program was originally designed to sort faxes in pdf format into folders.
As is, the program will not sort scanned/handwritten documents, only searchable pdfs.
It is up to you to implement OCR if you wish to sort handwritten and scanned documents. You may have an OCR machine that does this, or you may use command line utilities like Tesseract, Imagemagick, Ghostscript or others to achieve this.

Sorting rules are defined in the config.txt file in the format "MOVE:\<keyword\>:\<Folder Name\>:"
The only other thing you need to configure is the OID value to reflect the location of your faxes or pdf documents. The other two documents can be used if you wish to edit the program do any more pre or post processing.

#Requirements
Python3, Xpdf's "pdftotext", Whoosh - a python library (pip install Whoosh)
              
#How it works 
Wherever you decide to put the program on your machine, the faxes will be put in folders one level above. Make sure you don't have any folders with the same named like the ones you define in the config file. Also make sure, you don't have a folder named 'Unsorted' as this is automatically made for documents that don't match any of your rules.

#Usage notes
Rules are applied in the order they are defined. If one document matches two rules, the folder in the first rule defined will be the one the pdf gets sorted to.
