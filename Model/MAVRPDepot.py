class Depot:

    def __init__(self):
        self.coord_x = 0
        self.coord_y = 0

    def getX(self):
        return self.coord_x

    def getY(self):
        return self.coord_y
    
    def PrintDepot(self):
        print(f"x = {self.getX()}")
        print(f"y = {self.getY()}")
