from Model.MAVRPProblem import Problem
from Model.MAVRPTour import Tour
from Model.MAVRPSolution import Solution 
from Solver.RandomSolution import Solver

problem = Problem()
problem.readProblem(".\Data\OVRPMBLTW.csv")
solver = Solver()
solver.GenerateGiantTour(problem)
solver.PrintGiantTour()
V,P = solver.SplitGiantTour(problem.getDepot(),problem)
print(P)
solution = solver.SolutionExtraction(P)
solver.PrintSolution(problem,problem._depot[0])
solver.getTimeofEachNode(problem._depot[0],problem)

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