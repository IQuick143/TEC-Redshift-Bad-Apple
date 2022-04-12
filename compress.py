#Helper classes that write data in DATA statements suitable for reading by exas

class DataWriterCompression():
	"""Writer which compresses positive numbers by grouping single digits numbers
	into blocks of 4 digits if possible

	Larger numbers get mapped to negative values < -9999; -1 >
	
	Negative values not supported
	"""
	def __init__(self, filename):
		self.filename = filename

	def __enter__(self):
		self.fp = open(self.filename, "w")
		self.fp.write("DATA")
		self.remaining_chars = 20
		self.merge = ""
		return self

	def write(self, value: int):
		assert 0 <= value <= 9999, "Value outside allowed range"
		if 1 <= value <= 9:
			# Group single digits into a 4 digit number if possible
			if 0 < len(self.merge) < 4 and self.remaining_chars > 0:
				self.merge = str(value) + self.merge
				self.remaining_chars -= 1
			else:
				if len(self.merge) > 0:
					self.fp.write(" "+self.merge)
				self.merge = str(value)
				needed_chars = len(self.merge)+1
				if needed_chars > self.remaining_chars:
					self.newline()
				self.remaining_chars -= needed_chars
		else:
			# Flush the merge cache and write a large number
			if len(self.merge) > 0:
				self.fp.write(" "+self.merge)
				self.merge = ""
			value *= -1
			text = " "+str(value)
			needed_chars = len(text)
			if needed_chars > self.remaining_chars:
				self.newline()
			self.remaining_chars -= needed_chars
			self.fp.write(text)
	
	def newline(self):
		self.fp.write("\nDATA")
		self.remaining_chars = 20

	def __exit__(self, a,b,c):
		if len(self.merge) > 0:
			self.fp.write(" "+self.merge)
		self.fp.close()

class DataWriter():
	"""Writer which wraps lines as efficiently as possible
	"""
	def __init__(self, filename):
		self.filename = filename

	def __enter__(self):
		self.fp = open(self.filename, "w")
		self.fp.write("DATA")
		self.remaining_chars = 20
		return self

	def write(self, value: int):
		assert -9999 <= value <= 9999, "Value outside allowed range"
		text = " "+str(value)
		needed_chars = len(text)
		if needed_chars > self.remaining_chars:
			self.newline()
		self.remaining_chars -= needed_chars
		self.fp.write(text)
	
	def newline(self):
		self.fp.write("\nDATA")
		self.remaining_chars = 20

	def __exit__(self, a,b,c):
		self.fp.close()

"""#Old code for naive file writing
with open("out.examov", "r") as fp:
	with DataWriter("out.examovcompr") as writer:
		for line in fp.readlines():
			if "," in line:
				writer.newline()
				writer.newline()
			else:
				val = int(line.strip())
				writer.write(val)

counter = 0
with open("out.examov", "r") as fp:
	with DataWriterCompression("out.examovultracompr") as writer:
		for line in fp.readlines():
			if "," in line:
				writer.newline()
				writer.newline()
			else:
				val = int(line.strip())
				writer.write(val)
				counter += 1
				if counter >= 998:
					counter = 0
					writer.write(9999)
		if counter > 0:
			writer.write(9999)
"""