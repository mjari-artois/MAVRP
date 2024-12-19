from .MAVRPDepot import Depot
from .MAVRPNode import Node
import pandas as pd

class Problem:
    
    def __init__(self):
        self._depot =  []
        self._nodes = []
        self._vehicle_capacity = 1

    def addDepot(self,depot:Depot):
        self._depot.append(depot)

    def addNode(self,node:Node):
        self._nodes.append(node)
    
    def getDepot(self):
        return self._depot[0]

    def getNodes(self):
        return self._nodes
    
    def getNode(self,c):
        return self._nodes[c]
    
    def readProblem(self,filePath):
        try:
            instance = pd.read_csv(filePath)
        except Exception as e:
            raise ValueError(f"Error reading file {e}")
        
        depot = Depot()
        depot.coord_x = instance["x"].iloc[-2]
        depot.coord_y = instance["y"].iloc[-2]
        self.addDepot(depot)

        for _,row in instance[:-1].iterrows():
            node  =Node()
            node.id = int(row["Ids"])
            node.coord_x = float(row["x"])
            node.coord_y = float(row["y"])
            node.demand = float(row["demand_linehaul"])
            node.service_time = float(row["service_time"])
            self.addNode(node)
    
    def printProblem(self):
        print("Depot: ")
        for depot in self._depot:
            depot.PrintDepot()

        print("Nodes:")
        for node in self._nodes:
            node.PrintNode()        