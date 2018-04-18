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
		try:
			model.load_weights(weights)
		except:
			print("Error while loading weights from " + str(weights) + ".")
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

		#Model selection button
		self.modelSelect = Button(self, text="Browse", command=self.selectModel)
		self.modelSelect.place(x=300, y=145)

		#Model selection text
		self.modelDisplay = Label(self, textvariable=self.modelText)
		self.modelDisplay.place(x=380, y=150)

		#Melody selection button
		self.melodySelect = Button(self, text="Browse", command=self.selectMelody)
		self.melodySelect.place(x=300, y=290)

		#Melody selection text
		self.melodyDisplay = Label(self, textvariable=self.melodyText)
		self.melodyDisplay.place(x=380, y=295)

		#Run button
		self.startButton = Button(self, text="Compose", command=self.produceAccompaniment)
		self.startButton.place(x=520, y=440)

		#Progress bar
		self.progress = Progressbar(self, orient=HORIZONTAL, length=800, mode='indeterminate')
		self.progress.place(x=0, y=580)

	def selectModel(self):
		self.modelDir = tkFileDialog.askopenfilename(initialdir=os.getcwd(), title="Select .hdf5 file containing weights")
		splitmod = str(self.modelDir).split('/')
		self.modelText.set(splitmod[len(splitmod) - 1])

	def selectMelody(self):
		self.melodyDir = tkFileDialog.askopenfilename(initialdir=os.getcwd(), title="Select MIDI file containing melody")
		splitmel = str(self.melodyDir).split('/')
		self.melodyText.set(splitmel[len(splitmel) - 1])

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
		try:
			melmatrix = midi_to_statematrix.midiToNoteStateMatrix(self.melodyText)
		except:
			tkMessageBox.showerror('Error :(', 'Unable to read MIDI data in specified melody file')
			return
		melmatrix = numpy.array(melmatrix)

		#Start prediction
		model = createNewModel(self.modelDir)
		newacc = model.predict(melmatrix)

		#Construct complete MIDI
		fullpat = midi.Pattern()
		try:
			for track in melmidi:
				fullpat.append(track)
		except:
			tkMessageBox.showerror('Error :(', 'Unable to add melody track(s) to new MIDI pattern')
			return
		try:
			acctrack = midi_to_statematrix.noteStateMatrixToTrack(newacc)
			fullpat.append(acctrack)
		except:
			tkMessageBox.showerror('Error :(', 'Unable to convert produced accompaniment into MIDI track')
			return
		try:
			midi.write_midifile('newacc.mid', fullpat)
		except:
			tkMessageBox.showerror('Error :(', 'Unable to write final MIDI file')
			return
		os.rename(str(os.getcwd()) + '/newacc.mid', str(os.getcwd()) + '/output/newacc.mid')
		self.progress.stop()
		tkMessageBox.showinfo('Success!', 'New tune exported as newacc.mid')

#Start GUI
weaverwin = Window(weaverroot)
weaverwin.mainloop()
