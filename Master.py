import socket
import mysql.connector
from time import sleep

IP = "192.168.43.40"
PORT = 60900

mydb = mysql.connector.connect(
    host="localhost",
    user="root",
    password="root",
    database="Tiempo"
)
mycursor = mydb.cursor()


listOfServers = []

def toTime(num):
	cadena = ""
	cadena += str(num//10000)+":"
	num -= (num//10000)*10000
	cadena += str(num//100)+":"
	num -= (num//100)*100
	cadena += str(num)
	return cadena

def makeAjust(sock):
	prom = 0 
	global listOfServers
	if(len(listOfServers) > 0):
		for x in listOfServers:
			print("[%s , %d]" % (x , PORT) )
			sock.sendto(b'GTM',(x,PORT))
			data , addr = sock.recvfrom(100)
			prom += int(data.decode('utf-8'))
			print(prom)
		prom = prom // len(listOfServers)
		MSG = "CTM " + str(prom)
		hora = toTime(prom)
		sqlformula = "INSERT INTO Tiempo (hora) VALUES(\"%s\")"
		mycursor.execute(sqlformula,(hora,))
		mydb.commit()
		for x in listOfServers:
		#	print(()x , PORT)
			sock.sendto(MSG.encode('utf-8'),(x,PORT))
		



sock = socket.socket(socket.AF_INET , socket.SOCK_DGRAM)
sock.bind((IP,PORT))
#sock.settimeout(0.5)
x = input().split()
while(x[0] != "start"):
	if(x[0] == "add"):
		listOfServers.append(x[1])
	x = input().split()

while True:
	try:
		print("Consulta")
		makeAjust(sock)
		sleep(int(x[1]))
	except KeyboardInterrupt as k:
		break
