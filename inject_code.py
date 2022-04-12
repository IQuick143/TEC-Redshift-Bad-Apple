"""
Because Exapunks built-in IDE is horribly optimized, it lags terribly with this
many LOC hence we bypass the need to copy paste code into exapunks by directly
editing the save-file.

It all comes together here.
"""

from exapunks.solution import Exa, Solution

save_path = "[SAVE_FILE_YOU_WANNA_WRITE_TO]"

with open("EXA.exa", "r") as program_file:
	lines = program_file.readlines()
	assert len(lines) <= 1000
	code = "".join(lines).strip()

with open("EXA_music.exa", "r") as program_file:
	lines = program_file.readlines()
	assert len(lines) <= 1000
	music_code = "".join(lines).strip()

with open("out.examus", "r") as data_file:
	data = data_file.readlines()
	assert len(data) <= 1000
	music_data = "".join(data).strip()

# How many lines we can fit into an EXA
EXA_LIMIT = 1000

with open("out_final.examovultracompr", "r") as data_file:
	data = data_file.readlines()
	exa_data = [("".join(data[x:x+EXA_LIMIT]).strip()) for x in range(0, len(data), EXA_LIMIT)]
	n_video_data_exas = len(exa_data)
	assert n_video_data_exas <= 12

exas = []
exas.append(Exa(name="IQ", code=code, local_m_mode=True))
exa_names = ["UI", "CK", "XA", "XB", "XC", "BA", "DA", "PP", "LE", "XD", "BY", "XE"]
exa_names.extend(["X"+chr(ord("B") + i) for i in range(max(0, n_video_data_exas - 8))])
exas.extend([Exa(name=exa_names[i], code=exa_data[i]) for i in range(n_video_data_exas)])
exas.append(Exa(name="MU", code=music_code.replace("{FILE_ID}", str(400 + n_video_data_exas)), local_m_mode=False))
exas.append(Exa(name="SI", code=music_data))

sol = Solution(file_id="PB039", solution_name="BAD APPLE", exas=exas)
sol.update_metadata()
sol.to_file(save_path)
