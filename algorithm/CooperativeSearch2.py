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
#        elif self.parameters.get('architecture') == "RANDOM":  
#            self.random(state) 
#        elif self.parameters.get('architecture') == "BROADCAST" : 
#            self.broadcast(state) 
#        else  
#   self.ringSDI(state) 
 
    def run(self, sol=None):
        """ 
		@param problem.Problem _problem : 
		@return  :
		@author
		"""
		
        if self.parameters.get('architecture') == "RING": 
            self.cooperative(state)
            
            
# =============================================================================
#  public CooperativeSearch(Problem _problem, String _fileConfig,
#    StateOf _state) :
#    
#   self.stateFinal = (StateOf) _state.clone() 
# 
#   if (self.architecture.equals("RING")
#     || self.architecture.equals("RANDOM")
#     || self.architecture.equals("BROADCAST")) :
#    if (self.parameters.get('numberAgents') != self.parameters.get('listMethods').size()) :
#     print("Error! #agents != #methods") 
#     return 
#     
# 
#    #  Init the agents
#    for (int t = 0  t < self.parameters.get('numberAgents')  t++) :
#     self.agents.add(new Agent(_problem, self.parameters.get('configFiles')
#       .get(t), self.stateFinal)) 
#     #  AgentToSP agentX = new AgentToSP(self.incident,
#     #  self.magazine, self.time, self.parameters.get('configFiles').get(t),
#     #  self.parameters.get('listMethods').get(t), false) 
#     #  self.agents.add(agentX) 
#     
# 
#     else :
#    #  Init the agents
#    #  Revisar
#    self.agents.add(new Agent(_problem, "HCSDI",
#      compareStateOf(self.stateFinal))) 
#    self.agents.add(new Agent(_problem, "GASDI",
#      compareStateOf(self.stateFinal))) 
#    self.agents.add(new Agent(_problem, "KOSDI",
#      compareStateOf(self.stateFinal))) 
# =============================================================================
   

    def setParameters(self, fileConfig):
        """ 
  @param problem.Problem _problem : 
  @return  :
  @author
  """ 
  
        self.parameters = self.readParameters(fileConfig, self.shortTerm)
  # print(self.parameters)
        for i in range(7): # (int i = 0 i < nameParameters.size() i++) :
        
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
                self.parameters.update(dict(architecture="RANDOM"))    #  The other architecture is Broadcast RANDOM  
  # print(self.parameters)  
  
 

#    def broadcast(self, _init) :
#
#  if (self.parameters.get('numberAgents') != self.parameters.get('listMethods').size()) :
#   print("Error! #agents != #methods") 
#   return 
#   
#
#  #  define flag to end cycle
#  int _evals = 0 
#  #  print("EVALUATIONS "+self.objProblem.evaluationCounter) 
#  #  if (self.parameters.get('numberCycles') < 4) self.parameters.get('numberCycles') = 4 
#  _evals = 1 + (int) (self.objProblem.timeLimit / (self.parameters.get('numberAgents') * self.parameters.get('numberCycles'))) 
#  print("EVALUATIONS " + _evals) 
#
#  #  Define the temporally state
#  StateOf tmpState 
#
#  #  Init the agents
#  for (int t = 0  t < self.parameters.get('numberAgents')  t++) :
#   self.agents.add(new Agent(self.objProblem, self.parameters.get('configFiles')
#     .get(t), _init)) 
#   #  AgentToSP agentX = new AgentToSP(self.incident, self.magazine,
#   #  self.time, self.parameters.get('configFiles').get(t),
#   #  self.parameters.get('listMethods').get(t), false) 
#   #  self.agents.add(agentX) 
#   
#  print("LOADED AGENTS ") 
#  int f = 0 
#  while (f < self.parameters.get('numberCycles')) :
#   print("CYCLE " + (f + 1)) 
#   for (int t = 0  t < self.parameters.get('numberAgents')  t++) :
#    self.agents.get(t).init(_evals) 
#    
#
#   tmpState = (StateOf) self.agents.get(0).internalState.clone() 
#
#   for (int t = 1  t < self.parameters.get('numberAgents')  t++) :
#    if (tmpState.getFitnessOne() > self.agents.get(t).internalState
#      .getFitnessOne())
#     tmpState = (StateOf) self.agents.get(t).internalState
#       .clone() 
#    
#
#   for (int t = 0  t < self.parameters.get('numberAgents')  t++) :
#    #  print("..1 ") 
#    if (condUpdateInternal()
#      and tmpState.best(self.agents.get(t).internalState)) :
#     #  print("..2 ") 
#     self.agents.get(t).setInternalState(tmpState)  #  getInternalState
#     #  print(self.agents.get(t).getInternalState().prints()) 
#     
#   f++ 
#
#   for (int t = 0  t < self.parameters.get('numberAgents')  t++) :
#    self.agents.get(t).internalState.printStateOf("" + t) 
#    
#   
#  self.calcBetter() 

    def cooperative(self, init) :

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

        f = 0 
        
        architecture = self.parameters.get('numberAgents')

        while (f < self.parameters.get('numberCycles')) :

            print("CYCLE " + str(f + 1)) 
            for t in range(self.parameters.get('numberAgents')):  
                # self.agents[t].init(_evals)  
                self.agents[t].run()  
        
            if architecture == "RING" :
                self.ring(f)
            elif architecture == "BROADCAST" :
                self.broadcast(f)	
            elif architecture == "RANDOM" :
                self.random(f)		

            print("\n"+"AGENTS") 
            for t in range(self.parameters.get('numberAgents')): 
                self.agents[t].stats.solutions[f].prints("----" + str(t) ) 
    
            f = f + 1
            
        self.calcBetter()   



    def ring(self, f) :
        na = self.parameters.get('numberAgents')
        tmpState = self.agents[na - 1].stats.solutions[f] 

        for t in range(self.parameters.get('numberAgents') - 1):   
            #  agents.get(t).internalState.printStateOf(""+t) 
            # if self.condUpdateInternal():
            #      print("CCCR "+ str(t))                  
            if self.condUpdateInternal() and self.objProblem.op.isBetter([self.agents[na - t - 2].stats.solutions[f] , self.agents[na - t  - 1].stats.solutions[f] ]):
                     print("Changed "+ str(na - t - 2)+ " --> "+ str(na - t - 1)) 
                     #  self.agents[na - t - 1].objMetaheuristic.status.stateFinal = copy.deepcopy(self.agents[na - t - 2].stats.solutions[f]) 
                     self.agents[na - t - 1].replacement(self.agents[na - t - 2].stats.solutions[f])
                   #  print("..."+t) 
            print("\n"+"+++++")
     
    
            #  tmpState.printStateOf(""+(self.parameters.get('numberAgents')-1)) 
            if self.condUpdateInternal() and self.objProblem.op.isBetter([tmpState, self.agents[0].stats.solutions[f] ]):
                print("Changed "+ str(na - 1)+ " --> "+ str(0)) 
                self.agents[0].replacement(tmpState)  
 

    def broadcast(self, f) :
        na = self.parameters.get('numberAgents')
        tmpState = self.agents[0].stats.solutions[f] 

        for t in range(1, self.parameters.get('numberAgents')):   
            #  agents.get(t).internalState.printStateOf(""+t) 
            # if self.condUpdateInternal():
            #      print("CCCR "+ str(t))                  
            if self.objProblem.op.isBetter([self.agents[t].stats.solutions[f] , tmpState ]):
                #  self.agents[na - t - 1].objMetaheuristic.status.stateFinal = copy.deepcopy(self.agents[na - t - 2].stats.solutions[f]) 
                tmpState.replacement(self.agents[t].stats.solutions[f])
                #  print("..."+t) 
     
        for t in range(self.parameters.get('numberAgents')):   
            #  agents.get(t).internalState.printStateOf(""+t) 
            # if self.condUpdateInternal():
            #      print("CCCR "+ str(t))                  
            if self.condUpdateInternal() and self.objProblem.op.isBetter([tmpState , self.agents[t ].stats.solutions[f] ]):
                     print("Changed "+ str(t)+ " --> "+ str(t)) 
                     #  self.agents[na - t - 1].objMetaheuristic.status.stateFinal = copy.deepcopy(self.agents[na - t - 2].stats.solutions[f]) 
                     self.agents[t].replacement(tmpState)
                   #  print("..."+t) 
      
  

    def random(self, f) :
        nexchanges = self.parameters.get('numberAgents') 

        for t in range(nexchanges):   
            #  agents.get(t).internalState.printStateOf(""+t) 
            # if self.condUpdateInternal():
            #      print("CCCR "+ str(t))   
            a1 = np.random.randint(self.parameters.get('numberAgents'))
            a2 = np.random.randint(self.parameters.get('numberAgents'))  
            while  a2 == a1:   
                a2 = np.random.randint(self.parameters.get('numberAgents'))     
    
            #  tmpState.printStateOf(""+(self.parameters.get('numberAgents')-1)) 
            if self.condUpdateInternal() and self.objProblem.op.isBetter([self.agents[a1].stats.solutions[f], self.agents[a2].stats.solutions[f] ]):
                print("Changed "+ str(a1)+ " --> "+ str(a2)) 
                self.agents[a2].replacement(self.agents[a1].stats.solutions[f])
                                
                
                
    def ringe(self, init) :

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
  

# =============================================================================
#  def random(self,  _init) :
# 
#   if (self.parameters.get('numberAgents') != self.parameters.get('listMethods').size()) :
#    print("Error! #agents != #methods") 
#    return 
#    
# 
#   int _evals = 0 
# 
#   #  if (self.parameters.get('numberCycles') < 4) self.parameters.get('numberCycles') = 4 
#   _evals = 1 + (int) (self.objProblem.timeLimit / (double) (self.parameters.get('numberAgents') * self.parameters.get('numberCycles'))) 
#   print("EVALUATIONS " + _evals) 
# 
#   #  Define the temporally state
# #   StateOf tmpState 
# 
#   #  Init the agents
#   for (int t = 0  t < self.parameters.get('numberAgents')  t++) :
#    agents.add(new Agent(self.objProblem, self.parameters.get('configFiles')
#      .get(t), _init)) 
#    #  AgentToSP agentX = new AgentToSP(self.incident, self.magazine,
#    #  self.time, self.parameters.get('configFiles').get(t),
#    #  self.parameters.get('listMethods').get(t), false) 
#    #  agents.add(agentX) 
#    
# 
#   int f = 0 
# 
#   while (f < self.parameters.get('numberCycles')) :
#    print("CYCLE " + (f + 1)) 
#    for (int t = 0  t < self.parameters.get('numberAgents')  t++) :
#     agents.get(t).init(_evals) 
#     
# 
#    for (int t = 0  t < self.parameters.get('numberAgents') - 1  t++) :
#     int u1 = self.random.nextInt(self.parameters.get('numberAgents')) 
#     int u2 = self.random.nextInt(self.parameters.get('numberAgents')) 
#     if (condUpdateInternal()
#       and agents.get(u2).internalState.best(agents
#         .get(u1).internalState)) :
#      agents.get(u1).setInternalState(
#        agents.get(u2).internalState) 
#      
#     
# 
#    f++ 
#    for (int t = 0  t < self.parameters.get('numberAgents')  t++) :
#     agents.get(t).internalState.printStateOf("" + t) 
#     
#    
#   self.calcBetter() 
# =============================================================================
  

# =============================================================================
#  public void ringSDI(self,  _init) :
# 
#   #  define flag to end cycle
#   #  boolean control = true 
#   int _evals = 0 
# 
#   _evals = 1 + (int) (self.objProblem.timeLimit / (self.parameters.get('numberAgents') * self.parameters.get('numberCycles'))) 
#   print("EVALUATIONS " + _evals) 
# 
#   #  Define the temporally state
#   StateOf tmpState 
# 
#   #  Init the agents
#   #  Revisar
#   agents.add(new Agent(self.objProblem, "HCSDI", _init)) 
#   agents.add(new Agent(self.objProblem, "GASDI", _init)) 
#   agents.add(new Agent(self.objProblem, "KOSDI", _init)) 
# 
#   int f = 0 
#   while (f < self.parameters.get('numberCycles')) :
#    #  print("CYCLE "+(f+1)) 
#    int _evaltmp = _evals 
#    for (int t = 0  t < self.parameters.get('numberAgents')  t++) :
#     print("CYCLE " + (f + 1) + " - " + t + ":::"
#       + agents.get(t).internalState.getFitnessOne()) 
#     print("CYCLE " + (f + 1) + " - " + (t + 1)) 
#     if (t == 0)
#      _evaltmp = (int) (_evals * 1.0) 
#     if (t == 1)
#      _evaltmp = (int) (_evals * 1.5) 
#     if (t == 2)
#      _evaltmp = (int) (_evals * 0.5) 
#     #  agents.get(t).initializeII(_evaltmp, t) 
#     agents.get(t).init(_evaltmp) 
#     
# 
#    tmpState = (StateOf) (self.agents.get(2).internalState).clone() 
# 
#    for (int t = 0  t < self.parameters.get('numberAgents') - 1  t++) :
#     #  self.agents.get(t).internalState.printStateOf(""+t) 
#     if (condUpdateInternal()
#       and self.agents.get(self.parameters.get('numberAgents') - t - 2).internalState
#         .best(self.agents.get(self.parameters.get('numberAgents') - t
#           - 1).internalState)) :
#      self.agents.get(self.parameters.get('numberAgents') - t - 1)
#        .setInternalState(
#          self.agents.get(self.parameters.get('numberAgents') - t - 2).internalState) 
#      #  print("..."+t) 
#      
#     
#    #  tmpState.printStateOf(""+(self.parameters.get('numberAgents')-1)) 
#    if (condUpdateInternal()
#      and tmpState.best(self.agents.get(0).internalState)) :
#     self.agents.get(0).setInternalState(tmpState) 
#     
#    f++ 
# 
#    for (int t = 0  t < self.parameters.get('numberAgents')  t++) :
#     self.agents.get(t).internalState.printStateOf("" + t) 
#     
#    
#   self.calcBetter() 
#   
# =============================================================================

# =============================================================================
#     def ring(self, init, _problem, _evaluations) :
# 
#         _evals = 0 
# 
#         #  Define the temporally state
#         #  tmpState 
# 
#         #  if (self.parameters.get('numberCycles') < 4) self.parameters.get('numberCycles') = 4 
#         _evals = 1 + (int) (_evaluations / (self.parameters.get('numberAgents') * self.parameters.get('numberCycles'))) 
#         print("EVALUATIONS " + _evals) 
# 
#         for t in range(self.parameters.get('numberAgents') - 1):
#             if self.objProblem.op.isBetter([init, self.agents.get(t).internalState]):  
#                 #  self.popul = copy.deepcopy(popTemp)
#                 self.agents.get(t).setInternalState(init) 
# 
#         f = 0 
# 
#         while (f < self.parameters.get('numberCycles')) :
# 
#             print("CYCLE " + (f + 1)) 
#             for t in range(self.parameters.get('numberAgents')): 
#                 self.agents.get(t).init(_evals) 
#     
# 
#             tmpState = self.agents.get(self.parameters.get('numberAgents') - 1).internalState 
# 
#             for t in range(self.parameters.get('numberAgents') - 1):
#                 #  self.agents.get(t).internalState.printStateOf(""+t) 
#                 if (self.condUpdateInternal()and self.agents.get(self.parameters.get('numberAgents') - t - 2).internalState.best(self.agents.get(self.parameters.get('numberAgents') - t  - 1).internalState)) :
#                     self.agents.get(self.parameters.get('numberAgents') - t - 1).setInternalState( self.agents.get(self.parameters.get('numberAgents') - t - 2).internalState) 
#      #  print("..."+t) 
#      
#     
#             #  tmpState.printStateOf(""+(self.parameters.get('numberAgents')-1)) 
#             if (self.condUpdateInternal() and tmpState.best(self.agents.get(0).internalState)) :
#                 self.agents.get(0).setInternalState(tmpState) 
#     
#             f = f + 1
# 
#             for t in range(self.parameters.get('numberAgents')): 
#                 self.agents.get(t).internalState.printStateOf("" + t) 
#     
#    
#         self.calcBetterCoop() 
#         return self.stateFinal 
# =============================================================================
  

# def random(self,  _init, Problem _problem, int _evaluations) :
#
#  int _evals = 0 
#
#  #  if (self.parameters.get('numberCycles') < 4) self.parameters.get('numberCycles') = 4 
#  _evals = 1 + (int) (_evaluations / (double) (self.parameters.get('numberAgents') * self.parameters.get('numberCycles'))) 
#  print("EVALUATIONS " + _evals) 
#
#  #  Define the temporally state
##   StateOf tmpState 
#
#  for (int t = 0  t < self.parameters.get('numberAgents') - 1  t++) :
#   if (_init.best(self.agents.get(t).internalState)) :
#    self.agents.get(t).setInternalState((StateOf) _init.clone()) 
#    
#   
#
#  int f = 0 
#
#  while (f < self.parameters.get('numberCycles')) :
#   print("CYCLE " + (f + 1)) 
#   for (int t = 0  t < self.parameters.get('numberAgents')  t++) :
#    self.agents.get(t).init(_evals) 
#    
#
#   for (int t = 0  t < self.parameters.get('numberAgents') - 1  t++) :
#    int u1 = self.random.nextInt(self.parameters.get('numberAgents')) 
#    int u2 = self.random.nextInt(self.parameters.get('numberAgents')) 
#    if (condUpdateInternal()
#      and self.agents.get(u2).internalState.best(agents
#        .get(u1).internalState)) :
#     self.agents.get(u1).setInternalState(
#       self.agents.get(u2).internalState) 
#     
#    
#
#   f++ 
#   for (int t = 0  t < self.parameters.get('numberAgents')  t++) :
#    self.agents.get(t).internalState.printStateOf("" + t) 
#    
#   
#  self.calcBetterCoop() 
#  return self.stateFinal 
#  

# def broadcast(self,  _init, Problem _problem, int _evaluations) :
#
#  #  define flag to end cycle
#  int _evals = 0 
#  #  print("EVALUATIONS "+self.objProblem.evaluationCounter) 
#  #  if (self.parameters.get('numberCycles') < 4) self.parameters.get('numberCycles') = 4 
#  _evals = 1 + (int) (_evaluations / (self.parameters.get('numberAgents') * self.parameters.get('numberCycles'))) 
#  print("EVALUATIONS " + _evals) 
#
#  #  Define the temporally state
#  StateOf tmpState 
#
#  for (int t = 0  t < self.parameters.get('numberAgents') - 1  t++) :
#   if (_init.best(self.agents.get(t).internalState)) :
#    self.agents.get(t).setInternalState((StateOf) _init.clone())  
#   
#
#  print("LOADED AGENTS ") 
#  int f = 0 
#  while (f < self.parameters.get('numberCycles')) :
#   print("CYCLE " + (f + 1)) 
#   for (int t = 0  t < self.parameters.get('numberAgents')  t++) :
#    self.agents.get(t).init(_evals) 
#    
#
#   tmpState = (StateOf) self.agents.get(0).internalState.clone() 
#
#   for (int t = 1  t < self.parameters.get('numberAgents')  t++) :
#    if (tmpState.getFitnessOne() > self.agents.get(t).internalState
#      .getFitnessOne())
#     tmpState = (StateOf) self.agents.get(t).internalState
#       .clone() 
#    
#
#   for (int t = 0  t < self.parameters.get('numberAgents')  t++) :
#    #  print("..1 ") 
#    if (condUpdateInternal()
#      and tmpState.best(self.agents.get(t).internalState)) :
#     #  print("..2 ") 
#     self.agents.get(t).setInternalState(tmpState)  #  getInternalState
#     #  print(self.agents.get(t).getInternalState().prints()) 
#     
#    
#
#   f++ 
#
#   for (int t = 0  t < self.parameters.get('numberAgents')  t++) :
#    self.agents.get(t).internalState.printStateOf("" + t) 
#    
#   
#  self.calcBetterCoop() 
#  return self.stateFinal 
  

# =============================================================================
#  def ringSDI(self,  _init, Problem _problem, int _evaluations) :
# 
#   #  define flag to end cycle
#   #  boolean control = true 
#   int _evals = 0 
# 
#   _evals = 1 + (int) (_evaluations / (self.parameters.get('numberAgents') * self.parameters.get('numberCycles'))) 
#   print("EVALUATIONS " + _evals) 
# 
#   #  Define the temporally state
#   StateOf tmpState 
# 
#   int f = 0 
# 
#   for (int t = 0  t < self.parameters.get('numberAgents') - 1  t++) :
#    if (_init.best(self.agents.get(t).internalState)) :
#     self.agents.get(t).setInternalState((StateOf) _init.clone()) 
#     
#    
# 
#   while (f < self.parameters.get('numberCycles')) :
#    #  print("CYCLE "+(f+1)) 
#    int _evaltmp = _evals 
#    for (int t = 0  t < self.parameters.get('numberAgents')  t++) :
#     print("CYCLE " + (f + 1) + " - " + t + ":::"
#       + self.agents.get(t).internalState.getFitnessOne()) 
#     print("CYCLE " + (f + 1) + " - " + (t + 1)) 
#     if (t == 0)
#      _evaltmp = (int) (_evals * 1.0) 
#     if (t == 1)
#      _evaltmp = (int) (_evals * 1.5) 
#     if (t == 2)
#      _evaltmp = (int) (_evals * 0.5) 
#     #  self.agents.get(t).initializeII(_evaltmp, t) 
#     self.agents.get(t).init(_evaltmp) 
#     
# 
#    tmpState = (StateOf) (self.agents.get(2).internalState).clone() 
# 
#    for (int t = 0  t < self.parameters.get('numberAgents') - 1  t++) :
#     #  self.agents.get(t).internalState.printStateOf(""+t) 
#     if (condUpdateInternal()
#       and self.agents.get(self.parameters.get('numberAgents') - t - 2).internalState
#         .best(self.agents.get(self.parameters.get('numberAgents') - t
#           - 1).internalState)) :
#      self.agents.get(self.parameters.get('numberAgents') - t - 1)
#        .setInternalState(
#          self.agents.get(self.parameters.get('numberAgents') - t - 2).internalState) 
#      #  print("..."+t) 
#      
#     
#    #  tmpState.printStateOf(""+(self.parameters.get('numberAgents')-1)) 
#    if (condUpdateInternal()
#      and tmpState.best(self.agents.get(0).internalState)) :
#     self.agents.get(0).setInternalState(tmpState) 
#     
#    f++ 
# 
#    for (int t = 0  t < self.parameters.get('numberAgents')  t++) :
#     self.agents.get(t).internalState.printStateOf("" + t) 
#     
#    
#   self.calcBetterCoop() 
# 
#   return self.stateFinal 
# =============================================================================
  

    def compareStateOf(self, maria) :
        maria.printStateOf("INIT") 
        self.stateFinal.printStateOf("STAF") 

        if self.objProblem.op.isBetter([self.stateFinal, maria]): 
            return self.stateFinal 
        else :
            return maria  
  

    def calcBetter(self  ) :
        
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
        self.stateFinal = self.compareStateOf( self.agents[0].stats.solutions[0]) 

        for t in range(1, self.parameters.get('numberAgents') ): 
            if self.objProblem.op.isBetter([self.agents[t].stats.solutions[0], self.agents[t - 1].stats.solutions[0]]): 
                
                self.stateFinal = self.compareStateOf( self.agents[t].stats.solutions[0]) 
   #  self.internalState.copy(self.agents.get(t).getInternalState()) 
   #  # getInternalState
   
  

    def condUpdateInternal(self ) :
        return (np.random.rand() < self.parameters.get('probComm')) 
  

    def printsParameters(self ) :
        print("---->" + self.architecture) 
        print("---->" + self.objProblem.timeLimit) 
        print("NA:::" + self.parameters.get('numberAgents')) 
        print("NC:::" + self.parameters.get('numberCycles')) 
        print("PC:::" + self.parameters.get('probComm')) 
        print("MT:::" + self.parameters.get('listMethods')) 
        print("CF:::" + self.parameters.get('configFiles')) 
        print("TI:::" + self.typeInitialSolution) 
  

    def selectCP(self, _init, _problem,  _evals) :
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
   

  
 
