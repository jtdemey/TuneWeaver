#John DeMey
#SMP 2018
#############
#!/usr/bin/python3
import os
from Tkinter import *
from tkinter.ttk import Progressbar
from tkinter import messagebox
import tkFileDialog
from keras.models import Sequential
from keras.layers import LSTM, Dense, Activation, Dropout, Activation
import midi
import midi_to_statematrix

#Length of sequences in timesteps
sequence_length = 100
#Note range
note_range = 78

#Model construction method
def createNewModel():
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
	model.compile(loss="categorical_crossentropy", optimizer="rmsprop")
	print('Loading node weights...')
	model.load_weights(self.modelDir)
	print('Model created')
	return model

#Main window
weaverroot = Tk()
weaverroot.geometry("800x600")
class Window(Frame):

	def __init__(self, master=None):
		Frame.__init__(self, master)
		self.master = master
		self.makeComponents()
		self.modelDir = None
		self.melodyDir = None

	def makeComponents(self):
		self.master.title("TuneWeaver")
		self.pack(fill=BOTH, expand=1)

		#Background
		bgimg = PhotoImage(file='./weaver/bg.png')
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

		#Model selection field
		self.modelSelect = Button(self, text="Browse", command=self.selectModel)
		self.modelSelect.place(x=600, y=180)

		#Melody selection field
		self.melodySelect = Button(self, text="Browse", command=self.selectMelody)
		self.melodySelect.place(x=600, y=300)

		#Run button
		self.startButton = Button(self, text="Compose", command=self.produceAccompaniment)
		self.startButton.place(x=600, y=450)

		#Progress bar
		self.progress = Progressbar(self, orient=HORIZONTAL, length=800, mode='indeterminate')
		self.progress.place(x=0,y=580)

	def selectModel(self):
		self.modelDir = tkFileDialog.askopenfilename(initialdir=os.getcwd(), title="Select .hdf5 file containing trained model weights")

	def selectMelody(self):
		self.melodyDir = tkFileDialog.askopenfilename(initialdir=os.getcwd(), title="Select MIDI file containing melody")

	def produceAccompaniment(self):
		#Check for user input
		if self.modelDir == None:
			messagebox.showerror('Error', 'No model weights selected.')
			return
		if self.melodyDir == None:
			messagebox.showerror('Error', 'No melody file selected.')
			return

		#Prepare melody data
		try:
			melmidi = midi.read_midifile(self.melodyDir)
		except:
			messagebox.showerror('Error', 'Unable to read MIDI data in specified melody file')
			return
		melmatrix = midi_to_statematrix.midiToNoteStateMatrix(melmidi)
		melmatrix = numpy.array(melmatrix)
		#Start prediction
		self.progress.start()
		model = createNewModel()
		newacc = model.predict(melmatrix)
		accmidi = midi_to_statematrix.noteStateMatrixToMidi(newacc, name='newacc.mid')
		os.rename(str(os.getcwd()) + '/newacc.mid', 'output/newacc.mid')
		self.progress.stop()

#Start GUI
weaverwin = Window(weaverroot)
weaverwin.mainloop()
