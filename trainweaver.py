#John DeMey
#SMP 2018
#############
#!/usr/bin/python3
import os
import sys
from datetime import datetime
import pickle
import numpy
from keras.models import Sequential
from keras.layers import LSTM, Dense, Activation, Dropout, Activation
from keras.callbacks import ModelCheckpoint

#Directory to export models/weights
modeldir = os.path.abspath(os.path.join(os.path.dirname( __file__ ), 'models'))
if not os.path.exists(modeldir):
	os.makedirs(modeldir)

#Creates trainable model
def createNewModel(WEAVER_INPUT, WEAVER_OUTPUT, weights):
	if len(WEAVER_INPUT) < 1:
		print("Error: training data unavailable")
		sys.exit(0)
		return
	if len(WEAVER_OUTPUT) < 1:
		print("Error: output data unavailable")
		sys.exit(0)
		return
	print("Assembling model...")
	model = Sequential()
	model.add(LSTM(256, input_shape=(WEAVER_INPUT.shape[1], WEAVER_INPUT.shape[2]), return_sequences=True))
	print("Added LSTM")
	model.add(Dropout(0.25))
	print("Added 25% Dropout")
	model.add(LSTM(512, return_sequences=True))
	print("Added LSTM")
	model.add(Dropout(0.25))
	print("Added 25% Dropout")
	model.add(LSTM(256, return_sequences=True))
	print("Added LSTM")
	model.add(Dense(256))
	print("Added Dense layer")
	model.add(Dropout(0.25))
	print("Added 25% Dropout")
	model.add(Dense(note_range))
	print("Added final Dense layer")
	model.add(Activation("softmax"))
	print("Added softmax activation")
	if weights != None:
		try:
			model.load_weights(weights)
			print("Weights loaded from " + str(weights) + ".")
		except:
			print("Error while loading weights from " + str(weights) + ", starting training from scratch.")
	model.compile(loss="categorical_crossentropy", optimizer="rmsprop")
	return model

#Method for retrieving serialized melody/accompaniment data
def getMidiData(WEAVER_INPUT, WEAVER_OUTPUT):
	print("Retrieving melody data for network input...")
	meltotal = 0.0
	melsgot = 0.0
	acctotal = 0.0
	accsgot = 0.0
	#Gather totals
	for m in os.listdir(meldir):
		if m.endswith(".pkl"):
			meltotal = meltotal + 1
	for a in os.listdir(accdir):
		if a.endswith(".pkl"):
			acctotal = acctotal + 1
	#Gather sequences
	for melfile in os.listdir(meldir):
		#Open binarized melodies
		if melfile.endswith(".pkl"):
			mel = pickle.load(open(os.path.join(os.path.dirname( __file__ ), 'melodies/serialized/') + melfile, "rb"))
			melind = 0
			melsgot = melsgot + 1
			#Separate into batches whose size is determined by sequence_length
			for i in range(0, (len(mel) / sequence_length)):
				currbatch = mel[melind:(melind + sequence_length)]
				#currbatch.append(mel[melind:(melind + sequence_length)])
				melind += sequence_length
				WEAVER_INPUT.append(currbatch)
		sys.stdout.write("\r\tInput samples: " + str(len(WEAVER_INPUT)) + " (" + str(melsgot / meltotal * 100)[:5] + "%)")
		sys.stdout.flush()

	print("\nRetrieving accompaniment data for network output...")
	for accfile in os.listdir(accdir):
		#Open binarized accompaniments
		if accfile.endswith(".pkl"):
			acc = pickle.load(open(os.path.join(os.path.dirname( __file__ ), 'accompaniments/serialized/') + accfile, "rb"))
			accind = 0
			accsgot = accsgot + 1
			for i in range(0, (len(acc) / sequence_length)):
				currbatch = acc[accind:(accind + sequence_length)]
				#currbatch.append(acc[accind:(accind + sequence_length)])
				accind += sequence_length
				WEAVER_OUTPUT.append(currbatch)
		sys.stdout.write("\r\tOutput samples: " + str(len(WEAVER_OUTPUT)) + " (" + str(accsgot / acctotal * 100)[:5] + "%)")
		sys.stdout.flush()

	print("\nNormalizing and encoding data...")
	#WEAVER_INPUT = numpy.reshape(WEAVER_INPUT, (len(WEAVER_INPUT), sequence_length, 1))
	WEAVER_INPUT = numpy.array(WEAVER_INPUT)
	WEAVER_OUTPUT = numpy.array(WEAVER_OUTPUT)
	WEAVER_INPUT = WEAVER_INPUT / float(note_range)
	print("WEAVERSHAPE: " + str(WEAVER_INPUT.shape))
	return WEAVER_INPUT, WEAVER_OUTPUT
	
#Training method
def trainModel(intrain, outtrain, epochct, weights):
	#Check for serialized data
	if not os.path.exists(meldir):
		print("Error: unable to find /melodies/serialized directory. Have you run prepweaver.py?")
		sys.exit(0)
		return
	if not os.path.exists(accdir):
		print("Error: unable to find /accompaniments/serialized directory. Have you run prepweaver.py?")
		sys.exit(0)
		return
	#Gather data
	intrain, outtrain = getMidiData(intrain, outtrain)
	#Create Sequential model
	WEAVER_MODEL = createNewModel(intrain, outtrain, weights)
	#Enable saving of weights to file as checkpoint
	checkpath = str(os.getcwd()) + "/models/" + str(datetime.now()).split(" ")[0] + "-E{epoch:02d}-L{loss:.4f}.hdf5"
	checkpoint = ModelCheckpoint(
		checkpath,
		monitor='loss', 
		verbose=1,        
		save_best_only=True,        
		mode='min'
	)    
	callbacks_list = [checkpoint]
	#Train model
	print("=== " + str(datetime.now()) + " STARTING TUNEWEAVER TRAINING ===")
	WEAVER_MODEL.fit(intrain, outtrain, epochs=epochct, batch_size=64, callbacks=callbacks_list)

if __name__ == '__main__':
	print("################ TuneWeaver ################")
	print("--------------------------------------------")
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
	#Epoch count
	epochct = 200
	#Weight file (if resuming training)
	weightfile = None
	#Get input
	if len(sys.argv) > 1:
		try:
			epochct = int(sys.argv[1])
			print("Preparing to train for " + str(epochct) + " epochs.")
		except:
			print("Could not parse " + str(sys.argv[1]) + " as an integer, assuming 200 epochs.")
	if len(sys.argv) > 2:
		try:
			weightfile = sys.argv[2]
			print("Using pre-trained weights from " + str(weightfile) + ".")
		except:
			print("Could not load weights from " + str(sys.argv[2]) + ", starting training from scratch.")
	trainModel(WEAVER_INPUT, WEAVER_OUTPUT, epochct, weightfile)

