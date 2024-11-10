# coding=UTF-8
from problem.Problem import *
from problem.Internal import *
# from state.Operators import *

import json

class Heuristic(object):

	"""
	:version:
	:author:
	"""

	""" ATTRIBUTES

	shortTerm  (public)

	status  (public)

	objProblem  (public)

	op  (public)

	version of algorithm

	version  (implementation)

	   controlled to changes

	  changeOn  (implementation)

	   

	  nameParameters  (implementation)

	   

	  valueParameters  (implementation)

	  """
	  
	def __init__(self):  
		""" 
		@return:
		@author
		"""
		self.status = Internal();
		self.shortTerm = None
		self.objProblem = None
		self.parameters = None 
		
		
	def isStopCriteria (self):
		"""  
		@return boolean :
		@author
		"""
		if (self.objProblem.counter.getCount() <= self.objProblem.counter.getLimit()):
			return True  
		else :
			return False 


	def isStopCriteria2 (self, cycles):
		""" 
		@param long cycles :  
		@return boolean :
		@author
		"""
		if (self.objProblem.counter.getCount() <=  cycles):
			return True 
		else :
			return False


	def getMethods(self, _info):
		""" 
		@param String _info : 
		@return ArrayList<String> :
		@author
		"""
		pass


	def readParameters(self, nameFile, metaH):
		""" 
		@param String nameFile : 
		@param StrJing metaH : 
		@return  :
		@author
		""" 
		
		with open('./DATA/config/'+metaH+'/'+nameFile+'.json') as file:
			data = json.load(file)
		 
		return  data 	 
	 

	def processingParameter(self, _lineParameter):
		"""
		 

		@param String _lineParameter : 
		@return  :
		@author
		"""
		pass

	def readParameters2(self, nameFile):
		"""
		 

		@param String nameFile : 
		@return  :
		@author
		"""
		pass

	def processingParameter2(self, _lineParameter):
		"""
		 

		@param String _lineParameter : 
		@return  :
		@author
		"""
		pass

	def printsParameters(self):
		"""
		 

		@return  :
		@author
		"""
		pass



