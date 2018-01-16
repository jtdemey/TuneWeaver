import midi
import smtplib
from numpy import median

pattern = midi.read_midifile('test2.mid')

def medianExtract(pattern):
	tones = [] #Tones in main track
	notes = [] #NoteEvents in main track
	mel = [] #Melody notes
	acc = [] #Accompaniment notes
	nind = 0 #Note index
	#Obtain all NoteEvents from pattern
	for track in pattern:
		for note in track:
			if isinstance(note, midi.NoteEvent):
				tones.append(note.get_pitch())
				notes.append(note)
	#Determine median tone, slight padding
	med = median(tones) - 5
	#Use median to split melody and accompaniment
	for n in tones:
		print("NoteEvent: " + str(notes[nind]))
		#Median split
		if n > med:
			mel.append(notes[nind])
			acc.append(midi.NoteOnEvent(tick=notes[nind].tick, channel=0, data=[0, 0]))
		else:
			acc.append(notes[nind])
			mel.append(midi.NoteOnEvent(tick=notes[nind].tick, channel=0, data=[0, 0]))
		#Remove root note(s) of chords
		try:
			if notes[nind].data[1] != 0:
				print("velcheck " + str(notes[nind]))
				if notes[nind].tick < 1:
					print("tickcheck " + str(notes[nind]))
					try:
						mel.remove(notes[nind])
					except:
						print("whoa")
					print("chord note removed" + str(notes[nind]))
		except:
			print("No note velocity in data")
		if nind < len(notes):
				nind = nind + 1
	print(mel)
	#Export melody
	exportTrack(mel, acc, melody=True)
	exportTrack(mel, acc, melody=False)
	
def exportTrack(mel, acc, melody=True):
	newpat = midi.Pattern()
	newtrack = midi.Track()
	newpat.append(newtrack)
	newtrack.append(midi.TimeSignatureEvent(tick=0, data=[6, 3, 12, 8]))
	newtrack.append(midi.KeySignatureEvent(tick=0, data=[251, 0]))
	if melody == True:
		fname = "test1_mel.mid"
		for f in mel:
			newtrack.append(f)
	else:
		fname = "test1_acc.mid"
		for a in acc:
			newtrack.append(a)
	newtrack.append(midi.EndOfTrackEvent(tick=1))
	midi.write_midifile(fname, newpat)
	
def printPattern(pat):
	i = 0;
	for track in pat:
		print("Track " + str(i) + " ###################")
		for note in track:
			print(note)
			
def printPitches(pat):
	i = 0;
	for track in pat:
		print("Track " + str(i) + " ###################")
		for note in track:
			print(note.get_pitch())

def testPattern():
	testmidi = midi.Pattern(tracks=[[midi.TimeSignatureEvent(tick=0, data=[4, 2, 24, 8]),
	midi.KeySignatureEvent(tick=0, data=[0, 0]),
	midi.EndOfTrackEvent(tick=1, data=[])],
	[midi.NoteOnEvent(tick=0, channel=0, data=[64, 72]),
	midi.NoteOnEvent(tick=500, channel=0, data=[55, 70]),
	midi.NoteOnEvent(tick=48, channel=0, data=[64, 0]),
	#midi.NoteOnEvent(tick=25, channel=0, data=[62, 72]),
	#midi.NoteOnEvent(tick=231, channel=0, data=[62, 0]),
	midi.NoteOnEvent(tick=64, channel=0, data=[60, 71]),
	midi.NoteOnEvent(tick=88, channel=0, data=[62, 79]),
	midi.NoteOnEvent(tick=112, channel=0, data=[55, 0]),
	midi.NoteOnEvent(tick=136, channel=0, data=[62, 0]),
	midi.NoteOnEvent(tick=160, channel=0, data=[62, 0]),
	midi.EndOfTrackEvent(tick=1, data=[])]])
	midi.write_midifile('blah.mid', testmidi)
	print("File written")
	
def maryPattern():
	MARY_MIDI = midi.Pattern(tracks=[[midi.TimeSignatureEvent(tick=0, data=[4, 2, 24, 8]),
	midi.KeySignatureEvent(tick=0, data=[0, 0]),
	midi.EndOfTrackEvent(tick=1, data=[])],
	[midi.ControlChangeEvent(tick=0, channel=0, data=[91, 58]),
	midi.ControlChangeEvent(tick=0, channel=0, data=[10, 69]),
	midi.ControlChangeEvent(tick=0, channel=0, data=[0, 0]),
	midi.ControlChangeEvent(tick=0, channel=0, data=[32, 0]),
	midi.ProgramChangeEvent(tick=0, channel=0, data=[24]),
	midi.NoteOnEvent(tick=0, channel=0, data=[64, 72]),
	midi.NoteOnEvent(tick=0, channel=0, data=[55, 70]),
	midi.NoteOnEvent(tick=231, channel=0, data=[64, 0]),
	midi.NoteOnEvent(tick=25, channel=0, data=[62, 72]),
	midi.NoteOnEvent(tick=231, channel=0, data=[62, 0]),
	midi.NoteOnEvent(tick=25, channel=0, data=[60, 71]),
	midi.NoteOnEvent(tick=231, channel=0, data=[60, 0]),
	midi.NoteOnEvent(tick=25, channel=0, data=[62, 79]),
	midi.NoteOnEvent(tick=206, channel=0, data=[55, 0]),
	midi.NoteOnEvent(tick=25, channel=0, data=[62, 0]),
	midi.NoteOnEvent(tick=25, channel=0, data=[64, 85]),
	midi.NoteOnEvent(tick=0, channel=0, data=[55, 79]),
	midi.NoteOnEvent(tick=231, channel=0, data=[64, 0]),
	midi.NoteOnEvent(tick=25, channel=0, data=[64, 78]),
	midi.NoteOnEvent(tick=231, channel=0, data=[64, 0]),
	midi.NoteOnEvent(tick=25, channel=0, data=[64, 74]),
	midi.NoteOnEvent(tick=462, channel=0, data=[55, 0]),
	midi.NoteOnEvent(tick=0, channel=0, data=[64, 0]),
	midi.NoteOnEvent(tick=50, channel=0, data=[62, 75]),
	midi.NoteOnEvent(tick=0, channel=0, data=[55, 77]),
	midi.NoteOnEvent(tick=231, channel=0, data=[62, 0]),
	midi.NoteOnEvent(tick=25, channel=0, data=[62, 77]),
	midi.NoteOnEvent(tick=231, channel=0, data=[62, 0]),
	midi.NoteOnEvent(tick=25, channel=0, data=[62, 75]),
	midi.NoteOnEvent(tick=462, channel=0, data=[55, 0]),
	midi.NoteOnEvent(tick=0, channel=0, data=[62, 0]),
	midi.NoteOnEvent(tick=50, channel=0, data=[64, 82]),
	midi.NoteOnEvent(tick=0, channel=0, data=[55, 79]),
	midi.NoteOnEvent(tick=231, channel=0, data=[64, 0]),
	midi.NoteOnEvent(tick=25, channel=0, data=[67, 84]),
	midi.NoteOnEvent(tick=231, channel=0, data=[67, 0]),
	midi.NoteOnEvent(tick=25, channel=0, data=[67, 75]),
	midi.NoteOnEvent(tick=462, channel=0, data=[55, 0]),
	midi.NoteOnEvent(tick=0, channel=0, data=[67, 0]),
	midi.NoteOnEvent(tick=50, channel=0, data=[64, 73]),
	midi.NoteOnEvent(tick=0, channel=0, data=[55, 78]),
	midi.NoteOnEvent(tick=231, channel=0, data=[64, 0]),
	midi.NoteOnEvent(tick=25, channel=0, data=[62, 69]),
	midi.NoteOnEvent(tick=231, channel=0, data=[62, 0]),
	midi.NoteOnEvent(tick=25, channel=0, data=[60, 71]),
	midi.NoteOnEvent(tick=231, channel=0, data=[60, 0]),
	midi.NoteOnEvent(tick=25, channel=0, data=[62, 80]),
	midi.NoteOnEvent(tick=206, channel=0, data=[55, 0]),
	midi.NoteOnEvent(tick=25, channel=0, data=[62, 0]),
	midi.NoteOnEvent(tick=25, channel=0, data=[64, 84]),
	midi.NoteOnEvent(tick=0, channel=0, data=[55, 79]),
	midi.NoteOnEvent(tick=231, channel=0, data=[64, 0]),
	midi.NoteOnEvent(tick=25, channel=0, data=[64, 76]),
	midi.NoteOnEvent(tick=231, channel=0, data=[64, 0]),
	midi.NoteOnEvent(tick=25, channel=0, data=[64, 74]),
	midi.NoteOnEvent(tick=231, channel=0, data=[64, 0]),
	midi.NoteOnEvent(tick=25, channel=0, data=[64, 77]),
	midi.NoteOnEvent(tick=206, channel=0, data=[55, 0]),
	midi.NoteOnEvent(tick=25, channel=0, data=[64, 0]),
	midi.NoteOnEvent(tick=25, channel=0, data=[62, 75]),
	midi.NoteOnEvent(tick=0, channel=0, data=[55, 78]),
	midi.NoteOnEvent(tick=231, channel=0, data=[62, 0]),
	midi.NoteOnEvent(tick=25, channel=0, data=[62, 74]),
	midi.NoteOnEvent(tick=231, channel=0, data=[62, 0]),
	midi.NoteOnEvent(tick=25, channel=0, data=[64, 81]),
	midi.NoteOnEvent(tick=231, channel=0, data=[64, 0]),
	midi.NoteOnEvent(tick=25, channel=0, data=[62, 70]),
	midi.NoteOnEvent(tick=206, channel=0, data=[55, 0]),
	midi.NoteOnEvent(tick=25, channel=0, data=[62, 0]),
	midi.NoteOnEvent(tick=25, channel=0, data=[60, 73]),
	midi.NoteOnEvent(tick=0, channel=0, data=[52, 72]),
	midi.NoteOnEvent(tick=974, channel=0, data=[60, 0]),
	midi.NoteOnEvent(tick=0, channel=0, data=[52, 0]),
	midi.EndOfTrackEvent(tick=1, data=[])]])
	midi.write_midifile("test2.mid", MARY_MIDI)
	print("File written.")
	
medianExtract(pattern)
#printPattern(midi.read_midifile('test1.mid'))
#maryPattern()