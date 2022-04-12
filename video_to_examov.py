"""
Reads a video using FFMPEG and converts it into the examov format.
Outputs a stream of numbers into out.examov

The video processing begins here.
"""

import ffmpeg
import numpy as np

in_filename = 'BadApple.mp4'
# The size of a single exa sprite
EXAPIXEL = 10

# Video properties
width = 40
height = 20
FPS = 10

assert width % EXAPIXEL == 0 and height % EXAPIXEL == 0, f"Both spatial input video dimensions must be a multiple of {EXAPIXEL}px"

print(f"{width}x{height}")

# Read the video into a numpy array of numbers
out, _ = (
    ffmpeg
    .input(in_filename)
	.filter('scale', '120x60', flags='lanczos') # idk what I was doing here but apparently it worked well?
	.filter('unsharp', luma_amount=5)
	.filter('scale', f'{width}x{height}')
	.filter('fps', FPS)
    .output('pipe:', format='rawvideo', pix_fmt='rgb24')
    .run(capture_stdout=True)
)

# Quantize to bools and reshape
video = np.array([p > 127 for p in (
    np
    .frombuffer(out, np.uint8)
    .reshape([-1, height, width, 3])
)[:,:,:,1]], dtype=bool)

frames, width, height = video.shape

# XOR the video frames such that True = pixel changed across frames, False = pixel unchanged
# Basically a form of delta-encoding
for i in range(frames-1, 0, -1):
	for x in range(width):
		for y in range(height):
			video[i,x,y] = video[i,x,y] != video[i-1,x,y]

max_interval = 9900

# calculate a run-length encoding of the bit-flip data
# Runs are either a run of changing pixels, or a run of unchanging pixels
# These runs always alternate so there is no need to store the type
with open("out.examov", "w") as fp:
	for x_exa in range(width // EXAPIXEL):
		for y_exa in range(height // EXAPIXEL):
			fp.write(f"{x_exa}, {y_exa}\n0\n")
			# Length of an interval
			counter = 0
			# False = unchanged pixels, True = changing pixels
			# type stores the type of the pixel that is currently
			type = False
			# Iterate over rows, columns, frames corresponding to this exa
			for i in range(frames):
				for pos in range(EXAPIXEL * EXAPIXEL):
					if type == video[i, x_exa * EXAPIXEL + pos % EXAPIXEL, y_exa * EXAPIXEL + pos // EXAPIXEL]:
						# If pixel behaves according to the interval type, increment interval size
						counter += 1
						# maximum interval size limit, if surpassed, splits into two intervals
						if counter > max_interval:
							# Length of this (ended) interval
							fp.write(f"{max_interval}\n")
							# The other interval type is skipped by using a dummy 0 interval because we want to continue this interval type
							fp.write("0\n")
							counter -= max_interval
					else:
						# switch type of interval by ending the current one and making a new one
						fp.write(f"{counter}\n")
						type = not type
						# this pixel gets counted too
						counter = 1
				# We cant end a frame by overflowing while changing pixels, so we end this interval here and begin a unchanging pixel interval
				# An interval of unchanging pixels however can exceed a frame boundary
				if type == True:
					fp.write(f"{counter}\n")
					type = False
					counter = 0