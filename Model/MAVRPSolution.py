from .MAVRPNode import Node
from .MAVRPTour import Tour
import numpy as np 



class Solution:
    def __init__(self):
        self.Solution = []


    def addToursToSolution(self,tour:Tour):
        self.Solution.append(tour)

    def calculateDistance(self, node1: Node, node2: Node):
        return np.sqrt((node1.coord_x - node2.coord_x)**2 + (node1.coord_y - node2.coord_y)**2)
    
    def getCost(self):
        cost = 0
        for tour in self.Solution:
            cost += tour.getCost()
        return cost


    def PrintSolution(self):
        print(f"Solution Cost: {self.getCost()} ")
        for index,tour in enumerate(self.Solution):
            print(f"Tour {index}: Cost: {tour.getCost()} ")
            print(" => ".join(str(node.getID()) for node in tour.getTour()))




