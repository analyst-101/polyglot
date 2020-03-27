#!/usr/bin/python

## This is a simple steganograpy proof of concept to hide a message inside the pixels of a cover-object resulting in a stego-object output file.
## The steganography method that is being used, is simple least-significant-bit based.
## The proof of concept is not secure and does not try to make detection or recovery difficult.
## The hide.py script is accompanied by the recover.py script to recover the hidden message from the stego-object file.

## The hiding process is as follows:
##      * convert the message to a BASE64 string
##      * convert the BASE64 string to a bit-stream
##      * determine the length of the bit-stream
##      * pre-pend the length of the bit-stream to the bit-stream (for easy recovery)
##      * strart at the bottom left pixel of a BMP image (this is the first pixel for a BMP type image)
##      * hide the bit-stream bit-by-bit in the RGB pixels in the least-significant-bit (layer 7 only)
##      * wrtie the image to an output file
##
## The recover.py script uses the reverse process to recover the message



## Usage: python ./hide.py <cover-object file> <message file> 
## output: pixel_<cover-object file>


# Import libraries
from PIL import Image
import bitarray
import base64
#import math
import sys




## Open cover-object
in_file = sys.argv[1]
out_file = ("pixel_" + in_file)

im = Image.open(in_file).convert('RGB')
width, height = im.size


## Open message file
f = open(sys.argv[2], "r")
message = f.read()


## Convert message to Base64
encoded_message = base64.b64encode(message)

## Print BASE64-encoded message
#print(encoded_message)


## Convert the base64-message into a array of bits
ba = bitarray.bitarray()
ba.frombytes(encoded_message.encode('utf-8'))


## Convert to bitstream
bit_array = [int(i) for i in ba]

## calculate bit string length
bitStringLength = len(bit_array)


### Calculate the bitstream size of the base-64 message and prepend this to the message for easy recovery

## Convert bit string length from int to binary
lengthInBin = ([int(x) for x in bin(bitStringLength)[2:]])


## Prepand Zero's to binary representation of the bit string length to always have a standard 32 bit length to hold the message length
for x in range(len(lengthInBin),32):
        lengthInBin.insert(0,"0")



## compile complete message
data = lengthInBin + bit_array


## Start hiding message inside cover-object

i = 0
for y in range(0,height):
        for x in range(0,width):
                pixel = list(im.getpixel((x, y)))
                for n in range(0,3):
                        if(i < len(data)):
                                pixel[n] = pixel[n] & ~1 | int(data[i])
                                i+=1
                im.putpixel((x,y), tuple(pixel))


## save cover-object
im.save(out_file)

