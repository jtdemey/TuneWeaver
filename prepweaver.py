#John DeMey
#SMP 2018
#############
#!/usr/bin/python2.7
import os
import midi
import sys
import copy
import cPickle as pickle
from numpy import median
import midi_to_statematrix

#Directory for raw midi files
traindir = '/media/removable/USB Drive/rawmidis/'

#Directories for melody/accompaniment midi files
meldir = os.path.abspath(os.path.join(os.path.dirname( __file__ ), 'melodies'))
accdir = os.path.abspath(os.path.join(os.path.dirname( __file__ ), 'accompaniments'))

#Directories for saving serialized versions of melodies and accompaniments
melpkldir = os.path.abspath(os.path.join(os.path.dirname( __file__ ), 'melodies/serialized'))
accpkldir = os.path.abspath(os.path.join(os.path.dirname( __file__ ), 'accompaniments/serialized'))

#Directory for eventual output
outputdir = os.path.abspath(os.path.join(os.path.dirname( __file__ ), 'output'))

#Melodies will be exported to /melodies, accompaniments to /accompaniments
if not os.path.exists(meldir):
	os.makedirs(meldir)
if not os.path.exists(accdir):
	os.makedirs(accdir)
#Subdirectories for serialized note state matrices
if not os.path.exists(melpkldir):
	os.makedirs(melpkldir)
if not os.path.exists(accpkldir):
	os.makedirs(accpkldir)
if not os.path.exists(outputdir):
	os.makedirs(outputdir)

def revisedExtract(pattern, trackname):
	tones = [[] for i in range(len(pattern))] #Tones in main song
	notes = [[] for i in range(len(pattern))] #NoteEvents in main song
	velocities = [] #Keeping track of velocity values
	vind = 0 #Velocity index
	tind = 0 #Track index
	nind = 0 #Note index
	melnotes = 0 #Count of melody notes
	accnotes = 0 #Count of accompaniment notes

	#Obtain all NoteEvents from pattern
	for track in pattern:
		for note in track:
			if isinstance(note, midi.NoteEvent):
				tones[tind].append(note.get_pitch())
				notes[tind].append(note)
			#Modify time signatures to make them compatible with statematrix format
			elif isinstance(note, midi.TimeSignatureEvent):
				note.numerator = 4
		tind = tind + 1
	
	#Determine median tone, apply padding
	medianset = []
	for tr in tones:
		for t in tr:
			medianset.append(t)
	med = median(medianset)
	print("MEDIAN: " + str(med))
	del medianset

	#Use median to eliminate accompaniment notes
	tind = 0
	for track in pattern:
		for note in track:
			if isinstance(note, midi.NoteEvent):
				if note.data[0] < med:
					velocities.append(note.data[1])
					note.data[1] = 0
					melnotes += 1
	print("Exporting melody...")
	revisedExport(pattern, trackname, melody=True)

	#Repopulate pattern
	for track in pattern:
		for note in track:
			if isinstance(note, midi.NoteEvent):
				if note.data[0] < med:
					note.data[1] = velocities[vind]
					melnotes += 1
					vind += 1

	#Eliminate melody notes
	for track in pattern:
		for note in track:
			if isinstance(note, midi.NoteEvent):
				if note.get_pitch() >= med:
					note.data[1] = 0
					accnotes += 1

	print("Exporting accompaniment")
	revisedExport(pattern, trackname, melody=False)

def revisedExport(pat, trackname, melody=True):
	if melody == True:
		destdir = meldir
		fname = str(trackname[:-4]) + '_mel.mid'
	else:
		destdir = accdir
		fname = str(trackname[:-4]) + '_acc.mid'
	midi.write_midifile(fname, pat)
	os.rename(str(os.getcwd()) + '/' + fname, destdir + '/' + fname)

#Deprecated extract method
def medianExtract(pattern, trackname):
	tones = [[] for i in range(len(pattern))] #Tones in main song
	notes = [[] for i in range(len(pattern))] #NoteEvents in main song
	mel = [[] for i in range(len(pattern))] #Melody notes
	acc = [[] for i in range(len(pattern))] #Accompaniment notes
	tempos = [] #Tempo change info (shared in melody and accompaniment)
	tind = 0 #Track index
	nind = 0 #Note index
	abovec = 0.0 #Count of notes above middle C
	belowc = 0.0 #Count of notes below middle C
	percenthigh = 0.0 #Percentage of notes above middle C

	#Obtain all NoteEvents from pattern
	for track in pattern:
		for note in track:
			if isinstance(note, midi.NoteEvent):
				tones[tind].append(note.get_pitch())
				notes[tind].append(note)
				if note.get_pitch() < 60:
					belowc += 1
				else:
					abovec += 1
			elif isinstance(note, midi.SetTempoEvent):
				tempos.append(note)
		tind = tind + 1
	
	#Determine padding based on proportion of notes above C4
	percenthigh = (abovec / (abovec + belowc)) * 100
	print("NOTES ABOVE C4: " + str(abovec))
	print("NOTES BELOW C4: " + str(belowc))
	print(str(percenthigh) + '%')
	#Determine median tone, apply padding
	medianset = []
	for tr in tones:
		for t in tr:
			medianset.append(t)
	med = median(medianset) - 5
	print("MEDIAN: " + str(med))
	del medianset

	#Use median to split melody and accompaniment
	tind = 0
	for track in tones:
		for n in track:
			#Median split
			if n > med:
				mel[tind].append(notes[tind][nind])
				acc[tind].append(midi.NoteOnEvent(tick=notes[tind][nind].tick, channel=0, data=[0, 0]))
			else:
				acc[tind].append(notes[tind][nind])
				mel[tind].append(midi.NoteOnEvent(tick=notes[tind][nind].tick, channel=0, data=[0, 0]))
			nind = nind + 1
		tind = tind + 1
		nind = 0

	#Remove empty tracks (tracks with just metadata - no note events)
	for m in mel:
		if not m:
			del m
			print("Removing empty track")
	for a in acc:
		if not a:
			del a

	#Export melody/accompaniment
	print("Exporting separate MIDIs...")
	exportTrack(mel, acc, tempos, trackname, melody=True)
	exportTrack(mel, acc, tempos, trackname, melody=False)

#Deprecated export method
def exportTrack(mel, acc, tempos, trackname, melody=True):
	#Construct initial track
	newpat = midi.Pattern()
	firsttrack = midi.Track()
	#firsttrack.append(midi.TimeSignatureEvent(tick=0, data=[4, 2, 24, 8]))
	firsttrack.append(midi.KeySignatureEvent(tick=0, data=[251, 0]))
	if not tempos:
		firsttrack.append(midi.SetTempoEvent(tick=0, data=[16, 12, 226]))
	else:
		for t in tempos:
			firsttrack.append(t)
	firsttrack.append(midi.EndOfTrackEvent(tick=0, data=[]))
	newpat.append(firsttrack)
	print("TLEN: " + str(len(tempos)))
	#Construct note tracks
	if melody == True:
		fname = str(trackname[:-4]) + '_mel.mid'
		destdir = meldir
		for track in mel:
			newtrack = midi.Track()
			for melnote in track:
				newtrack.append(melnote)
			newtrack.append(midi.EndOfTrackEvent(tick=0, data=[]))
			newpat.append(newtrack)
	else:
		fname = str(trackname[:-4]) + '_acc.mid'
		destdir = accdir
		for track in acc:
			newtrack = midi.Track()
			for accnote in track:
				newtrack.append(accnote)
			newtrack.append(midi.EndOfTrackEvent(tick=0, data=[]))
			newpat.append(newtrack)

	#Write file
	midi.write_midifile(fname, newpat)
	#Move to proper directory
	os.rename(str(os.getcwd()) + '/' + fname, destdir + '/' + fname)

#Utility functions for testing
def printPattern(pat):
	i = 0
	for track in pat:
		print("Track " + str(i) + " ###################")
		i = i + 1
		for note in track:
			print(note)
			
def printPitches(pat):
	i = 0
	for track in pat:
		print("Track " + str(i) + " ###################")
		i = i + 1
		for note in track:
			print(note.get_pitch())

if __name__ == '__main__':
	#Gather necessary arguments
	if len(sys.argv) < 2:
		print("Usage: python prepweaver.py [directory of source MIDI files] {split-only / serialize-only / both}")
		sys.exit(0)
	print("################ TuneWeaver ################")
	print("--------------------------------------------")
	traindir = sys.argv[1]
	optarg = "both"
	if len(sys.argv) > 2:
		optarg = sys.argv[2]

	#Split MIDI files into their respective melodies and accompaniments
	if optarg == "split-only" or optarg == "both":
		print("Looking for MIDI files in " + str(traindir) + "...")
		try:
			for f in os.listdir(traindir):
				if str(f).endswith('.mid'):
					print('Splitting ' + str(f) + "...")
					revisedExtract(midi.read_midifile(traindir + '/' + f), str(f))
		except:
			print("Error: files in " + str(traindir) + "are not proper MIDI format.")
			sys.exit(0)

	#Serialize and save for network training
	if optarg == "serialize-only" or optarg == "both":
		#Serialize state matrices of melodies for training
		print("Saving melodies as state matrices...")
		try:
			mel_index = 1
			for m in os.listdir(meldir):
				if str(m) == "serialized":
					continue
				elif str(m).endswith('.mid'):
					print("\tConverting " + str(m) + " to note state matrix...")
					notestates = midi_to_statematrix.midiToNoteStateMatrix(meldir + "/" + str(m))
					print("\tSerializing " + str(m) + "...")
					with open((melpkldir + "/mel" + str(mel_index) + ".pkl"), "wb") as pdump:
						pickle.dump(notestates, pdump)
					mel_index += 1
		except:
			print("Error: unable to serialize melodies.")
			sys.exit(0)
		#Serialize state matrices of accompaniments for output comparison
		print("Saving accompaniments as state matrices...")
		try:
			acc_index = 1
			for a in os.listdir(accdir):
				if str(a) == "serialized":
					continue
				elif str(a).endswith('.mid'):
					print("\tConverting " + str(a) + " to note state matrix...")
					notestates = midi_to_statematrix.midiToNoteStateMatrix(accdir + "/" + str(a))
					print("\tSerializing " + str(a) + "...")
					with open((accpkldir + "/acc" + str(acc_index) + ".pkl"), "wb") as pdump:
						pickle.dump(notestates, pdump)
					acc_index += 1
		except:
			print("Error: unable to serialize accompaniments.")
			sys.exit(0)
