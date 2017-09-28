#John DeMey
#SMP 2017
#############

from Tkinter import *
from abjad import *

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
		#Entry field
		self.melodyField = Entry(self, textvariable=self.userInput, width=50, justify=CENTER)
		self.melodyField.place(x=50, y=500)
		#Run button
		self.startButton = Button(self, text="Run", command=self.showNote)
		self.startButton.place(x=500, y=495)

	def showNote(self):
		notesIn = self.userInput.get()
		thisnote = Note(notesIn)
		show(thisnote)

#Start GUI
weaverwin = Window(weaverroot)
weaverwin.mainloop()
