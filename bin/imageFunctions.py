#!/usr/bin/python

import binascii
import sys
import inspect
import logging

#### Initialise logger


## Log levels

## CRITICAL
## ERROR
## WARNING      |   Code output
## INFO         |   Main function call trace
## DEBUG        |   Detailed function calls and additional debug messages


# Modify the log-level in this line to change the log-level
logging.basicConfig(level=logging.ERROR, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')


#### Generic data structures
BMPDIBHEADERS = {
        "12" : {"name":"BITMAPCOREHEADER", "offsetBitmapSize":"0"},
        "16" : {"name":"OS22XBITMAPHEADER", "offsetBitmapSize":"0"},
        "40" : {"name":"BITMAPINFOHEADER", "offsetBitmapSize":"34"},
        "52" : {"name":"BITMAPV2INFOHEADER", "offsetBitmapSize":"34"},
        "56" : {"name":"BITMAPV3INFOHEADER", "offsetBitmapSize":"34"},
        "64" : {"name":"OS22XBITMAPHEADER", "offsetBitmapSize":"0"},
        "108" : {"name":"BITMAPV4HEADER", "offsetBitmapSize":"34"},
        "124" : {"name":"BITMAPV5HEADER", "offsetBitmapSize":"34"}
        }



#### File functions

def readFile(fileName):
    with open(fileName, 'rb') as f:
        localContent = f.read()
        logging.debug(localContent)
    return localContent



#### Hex functions

def calcHex(string):
    ## Calculates the Hex version of the input string and returns this as a string.
    logging.debug("Function: " + inspect.stack()[0][3])
    logging.debug("Called from: " + inspect.stack()[1][3])
    a = binascii.hexlify(string)
    a = "".join(reversed([a[i:i+2] for i in range(0, len(a),2)]))
    return (str(int(a,16)))

def convertToHex(stringContent):
    logging.debug("Function: " + inspect.stack()[0][3])
    logging.debug("Called from: " + inspect.stack()[1][3])
    ## Convert a string to the Hexadecimal version
    hexContent = binascii.hexlify(stringContent)
    return hexContent


def hexWithSpace(hexStringContent):
    logging.debug("Function: " + inspect.stack()[0][3])
    logging.debug("Called from: " + inspect.stack()[1][3])
    ## converts input hex string to a version where a space is included after every two characters (representing a character)
    return " ".join([hexStringContent[i:i+2] for i in range(0, len(hexStringContent),2) ] )
 


def printHex(stringContent):
    logging.debug("Function: " + inspect.stack()[0][3])
    logging.debug("Called from: " + inspect.stack()[1][3])
    ## Prints a string in hex format
    hexContent = binascii.hexlify(stringContent)
    
    for i in range(len(hexContent)):
        print hexContent[i] 


#### String functions

def stringInsert(sourceString, injectString, position):
    logging.debug("Function: " + inspect.stack()[0][3])
    logging.debug("Called from: " + inspect.stack()[1][3])
    # insert the "injectString" into "position" of the "sourceString"
    return sourceString[:position] + injectString + sourceString[position:]



def stringReplace(sourceString, index, replacementString):
    logging.debug("Function: " + inspect.stack()[0][3])
    logging.debug("Called from: " + inspect.stack()[1][3])
    # replace the "replacementString" in the "sourceString" at "sourceString" location of "index"
    return '%s%s%s'%(sourceString[:index],replacementString,sourceString[index+len(replacementString):])



#### Image structure functions

def checkMagic(string):
    logging.debug("Function: " + inspect.stack()[0][3])
    logging.debug("Called from: " + inspect.stack()[1][3])
    hexString = convertToHex(string)
    localMagic = ""
    
    if (string[:6] == "GIF89a"):
        logging.debug("Magic number: " + string[:6])
        localMagic = string[:6]
    elif (string[:6] == "GIF86a"):
        logging.debug("Magic number: " + string[:6])
        localMagic = string[:6]
    elif (string[:2] == "BM"):
        logging.debug("Magic number: " + string[:2])
        localMagic = string[:2]
    elif (string[1:4] == "PNG"):
        logging.debug("Magic number: " + string[1:4])
        localMagic = string[1:4]
    else:
        print "No magic number found"

    return localMagic

