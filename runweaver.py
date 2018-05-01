#John DeMey
#SMP 2018
#############
#!/usr/bin/python3
import os
from tkinter import *
from tkinter.ttk import Progressbar
import tkFileDialog
import tkMessageBox
from keras.models import Sequential
from keras.layers import LSTM, Dense, Activation, Dropout, Activation
import midi
import midi_to_statematrix
import numpy

#Length of sequences in timesteps
sequence_length = 100
#Note range
note_range = 78

#Model construction method
def createNewModel(weights):
	print("Assembling model...")
	model = Sequential()
	model.add(LSTM(256, input_shape=(sequence_length, note_range), return_sequences=True))
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
		print('Loading node weights...')
		#try:
		model.load_weights(weights)
		#except:
		#	print("Error while loading weights from " + str(weights) + ".")
	model.compile(loss="categorical_crossentropy", optimizer="rmsprop")
	print('Model created')
	return model

#Main window
weaverroot = Tk()
weaverroot.geometry("800x600")
class Window(Frame):

	def __init__(self, master=None):
		Frame.__init__(self, master)
		self.master = master
		self.modelDir = None
		self.melodyDir = None
		self.modelText = StringVar()
		self.melodyText = StringVar()
		self.makeComponents()

	def makeComponents(self):
		self.master.title("TuneWeaver")
		self.pack(fill=BOTH, expand=1)

		#Background
		bgimg = PhotoImage(file='./media/bg.png')
		bglbl = Label(self, image=bgimg)
		bglbl.image = bgimg
		bglbl.place(x=0, y=0, relwidth=1, relheight=1)

		#Menu bar
		menubar = Menu(weaverroot)
		#File...
		menu_file = Menu(menubar, tearoff=0)
		menu_file.add_command(label="Exit", command=weaverroot.quit)
		menubar.add_cascade(label="File", menu=menu_file)
		#Attach menu
		weaverroot.config(menu=menubar)

		#Model selection button
		self.modelSelect = Button(self, text="Browse", command=self.selectModel)
		self.modelSelect.place(x=320, y=175)

		#Model selection text
		self.modelDisplay = Label(self, textvariable=self.modelText)
		self.modelDisplay.place(x=400, y=180)

		#Melody selection button
		self.melodySelect = Button(self, text="Browse", command=self.selectMelody)
		self.melodySelect.place(x=320, y=320)

		#Melody selection text
		self.melodyDisplay = Label(self, textvariable=self.melodyText)
		self.melodyDisplay.place(x=400, y=325)

		#Run button
		self.startButton = Button(self, text="Compose", command=self.produceAccompaniment)
		self.startButton.place(x=540, y=470)

		#Progress bar
		self.progress = Progressbar(self, orient=HORIZONTAL, length=800, mode='indeterminate')
		self.progress.place(x=0, y=580)

	def selectModel(self):
		self.modelDir = tkFileDialog.askopenfilename(initialdir=os.getcwd(), title="Select .hdf5 file containing weights")
		splitmod = str(self.modelDir).split('/')
		self.modelText.set(splitmod[len(splitmod) - 1])

	def selectMelody(self):
		self.melodyDir = tkFileDialog.askopenfilename(initialdir=os.getcwd(), title="Select MIDI file containing melody")
		if '/' in self.melodyDir:
			splitmel = str(self.melodyDir).split('/')
			self.melodyText.set(splitmel[len(splitmel) - 1])
		else:
			self.melodyText.set(self.melodyDir)

	def produceAccompaniment(self):
		#Check for user input
		if self.modelDir == None:
			tkMessageBox.showerror('Error :(', 'No model weights selected.')
			return
		if self.melodyDir == None:
			tkMessageBox.showerror('Error :(', 'No melody file selected.')
			return

		#Prepare melody data
		self.progress.start()
		predmel = []
		melind = 0
		try:
			melmatrix = midi_to_statematrix.midiToNoteStateMatrix(self.melodyText.get())
		except:
			tkMessageBox.showerror('Error :(', 'Unable to read MIDI data in specified melody file')
			self.progress.stop()
			return
		for i in range(0, (len(melmatrix) / sequence_length)):
			currbatch = melmatrix[melind:(melind + sequence_length)]
			melind += sequence_length
			predmel.append(currbatch)
		predmel = numpy.array(predmel)
		predmel = predmel / float(note_range)

		#Start prediction
		model = createNewModel(self.modelDir)
		predacc = model.predict_classes(predmel)

		#Create statematrix for new accompaniment
		newacc = [[[0, 0] for k in range(78)] for i in range(predmel.shape[0] * predmel.shape[1])]
		newacc = numpy.array(newacc)

		#Transfer predicted accompaniment notes from sequences to statematrix
		ts_index = 0
		for seq in predacc:
			for tone in seq:
				newacc[ts_index][tone] = [1, 1]
				ts_index += 1
		newacc = numpy.array(newacc)

		#Establish held tones
		heldtone = 999
		note_index = 0
		for ts in newacc:
			note_index = 0
			for note in ts:
				if note[0] == 1 and note[1] == 1 and heldtone != note_index:
					heldtone = note_index
					#print("HELD TONE IS: " + str(note_index))
				elif note[0] == 1 and note[1] == 1 and heldtone == note_index:
					note[1] = 0
				note_index += 1

		#Construct complete MIDI
		fullpat = midi.read_midifile(self.melodyDir)
		for track in fullpat:
			for evt in track:
				if isinstance(evt, midi.SetTempoEvent):
					print("EVT: " + str(evt))
		#try:
		print(newacc.shape)
		print(newacc)
		acctrack = midi_to_statematrix.noteStateMatrixToTrack(newacc)
		fullpat.append(acctrack)
		#except:
			#tkMessageBox.showerror('Error :(', 'Unable to convert produced accompaniment into MIDI track')
			#self.progress.stop()
			#return
		try:
			midi.write_midifile('newacc.mid', fullpat)
		except:
			tkMessageBox.showerror('Error :(', 'Unable to write final MIDI file')
			self.progress.stop()
			return
		os.rename(str(os.getcwd()) + '/newacc.mid', str(os.getcwd()) + '/output/newacc.mid')
		self.progress.stop()
		tkMessageBox.showinfo('Success!', 'New tune exported as newacc.mid')

#Start GUI
weaverwin = Window(weaverroot)
weaverwin.mainloop()
