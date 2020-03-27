#!/usr/bin/python


## usage: hideDecoder.py <cover-object> <decoder_file>


##  argv[]
##      1   cover-object: input image file name
##      2   decoder_file: file containing the HTML decoder
##
##      BASH script to hide decoder in multiple files at the same time
##      for f in <file_name>; do ./hideDecoder.py $f decoder.html; done


# import some required libraries
import binascii
import sys
import imageFunctions as f
import logging
import inspect


# declare global variables
fileStructure = {}



def analyseImage(imageString):
    print "Analysing image"


    # Analyse the BMP image file structure to retrieve: Magic number, header size, DIB header size, Image data offset
    if (imageString[:2] == "BM"):
        fileStructure['TYPE'] = 'BMP'
        fileStructure['HEADER_SIZE'] = 14
        fileStructure['DIB_HEADER_SIZE'] = f.calcHex(imageString[14:18])
        fileStructure['IMAGE_DATA_OFFSET'] = f.calcHex(imageString[10:14])
        return True
    else:
        return False




def injectHTML(HTMLString,imageString):
    print "Injecting HTML"

    # calculate the length of the to be injected HTML string
    HTMLSize = len(HTMLString)

    # Modify the existing image string by injecting HTML comment block closing characters followed by the to be injected HTML
    # Insert this data at the current location of the image data (and, hence, push out the image data to the new offset)
    newString = f.stringInsert(imageString, "-->" + HTMLString, int(fileStructure['IMAGE_DATA_OFFSET']))

    # Calculate the new image data offset
    newDataOffset = int(fileStructure['IMAGE_DATA_OFFSET']) + HTMLSize + 3

    # create hex representation for new image data offset and remove 0x from the string
    d = hex(newDataOffset).replace("0x","")

    if len(d) % 2 != 0:
        d = ("0" + d)

    
    # reverse byte offset to little endian
    d = "".join([m[2:4]+m[0:2] for m in [d[i:i+4] for i in range(0, len(d),4)]])

    # change the new string representation of the image file to hex
    newStringHex = binascii.hexlify(newString)

    # replace the existing image data offset with the new offset
    newStringHex = f.stringReplace(newStringHex,20,d)

    # inject the hex representation of HTML comment block start characters into the image 
    newStringHex = f.stringReplace(newStringHex,4,binascii.hexlify("<!--"))

    # return the string representation of the new image
    return binascii.unhexlify(newStringHex)



def writeFile(imageString,outputFile):
    # write the new image string to the provided output file.
    print ("Writing to file: decoder_" + outputFile)
    
    outputFile = "decoder_" + outputFile
    
    f = open(outputFile,"a")
    f.write(imageString)
    f.close


def main(*argv):
    imageString = ""
    newImageString = ""

    # if input file is provided, try to read the file
    if (sys.argv[1]): imageString = f.readFile(sys.argv[1])
    else: print "ERROR: no input file provided"

    # analyse the input string and if it is of correct type, procede to inject code
    if (analyseImage(imageString) == True):
        # inject the HTML code into the BMP image
        newImageString = injectHTML(f.readFile(sys.argv[2]),imageString)

        # write the new image data to the correct output file
        writeFile(newImageString,sys.argv[1])
    else:
        print "ERROR: input file is not of correct type; please provide BMP file type"



if __name__ == '__main__': main()

