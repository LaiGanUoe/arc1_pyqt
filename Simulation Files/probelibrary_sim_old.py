from controller import make_controller
import time
import numpy as np
import config
#import sys
#sys.path.append('C:\\Users\\Alin\\AppData\\Roaming\\arc1pyqt\\ProgPanels')

#from TestModule import
#Wafer map
x=np.array([5,9,11,13,13,15,15,15,15,15,15,13,13,11,9,5]) #number of dice on each row (at least 1 element)
y=np.linspace(1,16,16) #number of rows
w=np.array([0,2,3,4,4,5,5,5,5,5,5,4,4,3,2,0]) #row offset relative to row 0

#Defined read dice
col=np.array([2,4])#desired die x-coordinate  (starts from column 0)
row=np.array([1,2])#desired die y-coordinate (starts from row 0)

#defined read subdice
#col_sub=np.array([0]) #column values for the desired subdice cooridinates
#row_sub=np.array([0]) #row values for the desired subdice cooridinates

#Input values
sleep_time=0.5 		#time for reading values
time_separation=0.5 #time for doing the separation or contact move
time_move_slow=4 	#time for moving in x-y direction (slower)
time_move_medium=2  #time for moving in x-y direction (medium)
time_move_fast=1    #time for moving in x-y direction (fast)
read_time=0 		#time for reading data

z_velocity=100 #velocity of the chuck moving in the Z direction in %
xy_velocity=100 #velocity of the chuck moving in the XY direction in %


skip_odd=1 # 1-don't skip, 2-skip one column (in case there are CB and SA dice)
index_x=9000 #die x-axis index
index_y=9000 #die y-axis index
subindex_x=3000 #subdie x-axis index
subindex_y=3000 #subdie y-axis index

#Contact, Alginment, Separation
#always negative values
contact_val=746
alignment_val=200
separation_val=500

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
		time.sleep(sleep_time)
		#raw = self.controller.ask('ReadChuckPosition\n').strip().decode()
        # typical response would look like
        # 0: -4771.904 11675.686 0.0
        # the first number (before the ':') indicating the status of the
        # command. When != 0 an error occurred

		#(status, resp) = raw.split(':')
        
		#if int(status) != 0 or resp == "None":
			#raise Exception('An error has occurred', resp.strip())
        
        # remove any leading/trailing spaces
		#resp = resp.strip()
        # split the numbers received by spaces present
        # and make them into floats
        # this can also be expressed in a more pythonic
        # way like so
        # >>> tuple(map(float, r.split(' ')))
        # but for clarity reasons it's kept simple
		#(x, y, z) = resp.split(' ')
		#(x, y, z) = (float(x), float(y), float(z))
        
		#return (x, y, z)
		
    # dx and dy MUST be microns
    # you can change that by switching the Y argument
    # of the command to other values indicating mm or cm
    # check the prober manual. Last argument is tolerance
    # This is an example of an asynchronous command. As of
    # now it's blocking but it can be possibly be offloaded to
    # a background thread.
	
	def read(self): 
	#define reading time for ArC measuremetns
		print("Reading...si astept semnal sa ca readingul e gata")
		while config.x != 0:
			if x == 0:
				print("received signal")
				break
		time.sleep(read_time)
	
	def move_relative(self, dx, dy, xy_velocity=100):
	#move relatively in x-y direction in um units
		self.controller.ask('$StartCommand MoveChuck %s %s R Y %s\n' % \
			(dx, dy, xy_velocity))
		print("Moved by %s, %s" %(dx,dy))
		time.sleep(time_move_fast)
   
	def move_home(self, dx, dy, xy_velocity=100):
	#move to wafer home position
		self.controller.ask('$StartCommand MoveChuck %s %s H Y %s\n' % \
			(dx, dy, xy_velocity))
		time.sleep(time_move_slow)
	
	def move_relative_z(self, dz):
	#move relatively in the Z direction
		self.controller.ask('$StartCommand MoveChuckZ %s R Y\n' %dz)
		time.sleep(time_move_fast)
	
	def move_home_z(self, dz):
	#move to home position in Z direction
		self.controller.ask('$StartCommand MoveChuckZ %s H Y\n' %dz)
		time.sleep(time_move_slow)
				
	def initchuck(self):
	#initialize the chuck, recommended after we turn on the probe.
	#It is automatically included in the initialization step
		self.controller.ask('$StartCommand InitChuck 7 0 0\n').decode().strip()
		while True:
			raw=self.controller.ask('$StartCommand ReadChuckStatus\n').decode().strip()
			if raw=="COMPLETE":
				return 1
				break
	def functie_random(self):
		print("Ataseaza waferul")
		self.read()
		print("Acum detaseaza waferul")
				
	def centering_to_zero(self):
		#centers the wafer to 0 position
		raw = self.controller.ask('ReadChuckPosition\n').strip().decode()
		(status, resp) = raw.split(':')
		print (resp)
		(a, x, y, z) = resp.split(' ')
		(x, y, z) = (-float(x), -float(y), -float(z))
        
		self.controller.ask('$StartCommand MoveChuck %s %s R Y \n' % \
			(x, y))
		time.sleep(time_move_slow)
	
	def set_chuck_heights(self, type, value):
	#loads the alignment, separation and contact distances
		self.controller.ask('SetChuckHeight %s V Y %s\n' %(type, value))
		time.sleep(0.2)
		
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
		#separation_relative=separation_val+c
		self.controller.ask('$StartCommand MoveChuckZ %s R Y %s\n' %(-separation_val, z_velocity))
		print("Moved to Separation height")
		time.sleep(time_separation)
		
		
	def move_contact(self): 
	#moves to contact position, the in-built function seems to no work too
		#a,b,c=self.position
		#contact_relative=contact_val+c
		self.controller.ask('$StartCommand MoveChuckZ %s R Y %s\n' %(separation_val, z_velocity))
		print("Moved to Contact height")
		time.sleep(time_separation)
		
	def set_chuck_index(self, dx, dy):
	#sets the index size for the size of die
		time.sleep(time_move_fast)
		self.controller.ask('$StartCommand SetChuckIndex %s %s Y\n' %(dx, dy))
		print("Index set to: %s, %s" %(dx, dy))
        
	def read_chuck_index(self):
	#read the current index values
		time.sleep(sleep_time)
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
		self.controller.ask('$StartCommand MoveChuckIndex %s %s R %s\n' %(ix, iy, xy_velocity))
		print("Moved by: %s, %s" %(ix, iy))
		if abs(ix)>3 or abs(iy)>3:
			time.sleep(time_move_slow)
		else:
			time.sleep(time_move_fast)
		
	def set_chuck_home(self):  
	#set chuck current position as home position
	#does not work as the home position can be changed only in wafer map
		self.controller.ask('SetChuckHome 0 Y \n')
		
	def stop_chuck_movement(self,dx,dy,dz):
	#stop movement in x,z,y directions (binary value)
		decimal=dx*1+dy*2+dz*4
		self.controller.ask('$StartCommand StopChuckMovement %s\n' %decimal)


	#Protocol functions
	def read_subdice(self):
	#perform the chuck movement in the given subdie in 
	#given sub_row, sub_col vectors
		print("\nStart subdice scanning/reading")
		self.set_chuck_index(subindex_x, subindex_y)
		self.move_chuck_index(col_sub[0], row_sub[0])

		for i in range(col_sub.size):
			print("Sub-column is %s, Sub-row is %s" % (col_sub[i], row_sub[i]))
			self.move_contact()
			self.read()
			self.move_separation()
			if i==(col_sub.size-1):
				self.move_chuck_index(-(-col_sub[i]), -row_sub[i])
			else:
				self.move_chuck_index(-(col_sub[i+1]-col_sub[i]), row_sub[i+1]-row_sub[i])

		self.set_chuck_index(index_x, index_y)
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
		self.set_chuck_heights("C", contact_val)
		self.set_chuck_heights("A", alignment_val)	
		self.set_chuck_heights("S", separation_val)			
		self.read_chuck_heights()#display the entered values
		self.set_chuck_index(index_x, index_y)#set index size
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
		self.set_chuck_index(index_x, index_y)
		self.read_chuck_index()
		a,b,c=self.position
		#print("Insert Any Row")
		#r = int(input())
		self.move_separation()
		self.move_chuck_index(-(-w[r]),r)

		for i in range(x[r]):
			print("Current die: "+str(i))
			if  int(i%skip_odd==0):
				self.read_subdice()
			if i==(x[r]-1):
				self.move_chuck_index(-(-i+w[r]),-r) #move back to (0,0)
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
		self.set_chuck_index(index_x, index_y)
		a,b,c=self.position
		#ix1 = int(input("Read from row: "))
		#ix2=  int(input("Read to row: "))
		self.move_chuck_index(-(-w[ix1]),ix1)#move to start position

		for i in range(ix2-ix1+1):
			for j in range(x[ix1+i]):
				print("Current row is: "+str(i+ix1))
				if int(j % skip_odd == 0):
					self.read_subdice()
				if j == (x[ix1+i]-1):
					self.move_chuck_index(j,0)
				else:
					self.move_chuck_index(-1,0)
			if i==(ix2-ix1):
				self.move_chuck_index(-w[ix2], -ix2)
			else:
				self.move_chuck_index((w[ix1+i+1]-w[ix1+i]),1)

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
		self.set_chuck_index(index_x, index_y)
		ix1 = 0
		ix2 = x.size-1 
		a,b,c=self.position #position correction reference
		self.move_chuck_index(-(-w[ix1]), ix1)  # move to start position

		for i in range(ix2 - ix1 + 1):
			for j in range(x[ix1 + i]):
				print("Current row is: " + str(i + ix1))
				if int(j % skip_odd == 0):
					self.read_subdice()
				if j == (x[ix1 + i] - 1):
					self.move_chuck_index(j, 0)
				else:
					self.move_chuck_index(-1, 0)
			if i == (ix2-ix1):
				self.move_chuck_index(-w[ix2], -ix2)
			else:
				self.move_chuck_index((w[ix1 + i + 1] - w[ix1 + i]), 1)
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
		self.set_chuck_index(index_x, index_y)
		a, b, c = self.position  # position correction reference
		self.move_chuck_index(col[0]-w[row[0]], row[0])

		for i in range(row.size):
			print("Current Row is: "+str(row[i]))
			self.read_subdice()
			if i==row.size-1:
				self.move_chuck_index(-(-col[i]+w[row[i]]),-row[i] )
				time.sleep(time_move_slow)
			else:
				self.move_chuck_index(\
				-((col[i+1]-col[i])-(w[row[i+1]]-w[row[i]])),\
				row[i+1]-row[i])
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
		
        
