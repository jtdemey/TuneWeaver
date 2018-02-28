#John DeMey
#SMP 2018
#############
#!/usr/bin/python2.7
import os
import midi
import sys
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

def medianExtract(pattern, trackname):
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
		#print("NoteEvent: " + str(notes[nind]))
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
				if notes[nind].tick < 1:
					try:
						mel.remove(notes[nind])
					except:
						print("Something odd happened involving a chord...")
		except:
			print("No note velocity in data")
		if nind < len(notes):
				nind = nind + 1
	#Export melody/accompaniment
	print("Exporting separate MIDIs...")
	exportTrack(mel, acc, trackname, melody=True)
	exportTrack(mel, acc, trackname, melody=False)
	
def exportTrack(mel, acc, trackname, melody=True):
	#Construct pattern
	newpat = midi.Pattern()
	newtrack = midi.Track()
	newpat.append(newtrack)
	newtrack.append(midi.TimeSignatureEvent(tick=0, data=[4, 2, 24, 8]))
	newtrack.append(midi.KeySignatureEvent(tick=0, data=[251, 0]))
	if melody == True:
		fname = str(trackname[:-4]) + '_mel.mid'
		destdir = meldir
		for f in mel:
			newtrack.append(f)
	else:
		fname = str(trackname[:-4]) + '_acc.mid'
		destdir = accdir
		for a in acc:
			newtrack.append(a)
	newtrack.append(midi.EndOfTrackEvent(tick=1))
	#Write file
	midi.write_midifile(fname, newpat)
	#Move to proper directory
	os.rename(str(os.getcwd()) + '/' + fname, destdir + '/' + fname)
	
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
		print("Usage: python prepdata.py [directory of source MIDI files] {split-only / serialize-only / both}")
		sys.exit(0)
	print("################ TuneWeaver ################")
	print("--------------------------------------------")
	traindir = sys.argv[1]
	if len(sys.argv) > 2:
		optarg = sys.argv[2]
	else:
		optarg = "both"

	#Split MIDI files into their respective melodies and accompaniments
	if optarg == "split-only" or optarg == "both":
		print("Looking for MIDI files in " + str(traindir) + "...")
		#test1 = midi_to_statematrix.midiToNoteStateMatrix('chpn-p1.mid')
		try:
			for f in os.listdir(traindir):
				print('Splitting ' + str(f) + "...")
				medianExtract(midi.read_midifile(traindir + '/' + f), str(f))
		except:
			print("Error: no MIDI files found in " + str(traindir))
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
				else:
					print("Converting " + str(m) + " to note state matrix...")
					notestates = midi_to_statematrix.midiToNoteStateMatrix(meldir + "/" + str(m))
					print("Serializing " + str(m) + "...")
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
				else:
					print("Converting " + str(a) + " to note state matrix...")
					notestates = midi_to_statematrix.midiToNoteStateMatrix(accdir + "/" + str(a))
					print("Serializing " + str(a) + "...")
					with open((accpkldir + "/acc" + str(acc_index) + ".pkl"), "wb") as pdump:
						pickle.dump(notestates, pdump)
					acc_index += 1
		except:
			print("Error: unable to serialize accompaniments.")
			sys.exit(0)
