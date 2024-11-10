from problem.Problem import *
## from util.MatrixI import *
## from state.Solution import *

import numpy as np 

class UniversityCourseTimetablingProblem (Problem):

	""" 
	Define the University Course Timetabling problem   
	:version:
	:author: Jhon Amaya
	"""

	def __init__(self, namInst=None):
		""" 
		@param String namInst : 
		@return  :
		@author
		"""
		super().__init__()
		self.nameShort = "UCTP"   
		# print(self.typeState)
		self.selOpers()
        
        # Utilizamos esta variable auxiliar para indicar Qué es la 
        # permutación tiene números repetidos
		self.typeVarMix = "INTEGER"
		# print(type(self.op))
		if (not namInst == None): 
			self.readInstance(namInst) 
            
	""" 	  
	Se define la solución como un vector cuya cuyo tamaño es el número 
    de aulas por los periodos disponibles .s utilizamos el cero para 
    indicar el aula vacía y los números para indicar las materias que 
    se tienen en cada aula. Se convierte en un problema permutacional.
	""" 
	def readInstance(self, namFile):
		""" 
		@param String namFile : 
		@return  :
		@ 
		""" 

		self.icourses = [] 
		self.irooms = [] 
		self.icurricula = [] 
		self.iunavailability = [] 
		self.iroomconstraints = []     
        
		self.rooms = 0
		self.days = 0
		self.periods = 0    
		self.courses = 0   
        
		with open('./DATA/instances/UCTP/'+namFile, 'r') as fileobj:
		    content = fileobj.read()
		    lines = content.split('\n')   
        
		# Each cycle is a instance
		cntr = '' 
        
		for j in range(len(lines)): 
			# auxili = lines[j]
			r = lines[j].split()        
			# 
            
          
			if (len(r) != 0):     
				#print('------', len(r), r)
				if (cntr == '' ): 
					if (r[0]=='Courses:'):
						self.courses = int(r[1])
						print(self.courses) 
					elif (r[0]=='Rooms:'):
						self.rooms = int(r[1])
						print(self.rooms)       
					elif (r[0]=='Days:'):
						self.days = int(r[1])
						print(self.days) 
					elif (r[0]=='Periods_per_day:'):
						self.periods = int(r[1])
						print(self.periods) 
					elif (r[0]=='Curricula:'):
						self.curricula = int(r[1])
						print(self.curricula) 
					elif (r[0]=='Min_Max_Daily_Lectures:'):
						self.minmaxdaylect = r[1:len(r)]
						print(self.minmaxdaylect ) 
					elif (r[0]=='UnavailabilityConstraints:'):
						self.unavailability = int(r[1])
						print(self.unavailability)       
					elif (r[0]=='RoomConstraints:'):
						self.roomconstraints = int(r[1])
						print(self.roomconstraints)  
					elif (r[0]=='COURSES:'):
						cntr = 'COURSES'
						print(cntr ) 
					elif (r[0]=='ROOMS:'):
						cntr = 'ROOMS'
						print(cntr ) 
					elif (r[0]=='CURRICULA:'):
						cntr = 'CURRICULA'
						print(cntr ) 
					elif (r[0]=='UNAVAILABILITY_CONSTRAINTS:'):
						cntr = 'UNAVAILABILITY_CONSTRAINT'
						print(cntr ) 
					elif (r[0]=='ROOM_CONSTRAINTS:'):
						cntr = 'ROOM_CONSTRAINTS'
						print(cntr ) 
                        

				elif (r[0]=='COURSES:'):
					cntr = 'COURSES'
					print(cntr ) 
				elif (r[0]=='ROOMS:'):
					cntr = 'ROOMS'
					print(cntr ) 
				elif (r[0]=='CURRICULA:'):
					cntr = 'CURRICULA'
					print(cntr ) 
				elif (r[0]=='UNAVAILABILITY_CONSTRAINTS:'):
					cntr = 'UNAVAILABILITY_CONSTRAINT'
					print(cntr ) 
				elif (r[0]=='ROOM_CONSTRAINTS:'):
					cntr = 'ROOM_CONSTRAINTS'
					print(cntr ) 
                    
				elif (cntr == 'COURSES' ):                
					self.icourses.append(r) 
					print(self.icourses) 
                
				elif (cntr == 'ROOMS' ):                
					self.irooms.append(r)  
					print(self.irooms)               
                 
				elif (cntr == 'CURRICULA' ):                
					self.icurricula.append(r) 
					print(self.icurricula)                
       
				elif (cntr == 'UNAVAILABILITY_CONSTRAINT'):                
					self.iunavailability.append(r) 
					print(self.iunavailability) 
                
				elif (cntr == 'ROOM_CONSTRAINTS'):                
					self.iroomconstraints.append(r)  
					print(self.iroomconstraints)                   
                    

		self.naLect=[] 
		self.naCour=[]
		for i in range(self.courses):
			if ( not self.icourses[i][1] in self.naLect):
				#  Verificar que no se repitan los profesores               
				self.naLect.append(self.icourses[i][1])
			if ( not self.icourses[i][0] in self.naCour):
				self.naCour.append(self.icourses[i][0])                
                

		self.nVar = self.rooms * self.days * self.periods  
		print(self.nVar)     
        
		self.perm = []
		for j in range(len(self.icourses)):         
			for i in range(int(self.icourses[j][2])): 
				self.perm.append(j+1)        
		if len(self.perm) < self.nVar:
			for i in range(self.nVar-len(self.perm)): 
				self.perm.append(0)     
                
                
		# self.perm = [4, 0, 0, 0, 2, 3, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 3, 4, 0, 4, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 3, 0, 0, 0, 0, 0, 2, 2, 0, 0, 0, 0, 0,  0, 0, 1, 0, 3, 0, 4, 0, 0, 4, 0, 3]        
		
		# print(len(self.perm))
		print(self.perm)        
        

	def evaluate(self, s, printing=""):
		"""  
		@param state.Solution s : 
		@return  :
		@author
		""" 
		count = 0  
		# PrintViolationsOnLectures(os);
		# PrintViolationsOnConflicts(os);
		# PrintViolationsOnAvailability(os);
		# PrintViolationsOnRoomOccupation(os);
		# PrintViolationsOnRoomCapacity(os);
		# PrintViolationsOnMinWorkingDays(os);
		# PrintViolationsOnIsolatedLectures(os);
        
		# "Violations of Lectures (hard) : " <<  CostsOnLectures() << std::endl;
		onLectures= 0 
        
        # 2 conferencistas no pueden tener clases al mismo tiempo
		for i in range(len(self.naLect)):
			tt=[]
			ss=[]
			for j in range(self.nVar):
				if (s.vars[j] !=0):
					if (self.icourses[s.vars[j] -1][1]==self.naLect[i]):
						dd=j//(self.periods*self.rooms)
						pp=j%self.periods
						tt.append(dd)
						ss.append(pp)
			# print(tt)
			# print(ss)                        
			for j in range(len(tt)-1):
				for k in range(j+1,len(tt)) : 
					if tt[j] == tt[k]:
						if ss[j]== ss[k]:
							# print(tt[j],tt[k],ss[j],ss[k])                            
							onLectures= onLectures+1 


		# "Violations of Conflicts (hard) : " <<  CostsOnConflicts() << std::endl;
		onConflicts= 0 
		# se verifica que no haya conflictos con el currículum
        
		pr=self.periods*self.rooms 
		# print(self.naLect) 
		for j in range(self.curricula):
			tmp=self.icurricula[j]
			icc=[]
			for i in range(int(tmp[1])):
				icc.append( self.naCour.index(tmp[2+i]) + 1)             
			# print(icc)              
			dd=self.nVar//pr
			for i in range(dd):          
				for k in range(self.periods) :   
					per=[]                    
					for l in range(self.rooms) :  
						idd = s.vars[i*self.days+(self.periods*l+k)]                     
						if idd!=0 and not idd in per and idd in icc:
							per.append(idd)  
					# print(i, k, per)                             
					if len(per)>1:
						onConflicts=	 onConflicts+1 



		# "Violations of Availability (hard) : " <<  CostsOnAvailability() << std::endl;
		onAvailability = 0
		# Se verifica si se viola las restricciones de indisponibilidad        
		for j in range(self.nVar):
			if (s.vars[j] !=0): 
				dd=j // (self.periods*self.rooms)
				pp=j % self.periods  
				cc=s.vars[j] - 1
				for i in range(self.unavailability): 
					# print(cc,dd,pp)                     
					vv=self.naCour.index(self.iunavailability[i][0])
					# print(vv,self.iunavailability[i][0])                    
					if cc==vv:                    
						if self.iunavailability[i][1]==dd:
							if self.iunavailability[i][2]==pp:
								# print("BBBB")                                                                
								# print(vv,self.iunavailability[i][1],self.iunavailability[i][2])                                
								onAvailability = onAvailability + 1                     
				# print()   				 

 
# =============================================================================
#   for (c = 0; c < in.Courses(); c++)
#     for (p = 0; p < in.Periods(); p++)
#       if (out(c,p) != 0 && !in.Available(c,p))
# 	onAvailability = onAvailability + 1
# =============================================================================
 

            

		# "Violations of RoomOccupation (hard) : " <<  CostsOnRoomOccupation() << std::endl;
		onRoomOccupation= 0 
# =============================================================================
#   for (p = 0; p < in.Periods(); p++)
#     for (r = 1; r <= in.Rooms(); r++)
#       if (out.RoomLectures(r,p) > 1)
# 	onRoomOccupation = onRoomOccupation +   out.RoomLectures(r,p) - 1;         
# =============================================================================
        
		for i in range(self.nVar):
			if (s.vars[i] !=0):  
				tmp = self.naCour[s.vars[i]-1]
				for j in range(len(self.iroomconstraints)):
					if (self.iroomconstraints[j][0]==tmp):   
						tmp = j // self.periods
						room = tmp % self.rooms  
						for x in range(len(self.irooms)):
							if (self.irooms[x][0]==self.iroomconstraints[j][1]):                         
								onRoomOccupation= onRoomOccupation+1

		# "Cost of RoomCapacity (soft) : " <<  CostsOnRoomCapacity() << std::endl;
		# se verifica que la capacidad de las aulas debe ser mayor que 
		# el número de estudiantes ofertados por asignatura
		onRoomCapacity= 0
        
		for i in range(self.nVar):
			if (s.vars[i] !=0): 
				pp=i//self.periods
				pp=pp%self.rooms   
				# print(i,s.vars[i],self.icourses[s.vars[i] -1][4],self.irooms[pp][1])                
				tmp = int(self.icourses[s.vars[i] -1][4]) - int(self.irooms[pp][1])
				if tmp > 0:
					onRoomCapacity = onRoomCapacity + (tmp) 
		# print()        

        

		# "Cost of MinWorkingDays (soft) : " <<  CostsOnMinWorkingDays() * MIN_WORKING_DAYS_COST << std::endl;
		# Verifica que  que el curso no se imparte en una cantidad de 
        # días menor a lo especificado en el curso
		onMinWorkingDays= 0
        
		for i in range(self.courses):  
			tt = []
			for j in range(self.nVar):         
				if s.vars[j] == i+1:   
					tmp = j // (self.periods*self.rooms)		 
					if not tmp in tt:
						tt.append(tmp)
			# print(tt,  self.icourses[i][3])                         
			st = len(tt) - int(self.icourses[i][3])         
			if st < 0:                         
				onMinWorkingDays = onMinWorkingDays - st      



		# "Cost of IsolatedLectures (soft) : " <<  CostsOnIsolatedLectures() * ISOLATED_LECTURES_COST << std::endl;
		onIsolatedLectures= 0
        

		for i in range(self.nVar):    
            
			rc = i // self.periods
			dc = i % self.periods
			b = False
            
			if (s.vars[i] !=0): 
				if dc == 0: 
					if  s.vars[i+1]==0 :
						b = True
				elif dc ==self.periods-1:  
					if s.vars[i-1]==0:
						b = True                
				else:     
					if s.vars[i-1]==0 and s.vars[i+1]==0:
						b = True                  
                 
				if b ==True: 
					onIsolatedLectures= onIsolatedLectures+1




		# "Cost of RoomStability (soft) : " <<  CostsOnRoomStability() * ROOM_STABILITY_COST << std::endl;
		# Verifica si una asignatura siempre está en el mismo salón si no es 
		# así suma 1 por cada aula diferente
		onRoomStability = 0  
        
		for i in range(self.courses):  
			tt = []
			for j in range(self.nVar):         
				if s.vars[j] == i+1:   
					tmp = j // self.periods
					room = tmp % self.rooms + 1

					if not room in tt:
						tt.append(room)
			onRoomStability = onRoomStability + (len(tt) - 1)           
			# print(tt)
		# print( )                    
                 
        
        
		# soft      
		count = onRoomStability +  onIsolatedLectures +  onMinWorkingDays +  onRoomOccupation 
		# print(onRoomStability, onIsolatedLectures, onMinWorkingDays, onRoomCapacity)  		
        # hard      
		count = count + 10000*( onRoomCapacity +  onAvailability +  onConflicts +  onLectures )
		# print(onRoomOccupation, onAvailability, onConflicts, onLectures)   
		
		s.setFitness(count)
        
		if printing != "":
			print("s", "onRoomOccupation", onRoomOccupation) 
			print("h", "onAvailability", onAvailability)  
			print("h", "onConflicts", onConflicts)     
			print("h", "onLectures", onLectures)  	
			print()             
            
			print("s", "onRoomStability", onRoomStability) 
			print("s", "onIsolatedLectures", onIsolatedLectures)  
			print("s", "onMinWorkingDays", onMinWorkingDays)     
			print("h", "onRoomCapacity", onRoomCapacity)  
			print("Fitness", count)   	
			print()             
			for i in range(self.nVar):     
				if (s.vars[i] !=0):      
					day = (i  //  (self.periods*self.rooms))
					periods = i % self.periods
					room = ((i // self.periods) % self.rooms)
					print("day", day+1, "room", self.irooms[room][0], "periods", periods+1, self.icourses[s.vars[i] -1][0], int(self.icourses[s.vars[i] -1][4]), self.irooms[room][1])          
                    
			# for i in range(self.courses):  
                
   