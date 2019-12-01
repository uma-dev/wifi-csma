from random import randrange
import numpy as np
from matplotlib import pyplot as plt
from collections import Counter

class Node:
    def  __init__(self, name):
        self.name = name
        self.cw = 16
        self.eb = randrange(self.cw)
        self.numOfCollitions = 0
        self.correct_paq = 0
        

    def getName(self):
        return self.name

    def setName(self, name):
        self.name = name

    def newCollition(self):
        self.numOfCollitions += 1
        
    def getEb(self):
        return self.eb

    def getCw(self):
        return self.cw

    def doubleCw(self):
        if(self.cw < 1024):           #max window
            self.cw = self.cw*2
        else:
            self.cw = 16
        self.eb = randrange(self.cw)   #update EB

    def updateCw(self):
        print("EB actualizado, nodo " + str(self.getName()) )
        self.cw = 16
        self.eb = randrange(self.cw)
        
    def decreaseEb(self):
        if(self.eb > 0):
            self.eb -= 1
            
    
class AP:
    Rbps = 1e6
    t_DIFS = 40.0*8/Rbps
    t_SIFS = 20.0*8/Rbps
    t_DATA = 1500.0*8/Rbps
    t_ACK  = 40.0*8/Rbps

    tc   = t_DIFS
    tl   = t_DATA + t_SIFS + t_ACK
    time = 0
    
    def __init__(self):
        self.nodes = []

    def addNode(self, node):
        self.nodes.append(node)

    def allNodes(self):
        return self.nodes

    def removeNode(self, node):
        print("Eliminando elemento "+ str(node))
        self.nodes.remove( self.getNode(node) )
        print("Nodo eliminado")
        
    def getNode(self, nameOfNode):
        i = 0
        for node in self.allNodes():
            if(node.getName() == nameOfNode):
                return i
            i += 1
            
    def decreasseAllEB(self):
        for node in self.allNodes():
            node.decreaseEb()
            print( str(node.getName())+" -> EB=" + str(node.getEb())  )
        print('--------------------')

    def doubleAllCw(self, listOfCollided):
        print("Doblando ventanas en los nodos " + str(listOfCollided))
        print("Las nuevas ventanas son:")
        for i in listOfCollided:
            self.nodes[self.getNode(i)].doubleCw()
            print(str(i) +  " -> CW= "+  str(self.nodes[self.getNode(i)].getCw()) + "-> EB= " + str(self.nodes[self.getNode(i)].getEb())) 
        print('.................')
        print('.................')

    def checkCollition(self):
        listCollided = []
        
        for node in self.allNodes():
            if( node.getEb()==0 ):
                listCollided.append( node.getName() )

        if( len(listCollided)>1 ):
            print("Hay nodos colicionados")
            for node in listCollided:
                self.allNodes()[node].newCollition()    #actualizar el numero de colisi de  cada nodo
            return True, listCollided
        else:                          #no hay coliones ni lista de colisionados
            print("No hay nodos colisionados")
            return False, []

    def checkAvailable(self):
        print("Revisando nodos disponibles..")
        for node in self.allNodes():
            if(node.getEb() == 0):
                return node.getName(), True
        return 66666, False  #el nodo prohibido
        
    def startSimulation(self, numOfNodes, numOfPackages):
        successNode = None
        freeChannel = True
        collition = False
        successPaq = 0
        count=1
        cols = 0
        scswindow = []
        self.nodes = []
        self.time = 0
        print("\n\nNodos-> "+ str(numOfNodes)+ "  Paquetes-> " + str(numOfPackages) )
        
        #start all nodes with EB
        for i in range(numOfNodes):
            self.addNode( Node(i) )
        print("Nodos inicializados")
        print("////////////////////\nLos Nodos son:")
        for node in  self.allNodes():
            print(str(node.getName())+" -> EB= " + str(node.getEb()))
        
        while(successPaq < numOfPackages):
            collition, listCollided  = self.checkCollition()
            if(collition == True):
                print("Hubo colision en " + str(listCollided))
                cols += 1
                self.doubleAllCw(listCollided)
                self.time += self.tl
                print("Aumentando un salto corto, time:  " + str(self.time))
            
            if(collition == False):
                successNode, available = self.checkAvailable()
                if(available == True):
                    print("Nodo "+ str(successNode) +" listo para Tx")
                    successPaq += 1
                    scswindow.append(self.nodes[self.getNode(successNode)].getCw())
                    self.time += ( self.tl + self.tc*self.nodes[self.getNode(successNode)].getEb()  )
                    print("Tx exitosa num: "+ str(successPaq) + "   time:" + str(self.time) +" por el nodo "+ str(successNode))
                    self.nodes[self.getNode(successNode)].updateCw()
                    #self.removeNode(successNode)   #Si solo queremos que un paquete tx por nodo
                else:
                    print("Ningun nodo listo para Tx")
                    print("Decrementando el EB de todos los nodos")
                    self.decreasseAllEB( )
                    self.time += self.tc
                    print("Aumentando un salto corto, time:  " + str(self.time))
            

            print("///////////////////////////////////")    
            print("Tiempo de simulacion: " + str(self.time))
            print("///////////////////////////////////\n\n")    
            count += 1              #Aumentar el numero de iteracion

            
            
        print("\n\n////////////////////////////////")
        print("El tiempo Total es " + str(self.time))
        print("////////////////////////////////")

        data = Counter(scswindow)
        window = data.most_common(1)[0][0]
        return [self.time, cols, window]
    
AP_1 = AP()

paqs = 1000
nodes = [ i for i in range(1,110,3)]
tiempos = []
rbps = []
cols = []
win = []
for node in nodes:
    results = AP_1.startSimulation(node,paqs)
    t, c, w = results[0], results[1], results[2]
    tiempos.append (t)
    cols.append (c)
    win.append (w)
    rbps.append(paqs*1500*8/t)

y_pos = np.arange(len(nodes))
#plt.bar(y_pos, tiempos, align='center', alpha=0.5)
#plt.bar(y_pos, win, align='center', alpha=0.5)
#plt.bar(y_pos, cols, align='center', alpha=0.5)
plt.bar(y_pos, rpbs, align='center', alpha=0.5,  color=(0.07, 0.978, 0.97, 0.1))
plt.xticks(y_pos, nodes)
plt.xlabel('#nodos')
plt.title('Ventana exitosa (moda) vs nodos')
plt.show()
