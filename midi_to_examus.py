"""Encodes a midi into an exa playable format"""

from mido import MidiFile, MidiTrack
from compress import DataWriter
# from matplotlib import pyplot as plt

BPM = 138.5
TPS = 30

nse = MidiFile("noise.mid")
sqr = MidiFile("square.mid")
vocal = MidiFile("vocal.mid")
tri = MidiFile("tri.mid")

def monophonic_history(track: MidiTrack):
	"""Converts a midi into a list of note changes"""
	time = 0
	current_note = 0
	events = []

	for message in track:
		time += message.time
		if hasattr(message, "note") and message.note == current_note and (message.type == 'note_off' or (message.type == 'note_on' and message.velocity == 0)):
			current_note = 0
			events.append((current_note, time))
		elif message.type == 'note_on':
			current_note = message.note
			events.append((current_note, time))
		#print(message)
		#print(str(current_note) + " " + str(time))
	events.sort(key=lambda a: a[0])
	return events

def convert_to_exa(track: MidiTrack, TPB: float, BPM: float, EXA_TPS: float):
	conversion_factor = 1.0 / TPB / BPM * 60 * EXA_TPS
	for note, time  in monophonic_history(track):
		converted_time = round(time * conversion_factor)
		yield (note, converted_time)

# Combine events into one array with channel data
all_events = []
all_events.extend([
	(0, a, b) for a,b in convert_to_exa(nse.tracks[0], nse.ticks_per_beat, BPM, TPS)
])
all_events.extend([
	(1, a, b) for a,b in convert_to_exa(sqr.tracks[0], sqr.ticks_per_beat, BPM, TPS)
])
all_events.extend([
	(2, a, b) for a,b in convert_to_exa(vocal.tracks[0], vocal.ticks_per_beat, BPM, TPS)
])
all_events.extend([
	(3, a, b) for a,b in convert_to_exa(tri.tracks[0], tri.ticks_per_beat, BPM, TPS)
])

# all_events.sort(key=lambda t: t[0])
# Sort chronologically
all_events.sort(key=lambda t: t[2])

#print(all_events[-1])

# Convert into a delta-time representation
for i in range(len(all_events)-1):
	(channel, value, time) = all_events[i]
	all_events[i] = (channel, value, all_events[i+1][2] - time)

(channel, value, _) = all_events[len(all_events) - 1]
all_events[len(all_events) - 1] = (channel, value, 0)

#print(all_events)

#print(sum([t for _, _, t in all_events]))

"""# Something about me being a dumbass and needing a lot of debugging code for this
NSE0 = 0
NSE0_graph = []
SQR0 = 0
SQR0_graph = []
SQR1 = 0
SQR1_graph = []
TRI0 = 0
TRI0_graph = []

for (channel, value, time) in all_events:
	if channel == 0:
		NSE0 = value
	elif channel == 1:
		SQR0 = value
	elif channel == 2:
		SQR1 = value
	elif channel == 3:
		TRI0 = value
	for i in range(time):
		NSE0_graph.append(NSE0)
		SQR0_graph.append(SQR0)
		SQR1_graph.append(SQR1)
		TRI0_graph.append(TRI0)

plt.scatter(range(len(NSE0_graph)), NSE0_graph, marker=",")
plt.scatter(range(len(SQR0_graph)), SQR0_graph, marker=",")
plt.scatter(range(len(SQR1_graph)), SQR1_graph, marker=",")
plt.scatter(range(len(TRI0_graph)), TRI0_graph, marker=",")

plt.show()
#"""

registers = [0,0,0,0]

cut_events = []

# Remove events with long pauses, by replacing them with multiple shorter ones
for (channel, value, time) in all_events:
	#print(channel, value, time)
	if time > 9:
		cut_events.append((channel, value, time % 9))
		registers[channel] = value
		# could be a for loop with a range but this had so many OBOEs I'm afraid to touch it
		j = time
		while j > 9:
			cut_events.append((0, registers[0], 9))
			j -= 9
		#cut_events.append((0, registers[0], j))
	else:
		cut_events.append((channel, value, time))
		registers[channel] = value

all_events = cut_events

#print(sum([t for _, _, t in all_events]))

#print(all_events)


print(len(all_events))
values = [x[1] for x in all_events]
print(f"Max value {max(values)}")
timings = [x[2] for x in all_events]
print(f"Max timing {max(timings)}")

"""
NSE0 = 0
NSE0_graph = []
SQR0 = 0
SQR0_graph = []
SQR1 = 0
SQR1_graph = []
TRI0 = 0
TRI0_graph = []

for (channel, value, time) in all_events:
	if channel == 0:
		NSE0 = value
	elif channel == 1:
		SQR0 = value
	elif channel == 2:
		SQR1 = value
	elif channel == 3:
		TRI0 = value
	for i in range(time):
		NSE0_graph.append(NSE0)
		SQR0_graph.append(SQR0)
		SQR1_graph.append(SQR1)
		TRI0_graph.append(TRI0)

plt.scatter(range(len(NSE0_graph)), NSE0_graph, marker=",")
plt.scatter(range(len(SQR0_graph)), SQR0_graph, marker=",")
plt.scatter(range(len(SQR1_graph)), SQR1_graph, marker=",")
plt.scatter(range(len(TRI0_graph)), TRI0_graph, marker=",")

plt.show()
#"""

# Events are encoded as CVVT - C - channel, V - value (note), T - time (waits)
with DataWriter("out.examus") as writer:
	# ngl I have no idea why this is here but it's probably important
	writer.write(1)
	for (channel, value, time) in all_events:
		writer.write(channel * 1000 + value * 10 + time)
	# Finish by closing all channels with a 0
	writer.write(0)
	writer.write(1000)
	writer.write(2000)
	writer.write(3000)