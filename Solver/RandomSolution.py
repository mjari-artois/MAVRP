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
        V = [float("inf")] * (n + 1)  # Minimum cost to reach each node
        P = [0] * (n + 1)             # Pointer array to track splits
        V[0] = 0                      # Cost to start from depot is 0

        for i in range(1, n + 1):
            time = 0
            load = 0
            distance = 0
            j = i

            while j <= n:
                sj = self.GiantTour[j - 1]
                load += problem.getNode(sj).getDemand()

                if i == j:
                    # First node in the tour segment
                    time = max(
                        self.calculateDistance(depot, problem.getNode(sj)),
                        problem.getNode(sj).est
                    ) + problem.getNode(sj).service_time
                    distance = 2 * self.calculateDistance(depot, problem.getNode(sj))
                else:
                    # Subsequent nodes in the tour segment
                    prev_sj = self.GiantTour[j - 2]
                    time = max(
                        time - self.calculateDistance(depot, problem.getNode(prev_sj)) +
                        self.calculateDistance(problem.getNode(prev_sj), problem.getNode(sj)),
                        problem.getNode(sj).est
                    )
                    distance = distance - self.calculateDistance(depot, problem.getNode(prev_sj)) + \
                            self.calculateDistance(problem.getNode(prev_sj), problem.getNode(sj))

                # Check constraints
                if time > problem.getNode(sj).lst or load > problem._vehicle_capacity:
                    print(f"it should stop at this moment {sj}")
                    break
                else:
                    time += problem.getNode(sj).service_time + self.calculateDistance(problem.getNode(sj), depot)
                    distance += self.calculateDistance(problem.getNode(sj), depot)

                    # Update minimum cost and pointer
                    if V[j] > V[i - 1] + distance:
                        V[j] = V[i - 1] + distance
                        P[j] = i - 1

                    j += 1

        return V, P

        
    def SolutionExtraction(self, P):
        j = len(P) - 1  # Start from the end of the giant tour

        while j > 0:
            route = []
            for k in range(P[j] + 1, j + 1):  # Collect nodes in the current route
                route.append(self.GiantTour[k - 1])
            self.Solution.insert(0, route)  # Insert at the beginning to maintain order
            j = P[j]  # Move to the predecessor index

        return self.Solution


    def print_route_details(self, depot: Depot, problem: Problem):
        """
        Prints detailed information about each route including:
        - Node sequence
        - Arrival time at each node
        - Time windows for each node
        - Service time
        - Travel time between nodes
        - Total route duration and distance

        Parameters:
        depot: Depot - the depot object
        problem: Problem - the problem instance containing node information
        """
        print("\n=== Detailed Route Information ===\n")
        
        for route_idx, route in enumerate(self.Solution, 1):
            print(f"Route {route_idx}:")
            print("-" * 100)
            print(f"{'Node':<8} {'Arrival':<12} {'Time Window':<20} {'Service Time':<15} {'Travel Time':<15} {'Departure':<12} {'Load':<12}")
            print("-" * 100)
            
            current_time = 0
            current_load = 0
            total_distance = 0
            
            # Start from depot
            print(f"Depot{'':<3} {current_time:<12.3f} [{0:>5}, {float('inf'):>5}]{'':<7} {'-':<15} {'-':<15} {current_time:<12.3f} {current_load:<8.3f}")
            
            for i, node_id in enumerate(route):
                node = problem.getNode(node_id)
                
                # Calculate travel time
                if i == 0:
                    travel_time = self.calculateDistance(depot, node)
                else:
                    prev_node = problem.getNode(route[i - 1])
                    travel_time = self.calculateDistance(prev_node, node)
                
                # Update total distance
                total_distance += travel_time
                
                # Calculate arrival time at this node
                arrival_time = current_time + travel_time
                
                # Check if we need to wait for time window
                if arrival_time < node.est:
                    waiting_time = node.est - arrival_time
                    current_time = node.est
                else:
                    waiting_time = 0
                    current_time = arrival_time
                
                # Update current time with service
                departure_time = current_time + node.service_time
                current_time = departure_time
                
                # Update load
                current_load += node.getDemand()
                
                # Print node information
                time_window = f"[{node.est:>5}, {node.lst:>5}]"
                print(f"Node {node_id:<3} {arrival_time:<12.3f} {time_window:<20} {node.service_time:<15.3f} {travel_time:<15.3f} {departure_time:<12.3f} {current_load:<8.3f}")
                
                # If this is the last node, add return to depot
                if i == len(route) - 1:
                    travel_time = self.calculateDistance(node, depot)
                    total_distance += travel_time
                    current_time += travel_time
            
            # Print return to depot
            print(f"Depot{'':<3} {current_time:<12.3f} [{0:>5}, {float('inf'):>5}]{'':<7} {'-':<15} {'-':<15} {current_time:<12.3f} {current_load:<8.3f}")
            print("-" * 100)
            print(f"Route Summary:")
            print(f"Total Distance: {total_distance:.2f}")
            print(f"Total Time: {current_time:.2f}")
            print(f"Total Load: {current_load:.3f}")
            print("\n")


    def validate_route(self, depot: Depot, problem: Problem, route: list) -> tuple[bool, str]:
        """
        Validates a single route for time window and capacity constraints
        
        Returns:
        tuple[bool, str]: (is_valid, error_message)
        """
        current_time = 0
        current_load = 0
        
        for i, node_id in enumerate(route):
            node = problem.getNode(node_id)
            
            # Calculate arrival time
            if i == 0:
                travel_time = self.calculateDistance(depot, node)
            else:
                prev_node = problem.getNode(route[i-1])
                travel_time = self.calculateDistance(prev_node, node)
            
            current_time += travel_time
            
            # Check time window constraint
            if current_time > node.lst:
                return False, f"Time window violation at node {node_id}: Arrived at {current_time:.2f}, latest allowed is {node.lst}"
            
            # Update time with service
            current_time = max(current_time, node.est) + node.service_time
            
            # Check capacity constraint
            current_load += node.getDemand()
            if current_load > problem._vehicle_capacity:
                return False, f"Capacity violation at node {node_id}: Load {current_load:.2f} exceeds capacity {problem._vehicle_capacity}"
        
        # Check return to depot
        last_node = problem.getNode(route[-1])
        current_time += self.calculateDistance(last_node, depot)
        
        return True, "Route is valid"
    


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
            print(f"Load: {round(float(load),4)}")
            # print(f"Cost of Tour {index}: {tour_cost:.2f}")

        print(f"Total Cost of Solution: {total_cost:.2f}")


    def getTimeofEachNode(self,depot:Depot,problem:Problem):
        for index,tour in enumerate(self.Solution):
            print(f"Tour {index}")
        
            for zinedx,node in enumerate(tour):
                node = node -1
                if zinedx==0:
                    time = max(
                            self.calculateDistance(depot,problem.getNode(node)),
                            problem.getNode(node).est
                        ) + problem.getNode(node).service_time
                    distance = self.calculateDistance(depot, problem.getNode(node)) + self.calculateDistance(depot, problem.getNode(node))
                    cost = distance + problem.getNode(node).service_time
                else:
                    time = max(
                            cost - self.calculateDistance(depot,problem.getNode(prev_sj)) + self.calculateDistance(problem.getNode(node),problem.getNode(prev_sj)),
                            problem.getNode(node).est
                        )+ problem.getNode(node).service_time
                    distance = distance - self.calculateDistance(depot,problem.getNode(prev_sj)) + self.calculateDistance(problem.getNode(node),problem.getNode(prev_sj))
                    cost = (
                            cost -
                            self.calculateDistance(problem.getNode(prev_sj), depot) +
                            self.calculateDistance(problem.getNode(prev_sj), problem.getNode(node)) +
                            problem.getNode(node).service_time +
                            self.calculateDistance(problem.getNode(node), depot)
                        )
                prev_sj = node
                time = round(time,3)
                print(f" node : {problem.getNode(node).id} time {time} [{problem.getNode(node).est},{problem.getNode(node).lst}]" )

                
                
                

            

                






