from Model.MAVRPProblem import Problem
from Model.MAVRPTour import Tour
from Model.MAVRPSolution import Solution 
from Solver.RandomSolution import Solver

# First part remains the same
problem = Problem()
problem.readProblem("OVRPMBLTW.csv")
solver = Solver()
solver.GenerateGiantTour(problem)
solver.PrintGiantTour()
V, P = solver.SplitGiantTour(problem.getDepot(), problem)
solution = solver.SolutionExtraction(P)
print("Raw solution:", solution)

# Add detailed route printing
print("\nDetailed Route Analysis:")
solver.print_route_details(problem.getDepot(), problem)

# Optionally validate each route
print("\nValidating Routes:")
for route_idx, route in enumerate(solution, 1):
    is_valid, message = solver.validate_route(problem.getDepot(), problem, route)
    print(f"Route {route_idx}: {message}")

#problem.printProblem()
# nodes = problem.getNodes()
# tour = Tour()
# solution = Solution()
# for node in nodes[:3]:
#     tour.addNodeToTour(node)
# solution.addToursToSolution(tour)
# tour = Tour()
# for node in nodes[3:8]:
#     tour.addNodeToTour(node)
# solution.addToursToSolution(tour)
# tour = Tour()
# for node in nodes[8:15]:
#     tour.addNodeToTour(node)
# solution.addToursToSolution(tour)

# solution.PrintSolution()