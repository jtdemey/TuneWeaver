#John DeMey
#SMP 2018
#############
#!/usr/bin/python3
import os
import sys
import midi
import midi_to_statematrix
import cPickle as pickle
import numpy
from keras.models import Sequential
from keras.layers import LSTM, Dense, Activation, Dropout, Activation
from keras.callbacks import ModelCheckpoint

#Creates trainable model
def createNewModel(WEAVER_INPUT, WEAVER_OUTPUT):
	if len(WEAVER_INPUT) == 0:
		print("Error: training data unavailable")
		sys.exit(0)
		return
	print("Assembling model...")
	model = Sequential()
	model.add(LSTM(256, input_shape=(WEAVER_INPUT.shape[1], WEAVER_INPUT.shape[2]), return_sequences=True))
	model.add(Dropout(0.25))
	model.add(LSTM(512, return_sequences=True))
	model.add(Dropout(0.25))
	model.add(LSTM(256))
	model.add(Dense(256))
	model.add(Dropout(0.25))
	model.add(Dense(note_range))
	model.add(Activation("softmax"))
	model.compile(loss="categorical_crossentropy", optimizer="rmsprop")
	return model

#Method for retrieving serialized melody/accompaniment data
def getMidiData(WEAVER_INPUT, WEAVER_OUTPUT):
	print("Retrieving melody data for network input...")
	progress = 0
	for melfile in os.listdir(meldir):
		if melfile.endswith(".pkl"):
			mel = pickle.load(open(os.path.join(os.path.dirname( __file__ ), 'melodies/serialized/') + melfile, "rb"))
			melind = 0
			for i in range(0, (len(mel) / sequence_length)):
				currbatch = []
				currbatch.append(mel[melind:(melind + sequence_length)])
				melind += sequence_length
				WEAVER_INPUT.append(currbatch)
		print("\tInput samples: " + str(len(WEAVER_INPUT)))
	print("Retrieving accompaniment data for network output...")
	for accfile in os.listdir(accdir):
		if accfile.endswith(".pkl"):
			acc = pickle.load(open(os.path.join(os.path.dirname( __file__ ), 'accompaniments/serialized/') + accfile, "rb"))
			accind = 0
			for i in range(0, (len(acc) / sequence_length)):
				currbatch = []
				currbatch.append(acc[accind:(accind + sequence_length)])
				accind += sequence_length
				WEAVER_OUTPUT.append(currbatch)
		print("\tOutput samples: " + str(len(WEAVER_OUTPUT)))
	print("Normalizing and encoding data...")
	print("INSIZE: " + str(len(WEAVER_INPUT)))
	#print(WEAVER_INPUT[0])
	#WEAVER_INPUT = numpy.reshape(WEAVER_INPUT, (len(WEAVER_INPUT), sequence_length, 1))
	WEAVER_INPUT = numpy.array(WEAVER_INPUT)
	WEAVER_INPUT = WEAVER_INPUT / float(note_range)
	return WEAVER_INPUT, WEAVER_OUTPUT
	

#Training method
def trainModel(intrain, outtrain):
	if not os.path.exists(meldir):
		print("Error: unable to find /melodies/serialized directory. Have you run prepdata.py?")
		sys.exit(0)
		return
	if not os.path.exists(accdir):
		print("Error: unable to find /accompaniments/serialized directory. Have you run prepdata.py?")
		sys.exit(0)
		return
	intrain, outtrain = getMidiData(intrain, outtrain)
	WEAVER_MODEL = createNewModel(intrain, outtrain)
	checkpath = "weights-improvement-{epoch:02d}-{loss:.4f}-bigger.hdf5"    
	checkpoint = ModelCheckpoint(
		checkpath,
		monitor='loss', 
		verbose=0,        
		save_best_only=True,        
		mode='min'
	)    
	callbacks_list = [checkpoint]     
	WEAVER_MODEL.fit(intrain, outtrain, epochs=200, batch_size=64, callbacks=callbacks_list)

if __name__ == '__main__':
	#Directories for melody/accompaniment midi files
	meldir = os.path.abspath(os.path.join(os.path.dirname( __file__ ), 'melodies/serialized'))
	accdir = os.path.abspath(os.path.join(os.path.dirname( __file__ ), 'accompaniments/serialized'))
	#Data to take as input (melodies)
	WEAVER_INPUT = []
	#Data to compare output to (accompaniments)
	WEAVER_OUTPUT = []
	#Length of sequences in timesteps
	sequence_length = 100
	#Note range
	note_range = 78
	trainModel(WEAVER_INPUT, WEAVER_OUTPUT)
	
