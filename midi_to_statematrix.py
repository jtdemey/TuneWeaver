# OBTAINED FROM: https://github.com/hexahedria/biaxial-rnn-music-composition
# Written by hexahedria
# Modified/supplemented by John DeMey
# Utility script used for converting MIDI data into a numeric note sequence
import midi, numpy

lowerBound = 24
upperBound = 102

def midiToNoteStateMatrix(midifile):

    pattern = midi.read_midifile(midifile)

    timeleft = [track[0].tick for track in pattern]

    posns = [0 for track in pattern]

    statematrix = []
    span = upperBound-lowerBound
    time = 0

    state = [[0,0] for x in range(span)]
    statematrix.append(state)
    while True:
        if time % (pattern.resolution / 4) == (pattern.resolution / 8):
            # Crossed a note boundary. Create a new state, defaulting to holding notes
            oldstate = state
            state = [[oldstate[x][0],0] for x in range(span)]
            statematrix.append(state)

        for i in range(len(timeleft)):
            while timeleft[i] == 0:
                track = pattern[i]
                pos = posns[i]

                evt = track[pos]
                if isinstance(evt, midi.NoteEvent):
                    if (evt.pitch < lowerBound) or (evt.pitch >= upperBound):
                        pass
                        # print "Note {} at time {} out of bounds (ignoring)".format(evt.pitch, time)
                    else:
                        if isinstance(evt, midi.NoteOffEvent) or evt.velocity == 0:
                            state[evt.pitch-lowerBound] = [0, 0]
                        else:
                            state[evt.pitch-lowerBound] = [1, 1]
                elif isinstance(evt, midi.TimeSignatureEvent):
                    if evt.numerator not in (2, 4):
                        # We don't want to worry about non-4 time signatures. Bail early!
                        print "Found time signature event {}. Bailing!".format(evt)
                        return statematrix

                try:
                    timeleft[i] = track[pos + 1].tick
                    posns[i] += 1
                except IndexError:
                    timeleft[i] = None

            if timeleft[i] is not None:
                timeleft[i] -= 1

        if all(t is None for t in timeleft):
            break

        time += 1

    #Convert note state arrays to ints to conform to Keras' learning model specifications
    statematrix = convertNotesToInts(statematrix)
    return statematrix

def noteStateMatrixToMidi(statematrix, name="example"):
    #Transform single-integer encoded notes back into arrays
    statematrix = convertIntsToNotes(statematrix)

    statematrix = numpy.asarray(statematrix)
    pattern = midi.Pattern()
    track = midi.Track()
    pattern.append(track)
    
    span = upperBound-lowerBound
    tickscale = 55
    
    lastcmdtime = 0
    prevstate = [[0,0] for x in range(span)]
    for time, state in enumerate(statematrix + [prevstate[:]]):  
        offNotes = []
        onNotes = []
        for i in range(span):
            n = state[i]
            p = prevstate[i]
            if p[0] == 1:
                if n[0] == 0:
                    offNotes.append(i)
                elif n[1] == 1:
                    offNotes.append(i)
                    onNotes.append(i)
            elif n[0] == 1:
                onNotes.append(i)
        for note in offNotes:
            track.append(midi.NoteOffEvent(tick=(time-lastcmdtime)*tickscale, pitch=note+lowerBound))
            lastcmdtime = time
        for note in onNotes:
            track.append(midi.NoteOnEvent(tick=(time-lastcmdtime)*tickscale, velocity=40, pitch=note+lowerBound))
            lastcmdtime = time
            
        prevstate = state
    
    eot = midi.EndOfTrackEvent(tick=1)
    track.append(eot)

    midi.write_midifile("{}.mid".format(name), pattern)

#Modified noteStateMatrixToMidi that simply returns a track object with note events without writing MIDI file
def noteStateMatrixToTrack(statematrix):

    statematrix = numpy.asarray(statematrix)
    track = midi.Track()
    
    span = upperBound-lowerBound
    tickscale = 74
	#55
    
    lastcmdtime = 0
    prevstate = [[0,0] for x in range(span)]
    for time, state in enumerate(statematrix + [prevstate[:]]):  
        offNotes = []
        onNotes = []
        for i in range(span):
            n = state[i]
            p = prevstate[i]
            if p[0] == 1:
                if n[0] == 0:
                    offNotes.append(i)
                elif n[1] == 1:
                    offNotes.append(i)
                    onNotes.append(i)
            elif n[0] == 1:
                onNotes.append(i)
        for note in offNotes:
            track.append(midi.NoteOffEvent(tick=(time-lastcmdtime)*tickscale, pitch=note+lowerBound))
            lastcmdtime = time
        for note in onNotes:
            track.append(midi.NoteOnEvent(tick=(time-lastcmdtime)*tickscale, velocity=40, pitch=note+lowerBound))
            lastcmdtime = time
            
        prevstate = state
    
    eot = midi.EndOfTrackEvent(tick=1)
    track.append(eot)
    return track

#Added method for one-hot character encoding the four possible note values
def convertNotesToInts(statematrix):
	for i in range(0, len(statematrix)):
		timestep = statematrix[i]
		for n in range(0, len(timestep)):
			note = timestep[n]
			if note == [0, 0]:
				timestep[n] = 0
			elif note == [1, 1]:
				timestep[n] = 1
			elif note == [1, 0]:
				timestep[n] = 1
			elif note == [0, 1]:
				timestep[n] = 1
			else:
				print("Non-note detected")
				print(note)
				timestep[n] = 0
			#print(str(note) + ' converted to ' + str(timestep[n]))
		statematrix[i] = timestep
	return statematrix

#Convert int notes back to their array form
def convertIntsToNotes(statematrix):
	for i in range(0, len(statematrix)):
		timestep = statematrix[i]
		for n in range(0, len(timestep)):
			note = timestep[n]
			#print(note)
			if note == 0:
				timestep[n] = [0, 0]
			elif note == 1:
				timestep[n] = [1, 1]
			elif note == 2:
				timestep[n] = [1, 0]
			elif note == 3:
				timestep[n] = [0, 1]
			else:
				print("Non-note detected")
				timestep[n] = [0, 0]
			#print(str(note) + ' converted to ' + str(timestep[n]))
		statematrix[i] = timestep
	return statematrix

#Convert note probabilities (network output) into notes
def convertProbabilitiesToNotes(statematrix):
	for i in range(0, len(statematrix)):
		timestep = statematrix[i]
		for n in range(0, len(timestep)):
			probs = timestep[n]
			noteind = probs.index(max(probs))
			note = [[0, 0] for i in range(len(probs))]
			note[noteind] = [1, 1]
			if note == 0:
				timestep[n] = [0, 0]
			elif note == 1:
				timestep[n] = [1, 1]
			elif note == 2:
				timestep[n] = [1, 0]
			elif note == 3:
				timestep[n] = [0, 1]
			else:
				print("Non-note detected")
				timestep[n] = [0, 0]
			#print(str(note) + ' converted to ' + str(timestep[n]))
		statematrix[i] = timestep
	return statematrix

testmatrix = midiToNoteStateMatrix('elise_mel.mid')
testfile = noteStateMatrixToMidi(testmatrix, 'testtttt.mid')
