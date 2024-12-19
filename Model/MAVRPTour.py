from .MAVRPNode import Node
import numpy as np


class Tour:

    def __init__(self):
        self.Tour = []
        pass
    
    def calculateDistance(self, node1: Node, node2: Node):
        return np.sqrt((node1.coord_x - node2.coord_x)**2 + (node1.coord_y - node2.coord_y)**2)

    def getTour(self):
        return self.Tour
    
    def getCost(self):
        cost = 0
        for i in range(len(self.Tour)-1):
            cost+= self.calculateDistance(self.Tour[i],self.Tour[i+1])
        return cost
    
    def PrintTour(self):
        print(f"Cost of Tour: {self.getCost()}")
        print("Tour:")
        print(" => ".join(str(node.getID()) for node in self.Tour))

    def addNodeToTour(self,node:Node):
        self.Tour.append(node)


    
            

