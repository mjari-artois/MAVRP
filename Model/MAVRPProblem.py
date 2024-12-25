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
        depot.coord_x = round(instance["x"].iloc[-2], 4)  
        depot.coord_y = round(instance["y"].iloc[-2], 4) 
        self.addDepot(depot)  

        for index, row in instance[:-1].iterrows():
            node = Node()  
            node.id = index 
            node.coord_x = round(float(row["x"]), 4)  
            node.coord_y = round(float(row["y"]), 4)  
            node.demand = round(float(row["demand_linehaul"]), 4)  
            node.service_time = round(float(row["service_time"]), 4)  
            node.est = round(float(row["time_window_start"]), 4) 
            node.lst = round(float(row["time_window_end"]+4), 4) 

            self.addNode(node)

    
    def printProblem(self):
        print("Depot: ")
        for depot in self._depot:
            depot.PrintDepot()

        print("Nodes:")
        for node in self._nodes:
            node.PrintNode()        