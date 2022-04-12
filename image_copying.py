"""
I actually had to write my own image-transposer algorithm, because the one
online did not work, I assume it works with the two least significatnt bits in
each channel, however my file is so big it reaches over into the third bit.

Optional, makes the cartridge look cool.
"""

from PIL import Image
import numpy as np

source = np.array(Image.open("[SOURCE_ENCODED_IMAGE_FROM_EXAPUNKS]"))
target = np.array(Image.open("[TARGET_IMAGE]"))

# How many layers of bits are to be copied from the source, tests have shown that at least 3 are needed here
bits = 3

mask = (2 ** bits) - 1

# bit magic goes brrrrr
output = target ^ (source & mask) ^ (target & mask)

Image.fromarray(output).save("[SAVE_LOCATION]", mode='RGBA')
