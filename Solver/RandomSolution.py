from Model.MAVRPProblem import Problem
import random
from Model.MAVRPNode import Node
import numpy as np 
from Model.MAVRPDepot import Depot

class Solver:

    def __init__(self):
        self.GiantTour = []
        self.Solution = []

    def GenerateGiantTour(self, problem: Problem):
        nodes = problem._nodes
        nodesIds = []
        for node in nodes:
            nodesIds.append(node.getID())
        while nodesIds:
            selectedNode = random.choice(nodesIds)
            self.GiantTour.append(selectedNode)
            nodesIds.remove(selectedNode)

    def calculateDistance(self, node1: Node, node2: Node):
        return np.sqrt((node1.coord_x - node2.coord_x)**2 + (node1.coord_y - node2.coord_y)**2)

    def SplitGiantTour(self, depot: Depot, problem: Problem):
        n = len(self.GiantTour)
        V = [float("inf")] * (n + 1)  # Cost array
        P = [0] * (n + 1)  # Predecessor array
        V[0] = 0  # Cost at depot is 0

        for i in range(1, n + 1):
            j = i
            load = 0
            cost = 0

            while j <= n:
                sj = self.GiantTour[j - 1] - 1  # Adjust for 0-based indexing

                load += problem.getNode(sj).demand

                if i == j:
                    cost = (
                        self.calculateDistance(depot, problem.getNode(sj)) +
                        problem.getNode(sj).service_time +
                        self.calculateDistance(problem.getNode(sj), depot)
                    )
                else:
                    prev_sj = self.GiantTour[j - 2] - 1  # Previous customer
                    cost = (
                        cost -
                        self.calculateDistance(problem.getNode(prev_sj), depot) +
                        self.calculateDistance(problem.getNode(prev_sj), problem.getNode(sj)) +
                        problem.getNode(sj).service_time +
                        self.calculateDistance(problem.getNode(sj), depot)
                    )

                if V[i - 1] + cost < V[j] and load <= problem._vehicle_capacity + 1e-6:
                    V[j] = V[i - 1] + cost
                    P[j] = i - 1

                j += 1

        return V, P


    def SolutionExtraction(self, P):
       
        j = len(P) - 1  # Start from the end of the tour

        while j > 0:
            route = []
            for k in range(P[j] + 1, j + 1):
                route.append(self.GiantTour[k - 1])
            self.Solution.insert(0, route)  # Insert at the beginning to maintain order
            j = P[j]  # Move to predecessor

        return self.Solution


    def PrintGiantTour(self):
        print(f"length of the GiantTour: {len(self.GiantTour)}")
        print(" => ".join(str(node) for node in self.GiantTour))

    def PrintSolution(self, problem: Problem, depot: Depot):
        total_cost = 0

        for index, sol in enumerate(self.Solution):
            print(f"Tour {index}: {sol}")

            load = 0
            tour_cost = 0

            for node in sol:
                load += problem._nodes[node - 1].getDemand()

            if len(sol) > 0:
                first_node = problem._nodes[sol[0] - 1]
                tour_cost += self.calculateDistance(depot, first_node)

                for i in range(len(sol) - 1):
                    current_node = problem._nodes[sol[i] - 1]
                    next_node = problem._nodes[sol[i + 1] - 1]
                    tour_cost += self.calculateDistance(current_node, next_node)

                last_node = problem._nodes[sol[-1] - 1]
                tour_cost += self.calculateDistance(last_node, depot)

            total_cost += tour_cost
            print(f"Load: {load}")
            # print(f"Cost of Tour {index}: {tour_cost:.2f}")

        print(f"Total Cost of Solution: {total_cost:.2f}")

                





