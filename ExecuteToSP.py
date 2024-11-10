from agent.Agent import * 
from examples.ToolSwitchingProblem import *  

from state.Solution import * 

import numpy as np 
     
problemv = ToolSwitchingProblem(["matrix_10j_9to_NSS_1.txt", 4])

# print a random solution
state = Solution(problemv, "RANDOM") 
problemv.evaluate(state) 
state.prints( )

agent = Agent(problemv, ["GA", "GAS",  3250, 5]) 
# agent = Agent(problemv, ["DE", "DEc", 12500, 6])
# agent = Agent(problemv, ["CE", "CEc", 1250  , 6]) 
# agent = Agent(problemv, ["SA", "SAR", 12500, 12])

agent.init()

# other problem
# problemv = NQueens(15)
# agent = Agent(problemv, ["SA", "SAS", 25000, 12])
# agent = Agent(problemv, ["GA", "GAS", 2500, 12]) 
# agent.init()
