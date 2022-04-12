"""
Data in .examov format assumes it gets split into chunks that get passed
directly to exas which then show the video, however this is infeasible due to
exa-file size limits, so the data needs to be streamed in chunks which are
generated by a central exa.

Due to synchronization problems, this requires planning ahead such that there
are never multiple exas that require a "refill" just few frames apart as they
would not have their data ready yet and would become delayed by a frame and
later clog up the entire pipeline.

Another aspect is that the data needs to be compressed due to size constraints.
Compression involves utilizing each line of data files to store the most bits.
See: compress.py and DataWriterCompression
"""

from compress import DataWriterCompression

"""
assoc array of EXAs, each exa datapoint keeps track of variables to simulate
a simplified model of the video decoder:
X - X register, stores current pixel pointer of the exa
wait - how many frames to sleep
consumed - how much data was used (file pointer)
data - the data this exa needs to process (file)
As well as information that describes the speed the data gets used and written:
consumption_history - timings of when and how much data was used
 - Later recieves the information of how many frames until a new file is needed
written - how much of the exas data was already written
"""
EXA = {}

# Parse out.examov and initialize EXA's with the data they are assigned
with open("out.examov", "r") as file:
	x = 0
	y = 0
	for line in file.readlines():
		if "," in line:
			(x, y) = line.split(", ")
			x = int(x)
			y = int(y)
			EXA[x,y] = {"data":[], "X":0, "wait":0, "consumed":0, "consumption_history":[(0,0)], "written":0}
		else:
			EXA[x,y]["data"].append(int(line.strip()))

# Merge the intervals into pairs of (changed px, no change px) to reflect how the exa code reads them
for exa in EXA:
	# Append a zero interval in case of wrong parity
	if len(EXA[exa]["data"]) % 2 == 1:
		EXA[exa]["data"].append(0)
	EXA[exa]["data"] = [(EXA[exa]["data"][2*i],EXA[exa]["data"][2*i+1]) for i in range(len(EXA[exa]["data"]) // 2)]

# Run a simulation of the EXA video player to calculate how much data was used on any given frame
frame = 0
while True:
	for exa in EXA:
		# Run through the data until exa needs to wait till next frame, or runs out of data
		while EXA[exa]["consumed"] < len(EXA[exa]["data"]) and EXA[exa]["wait"] == 0:
			# Read a pair of read/write
			(a,b) = EXA[exa]["data"][EXA[exa]["consumed"]]
			EXA[exa]["consumed"] += 1
			EXA[exa]["X"] += a
			assert EXA[exa]["X"] <= 100, "Should not happen, if it does, indicates wrongly encoded video"
			EXA[exa]["X"] += b
			# How many frames we have data for (100px = 1 frame)
			EXA[exa]["wait"] += EXA[exa]["X"] // 100
			EXA[exa]["X"] %= 100
		
		EXA[exa]["consumption_history"].append((frame, EXA[exa]["consumed"]))
		EXA[exa]["wait"] -= 1
	frame += 1
	# If all exas ran out of data terminate
	for exa in EXA:
		if EXA[exa]["wait"] > 0 or EXA[exa]["consumed"] < len(EXA[exa]["data"]):
			break
	else:
		break

last_frame = frame

# compute how many steps we can go ahead from any given consumption till a refill is strictly needed
for exa in EXA:
	for i in range(len(EXA[exa]["consumption_history"])):
		for j in range(i, len(EXA[exa]["consumption_history"])):
			# on frame j, since frame i, we have moved more the pointer by than how much fits into a file so we need anotha one
			if EXA[exa]["consumption_history"][j][1] >= EXA[exa]["consumption_history"][i][1] + 998//2:
				(frame, used) = EXA[exa]["consumption_history"][i]
				EXA[exa]["consumption_history"][i] = (frame, used, j - i - 1)
				break
		else:
			# we have managed to put all remaining data into the file
			(frame, used) = EXA[exa]["consumption_history"][i]
			EXA[exa]["consumption_history"][i] = (frame, used, len(EXA[exa]["consumption_history"]) - 1 - i)

# keep track of which frames are already occupied by a refill
used_frames = set()
# Store the data intervals we need to cut the data into
# (exa, frame, amount) - what exa, what frame, how much data
data_fills = []

# Naive greedy algorithm that fills the latest possible free spot
for exa in EXA:
	loaded = 0
	# last refill
	i = 0
	while loaded < len(EXA[exa]["data"]):
		# Take the latest possible frame for a refill and iterate backwards
		for j in range(EXA[exa]["consumption_history"][i][2],0,-1):
			# Check if there are no refills within +-2 frames (tested to be enough for this case)
			# Yes I know this is extrmely inelegant >who cares
			if (j+i not in used_frames and j+i+1 not in used_frames and j+i-1 not in used_frames and
				j+i+2 not in used_frames and j+i-2 not in used_frames) or j+i == last_frame:
				used_frames.add(j+i)
				needed = EXA[exa]["consumption_history"][j+i][1] - EXA[exa]["consumption_history"][i][1]
				data_fills.append((exa, i, needed))
				loaded += needed
				i += j
				break
		else:
			# All spots were used up and this exa couldn't get a spot.
			print(used_frames)
			print(data_fills)
			raise Exception(f"Could not solve for {exa}")

# Order the data fills chronologically by the frame
data_fills.sort(key=lambda a: a[1])

print([x[1] for x in data_fills])
print([x[2] for x in data_fills])

# Write the data into DATA lines as efficiently as possible
with DataWriterCompression("out_final.examovultracompr") as writer:
	for (exa, frame, amount) in data_fills:
		for i in range(EXA[exa]["written"], EXA[exa]["written"] + amount):
			(a, b) = EXA[exa]["data"][i]
			writer.write(a)
			writer.write(b)
		EXA[exa]["written"] += amount
		# -9999 is used as a delimiter between data chunks
		writer.write(9999)