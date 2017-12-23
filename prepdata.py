import midi
from numpy import median

pattern = midi.read_midifile('chpn_op27_2.mid')

def medianExtract(pattern):
	tones = []
	notes = []
	final = []
	testind = 0
	#print(pattern[0][10])
	for track in pattern:
		for note in track:
			if isinstance(note, midi.NoteEvent):
				tones.append(note.get_pitch())
				notes.append(note)
	med = median(tones)
	for n in tones:
		testind = testind + 1
		if n > med:
			final.append(notes[testind])
	print(final)
	newpat = midi.Pattern()
	newtrack = midi.Track()
	newpat.append(newtrack)
	newtrack.append(midi.TimeSignatureEvent(tick=0, data=[6, 3, 12, 8]))
	newtrack.append(midi.KeySignatureEvent(tick=0, data=[251, 0]))
	for f in final:
		newtrack.append(f)
	newtrack.append(midi.EndOfTrackEvent(tick=1))
	midi.write_midifile("test1.mid", newpat)
	
	
medianExtract(pattern)