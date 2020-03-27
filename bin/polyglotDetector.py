#!/usr/bin/python

## usage: polyglotDetector.py <file_name>


### Expected arguments
##  argv[]
##      1   input image file name (must be of type BMP)


## Bash script for analysing many images at the same time
## for f in <file_name>; do python ./polyglotDetector.py $f; done



# import some required libraries
import binascii
import sys
import imageFunctions as f
import logging
import inspect
import re
from collections import Counter


# Initialise log wrapper
def logger(fn):
    from functools import wraps
    import inspect
    @wraps(fn)
    def wrapper(*args, **kwargs):
        log = logging.getLogger(fn.__name__)
        log.info('About to run: %s' % fn.__name__)

        out = apply(fn, args, kwargs)

        log.info('Done running: %s' % fn.__name__)

        return out
    return wrapper


log = logging.getLogger(__name__)
log.info('Entered module: %s' % __name__)



# declare global variables
fileStructure = {}
#verbose = "FALSE"
COMMENT_STRING_LIST = ["/*", "*/", "<!--", "-->"]

ARTIFACTSCORE = {
        "01_FILE_SIZE_FIELD" : {"score":"FALSE"},
        "02_FILE_SIZE_STRING" : {"score":"FALSE"},
        "03_COMMENTS" : {"score":"FALSE"},
        "04_OFFSET" : {"score":"FALSE"},
        "05_CODE_TAGS" : {"score":"FALSE"},
        "06_STRINGS" : {"score":"FALSE"},
        "07_CALCULATED_FILE_SIZE" : {"score":"FALSE"},
        "08_SUSPICIOUS_CHARACTERS" : {"score":"FALSE"},
        }





@logger
def countCollectionOccurrences(coll, key):
    result = 0

    for k,v in coll.items():
        if (v['score'] == key):
            result += 1
    return result


@logger
def printDetectionResults():
    tested = len(ARTIFACTSCORE)
    found = countCollectionOccurrences(ARTIFACTSCORE,'TRUE')
    malicious = ("Suspicious !") if (found > 4) else "Clean"

    print(sys.argv[1] + " | Artifacts tested: " + str(tested) + " | Artifacts found: " + str(found) + " | " + malicious +
          " | [" + " : ".join([k for k,v in ARTIFACTSCORE.items() if v["score"] == "TRUE"]) + "]" )



@logger
def detectFileArtifacts(imageString):

    # (1) Test for file size anomaly
    if ( len(imageString) != int(fileStructure['FILE_SIZE']) ):
        ARTIFACTSCORE['01_FILE_SIZE_FIELD']['score'] = 'TRUE'
        logging.warn("File size field anomalie found! | File: " + sys.argv[1] + " | Field: " + fileStructure['FILE_SIZE'] + " | Real: " + str(len(imageString)))


    # (2) Test for COMMENT characters in file size field
    for i in COMMENT_STRING_LIST:
        if (imageString[2:(2+len(i))] == i):
            ARTIFACTSCORE['02_FILE_SIZE_STRING']['score'] = 'TRUE'


    # (3) Test for COMMENT characters anywhere else in the file
    a = re.search("[\/*<\-Rr][\\\/*<>!\-EeMm]{1,3}", imageString[6:])
    if a is not None:
        ARTIFACTSCORE['03_COMMENTS']['score'] = 'TRUE'

    # (4) Image Offset test
    if (fileStructure['IMAGE_DATA_OFFSET'] == "0"):
        ARTIFACTSCORE['04_OFFSET']['score'] = 'TRUE'

    imageEndOffset = ( (  (  (int(fileStructure['IMAGE_WIDTH']) * int(fileStructure['BITS_PER_PIXEL']) ) / 32 ) * 4 ) * int(fileStructure['IMAGE_HEIGTH'])) + int(fileStructure['IMAGE_DATA_OFFSET'])
    # (5) Test for code (HTML tags / JavaScript / VBScript

    # Test for HTML tags
    if ( (len(re.findall("<\/?\w+>",imageString[6:int(fileStructure['IMAGE_DATA_OFFSET'])]) ) != 0) or (len(re.findall("<\/?\w+>",imageString[imageEndOffset:]) ) != 0)):
        ARTIFACTSCORE['05_CODE_TAGS']['score'] = 'TRUE'


    # Test for JavaScript code
    ignoreCasePattern = re.compile('javascript|return|alert\(.*?\)|var|call|eval|switch|break|document\.getElementById|document\.write', re.IGNORECASE)
    if ( (len(re.findall(ignoreCasePattern,imageString[6:int(fileStructure['IMAGE_DATA_OFFSET'])]) ) != 0) or (len(re.findall(ignoreCasePattern,imageString[imageEndOffset:]) ) != 0)):
        ARTIFACTSCORE['05_CODE_TAGS']['score'] = 'TRUE'

    # Test for VBScript code
    pattern = re.compile('vbscript|Dim\s|ReDim|Rem|Msgbox|Let|Const|Loop|Private|ByRef|ByVal|GoTo|ExecuteGlbal|Execute|Enu|Eqv', re.IGNORECASE)
    if ( (len(re.findall(pattern,imageString[6:int(fileStructure['IMAGE_DATA_OFFSET'])]) ) != 0) or (len(re.findall(pattern,imageString[imageEndOffset:]) ) != 0)):
        ARTIFACTSCORE['05_CODE_TAGS']['score'] = 'TRUE'


    # (6) Test for multiple text characters
    a = re.findall("(?:\w{4,})", imageString[6:int(fileStructure['IMAGE_DATA_OFFSET'])])
    if len(a) != 0:
        ARTIFACTSCORE['06_STRINGS']['score'] = 'TRUE'


    # (7) Test for file size Anomaly
    # File size is HEADER + DIB HEADER (TOTAL_HEADER_SIZE) + BITMAP_DATA_SIZE
    imageSize = int(fileStructure['TOTAL_HEADER_SIZE']) + int(fileStructure['BITMAP_DATA_SIZE'])
    if (imageSize != len(imageString)):
        ARTIFACTSCORE['07_CALCULATED_FILE_SIZE']['score'] = 'TRUE'


    # (8) Test for suspect characters (characters and character patterns that indicate shellcode)
    # %u0000 | \u9090 | &amp;#x9090; | &Chr(211)
    a = re.findall("(?:%u|\\u|&amp;#x|&Chr\()(?:\d){2,4}",imageString)
    if len(a) != 0:
        ARTIFACTSCORE['08_SUSPICIOUS_CHARACTERS']['score'] = 'TRUE'

    

@logger
def analyseImage(imageString):
    # Analyse the BMP image file structure to retrieve: Magic number, header size, DIB header size, Image data offset
    if (imageString[:2] == "BM"):
        fileStructure['TYPE'] = 'BMP'
        fileStructure['FILE_SIZE'] = f.calcHex(imageString[2:6])
        fileStructure['FILE_SIZE_CHARACTERS'] = imageString[2:6]
        fileStructure['HEADER_SIZE'] = 14
        fileStructure['DIB_HEADER_SIZE'] = f.calcHex(imageString[14:18])
        fileStructure['DIB_HEADER_NAME'] = f.BMPDIBHEADERS[fileStructure['DIB_HEADER_SIZE']]["name"]
        fileStructure['IMAGE_WIDTH'] = (f.calcHex(imageString[18:22]))
        fileStructure['IMAGE_HEIGTH'] = (f.calcHex(imageString[22:26]))
        fileStructure['BITS_PER_PIXEL'] = f.calcHex(imageString[28:30])
        fileStructure['TOTAL_HEADER_SIZE'] = int(fileStructure['HEADER_SIZE']) + int(fileStructure['DIB_HEADER_SIZE'])
        fileStructure['IMAGE_DATA_OFFSET'] = f.calcHex(imageString[10:14])   ### + " (" + f.convertToHex(imageString[10:14]) + ")"

        offset = int(f.BMPDIBHEADERS[fileStructure['DIB_HEADER_SIZE']]["offsetBitmapSize"])
        fileStructure['BITMAP_DATA_SIZE'] = f.calcHex(imageString[offset:offset+4])
        fileStructure['BITMAP_DATA_SIZE_HEX'] = f.convertToHex(imageString[offset:offset+4])

        logging.info("Done running: " + inspect.stack()[0][3])
        return True
    else:
        logging.info("Done running: " + inspect.stack()[0][3])
        return False



@logger
def main(*argv):
    imageString = ""
 

    try:
        sys.argv[1]
    except Exception as e:
        logging.info("ERROR: no input file provided")
        sys.exit(e)
    else:
        imageString = f.readFile(sys.argv[1])


    # analyse the input string and if it is of correct type, procede to inject code
    if (analyseImage(imageString) == True):
        detectFileArtifacts(imageString)
        printDetectionResults()
        
    else:
        print "ERROR: input file is not of correct type; please provide BMP file type"



if __name__ == '__main__': main()
