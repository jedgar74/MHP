"""
Created on Sun Feb  2 18:47:40 2020

@author: tauger
"""
from algorithm.Heuristic import *
from problem.Problem import * 
from state.Solution import * 
# from agent.Agent import *
import agent.Agent as ag

import numpy as np

import math 
import copy


class CooperativeSearch (Heuristic): 
   
    
    def __init__(self, problem, fileConfig, run=True):
        super().__init__()
        # int factorNeighs = 0 
        # String allNeighs = "NONE"  #  can be ALL or NONE 
        self.shortTerm  = "CooS"
        self.objProblem = problem 
   
        self.setParameters(fileConfig)   
  
        #  String initSolution = ""  #  solution initial equi o aleatoria
        #  EQUI/RANDOM
 
        self.agents = []
        self.typeInitialSolution = "" 
        
        self.status.stateInitial = Solution(self.objProblem, self.parameters.get('initialTypeSolution')) 
        self.objProblem.evaluate(self.status.stateInitial) 
        self.objProblem.counter.incCount() 
        self.status.stateFinal = copy.deepcopy(self.status.stateInitial) 
        self.status.stateFinal = self.status.stateInitial  
        self.status.stateFinal.prints("............\n")
        
        
        #  Init the agents 
        _evals = 0 
        print("AGENTS "+str(self.parameters.get('numberAgents'))) 
        print("CYCLES "+str(self.parameters.get('numberCycles')))
        print("ARCHITECTURE "+str(self.parameters.get('architecture')))
        #  if (self.parameters.get('numberCycles') < 4) self.parameters.get('numberCycles') = 4 
        _evals = 1 + (self.objProblem.counter.getLimit() // (self.parameters.get('numberAgents') * self.parameters.get('numberCycles') )) 
        print("EVALUATIONS " + str(_evals) )
        for t in range(self.parameters.get('numberAgents')): 
            # self.agents.add(Agent(self.objProblem, self.parameters.get('configFiles').get(t), self.stateFinal) ) 
           
            agentd = ag.Agent(self.objProblem, [self.parameters.get('listMethods')[t], self.parameters.get('configFiles')[t], _evals, 1] )
            self.agents.append(agentd) 
  #  StateOf _state = new StateOf(objProblem.nBits, typeInitialSolution) 
  
  #  self.stateFinal = (StateOf) _state.clone() 
  #  print("EVALUATIONS "+self.objProblem.timeLimit) 

  #  self.printsParameters() 

        if run==True :
            if self.parameters.get('architecture') == "RING":  
                self.cooperative(self.status.stateInitial) 
            elif self.parameters.get('architecture') == "RANDOM":  
                self.cooperative(self.status.stateInitial)
            elif self.parameters.get('architecture') == "BROADCAST" : 
                self.cooperative(self.status.stateInitial)
#        else  
#   self.ringSDI(state) 
 
    
    def run(self, sol=None):
        """ 
		@param problem.Problem _problem : 
		@return  :
		@author
		"""
		
        if self.parameters.get('architecture') == "RING": 
            self.cooperative(sol)
        elif self.parameters.get('architecture') == "RANDOM":  
            self.cooperative(sol)
        elif self.parameters.get('architecture') == "BROADCAST" : 
            self.cooperative(sol)
            
             

    def setParameters(self, fileConfig):
        """ 
        @param problem.Problem _problem : 
        @return  :
        @author
        """ 
  
        self.parameters = self.readParameters(fileConfig, self.shortTerm)
  # print(self.parameters)
        for i in range(8): # (int i = 0 i < nameParameters.size() i++) :
        
            if not 'listMethods' in self.parameters : 
                self.parameters.update(dict(listMethods=[])) 
     
            if not 'configFiles' in self.parameters : 
                self.parameters.update(dict(configFiles=[])) 
                
            if not 'probComm' in self.parameters :
                self.parameters.update(dict(probComm=1))    
                
            if not 'initialTypeSolution' in self.parameters : 
                self.parameters.update(dict(initialTypeSolution="RANDOM")) 
                
            if not 'numberCycles' in self.parameters : 
                self.parameters.update(dict(numberCycles=3))  
            
            if not 'numberAgents' in self.parameters : 
                self.parameters.update(dict(numberAgents=1))  
                
            if not 'architecture' in self.parameters : 
                self.parameters.update(dict(architecture="RANDOM")) # The other architecture is Broadcast RANDOM  
  # print(self.parameters)  
  
            if not 'changeoftopology' in self.parameters : 
                self.parameters.update(dict(changeoftopology="OFF")) 
 

    def cooperative(self, init) :
        """ 
        @param problem.Problem _problem : 
        @return  :
        @author
        """ 
        
        if (self.parameters.get('numberAgents') != len(self.parameters.get('listMethods')) ) :
            print("Error! #agents != #methods") 
            return  

        evals = 0 

        #  if (self.parameters.get('numberCycles') < 4) self.parameters.get('numberCycles') = 4 
        evals = 1 + (self.objProblem.counter.getLimit() // (self.parameters.get('numberAgents') * self.parameters.get('numberCycles') )) 
        print("EVALUATIONS " + str(evals) )

        #  Define the temporally state
        #  StateOf tmpState 
    
        #  Init the agents
        for t in range(self.parameters.get('numberAgents')):  
            agentd = ag.Agent(self.objProblem, [self.parameters.get('listMethods')[t], self.parameters.get('configFiles')[t], evals, 1] )
            self.agents.append(agentd)  
            self.agents[t].init2() 

        ccycles = 0  
        architecture = self.parameters.get('architecture')  
        nc = 0 
        la = ["RING", "BROADCAST" , "RANDOM"]

        while (ccycles < self.parameters.get('numberCycles')) :
            best = self.getBetter()
            print("\nCYCLE " + str(ccycles + 1)) 
            for t in range(self.parameters.get('numberAgents')):  
                # self.agents[t].init(_evals)  
                self.agents[t].run()  
        
            print("\n"+"AGENTS BEFORE") 
            for t in range(self.parameters.get('numberAgents')): 
                self.agents[t].stats.solutions[ccycles].prints("----" + str(t) ) 
          
            
            if architecture == "RING" :
                self.ring(ccycles)
            elif architecture == "BROADCAST" :
                self.broadcast(ccycles)	
            elif architecture == "RANDOM" :
                self.random(ccycles)		

            nc = self.getNChanges(best)
            print("\n"+architecture) 
            print( str(nc) )
#            print("\n"+"AGENTS a") 
#            for t in range(self.parameters.get('numberAgents')): 
#                self.agents[t].stats.solutions[ccycles].prints("----" + str(t) ) 
            
            if self.parameters.get('changeoftopology') == "ON" :  
                if nc == 0 : 
                    ca = np.random.randint(3)  
                    while  architecture == la[ca]:   
                        ca = np.random.randint(3)     
                    architecture = la[ca]    
                    print("..."+ architecture ) 
                
            ccycles = ccycles + 1
            
        self.calcBetter()   



    def ring(self, ccycles) :
        """ 
        @param problem.Problem _problem : 
        @return  :
        @author
        """ 
        
        na = self.parameters.get('numberAgents')
        tmpState = self.agents[na - 1].stats.solutions[ccycles] 
        
        for t in range(self.parameters.get('numberAgents') - 1):   
            #  agents.get(t).internalState.printStateOf(""+t) 
            # if self.condUpdateInternal():
#            ini = self.agents[0].stats.solutions[ccycles].fitness
#            fin = self.parameters.get('numberAgents')
#            print("CCCR "+ str(ini ) )  
            if self.condUpdateInternal() and self.objProblem.op.isBetter([self.agents[na - t - 2].stats.solutions[ccycles] , self.agents[na - t  - 1].stats.solutions[ccycles] ]):
                print("Changed "+ str(na - t - 2)+ " --> "+ str(na - t - 1)+ " ... "+ str(self.agents[na - t - 2].stats.solutions[ccycles].fitness)+ " --> "+ str (self.agents[na - t - 1].stats.solutions[ccycles].fitness)) 
                #  self.agents[na - t - 1].objMetaheuristic.status.stateFinal = copy.deepcopy(self.agents[na - t - 2].stats.solutions[f]) 
                self.agents[na - t - 1].replacement(self.agents[na - t - 2].stats.solutions[ccycles])
                #  print("..."+t)   
    
            #  tmpState.printStateOf(""+(self.parameters.get('numberAgents')-1)) 
            if self.condUpdateInternal() and self.objProblem.op.isBetter([tmpState, self.agents[0].stats.solutions[ccycles] ]):
                print("Changed "+ str(na - 1)+ " --> "+ str(0)+ " ... "+ str(self.agents[na - 1].stats.solutions[ccycles].fitness)+ " --> "+ str (self.agents[0].stats.solutions[ccycles].fitness)  )
                self.agents[0].replacement(tmpState)   
                
#        print("\n"+"AGENTS af") 
#        for t in range(self.parameters.get('numberAgents')): 
#            self.agents[t].stats.solutions[ccycles].prints("----" + str(t) )          

    def broadcast(self, ccycles) :
        """ 
        @param problem.Problem _problem : 
        @return  :
        @author
        """         
        
        na = self.parameters.get('numberAgents')
        tmpState = self.agents[0].stats.solutions[ccycles] 
        cs = 0

        for t in range(1, self.parameters.get('numberAgents')):   
            #  agents.get(t).internalState.printStateOf(""+t) 
            # if self.condUpdateInternal():
            #      print("CCCR "+ str(t))                  
            if self.objProblem.op.isBetter([self.agents[t].stats.solutions[ccycles] , tmpState ]):
                #  self.agents[na - t - 1].objMetaheuristic.status.stateFinal = copy.deepcopy(self.agents[na - t - 2].stats.solutions[f]) 
                #  tmpState.replacement(self.agents[t].stats.solutions[ccycles])
                tmpState = copy.deepcopy(self.agents[t].stats.solutions[ccycles]) 
                #  print("..."+t) 
                cs = t
 
     
        for t in range(self.parameters.get('numberAgents')):   
            #  agents.get(t).internalState.printStateOf(""+t) 
            # if self.condUpdateInternal():
            #      print("CCCR "+ str(t))                  
            if self.condUpdateInternal() and self.objProblem.op.isBetter([tmpState , self.agents[t ].stats.solutions[ccycles] ]):
                     print("Changed "+ str(cs)+ " --> "+ str(t)) 
                     #  self.agents[na - t - 1].objMetaheuristic.status.stateFinal = copy.deepcopy(self.agents[na - t - 2].stats.solutions[f]) 
                     self.agents[t].replacement(tmpState)
                   #  print("..."+t)  
  

    def random(self, ccycles) :
        """ 
        @param problem.Problem _problem : 
        @return  :
        @author
        """         
        
        na = self.parameters.get('numberAgents')

        for t in range(self.parameters.get('numberAgents')):    
 
            a1 = np.random.randint(self.parameters.get('numberAgents'))
            a2 = np.random.randint(self.parameters.get('numberAgents'))  
            while  a2 == a1:   
                a2 = np.random.randint(self.parameters.get('numberAgents'))     
    
            #  tmpState.printStateOf(""+(self.parameters.get('numberAgents')-1)) 
            if self.condUpdateInternal() and self.objProblem.op.isBetter([self.agents[a1].stats.solutions[ccycles], self.agents[a2].stats.solutions[ccycles] ]):
                print("Changed "+ str(a1)+ " --> "+ str(a2)+ " ... "+ str(self.agents[a1].stats.solutions[ccycles].fitness)+ " --> "+ str (self.agents[a2].stats.solutions[ccycles].fitness)  ) 
                self.agents[a2].replacement(self.agents[a1].stats.solutions[ccycles])
                                
                
                
    def ringe(self, init) :
        """ 
        @param problem.Problem _problem : 
        @return  :
        @author
        """ 
        if (self.parameters.get('numberAgents') != len(self.parameters.get('listMethods')) ) :
            print("Error! #agents != #methods") 
            return  

        _evals = 0 

        #  if (self.parameters.get('numberCycles') < 4) self.parameters.get('numberCycles') = 4 
        _evals = 1 + (self.objProblem.counter.getLimit() // (self.parameters.get('numberAgents') * self.parameters.get('numberCycles') )) 
        print("EVALUATIONS " + str(_evals) )

        #  Define the temporally state
        #        StateOf tmpState 

        #  Init the agents
        for t in range(self.parameters.get('numberAgents')): 
            # self.agents.add(Agent(self.objProblem, self.parameters.get('configFiles').get(t), self.stateFinal) ) 
           
            agentd = ag.Agent(self.objProblem, [self.parameters.get('listMethods')[t], self.parameters.get('configFiles')[t], _evals, 1] )
            self.agents.append(agentd)
   #  AgentToSP agentX = new AgentToSP(self.incident, self.magazine,
   #  self.time, self.parameters.get('configFiles').get(t),
   #  self.parameters.get('listMethods').get(t), false) 
   #  self.agents.add(agentX)  

        f = 0 

        while (f < self.parameters.get('numberCycles')) :

            print("CYCLE " + str(f + 1)) 
            for t in range(self.parameters.get('numberAgents')):  
                # self.agents[t].init(_evals)  
                self.agents[t].init()  
        
            tmpState = self.agents[self.parameters.get('numberAgents') - 1].stats.solutions[0] 

            for t in range(self.parameters.get('numberAgents') - 1):   
                #  agents.get(t).internalState.printStateOf(""+t) 
                if self.condUpdateInternal() and self.objProblem.op.isBetter([self.agents[self.parameters.get('numberAgents') - t - 2], self.agents[self.parameters.get('numberAgents') - t  - 1]]):
                     self.agents[self.parameters.get('numberAgents') - t - 1].setInternalState(self.agents[self.parameters.get('numberAgents') - t - 2].internalState) 
                   #  print("..."+t)  
    
            #  tmpState.printStateOf(""+(self.parameters.get('numberAgents')-1)) 
            if self.condUpdateInternal() and self.objProblem.op.isBetter([tmpState, self.agents[0]]):
                self.agents[0].setInternalState(tmpState) 
    
            f = f + 1

            print("\n"+"AGENTS") 
            for t in range(self.parameters.get('numberAgents')): 
                self.agents[t].stats.solutions[0].prints("----" + str(t) )
     
        self.calcBetter() 
  
   

    def compareStateOf(self, sol) :
        """ 
        @param problem.Problem _problem : 
        @return  :
        @author
        """         
        
        sol.printStateOf("INIT") 
        self.stateFinal.printStateOf("STAF") 

        if self.objProblem.op.isBetter([self.stateFinal, sol]): 
            return self.stateFinal 
        else :
            return sol  
  


    def calcBetter(self  ) :
        """ 
        @param problem.Problem _problem : 
        @return  :
        @author
        """         
        
        ncs = self.parameters.get('numberCycles') - 1
        self.status.stateFinal =  copy.deepcopy(self.agents[0].stats.solutions[ncs])
        self.status.stateFinal.prints("----" + "I" )

        for t in range(1, self.parameters.get('numberAgents') ):
            
            if self.objProblem.op.isBetter([self.agents[t].stats.solutions[ncs], self.status.stateFinal]): 
                  # self.stateFinal = self.agents[t].stats.solutions[0] 
                  self.status.stateFinal =  copy.deepcopy(self.agents[t].stats.solutions[ncs]) 
        self.status.stateFinal.prints("----" + "F" )          
   #  self.internalState.copy(self.agents.get(t).getInternalState()) 
   #  # getInternalState
   
  

    def calcBetterCoop(self ) :
        """ 
        @param problem.Problem _problem : 
        @return  :
        @author
        """         
        
        self.stateFinal = self.compareStateOf( self.agents[0].stats.solutions[0]) 

        for t in range(1, self.parameters.get('numberAgents') ): 
            if self.objProblem.op.isBetter([self.agents[t].stats.solutions[0], self.agents[t - 1].stats.solutions[0]]): 
                
                self.stateFinal = self.compareStateOf( self.agents[t].stats.solutions[0]) 
   #  self.internalState.copy(self.agents.get(t).getInternalState()) 
   #  # getInternalState
    
    

    def condUpdateInternal(self ) :
        """ 
        @param problem.Problem _problem : 
        @return  :
        @author
        """         
        return (np.random.rand() < self.parameters.get('probComm')) 
  


    def printsParameters(self ) :
        """ 
        @param problem.Problem _problem : 
        @return  :
        @author
        """         
        print("---->" + self.architecture) 
        print("---->" + self.objProblem.timeLimit) 
        print("NA:::" + self.parameters.get('numberAgents')) 
        print("NC:::" + self.parameters.get('numberCycles')) 
        print("PC:::" + self.parameters.get('probComm')) 
        print("MT:::" + self.parameters.get('listMethods')) 
        print("CF:::" + self.parameters.get('configFiles')) 
        print("TI:::" + self.typeInitialSolution) 
  
  

    def selectCP(self, _init, _problem,  _evals) :
        """ 
        @param problem.Problem _problem : 
        @return  :
        @author
        """         
        print("WANT TO________" + self.architecture) 
        if (self.architecture.equals("RING")) :
            #  print("::::::::::::::::::::::::::::::ffff::::::::::::::::::::::::::::::::::::::::::") 
            return self.ring(_init, _problem, _evals) 
#  elif (self.architecture.equals("RANDOM"))
#   return random(_init, _problem, _evals) 
#  elif (self.architecture.equals("BROADCAST"))
#   return broadcast(_init, _problem, _evals) 
#  else :
#   return ringSDI(_init, _problem, _evals) 
            
            
            
    def getBetter(self ) :
        """ 
        @param problem.Problem _problem : 
        @return  :
        @author
        """   
        better=self.agents[0].objMetaheuristic.status.stateFinal           
        for t in range(1,self.parameters.get('numberAgents')): 
            if self.objProblem.op.isBetter([self.agents[t].objMetaheuristic.status.stateFinal, better]): 
                  # self.stateFinal = self.agents[t].stats.solutions[0] 
                  better = copy.deepcopy(self.agents[t].objMetaheuristic.status.stateFinal)   
            
        return better


  
    def getNChanges(self, bbest ) :
        """ 
        @param problem.Problem _problem : 
        @return  :
        @author
        """   
        
        abest = self.getBetter() 
        better = 0
        
        bbest.prints("----" + "B" ) 
        abest.prints("----" + "A" ) 
        if self.objProblem.op.isBetter([abest, bbest] ): 
            # self.stateFinal = self.agents[t].stats.solutions[0] 
           better = 1   
            
        return better 
