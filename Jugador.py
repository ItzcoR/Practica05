import socket
import time
from tkinter import filedialog
from tkinter import *
import tkinter as tk
import threading
import random



HOST = '192.168.43.199'  # The server's hostname or IP address
PORT = 65432        # The port used by the server
random.seed(99)
class clockClient:	#Clase Reloj
    def __init__(self, win, _x, _y ):
        file2open="No has seleccionado un archivo"
        self.file=file2open
        self.h = random.randint(0,23)
        self.m = random.randint(0,59)
        self.s = random.randint(0,59)
        self.secTimer = 1 #Valor del sleep para los segundos
        self.status = True
        self.lbl = Label(win,text="%02d:%02d:%02d" % (self.h ,self.m,self.s))
        self.lbl.grid(row = _x , column = _y, columnspan=2)
        self.btn = Button(win, text ="Cargar", command = lambda: self.popup_open_file(win, file2open)  )
        self.btn.grid(row = _x+1, column = _y)
        self.btn = Button(win, text ="Enviar", command = lambda: self.RunClient( self.file)  )
        self.btn.grid(row = _x+1, column = _y+1)
        self.lblfile = Label(win, text=file2open)
        self.lblfile.grid(row = _x+2, column= _y, columnspan=2)
        self.t = threading.Thread(target=self.start , args=(self.lbl, )) #Creamos un atributo de tipo Thread el cual manejara el avance y actualizacion del reloj
        self.t.setDaemon(True)#setDaemon true indica a python que cuando se cierre el programa, mate tambien al hilo
        self.t.start()
    def start(self , lbl):	#El thread de cada clock llamara a esta funcion
        while(1): #While true para que siempre cheque el status y actualice el reloj
        #print(self.status)
            if(self.status==True):	#Status del reloj, sirve para pausarlo
                time.sleep(self.secTimer)	#Segun el valor del atributo secTimer es la pausa
                self.s += 1
                if(self.s >= 60 ): #Reset de los segundos si se pasa de 60
                    self.s = 0
                    self.m += 1
                if(self.m >= 60): #Reset de los minutos si se pasa de 60
                    self.m = 0
                    self.h += 1
                if(self.h >= 24):#Reset de las horas si se pasa de 24
                    self.h = 0
                lbl.config(text = "%02d:%02d:%02d" % (self.h , self.m , self.s))
            else:
                time.sleep(1)
    def pauseClock(self):
        self.status=False
    def resumeClock(self):
        self.status=True
    def popup_open_file(self, win, file2open):
        file2open= tk.filedialog.askopenfilename(initialdir = "/home/itzco/Desarrollo-de-sistemas-distribuidos/Practica_03/",title = "Elige un archivo para mandar al servidor",filetypes = (("txt files","*.txt"),("all files","*.*")))
        self.lblfile.config( text = file2open)
        print(file2open)
        self.file= file2open
        return file2open
    def RunClient(self, file2open):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((HOST, PORT))
            #time.sleep(0.001)
            archivo = open(file2open, "rb")
            print("Enviando...")
            l = archivo.read(1024)
            while (l):
                print("Enviando...")
                s.send(l)
                l = archivo.read(1024)
            archivo.close()
            print("Envio Completado")
            print (s.recv(1024))
            s.shutdown(socket.SHUT_WR)
            s.close
            #s.sendall(b'Hello, world')
            #data = s.recv(32)
            #print( repr(data)  )
            #s.shutdown(socket.SHUT_RDWR)
            #s.close()



win = tk.Tk()
win.geometry("800x600")
#lbl = Label(win , text="%02d" % (0))
clk1 = clockClient(win,0,0)
#lbl.grid(row = 0 , column = 0 , columnspan = 2)
"""clientThread = threading.Thread(target = RunClient , args = (clk1, ))
clientThread.setDaemon(True)
clientThread.start()"""
win.mainloop()
