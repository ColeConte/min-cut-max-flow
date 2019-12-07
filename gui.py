import tkinter as tk
from driver import *
import libDriver
from tkinter.filedialog import askopenfilename
import os.path

#To Fix:
#Validate text and integer inputs
#Validate at least one input
#Validate for no repeat entries

class MainApplication(tk.Tk):
	def __init__(self):
		super(MainApplication,self).__init__()
		self.selectionWindow = SelectionWindow(self)
		self.RegionInputWindow = None
		self.HospitalInputWindow = None
		self.AmbulanceInputWindow = None
		self.WriteOutputWindow = None
		self.OutputWindow = None
		self.fromGUI = None
		self.regionsText = "[Regions]\n"
		self.regions = []
		self.hospitalsText = "[Hospitals]\n"
		self.hospitals = []
		self.ambulancesText = "[Ambulatory Service]\n"
		self.ambulances = []
		self.selectionWindow.show()

	'''Creates GUI input window.'''	
	def createRegionInputWindow(self):
		self.RegionInputWindow = RegionInputWindow(self)

	'''Creates GUI input window.'''	
	def createHospitalInputWindow(self):
		self.HospitalInputWindow = HospitalInputWindow(self)

	'''Creates GUI input window.'''	
	def createAmbulanceInputWindow(self):
		self.AmbulanceInputWindow = AmbulanceInputWindow(self)	

	'''Creates GUI output window.'''	
	def createWriteOutputWindow(self):
		self.WriteOutputWindow = WriteOutputWindow(self)	

	'''Creates GUI output window.'''	
	def createOutputWindow(self):
		self.OutputWindow = OutputWindow(self)

	'''
	Imports JSON or CSV file, or reads from GUI input
	'''
	def importFile(self,writeToFile):
		if self.fromGUI:
			text = self.regionsText + '\n' + self.hospitalsText + '\n' + self.ambulancesText
			vNum, fDemanded, edges, names = processGuiInput(text)
		else:	
			file = askopenfilename(filetypes=(('csv files','*.csv'),('json files','*.json')),title='Select a file')
			extension = os.path.splitext(file)[1]
			if extension == ".csv":
				vNum, fDemanded, edges, names = extractFile(file)
			elif extension == ".json":
				vNum, fDemanded, edges, names = libDriver.extractFromJson(file,True)
		self.createOutputWindow()
		self.generateOutput(vNum, fDemanded, edges, names,writeToFile)
		self.OutputWindow.show()

	'''Generates text for GUI output window.'''
	def generateOutput(self,vNum, fDemanded, edges, names,writeToFile):
		flowSupplied, pathing = fordFulkerson(vNum, edges, 0, vNum-1)
		#Option to generate an output file
		files = [self.OutputWindow.textvar]
		if writeToFile:
			file = open("output.txt","w+")
			files.append(file)
		for f in files:
			if(fDemanded == flowSupplied):
				print("Ambulatory Network can sustain all injured.",file=f)
				print("Quickly use the following routes:",file=f)
			else:
				print("Ambulatory Network *cannot* sustain all injured.",file=f)
				print("To minimize loss of life, triage and use the following routes: ",file=f)
			for (injured, path) in pathing:
				print("\nSend %05d Injured Along: " % injured, end="",file=f)
				for i, route in enumerate(path[1:-1]):
					print("%s" % (names[route]), end="",file=f)
					if(i < len(path)-3):
						print(" -> ", end="",file=f)


class SelectionWindow(tk.Frame):
	def __init__(self,root):
		super(SelectionWindow,self).__init__()
		self.root = root
		self.radioSelection = tk.IntVar()
		self.fromFile = tk.Radiobutton(self, text='From File',variable=self.radioSelection,value=0).pack()
		self.fromGUI = tk.Radiobutton(self, text='From GUI',variable=self.radioSelection,value=1).pack()
		self.cont = tk.Button(self, text='Continue', width=25, command=self.inputType).pack()
		self.stop = tk.Button(self, text='Stop', width=25, command=self.root.destroy).pack()

	'''Shows selection window.'''
	def show(self):
		self.pack()

	'''Determines user radio button selection.'''
	def inputType(self):
		selected = self.radioSelection.get()
		if(selected == 0):
			self.root.fromGUI = False
			self.root.createWriteOutputWindow()
			self.destroy()
			self.root.WriteOutputWindow.show()
		else:
			self.root.fromGUI = True
			self.root.createRegionInputWindow()
			self.destroy()
			self.root.RegionInputWindow.show()


class RegionInputWindow(tk.Frame):
	def __init__(self,root):
		super(RegionInputWindow,self).__init__()
		self.root = root
		regionLabel = (tk.Label(self, text='Region: ')).grid(row=0,column=0)
		victimCountLabel = (tk.Label(self, text='Victims: ')).grid(row=1,column=0)
		self.regionTextEntry = tk.StringVar()
		self.victimCountEntry = tk.IntVar()
		self.region = tk.Entry(self, textvariable = self.regionTextEntry).grid(row=0,column=1) #need to validate text
		self.victims = tk.Entry(self, textvariable = self.victimCountEntry).grid(row=1,column=1) #need to validate integer
		self.add = tk.Button(self, text='Add', width=25, command=self.addToRegions).grid(row=2,column=0)
		self.cont = tk.Button(self, text='Continue', width=25, command=self.toHospitalInput).grid(row=2,column=1)
		self.stop = tk.Button(self, text='Stop', width=25, command=self.root.destroy).grid(row=3,column=0,columnspan=2)

	'''Shows input window.'''
	def show(self):
		self.pack()

	def addToRegions(self):
		region = self.regionTextEntry.get()
		self.root.regions.append(region) #validate
		victims = self.victimCountEntry.get()
		self.root.regionsText += (region+', '+str(victims)+'\n')

	def toHospitalInput(self):
		self.root.regionsText += ('\n')
		self.root.createHospitalInputWindow()
		self.destroy()
		self.root.HospitalInputWindow.show()


class HospitalInputWindow(tk.Frame):
	def __init__(self,root):
		super(HospitalInputWindow,self).__init__()
		self.root = root
		hospitalLabel = (tk.Label(self, text='Hospital: ')).grid(row=0,column=0)
		capacityLabel = (tk.Label(self, text='Capacity: ')).grid(row=1,column=0)
		self.hospitalTextEntry = tk.StringVar()
		self.capacityEntry = tk.IntVar()
		self.hospital = tk.Entry(self, textvariable = self.hospitalTextEntry).grid(row=0,column=1)#need to validate text
		self.capacity = tk.Entry(self,textvariable = self.capacityEntry).grid(row=1,column=1) #need to validate integer
		self.add = tk.Button(self, text='Add', width=25, command=self.addToHospitals).grid(row=2,column=0)
		self.cont = tk.Button(self, text='Continue', width=25, command=self.toAmbulanceInput).grid(row=2,column=1)
		self.stop = tk.Button(self, text='Stop', width=25, command=self.root.destroy).grid(row=3,column=0,columnspan=2)

	'''Shows input window.'''
	def show(self):
		self.pack()

	def addToHospitals(self):
		hospital = self.hospitalTextEntry.get()
		self.root.hospitals.append(hospital) #validate
		capacity = self.capacityEntry.get()
		self.root.hospitalsText += (hospital+', '+str(capacity)+'\n')

	def toAmbulanceInput(self):
		self.root.hospitalsText += ('\n')
		self.root.createAmbulanceInputWindow()
		self.destroy()
		self.root.AmbulanceInputWindow.show()

class AmbulanceInputWindow(tk.Frame):
	def __init__(self,root):
		super(AmbulanceInputWindow,self).__init__()
		self.root = root
		regionLabel = tk.Label(self, text='Region: ').grid(row=0,column=0)
		hospitalLabel = tk.Label(self, text='Hospital: ').grid(row=1,column=0)
		ambulanceLabel = tk.Label(self, text='Ambulance: ').grid(row=2,column=0)
		capacityLabel = tk.Label(self, text='Capacity: ').grid(row=3,column=0)
		self.ambulanceTextEntry = tk.StringVar()
		self.capacityEntry = tk.IntVar()
		self.regionEntry = tk.StringVar()
		self.regionEntry.set(self.root.regions[0]) # default value
		self.hospitalEntry = tk.StringVar()
		self.hospitalEntry.set(self.root.hospitals[0]) # default value
		self.region = tk.OptionMenu(self, self.regionEntry, *self.root.regions).grid(row=0,column=1)
		self.hospital = tk.OptionMenu(self, self.hospitalEntry, *self.root.hospitals).grid(row=1,column=1)
		self.ambulance = tk.Entry(self, textvariable = self.ambulanceTextEntry).grid(row=2,column=1) #need to validate text
		self.capacity = tk.Entry(self, textvariable = self.capacityEntry).grid(row=3,column=1) #need to validate integer
		self.add = tk.Button(self, text='Add', width=25, command=self.addToAmbulances).grid(row=4,column=0)
		self.finish = tk.Button(self, text='Finish', width=25, command=self.finish).grid(row=4,column=1)
		self.stop = tk.Button(self, text='Stop', width=25, command=self.root.destroy).grid(row=5,column=0,columnspan=2)

	'''Shows input window.'''
	def show(self):
		self.pack()

	def addToAmbulances(self):
		ambulance = self.ambulanceTextEntry.get()
		region = self.regionEntry.get()
		hospital = self.hospitalEntry.get()
		self.root.ambulances.append(ambulance) #validate
		capacity = self.capacityEntry.get()
		self.root.ambulancesText += (ambulance+', '+region+', '+hospital+', '+str(capacity)+'\n')

	def finish(self):
		self.root.ambulancesText += ('\n')
		self.root.createWriteOutputWindow()
		self.destroy()
		self.root.WriteOutputWindow.show()

class WriteOutputWindow(tk.Frame):
	def __init__(self,root):
		super(WriteOutputWindow,self).__init__()
		self.root = root
		self.radioSelection = tk.IntVar()
		writeLabel = tk.Label(self, text='Write Output to File?').pack()
		self.yes = tk.Radiobutton(self, text='Yes',variable=self.radioSelection,value=0).pack()
		self.no = tk.Radiobutton(self, text='No',variable=self.radioSelection,value=1).pack()
		self.cont = tk.Button(self, text='Continue', width=25, command=self.toOutput).pack()

	'''Shows selection window.'''
	def show(self):
		self.pack()

	'''Determines user radio button selection.'''
	def toOutput(self):
		selected = self.radioSelection.get()
		if(selected == 0):
			self.root.importFile(True)
		else:
			self.root.importFile(False)
		self.destroy()
		self.root.OutputWindow.show()


class OutputWindow(tk.Frame):
	def __init__(self,root):
		super(OutputWindow,self).__init__()
		self.root = root
		self.textvar = WritableStringVar(root)
		outputLabel = tk.Label(self, textvariable=self.textvar,wraplength='800')
		outputLabel.pack()
		self.stop = tk.Button(self, text='End', command=self.root.destroy).pack()

	'''Shows selection window.'''
	def show(self):
		self.pack()


class WritableStringVar(tk.StringVar):
	'''Writable subclass of StringVar class.
	Code taken from: 
	https://stackoverflow.com/questions/42195572/setting-multiple-lines-to-a-label-tkinter'''
	def write(self, added_text):
		new_text = self.get() + added_text
		self.set(new_text)
	def clear(self):
		self.set("")

root = MainApplication()
root.title("Emergency Services")
root.mainloop()