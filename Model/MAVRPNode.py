class Node:

    def __init__(self):
        self.id = 0
        self.coord_x = 0
        self.coord_y = 0
        self.demand_linehaul = 0 #deliveries 
        self.demand_backhaul = 0 #pickups
        self.service_time = 0

    def getID(self):
        return self.id

    def getX(self):
        return self.coord_x  

    def getY(self):
        return self.coord_y  

    def getDemandBackhaul(self):
        return self.demand_backhaul
    
    def getDemandLinehaul(self):
        return self.demand_linehaul

    def getSeviceTime(self):
        return self.service_time
    

    def PrintNode(self):
        print(f"id = {self.getID()}")
        print(f"x = {self.getX()}")  
        print(f"y = {self.getY()}")  
        print(f"demand linehaul = {self.getDemandLinehaul()}")
        print(f"demand backhaul = {self.getDemandBackhaul()}")  
        print(f"service time = {self.getSeviceTime()}")  

