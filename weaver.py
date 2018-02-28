#John DeMey
#SMP 2018
#############
#!/usr/bin/python3
from Tkinter import *
from abjad import *
from keras.models import Sequential
from keras.layers import Dense, Activation
import midi

#Main window
weaverroot = Tk()
weaverroot.geometry("800x600")
class Window(Frame):

	def __init__(self, master=None):
		Frame.__init__(self, master)
		self.master = master
		self.userInput = StringVar()
		self.makeComponents()

	def makeComponents(self):
		self.master.title("Weaver (alpha)")
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
		#Entry field
		self.melodyField = Entry(self, textvariable=self.userInput, width=75, justify=CENTER)
		self.melodyField.place(x=50, y=300)
		#Run button
		self.startButton = Button(self, text="Compose", command=self.showNote)
		self.startButton.place(x=660, y=296)

	def showNote(self):
		notesIn = self.userInput.get()
		thisnote = Note(notesIn)
		show(thisnote)

#Start GUI
weaverwin = Window(weaverroot)
weaverwin.mainloop()
