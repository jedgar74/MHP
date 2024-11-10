#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jun 15 11:52:26 2020

@author: tauger
"""
from problem.Problem import *
from agent.Agent import *
import numpy as np

class MultiInAgent():

    """ 
    Define the classic problem termed MoMO problems
    :version:
    :author: Jhon Amaya
    """


    def __init__(self, problem, instances, nEvalsXInst, methods, configFiles, nExperiments):
        """ 
        @return  :
        @author
        """
        self.problem = problem  
        self.instances = instances  
        self.nEvalsXInst = nEvalsXInst
        self.methods = methods
        self.configFiles = configFiles 
        self.nExperiments = nExperiments       
        
        self.nameParameters = [ ] 
        self.nameinstances = [ ]
	# def __init__(self, nVar):
	# 	"""  
	# 	@param int nVar : 
	# 	@return  :
	# 	@author
	# 	"""
	# 	super().__init__()
	# 	self.nameShort = "LV"  
	# 	self.nVar =  nVar 
    
    def printer(self) :    
        i = 1
        ranges = [ ]
        ins = self.nameinstances[0]

        ranges.append( 0)
    
        while (i < len(self.nameinstances)):
            if ( ins != self.nameinstances[i] ):
                ranges.append( i)
                ins = self.nameinstances[i]
			
            i  =  i + 1  
		 
        for rd in range(len(ranges)):  
            ini = ranges[rd] 
            fin = 0
            if (rd < len(ranges) - 1):
                fin = ranges[rd+1] 
            else :
                fin = len(self.nameParameters)  
			 
            print("\n:: Instance :: " + str(self.nameinstances[ini]))
            tmp =  len(self.nameParameters[ini].solutions)
            print(":: N. Experiment.:: " + str(tmp)) 
            print("-----------------------------------") 
            print('{: <24s}'.format(""), end="")
            print('{: <9s}'.format("Better"), end="")
            print('{: <9s}'.format("N.Bet."), end="")
            print('{: <9s}'.format('Mean'), end="")
            print('{: <9s}'.format("S.D."))
            print("-----------------------------------") 
 
            for r in range(ini, fin):
                print('{: <24s}'.format(self.nameParameters[r].getLabel()), end="")  
                print('{: <9.4f}'.format(round(self.nameParameters[r].getBetter(), 4 )), end="") 
                print('{: <9d}'.format(self.nameParameters[r].getNBetter() ), end="")
                ave = self.nameParameters[r].average()
                print('{: <9.4f}'.format(round(ave, 4 )), end="")
                print('{: <9.4f}'.format(round(self.nameParameters[r].stDeviat(ave), 4 )))
 
    
    def getMatrix(self) : 
        labels  = [ ]
        for r in range(len(self.nameParameters) ):  
            s = self.nameParameters[r].getLabel()
            v = s.index("[")
            r = s[0:v] 
            if (not r in labels):
                labels.append(r)     
            
        i = 1
        ranges  = [ ]
        ins = self.instances[0] 
        ranges.append( 0) 
    
        while (i < len(self.instances)):
            if ( ins != self.instances[i] ):
                ranges.append(i)
                ins = self.instances[i]
			
            i  =  i + 1  
    
        val = len(self.nameParameters)//len(ranges) 
    
        valuesx = np.zeros( (len(ranges), len(self.nameParameters)//len(ranges)) ) 
 
        for rd in range(len(ranges)):  
            # print(ranges[rd])	 
            ini = ranges[rd] * val 
            fin = ini + val -1

            for r in range(ini, fin+1):
                # print(str(rd)+"  "+str(r)+"  "+str(ini)+"  "+str(fin))
                valuesx[rd][r-ini] =  round(self.nameParameters[r].average(), 4 )  

    
        return labels, valuesx
 
    
    def init(self) :     
        for j in range(len(self.instances)):  
            # problemv = NQueens(self.instances[j])
            self.problem.readInstance(self.instances[j])
            print("\n--------instance------ "+ str(self.instances[j]) ) 
            for i in range(len(self.methods)):    
            	print("\n---------------------- "+self.methods[i]+ " --- "+self.configFiles[i])
            	agentx = Agent(self.problem, [self.methods[i], self.configFiles[i], self.nEvalsXInst[j], self.nExperiments])
            	agentx.init() 
	    
        		# if (allSolution): 
        		# 	agent.info.printAllSolution()
        
            	self.nameParameters.append(agentx.stats) 
            	self.nameinstances.append(self.instances[j])  