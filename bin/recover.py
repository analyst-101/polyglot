#!/usr/bin/python

## This script complements the hide.py script to recover the original message from the stego-object output file of hide.py



## usage: python ./recover.py <stego-object file>


## import libraries
import base64
from PIL import Image
import sys

## Load stego-object
image = Image.open(sys.argv[1])

## Initialise variable(s)
extracted = []
chars = []

pixels = image.load()



#### Iterate over pixels to recover the hidden message

## Retrieve all the least-significant-bits from the pixels        
for y in range(0,image.height):
    for x in range(0,image.width):
        pixel = list(image.getpixel((x, y)))
        for n in range(0,3):
            extracted.append(pixel[n]&1)


## Determine message length from first 32 bits of the message
mesLength = int(''.join([str(bit) for bit in extracted[:32]]), 2)


## Recover the actual message based on the message length
for i in range(mesLength/8):
    byte = extracted[32+(i*8):32+((i+1)*8)]
    chars.append(chr(int(''.join([str(bit) for bit in byte]), 2)))

## Print BASE64-encoded message
#print(''.join(chars))


## Decode the BASE64 message
message = base64.b64decode(''.join(chars))

## Print the output
print (message)

