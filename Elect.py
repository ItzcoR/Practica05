from tkinter import *
import tkinter as tk
from datetime import datetime
import random
from time import sleep
import threading
import socket
import mysql.connector
import pdb 
#HOST = '127.0.0.1'   Standard loopback interface address (localhost)
HOST = '10.0.2.15' #Direccion IP de este server
BKHOST = "127.0.0.1"
BroadcastAdress = "192.168.43.255"
PORT = 65432        # Port to listen on (non-privileged ports are > 1023)
BCKPORT = 65433        # Port to listen on (non-privileged ports are > 1023)
TIMEPORT = 60432
ELECTIONPORT = 60600

now = datetime.now() # Fecha y hora actuales
random.seed(99)
mydb = mysql.connector.connect(
    host="localhost",
    user="root",
    password="Dragon",
    database="Central"
)
mycursor = mydb.cursor()
sqlformula = "INSERT INTO Sumas (resultado, ip, hora) VALUES(%s,%s,%s)"

#Necesitamos una lista de servidores de nuestro sistema ya definida
#LA lista es bidimensional con el primer valor indicando la direccion IP
#El segundo valor es la prioridad del servidor
#La prioridad nos indica cual es preferible para ser Coordinador 
listOfServers=[["192.168.43.40",3],["192.168.43.50",2],["192.168.43.60",1]]

def toTime(num):
    cadena = ""
    cadena += str(num//10000)+":"
    num -= (num//10000)*10000
    cadena += str(num//100)+":"
    num -= (num//100)*100
    cadena += str(num)
    return cadena

class Comunicator:
    def __init__(self ):
        self.backupEnable = False
        self.addr = ""
        self.MasterStatus = False
        self.ElectionStatus = False
        self.BanderaVictoria = False
        self.Prioridad = 3  #Asignamos una prioridad al servidor, 
        #debe ser distinta para todos y coincidir con la de la lista
        #Creamos un cliente y un servidor broadacst para manejar el proceso de eleccion
        pdb.set_trace()
        self.bserver = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        self.bserver.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        # Set a timeout so the socket does not block
        # indefinitely when trying to receive data.
        self.bserver.settimeout(0.8)
        self.bserver.bind((HOST, 44444))
        self.bclient = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # UDP
        self.bclient.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        self.bclient.bind((HOST, 37020))
        self.bclient.settimeout(2)
        #Creamos un socket para el proceso de eleccion
        self.ElectionSock = socket.socket(socket.AF_INET , socket.SOCK_DGRAM)
        self.ElectionSock.bind((HOST,ELECTIONPORT))
        self.ElectionSock.settimeout(0.6)
    
        #RunListenThread = threading.Thread(target=self.RunSocket , args=(clk1 , ))
        #listenBCKThread = threading.Thread(target=self.listenBackUp , args=(clk1, ))		
        #turnOnBackUpThread = threading.Thread(target=self.turnOnBackUp , args=(IPBackUp,))
        RunElectionThread = threading.Thread(target=self.ElectionThread)
        RunMasterSerThread = threading.Thread(target=self.TimeThread)
        pdb.set_trace()
        RunElectionThread.setDaemon(True)
        #RunListenThread.setDaemon(True)
        #turnOnBackUpThread.setDaemon(True)
        #SlistenBCKThread.setDaemon(True)
        RunMasterSerThread.setDaemon(True)
        RunElectionThread.start()

        #RunListenThread.start()
        #listenBCKThread.start()
        #turnOnBackUpThread.start()
        #listenTimeThread = threading.Thread(target=self.listenTime , args=(clk1,))
        #listenTimeThread.setDaemon(True)
        #listenTimeThread.start()
        self.NotifyElection()
    def NotifyElection(self):
        global listOfServers
        self.backupEnable = False
        self.MasterStatus = False
        self.ElectionStatus = True 
        message = b"ELECT"
        self.bserver.sendto(message, (BroadcastAdress, 37020))
        print("Proceso de Elección comenzando, Notificacion mandada por broadcast")
    def ElectionThread(self): #Hilo que escuchara al proceso de eleccion 
        global listOfServers
        #Ordenar lista por prioridad
        sorted(listOfServers, key= lambda x: x[1], reverse= True)
        print(listOfServers)
        self.backupEnable= False
        self.MasterStatus= False
        self.ElectionStatus= True
        self.BanderaVictoria = False
        pdb.set_trace()
        while True:
            try:
                data, addr = self.bclient.recvfrom(1024)
                #print("broadcast client received data: %s"%data)
                revcmess = data.decode('utf-8').split()
                print("broadcast client received data: %s"%revcmess[0])
                if(revcmess[0] == "ELECT") :
                    #Si recibimos un mensaje de Eleccion debemos mandar
                    #nuestra prioridad a aquellos servidores con menor prioridad
                    if(listOfServers[0][1] <= self.prioridad) :#Checamos si tenemos la prioridad mas alta
                        #De ser asi, ganamos y mandamos un mensaje de victoria a todos los demas
                        self.BanderaVictoria=True
                        self.bserver.sendto("VICT" + HOST, (BroadcastAdress, 37020))
                        WaitForVictAcc()
                        """data2, addr2 = self.bclient.recvfrom(1024)
                        victRes = data.decode('utf-8').split()
                        if (victRes[0] == "OKVict"):
                        self.backupEnable= False
                        self.MasterStatus= True
                        self.ElectionStatus= False
                        self.RunTimeThread.start()"""
                    else:
                        BullyStandBy()
                elif(revcmess[0] == "VICT"):
                    #Si nos llega un mensaje de victoria Comprobar que su prioridad sea mayor
                    #En caso de ser
                    print(revcmess[1])#Esta deberia ser la ip del vencedor de la eleccion
                    self.BanderaVictoria=False
                    self.backupEnable= False
                    self.MasterStatus= False
                    self.ElectionStatus= False
                    #self.RunListenThread.start()
                    #self.listenBCKThread.start()
                    #self.turnOnBackUpThread.start()
                    #self.listenTimeThread.start()
                    self.ElectionSock.sendto("OKVict", (revcmess[1], 37020))
            except socket.error:
                print("Socket timed out, Vencedor por default ")
                self.BanderaVictoria=True
                self.backupEnable= False
                self.MasterStatus= True
                self.ElectionStatus= False
            
    
    def WaitForVictAcc():
        global listOfServers
        BandVictReconocida = False
        pdb.set_trace()
        if (self.BanderaVictoria == True):

            for h in range(0,len(listOfServers)-1):
                data2, addr2 = self.ElectionSock.recvfrom(1024)
                victRes = data.decode('utf-8').split()
                print(victRes)
                if (victRes[0] == "OKVict" and h == len(listOfServers)-1):
                    self.backupEnable= False
                    self.MasterStatus= True
                    self.ElectionStatus= False
                    self.RunTimeThread.start()
    def BullyStandBy(self):
        global listOfServers
        #Ordenar lista por prioridad
        sorted(listOfServers, key= lambda x: x[1], reverse= True)
        #Mandar mensaje  a todos los que tengan mayor prioridad 
        pdb.set_trace()        
        if (listOfServers[0][1] > self.prioridad):
            for i in range(0,len(listOfServers)):
                if(listOfServers[i][1]< self.prioridad) :
                    ElectionSock.sendto(b"SerBigPri"+str(self.prioridad),(listOfServers[i][0], ELECTIONPORT))
        electRes, electAddr = self.bclient.recvfrom(1024)
        electRes = data.decode('utf-8').split()
        #if ():
                            

                    
          
                
                
    """def turnOnBackUp(self , IPBackUp):

        if (IPBackUp != ""):
            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
                try:
                    s.sendto(b"ACKB",(IPBackUp,BCKPORT))
                    data , self.addr = s.recvfrom(4)
                    if(repr(data)[2:-1] == "ACKB"):
                        self.backupEnable = True
                        s.sendto(b"ACKC" , (HOST , BCKPORT))
                except EnvironmentError as e:
                    pass
                
        sleep(0.01)"""


    """def listenBackUp(self , clk1):
        global BKHOST
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.bind((HOST , BCKPORT))
            while not self.backupEnable:
                data , self.addr = s.recvfrom(4)
                if(repr(data)[2:-1] == "ACKB"):
                    self.backupEnable = True
                    s.sendto(b"ACKB" , self.addr)
                    BKHOST = self.addr[0]
        self.listenServer(clk1)

    def listenServer(self , clk1):
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.bind((HOST , BCKPORT))
            while self.backupEnable:
                data , x = s.recvfrom(1024)
                args = data.decode('utf-8').split()
                self.executeSQLInsert(args[0] , args[1] , args[2] , clk1)



    def RunSocket(self,GUIclk):
        totalData=0
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s: #Creamos el socket le ponemos el nombre de s, AF_INET=IPV4 SOCK_STREAM=TCP
            s.bind((HOST, PORT))#Publicamos la ip y puerto
            s.listen(6)#Aceptaremos maximo 6 conexiones
            while True:#Loop infinito para siempre estar escucahndo al puerto especificado
                conn, addr = s.accept() #Aceptar la conexion
                print(f"Conection desde {addr} ha sido establecida")
                conn.send(bytes("Conectado a servidor", "utf-8"))
                totalData=0
                l = conn.recv(1024)
                while (l): #Mientras l reciva algo entrara en este loop
                    print("Recibiendo...")
                    print(l)	#Recibiremos una cadena de bytes
                    #print (type(l))
                    listofData=l.split(b'\n') #Separamos la cadena de bytes por breaklines
                    print(listofData)#l ahora es una lista con cadenas de bytes
                    for i in range(0, len(listofData)):
                        if ( listofData[i].decode("utf-8")=='' ):
                            listofData[i]=0
                        else:
                            listofData[i] = int(listofData[i].decode("utf-8") ) #se decodifica y castea a entero
                        totalData = listofData[i]+totalData
                        print(totalData)
                    print(listofData)
                    l = conn.recv(1024)
                print("Termine de recibir")
                conn.send(b'Envio Completado')
                conn.close()
                GUIclk.total = totalData
                hour = str(GUIclk.clk.h).zfill(2) + ":" +str(GUIclk.clk.m).zfill(2)+ ":" +str(GUIclk.clk.s).zfill(2)
                ip = addr[0]

                self.executeSQLInsert(str(totalData) , ip , hour , GUIclk)
                if(self.backupEnable):
                    MGS = str(totalData) + " " + str(ip) + " " + str(hour)
                    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
                        print(BKHOST)
                        sock.sendto(MGS.encode('utf-8') , (BKHOST , BCKPORT))"""

    def makeAjust(self):
        prom = 0 
        global listOfServers
        if(len(listOfServers) > 0):
            for x in range(len(listOfServers)):
                print("[%s , %d]" % (listOfServers[x][0] , PORT) )
                sock.sendto(b'GTM',(listOfServers[x][0], PORT))
                data , addr = sock.recvfrom(100)
                prom += int(data.decode('utf-8'))
                print(prom)

        prom = prom // len(listOfServers)
        MSG = "CTM " + str(prom)
        hora = toTime(prom)
        sqlformula = "INSERT INTO Tiempo (hora) VALUES(\"%s\")"
        mycursor.execute(sqlformula,(hora,))
        mydb.commit()
        for x in range(len(listOfServers)):
            #print(()x , PORT)
            sock.sendto(MSG.encode('utf-8'),(listOfServers[x][0],PORT))
		

    def TimeThread(self):
        if(self.MasterStatus == True) :
            
            sock = socket.socket(socket.AF_INET , socket.SOCK_DGRAM)
            sock.bind((HOST,TIMEPORT))
            sock.settimeout(0.5)
            """x = input().split()
            while(x[0] !|= "start"):
            if(x[0] == "add"):
                listOfServers.append(x[1])
            x = input().split()"""
            while True:
                try:
                    print("Consulta")
                    makeAjust(sock)
                    sleep(3)
                except KeyboardInterrupt as k:
                    break

    """def executeSQLInsert(self , totalData , ip , hour , GUIclk):
        outcome =  (totalData, ip, hour)
        mycursor.execute(sqlformula,outcome)
        mydb.commit()
        GUIclk.lbltotal.config(text = "La suma de los elementos recibidos %d" %int(totalData))"""

    """def listenTime(self , clk1):
        sock = socket.socket(socket.AF_INET , socket.SOCK_DGRAM)
        sock.bind((HOST , TIMEPORT))
        while True:
            data , addr = sock.recvfrom(100)
            cmdArgs = data.decode('utf-8').split()
            if(cmdArgs[0] == "GTM"):
                msg = str(clk1.clk.getTimeToNumber())
                sock.sendto(msg.encode('utf-8'),(addr))
            elif(cmdArgs[0] == "CTM"):
                clk1.clk.setTimeFromNumber(int(cmdArgs[1]))"""

#win.resizable(1,1)	#Esto permite a la app adaptarse al tamaño
pdb.set_trace()
com = Comunicator()
