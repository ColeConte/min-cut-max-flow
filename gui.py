import tkinter as tk
from driver import *
import libDriver
from tkinter.filedialog import askopenfilename
import os.path

class MainApplication(tk.Tk):
	'''Controller for all windows in GUI'''
	def __init__(self):
		super(MainApplication,self).__init__()
		self.selectionWindow = SelectionWindow(self)
		self.RegionInputWindow = None
		self.HospitalInputWindow = None
		self.AmbulanceInputWindow = None
		self.WriteOutputWindow = None
		self.OutputWindow = None
		self.regionsText = "[Regions]\n"
		self.regions = []
		self.hospitalsText = "[Hospitals]\n"
		self.hospitals = []
		self.ambulancesText = "[Ambulatory Service]\n"
		self.ambulances = []
		self.fileData = None
		self.selectionWindow.show()
	
	def createRegionInputWindow(self):
		'''Creates GUI input window.'''	
		self.RegionInputWindow = RegionInputWindow(self)
	
	def createHospitalInputWindow(self):
		'''Creates GUI input window.'''	
		self.HospitalInputWindow = HospitalInputWindow(self)
	
	def createAmbulanceInputWindow(self):
		'''Creates GUI input window.'''	
		self.AmbulanceInputWindow = AmbulanceInputWindow(self)	
	
	def createWriteOutputWindow(self,guiInput):
		'''Creates option to write output to file window.'''
		self.WriteOutputWindow = WriteOutputWindow(self,guiInput)	
		
	def createOutputWindow(self):
		'''Creates output window.'''
		self.OutputWindow = OutputWindow(self)

	def handleGUIFile(self,writeToFile):
		'''Reads from GUI input.'''
		text = self.regionsText + '\n' + self.hospitalsText + '\n' + self.ambulancesText
		extraction = processGuiInput(text)
		self.createOutputWindow()
		if(extraction):
			vNum, fDemanded, edges, names = extraction
			self.generateOutput(vNum, fDemanded, edges, names,writeToFile)
		else:
			print("Error on input file", file=self.OutputWindow.textvar)
		self.OutputWindow.show()

	def importFile(self):
		'''Imports JSON or CSV file.'''
		file = askopenfilename(filetypes=(('csv files','*.csv'),('json files','*.json')),title='Select an input file')
		extension = os.path.splitext(file)[1]
		if extension == ".csv":
			extraction = extractFile(file)
		elif extension == ".json":
			extraction = libDriver.extractFromJson(file,True)
		if('extraction' in locals()):
			self.fileData = extraction
			self.createWriteOutputWindow(False)
			self.WriteOutputWindow.show()
			
	def handleFile(self,writeToFile):
		'''Handles CSV/JSON input.'''
		self.createOutputWindow()
		if(self.fileData):
				vNum, fDemanded, edges, names = self.fileData
				self.generateOutput(vNum, fDemanded, edges, names,writeToFile)
		else:
			print("Error on input file", file=self.OutputWindow.textvar)
		self.OutputWindow.show()

	def generateOutput(self,vNum, fDemanded, edges, names,writeToFile):
		'''Generates text for GUI output window.'''
		flowSupplied, pathing = fordFulkerson(vNum, edges, 0, vNum-1)
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
	'''Window that allows user to select input type.'''
	def __init__(self,root):
		super(SelectionWindow,self).__init__()
		self.root = root
		self.radioSelection = tk.IntVar()
		fromFile = tk.Radiobutton(self, text='From File',variable=self.radioSelection,value=0).pack()
		fromGUI = tk.Radiobutton(self, text='From GUI',variable=self.radioSelection,value=1).pack()
		cont = tk.Button(self, text='Continue', width=25, command=self.inputType).pack()
		stop = tk.Button(self, text='Stop', width=25, command=self.root.destroy).pack()
	
	def show(self):
		'''Shows selection window.'''
		self.pack()
	
	def inputType(self):
		'''Determines user radio button selection.'''
		selected = self.radioSelection.get()
		if(selected == 0):
			self.root.fromGUI = False
			self.root.importFile()
			self.destroy()
		else:
			self.root.fromGUI = True
			self.root.createRegionInputWindow()
			self.destroy()
			self.root.RegionInputWindow.show()

class RegionInputWindow(tk.Frame):
	'''GUI Input Window (region).'''
	def __init__(self,root):
		super(RegionInputWindow,self).__init__()
		self.regionValid = False
		self.victimsValid = False
		self.root = root
		self.regionTextEntry = tk.StringVar()
		self.victimCountEntry = tk.IntVar()
		self.add = tk.Button(self, text='Add', width=25, command=self.addToRegions,state='disabled')
		self.add.grid(row=2,column=0)
		v1 = (self.register(self.regionValidate))
		self.region = tk.Entry(self, textvariable = self.regionTextEntry,validate='key',validatecommand=(v1,'%d','%P'))
		self.region.grid(row=0,column=1)
		v2 = (self.register(self.victimsValidate))
		self.victims = tk.Entry(self, textvariable = self.victimCountEntry, validate='key',validatecommand=(v2,'%d','%P','%S'))
		self.victims.grid(row=1,column=1)
		self.cont = tk.Button(self, text='Continue', width=25, command=self.toHospitalInput,state='disabled')
		self.cont.grid(row=2,column=1)
		regionLabel = (tk.Label(self, text='Region: ')).grid(row=0,column=0)
		victimCountLabel = (tk.Label(self, text='Victims: ')).grid(row=1,column=0)
		stop = tk.Button(self, text='Stop', width=25, command=self.root.destroy).grid(row=3,column=0,columnspan=2)	

	def show(self):
		'''Shows input window.'''
		self.pack()

	def regionValidate(self,d,P):
		'''Validate region input is not blank.'''
		if(d=='0' and P==''):
			self.regionValid = False
		else:
			self.regionValid = True
		if(self.regionValid and self.victimsValid):
			self.add['state']='normal'
		else:
			self.add['state']='disabled'
		return True

	def victimsValidate(self,d,P,S):
		'''Validate victim input is an integer.'''
		if(d=='1'):
			if(S.isdigit()):
				if(int(P)>0):
					self.victimsValid = True
				if(self.regionValid and self.victimsValid):
					self.add['state']='normal'
				else:
					self.add['state']='disabled'	
				return True
			return False
		else:
			if(P=='' or int(P)==0):
				self.victimsValid = False
			if(self.regionValid and self.victimsValid):
				self.add['state']='normal'
			else:
				self.add['state']='disabled'
			return True

	def addToRegions(self):
		'''Adds input text to list of entries.'''
		region = self.regionTextEntry.get()
		self.root.regions.append(region) #validate
		victims = self.victimCountEntry.get()
		self.root.regionsText += (region+', '+str(victims)+'\n')
		if(self.cont['state']=='disabled'):
			self.cont['state']='normal'

	def toHospitalInput(self):
		'''Proceeds to next input window.'''
		self.root.regionsText += ('\n')
		self.root.createHospitalInputWindow()
		self.destroy()
		self.root.HospitalInputWindow.show()

class HospitalInputWindow(tk.Frame):
	'''GUI Input Window (hospital).'''
	def __init__(self,root):
		super(HospitalInputWindow,self).__init__()
		self.root = root
		self.hospitalValid = False
		self.capacityValid = False
		self.hospitalTextEntry = tk.StringVar()
		self.capacityEntry = tk.IntVar()
		self.add = tk.Button(self, text='Add', width=25, command=self.addToHospitals,state='disabled')
		self.add.grid(row=2,column=0)
		self.cont = tk.Button(self, text='Continue', width=25, command=self.toAmbulanceInput,state='disabled')
		self.cont.grid(row=2,column=1)
		hospitalLabel = (tk.Label(self, text='Hospital: ')).grid(row=0,column=0)
		capacityLabel = (tk.Label(self, text='Capacity: ')).grid(row=1,column=0)
		v1 = (self.register(self.hospitalValidate))
		v2 = (self.register(self.capacityValidate))
		self.hospital = tk.Entry(self, textvariable = self.hospitalTextEntry,validate='key',validatecommand=(v1,'%d','%P'))
		self.hospital.grid(row=0,column=1)
		self.capacity = tk.Entry(self,textvariable = self.capacityEntry,validate='key',validatecommand=(v2,'%d','%P','%S'))
		self.capacity.grid(row=1,column=1)
		stop = tk.Button(self, text='Stop', width=25, command=self.root.destroy).grid(row=3,column=0,columnspan=2)

	def show(self):
		'''Shows input window.'''
		self.pack()

	def hospitalValidate(self,d,P):
		'''Validate hospital input is not blank.'''
		if(d=='0' and P==''):
			self.hospitalValid = False
		else:
			self.hospitalValid = True
		if(self.hospitalValid and self.capacityValid):
			self.add['state']='normal'
		else:
			self.add['state']='disabled'
		return True

	def capacityValidate(self,d,P,S):
		'''Validate capacity input is an integer.'''
		if(d=='1'):
			if(S.isdigit()):
				if(int(P)>0):
					self.capacityValid = True
				if(self.hospitalValid and self.capacityValid):
					self.add['state']='normal'
				else:
					self.add['state']='disabled'	
				return True
			return False
		else:
			if(P=='' or int(P)==0):
				self.capacityValid = False
			if(self.hospitalValid and self.capacityValid):
				self.add['state']='normal'
			else:
				self.add['state']='disabled'
			return True

	def addToHospitals(self):
		'''Adds input text to list of entries.'''
		hospital = self.hospitalTextEntry.get()
		self.root.hospitals.append(hospital) #validate
		capacity = self.capacityEntry.get()
		self.root.hospitalsText += (hospital+', '+str(capacity)+'\n')
		if(self.cont['state']=='disabled'):
			self.cont['state']='normal'

	def toAmbulanceInput(self):
		'''Proceeds to next input window.'''
		self.root.hospitalsText += ('\n')
		self.root.createAmbulanceInputWindow()
		self.destroy()
		self.root.AmbulanceInputWindow.show()

class AmbulanceInputWindow(tk.Frame):
	'''GUI Input Window (ambulance).'''
	def __init__(self,root):
		super(AmbulanceInputWindow,self).__init__()
		self.root = root
		self.ambulanceValid = False
		self.capacityValid = False
		self.ambulanceTextEntry = tk.StringVar()
		self.capacityEntry = tk.IntVar()
		self.regionEntry = tk.StringVar()
		self.regionEntry.set(self.root.regions[0])
		self.hospitalEntry = tk.StringVar()
		self.hospitalEntry.set(self.root.hospitals[0])
		self.add = tk.Button(self, text='Add', width=25, command=self.addToAmbulances,state='disabled')
		self.add.grid(row=4,column=0)
		self.finish = tk.Button(self, text='Finish', width=25, command=self.finish,state='disabled')
		self.finish.grid(row=4,column=1)
		v1 = (self.register(self.ambulanceValidate))
		v2 = (self.register(self.capacityValidate))
		self.ambulance = tk.Entry(self, textvariable = self.ambulanceTextEntry,validate='key',validatecommand=(v1,'%d','%P'))
		self.ambulance.grid(row=2,column=1)
		self.capacity = tk.Entry(self, textvariable = self.capacityEntry,validate='key',validatecommand=(v2,'%d','%P','%S'))
		self.capacity.grid(row=3,column=1)
		regionLabel = tk.Label(self, text='Region: ').grid(row=0,column=0)
		hospitalLabel = tk.Label(self, text='Hospital: ').grid(row=1,column=0)
		ambulanceLabel = tk.Label(self, text='Ambulance: ').grid(row=2,column=0)
		capacityLabel = tk.Label(self, text='Capacity: ').grid(row=3,column=0)
		region = tk.OptionMenu(self, self.regionEntry, *self.root.regions).grid(row=0,column=1)
		hospital = tk.OptionMenu(self, self.hospitalEntry, *self.root.hospitals).grid(row=1,column=1)
		stop = tk.Button(self, text='Stop', width=25, command=self.root.destroy).grid(row=5,column=0,columnspan=2)
	
	def show(self):
		'''Shows input window.'''
		self.pack()

	def ambulanceValidate(self,d,P):
		'''Validate ambulance input is not blank.'''
		if(d=='0' and P==''):
			self.ambulanceValid = False
		else:
			self.ambulanceValid = True
		if(self.ambulanceValid and self.capacityValid):
			self.add['state']='normal'
		else:
			self.add['state']='disabled'
		return True

	def capacityValidate(self,d,P,S):
		'''Validate capacity input is an integer.'''
		if(d=='1'):
			if(S.isdigit()):
				if(int(P)>0):
					self.capacityValid = True
				if(self.ambulanceValid and self.capacityValid):
					self.add['state']='normal'
				else:
					self.add['state']='disabled'	
				return True
			return False
		else:
			if(P=='' or int(P)==0):
				self.capacityValid = False
			if(self.ambulanceValid and self.capacityValid):
				self.add['state']='normal'
			else:
				self.add['state']='disabled'
			return True

	def addToAmbulances(self):
		'''Adds input text to list of entries.'''
		ambulance = self.ambulanceTextEntry.get()
		region = self.regionEntry.get()
		hospital = self.hospitalEntry.get()
		self.root.ambulances.append(ambulance) #validate
		capacity = self.capacityEntry.get()
		self.root.ambulancesText += (ambulance+', '+region+', '+hospital+', '+str(capacity)+'\n')
		if(self.finish['state']=='disabled'):
			self.finish['state']='normal'

	def finish(self):
		'''Proceeds to output option window.'''
		self.root.ambulancesText += ('\n')
		self.root.createWriteOutputWindow(True)
		self.destroy()
		self.root.WriteOutputWindow.show()

class WriteOutputWindow(tk.Frame):
	'''Provides the user an option to print output to a text file.'''
	def __init__(self,root,guiInput):
		super(WriteOutputWindow,self).__init__()
		self.root = root
		self.guiInput = guiInput
		self.radioSelection = tk.IntVar()
		writeLabel = tk.Label(self, text='Write Output to File?').pack()
		yes = tk.Radiobutton(self, text='Yes',variable=self.radioSelection,value=0).pack()
		no = tk.Radiobutton(self, text='No',variable=self.radioSelection,value=1).pack()
		cont = tk.Button(self, text='Continue', width=25, command=self.toOutput).pack()
	
	def show(self):
		'''Shows option window.'''
		self.pack()
	
	def toOutput(self):
		'''Determines user radio button selection, proceeds to output window.'''
		selected = self.radioSelection.get()
		if(self.guiInput):
			if(selected == 0):
				self.root.handleGUIFile(True)
			else:
				self.root.handleGUIFile(False)
		else:
			if(selected == 0):
				self.root.handleFile(True)
			else:
				self.root.handleFile(False)
		self.destroy()
		self.root.OutputWindow.show()

class OutputWindow(tk.Frame):
	'''Output window.'''
	def __init__(self,root):
		super(OutputWindow,self).__init__()
		self.root = root
		self.textvar = WritableStringVar(root)
		outputLabel = tk.Label(self, textvariable=self.textvar,wraplength='800')
		outputLabel.pack()
		stop = tk.Button(self, text='End', command=self.root.destroy).pack()

	def show(self):
		'''Shows output window.'''
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
