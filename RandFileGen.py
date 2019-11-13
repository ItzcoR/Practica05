import random #Generador de archivos con numeros random

n_archivos= int(input("¿Cuantos archivos deseas generar?"))
randfile = [None]*n_archivos
for j in range(0 , n_archivos ):
    randfile[j] = open("RandNums/RandomNums" + str(j) + ".txt", "w+" )
    n=int(input('How many to generate?: '))
    for i in range(0,n):
        if(i==n-1):
            line = str(random.randint(1, 100))
            randfile[j].write(line)
        else:
            line = str(random.randint(1, 100)) + "\n"
            randfile[j].write(line)
    #print(line)
for j in range(0 , n_archivos ):
    randfile[j].close()
