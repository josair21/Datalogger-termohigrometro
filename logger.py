from tkinter import *
import serial.tools.list_ports
import functools
from datetime import date
from time import sleep
import pandas as pd
import os
from cryptography.fernet import Fernet

root = Tk()
root.config(bg = 'grey')
root.geometry('240x500')
root.title('LOGGER')
root.resizable(0,0)
print('Hello World')

text = ''
isDecrypted = False
headerList = ['Hora', 'Temperatura', 'Humedad']
serialCom = serial.Serial()
ComConnected = ['COM0']
customFont = ("Helvetica", 12, "bold")
customFont2 = ("Helvetica", 10)
selectedPort = StringVar(root)
selectedPort.set('Seleccionar COM')
selectedName = StringVar(root)
selectedName.set(date.today().strftime("%d-%m-%Y"))

frame1 = Frame(root, bg="black", width=240, height=50)
frame1.configure(bg = 'cyan')
frame1.place(x = 0, y = 0)

frame2 = Frame(root, bg="black", width=240, height=80)
frame2.configure(bg = 'grey')
frame2.place(x = 0, y = 50)

frame3 = Frame(root, bg="black", width=240, height=50)
frame3.configure(bg = 'yellow')
frame3.place(x = 0, y = 130)

with open('filekey.key', 'rb') as filekey: 
    key = filekey.read() 
fernet = Fernet(key) 


def readComList():
	ComList = serial.tools.list_ports.comports()
	for element in ComList:
	    ComConnected.append(element.device)

def selectComPort():
	opt = OptionMenu(root, selectedPort, *ComConnected)
	opt.config(width = 15, bg = 'white', justify='center', font = customFont)
	opt.pack(padx = 20, pady = 8)

def filename():
	text = Label(root, text = 'Nombre de archivo')
	text.config(bg = 'grey', justify='center', font = customFont)
	text.place(x = 120, y = 75, anchor=CENTER)

	name = Entry(root, textvariable = selectedName)
	name.config(width = 20, bg = 'white', justify='center', font = customFont)
	name.pack(padx = 20, pady = 40)

def buttonStart():
	start = Button(text = 'Iniciar', command = startCom)
	start.configure(width = 8, justify='center', font = customFont)
	start.place(x = 60, y = 155, anchor=CENTER)
	
def startCom():
	global logfile
	global logfilecr
	global file_size
	try:
		serialCom.port = selectedPort.get()
		serialCom.baudrate = 9600
		serialCom.open()
		serialCom.flush()
		print("INICIADO")
		sleep(0.1)
		logfile = open(selectedName.get() + '.csv', 'a')
		sleep(0.5)
		file_size = os.stat(selectedName.get() + '.csv').st_size
		if file_size == 0:
			header = 'Hora,Temperatura,Humedad\n'
			logfile.write(header)
			logfile.flush()
			with open('temp/' + selectedName.get() + '-encrypted.csv', 'wb') as enc_file: 
				enc_file.write(header.encode('utf-8'))
		else:
			with open('temp/' + selectedName.get() + '-encrypted.csv', 'rb') as enc_file: 
				temp_data = enc_file.read()
			temp_data = fernet.decrypt(temp_data)
			sleep(0.1)
			with open('temp/' + selectedName.get() + '-encrypted.csv', 'wb') as enc_file: 
				enc_file.write(temp_data)
		sleep(0.1)
		Label(dataFrame, text = 'File: ' + selectedName.get() + '.csv', font = customFont2, bg = 'white').pack(anchor = 'w')
		dataCanvas.yview_moveto( 1 )
		print("Archivo nombrado:", selectedName.get())
		sleep(0.1)
	except:
		Label(dataFrame, text = 'Iniciado con problemas', font = customFont2, bg = 'white').pack(anchor = 'w')
		dataCanvas.yview_moveto( 1 )
		print('except occurred')

def buttonStop():
	stop = Button(text = 'Detener', command = stopCom)
	stop.configure(width = 8, justify='center', font = customFont)
	stop.place(x = 180, y = 155, anchor=CENTER)

def stopCom():
	try:
		serialCom.close()
		logfile.close()
		sleep(0.1)
		print("DETENIDO")
		Label(dataFrame, text = 'DETENIDO', font = customFont2, bg = 'white').pack(anchor = 'w')
		sleep(0.1)
		print("DETENIDO2")
		with open('temp/' + selectedName.get() + '-encrypted.csv', 'rb') as enc_file: 
		    temp_data = enc_file.read()
		temp_data = fernet.encrypt(temp_data) 
		with open('temp/' + selectedName.get() + '-encrypted.csv', 'wb') as dec_file: 
			dec_file.write(temp_data) 
		sleep(0.1)
		os._exit(0)
		root.destroy()
		
	except:
		root.destroy()
		print("PUERTO CERRADO")
		os._exit(0)
		

def logCanvas():
	global dataCanvas
	global vbar
	global dataFrame
	dataCanvas = Canvas(root, width = 220, heigh = 10, bg = 'white')
	vbar = Scrollbar(root, orient = VERTICAL, command = dataCanvas.yview)
	vbar.pack(side = RIGHT, fill = Y, pady = (25,0))
	dataCanvas.config(yscrollcommand = vbar.set)
	dataCanvas.pack(side = LEFT, fill = BOTH, pady = (25,0))
	dataFrame = Frame(dataCanvas, bg = 'white', width = 220)
	dataCanvas.create_window((5, 220), window = dataFrame, anchor = 'nw')

def checkSerialPort():
	if serialCom.isOpen() and serialCom.in_waiting:
		recentPacket = serialCom.readline()
		recentPacketString2 = recentPacket.decode('utf').rstrip('\n')
		recentPacketString = recentPacket.decode('utf').rstrip()
		data = recentPacketString.split(',')
		Label(dataFrame, text = data[0] + '    ' + data[1] + ' °C    ' + data[2] + ' %HR', font = customFont2, bg = 'white').pack(anchor = 'w')
		dataCanvas.yview_moveto( 1 )

		print(recentPacketString)
		logfile.write(recentPacketString2)
		logfile.flush()
		with open('temp/' + selectedName.get() + '-encrypted.csv', 'ab') as enc_file: 
			enc_file.write(recentPacketString2.encode('utf-8'))

readComList()
selectComPort()
filename()
buttonStart()
buttonStop()
logCanvas()
root.protocol("WM_DELETE_WINDOW", stopCom)
while True:
	try:
		root.update()
		checkSerialPort()
		dataCanvas.config(scrollregion = dataCanvas.bbox('all'))
	except:
		None