from controller import make_controller
import time
import numpy as np
import config
from arc1pyqt import state
#from TestModule import
#Wafer map
#config.x=np.array([5,9,11,13,13,15,15,15,15,15,15,13,13,11,9,5]) #number of dice on each row (at least 1 element)
#config.w=np.array([0,2,3,4,4,5,5,5,5,5,5,4,4,3,2,0]) #row offset relative to row 0

#Defined read dice
#config.col=np.array([2,4])#desired die x-coordinate  (starts from column 0)
#config.row=np.array([1,2])#desired die y-coordinate (starts from row 0)

#defined read subdice
#col_sub=np.array([0]) #column values for the desired subdice cooridinates
#row_sub=np.array([0]) #row values for the desired subdice cooridinates

#Input values
#config.sleep_time=0.5 		#time for reading values
#config.time_separation=0.5 #time for doing the separation or contact move
#config.time_move_slow=4 	#time for moving in x-y direction (slower)
#time_move_medium=2  #time for moving in x-y direction (medium)
#config.time_move_fast=1    #time for moving in x-y direction (fast)
#config.read_time=0 		#time for reading data

#config.z_velocity=100 #velocity of the chuck moving in the Z direction in %
#config.xy_velocity=100 #velocity of the chuck moving in the XY direction in %


#config.skip_odd=1 # 1-don't skip, 2-skip one column (in case there are CB and SA dice)
#config.index_x=9000 #die x-axis index
#config.index_y=9000 #die y-axis index
#config.subindex_x=3000 #subdie x-axis index
#config.subindex_y=3000 #subdie y-axis index

#Contact, Alginment, Separation
#always negative values
#config.contact_val=746
#alignment_val=200
#config.separation_val=500

class ProbeStation():
    
    # Arguments here are as follows
    # addr: GPIB address (typically 22)
    # cntrl: Controller type. This is one value of the enumerate
    #        CNTRL_TYPE defined in controller.pythonic
    # cntrl_args: array of arguments to pass to the controller
    # cntrl_kwargs: keyword arguments to pass to the controller
    #
    # Typically for VISA no more arguments are required. For
    # prologix only ['COMXX'] is needed
    # examples
    # >>> station = ProbeStation(22, CNTRL_TYPE.VISA)
    # or
    # >>> station = ProbeStation(22, CNTRL_TYPE.PROLOGIX, ['COMXY'])
	def __init__(self, addr, cntrl, cntrl_args=[], cntrl_kwargs={}):
		self.controller = make_controller(cntrl, addr, cntrl_args, \
			cntrl_kwargs)
        
	@property
	def position(self):
		"""
		Returns the current position of the chuck checking for any errors
		This is a property so it can be called either as a function or as
		a, well..., property.
		>>> station.position()
		or
		>>> station.position
		"""
		time.sleep(config.sleep_time)
		raw = self.controller.ask('ReadChuckPosition\n').strip().decode()
        # typical response would look like
        # 0: -4771.904 11675.686 0.0
        # the first number (before the ':') indicating the status of the
        # command. When != 0 an error occurred

		(status, resp) = raw.split(':')
        
		if int(status) != 0 or resp == "None":
			raise Exception('An error has occurred', resp.strip())
        
        # remove any leading/trailing spaces
		resp = resp.strip()
        # split the numbers received by spaces present
        # and make them into floats
        # this can also be expressed in a more pythonic
        # way like so
        # >>> tuple(map(float, r.split(' ')))
        # but for clarity reasons it's kept simple
		(x, y, z) = resp.split(' ')
		(x, y, z) = (float(x), float(y), float(z))
        
		return (x, y, z)
		
    # dx and dy MUST be microns
    # you can change that by switching the Y argument
    # of the command to other values indicating mm or cm
    # check the prober manual. Last argument is tolerance
    # This is an example of an asynchronous command. As of
    # now it's blocking but it can be possibly be offloaded to
    # a background thread.
	
	def read(self): 
	#define reading time for ArC measuremetns
		#print("Subdice cols %s"%config.col_sub)
		#print("Subdice rows %s"%config.row_sub)
		print("Reading pla...")
		time.sleep(config.read_time)

	def check_move_status(self):
		#print("move status")
		while True:
			raw = self.controller.ask('$StartCommand ReadChuckStatus\n').decode().strip()
			if raw == "COMPLETE":
				break
		#print("Move finished")
		time.sleep(0.1)
		
	def check_chuck_contact(self):
		raw = self.controller.ask('ReadChuckStatus\n').decode().strip()
		result=[]
		result = raw.split(': ')
		result = result[1].split(' ')
		if result[6]=='C':
			state.Application.check_contact=1
			print("Checking...Chuck is set to Contact")
		elif result[6]=='S':
			state.Application.check_contact=0
		else:
			state.Application.check_contact=-1


	def move_relative(self, dx, dy):
	#move relatively in x-y direction in um units
		self.move_separation()
		self.controller.ask('$StartCommand MoveChuck %s %s R Y %s\n' % \
		(dx, dy, config.xy_velocity))
		self.check_move_status()
		print("Moved by %s, %s" %(dx,dy))

   
	def move_home(self, dx, dy):
	#move to wafer home position
		self.controller.ask('$StartCommand MoveChuck %s %s H Y %s\n' % \
			(dx, dy, config.xy_velocity))
		time.sleep(config.time_move_slow)
	
	def move_relative_z(self, dz):
	#move relatively in the Z direction
		self.controller.ask('$StartCommand MoveChuckZ %s R Y\n' %dz)
		time.sleep(config.sleep_time)
		self.check_move_status()
	
	def move_home_z(self, dz):
	#move to home position in Z direction
		self.controller.ask('$StartCommand MoveChuckZ %s H Y\n' %dz)
		self.check_move_status()

	def initchuck(self):
	#initialize the chuck, recommended after we turn on the probe.
	#It is automatically included in the initialization step
		self.controller.ask('$StartCommand InitChuck 7 0 0\n').decode().strip()
		self.check_move_status()

	def centering_to_zero(self):
		#centers the wafer to 0 position
		raw = self.controller.ask('ReadChuckPosition\n').strip().decode()
		(status, resp) = raw.split(':')
		print (resp)
		(a, x, y, z) = resp.split(' ')
		(x, y, z) = (-float(x), -float(y), -float(z))
        
		self.controller.ask('$StartCommand MoveChuck %s %s R Y \n' % \
			(x, y))
		self.check_move_status()

	def set_chuck_heights(self, type, value):
	#loads the alignment, separation and contact distances
		self.controller.ask('SetChuckHeight %s V Y %s\n' %(type, value))
		time.sleep(0.1)
		
	def read_chuck_heights(self):
	#read the alignment, separation and contact distances
		raw = self.controller.ask('ReadChuckHeights\n').strip().decode()
		(status, resp) = raw.split(':')
		resp = resp.strip()
		contact, overtravel, alignment, separation, search= resp.split(" ") 
        
		print("Contact=" +str(contact)+" Overtravel="+str(overtravel)+" Alignment="\
		+str(alignment)+" Separation="+str(separation)+" Search="+str(search))
        
	def move_separation(self):
	#moves to separation position, the in-built function seems to no work
		#a,b,c=self.position
		#separation_relative=config.separation_val+c
		self.check_chuck_contact()
		if state.Application.check_contact == 1:  # contact
			self.controller.ask('$StartCommand MoveChuckZ %s R Y %s\n'\
			%(-config.separation_val, config.z_velocity))
			print("Moved to Separation height")
			#time.sleep(config.time_separation)
			self.check_move_status()

	def move_contact(self): 
	#moves to contact position, the in-built function seems to no work too
		#a,b,c=self.position
		#contact_relative=config.contact_val+c   
		self.check_chuck_contact()
		if state.Application.check_contact == 0:  # contact        
			self.controller.ask('$StartCommand MoveChuckZ %s R Y %s\n' \
			%(config.separation_val, config.z_velocity))
			print("Moved to Contact height")
			#time.sleep(config.time_separation)
			self.check_move_status()
		
	def set_chuck_index(self, dx, dy):
	#sets the index size for the size of die
		time.sleep(config.sleep_time)
		self.controller.ask('$StartCommand SetChuckIndex %s %s Y\n' %(dx, dy))
		print("Index set to: %s, %s" %(dx, dy))

        
	def read_chuck_index(self):
	#read the current index values
		time.sleep(config.sleep_time)
		raw = self.controller.ask('ReadChuckIndex\n').strip().decode()
		(status, resp) = raw.split(':')
		resp = resp.strip()
		dx, dy= resp.split(" ")
		print("Index Size is X=" +str(dx)+" Y="+str(dy))
		return (dx, dy)
        
	def read_index_position(self):
	#not finished yet
		a,b,c=self.position
		return (int(a), int(b), int(c))
      	
	def move_chuck_index(self, ix, iy):
	#moves chuck in x-y direction in index units
		self.check_chuck_contact()
		if state.Application.check_contact == 0:  # separation height
			self.controller.ask('$StartCommand MoveChuckIndex %s %s R %s\n'\
			%(ix, iy, config.xy_velocity))
			self.check_move_status()
			print("Moved by: %s, %s" % (ix, iy))

            
		elif state.Application.check_contact==1: #contact height
			self.move_separation()
			self.controller.ask('$StartCommand MoveChuckIndex %s %s R %s\n'\
			%(ix, iy, config.xy_velocity))
			self.check_move_status()
			self.move_contact()
			print("Moved by: %s, %s" % (ix, iy))
            
            

	def set_chuck_home(self):  
	#set chuck current position as home position
	#does not work as the home position can be changed only in wafer map
		self.controller.ask('SetChuckHome 0 Y \n')
		
	def stop_chuck_movement(self,dx,dy,dz):
	#stop movement in x,z,y directions (binary value)
		decimal=dx*1+dy*2+dz*4
		self.controller.ask('$StartCommand StopChuckMovement %s\n' %decimal)
		self.check_move_status()

#Protocol functions
	def read_subdice(self):
	#perform the chuck movement in the given subdie in 
	#given sub_row, sub_col vectors
		print("\nStart subdice scanning/reading")
		self.set_chuck_index(config.subindex_x, config.subindex_y)
		self.move_chuck_index(-config.col_sub[0], config.row_sub[0])

		for i in range(config.col_sub.size):
			print("Sub-column is %s, Sub-row is %s" % (config.col_sub[i],\
			config.row_sub[i]))
			self.move_contact()
			self.read()
			self.move_separation()
			if i==(config.col_sub.size-1):
				self.move_chuck_index(-(-config.col_sub[i]), -config.row_sub[i])
			else:
				self.move_chuck_index(-(config.col_sub[i+1]-config.col_sub[i]),\
				config.row_sub[i+1]-config.row_sub[i])

		self.set_chuck_index(config.index_x, config.index_y)
		self.read_chuck_index()
		print(" Subdice Finished!\n")

	def initialize(self):
	#initialize the probe station and set it ready for automated movement
	#please load this function first after running the bench script
	
		input("Turn On Probe-Press any key to continue")
		input("Turn Velox On")
		input("Turn on GPIB function in Velox")
		#input("Press any key to initialize the probe")
		#self.initchuck()
		input("Load Wafer-Press any key to continue")
		input("Load your corresponding wafer map in Velox")
		input("Press any key to set the chuck heights")
		self.set_chuck_heights("C", config.contact_val)
		self.set_chuck_heights("A", alignment_val)	
		self.set_chuck_heights("S", config.separation_val)
		self.read_chuck_heights()#display the entered values
		self.set_chuck_index(config.index_x, config.index_y)#set index size
		self.read_chuck_index() #display chuck position
		input("Do the 2-point Alignment then press any key to continue")
		input("Go to D1, SD1 then press any key to continue")
		input("Select Contact Mode then press any key to continue")
		input("Put lever down and reposition die properly\
		if needed- then press any key to continue")
		input("Select Separation mode then press any key to continue")
		
	def read_any_row(self, r):
	#read any preferred single die row in the wafer
		#changed to the inverse move direction than the prototype code
		self.set_chuck_index(config.index_x, config.index_y)
		self.read_chuck_index()
		a,b,c=self.position
		#print("Insert Any Row")
		#r = int(input())
		self.move_separation()
		self.move_chuck_index(-(-config.w[r]),r)

		for i in range(config.x[r]):
			print("Current die: "+str(i))
			if  int(i%config.skip_odd==0):
				self.read_subdice()
			if i==(config.x[r]-1):
				self.move_chuck_index(-(-i+config.w[r]),-r) #move back to (0,0)
			else:
				self.move_chuck_index(-1,0)
		print("reading Finished\n")
		
		#Execute the position correction relatively
		#to the position at the beginning of the function
		a_final,b_final,c_final=self.position
		print("wafer position uncorrected")
		print(self.position)
		a=a_final-a
		b=b_final-b
		self.move_relative(a,b)
		print("Wafer position corrected")
		print(self.position)

		
	def read_row_range(self): 
	#it is used for reading a range of rows<maximum wafer rows. For that use read all wafer function
	#changed to the inverse move direction than the prototype code
		self.set_chuck_index(config.index_x, config.index_y)
		a,b,c=self.position
		#ix1 = int(input("Read from row: "))
		#ix2=  int(input("Read to row: "))
		self.move_chuck_index(-(-config.w[ix1]),ix1)#move to start position

		for i in range(ix2-ix1+1):
			for j in range(config.x[ix1+i]):
				print("Current row is: "+str(i+ix1))
				if int(j % config.skip_odd == 0):
					self.read_subdice()
				if j == (config.x[ix1+i]-1):
					self.move_chuck_index(j,0)
				else:
					self.move_chuck_index(-1,0)
			if i==(ix2-ix1):
				self.move_chuck_index(-config.w[ix2], -ix2)
			else:
				self.move_chuck_index((config.w[ix1+i+1]-config.w[ix1+i]),1)

			print("\n")
		print("Reading Finished\n")
		
		#Execute the position correction relatively
		#to the position at the beginning of the function
		a_final,b_final,c_final=self.position
		print("wafer position uncorrected")
		print(self.position)
		a=a_final-a
		b=b_final-b
		self.move_relative(a,b)
		print("Wafer position corrected")
		print(self.position)


	def read_full_wafer(self):
	#read all the wafer dice, but keeps the selection for subdie defined by the coordinates
    #in col_sub, row_sub vectors
	#changed to the inverse move direction than the prototype code
		self.set_chuck_index(config.index_x, config.index_y)
		ix1 = 0
		ix2 = x.size-1 
		a,b,c=self.position #position correction reference
		self.move_chuck_index(-(-config.w[ix1]), ix1)  # move to start position

		for i in range(ix2 - ix1 + 1):
			for j in range(config.x[ix1 + i]):
				print("Current row is: " + str(i + ix1))
				if int(j % config.skip_odd == 0):
					self.read_subdice()
				if j == (config.x[ix1 + i] - 1):
					self.move_chuck_index(j, 0)
				else:
					self.move_chuck_index(-1, 0)
			if i == (ix2-ix1):
				self.move_chuck_index(-config.w[ix2], -ix2)
			else:
				self.move_chuck_index((config.w[ix1 + i + 1] - config.w[ix1 + i]), 1)
			print("\n")
		print("Reading Finished\n")
		
		#Execute the position correction relatively
		#to the position at the beginning of the function
		a_final,b_final,c_final=self.position
		print("wafer position uncorrected")
		print(self.position)
		a=a_final-a
		b=b_final-b
		self.move_relative(a,b)
		print("Wafer position corrected")
		print(self.position)
		
		
	def read_defined(self): 
	#read the defined dice at the coordiates defined in col (y-axis) and row(x-axis) vectors
	#changed to the inverse move direction than the prototype code
		self.set_chuck_index(config.index_x, config.index_y)
		a, b, c = self.position  # position correction reference
		self.move_chuck_index(config.col[0]-config.w[config.row[0]], config.row[0])

		for i in range(config.row.size):
			print("Current Row is: "+str(config.row[i]))
			self.read_subdice()
			if i==config.row.size-1:
				self.move_chuck_index(-(-config.col[i]+\
				config.w[config.row[i]]),-config.row[i] )
			else:
				self.move_chuck_index(\
				-((config.col[i+1]-config.col[i])-\
				(config.w[config.row[i+1]]-config.w[config.row[i]])),\
				config.row[i+1]-config.row[i])
		print("Reading Finished\n")
		
		#Execute the position correction relatively
		#to the position at the beginning of the function
		a_final,b_final,c_final=self.position
		print("wafer position uncorrected")
		print(self.position)
		a=a_final-a
		b=b_final-b
		self.move_relative(a,b)
		print("Wafer position corrected")
		print(self.position)

	def exit():
		return 1
	
	def case(self):
	#combine all functions in a single switch case function
		print("For Initializing press 1 \n \
For Reading single row press 2 \n \
For reading a row range press 3 \n \
For reading the full wafer press 4 \n \
For reading specific dice press 5 \n\
For exit press 6\n")
	
		option=int(input("Your option: "))
		dictionary={
			1: self.initialize,
			2: self.read_any_row,
			3: self.read_row_range,
			4: self.read_full_wafer,
			5: self.read_defined,
			6: exit
		}
		dictionary.get(option)()
		
        
