#this file sets the parameters required for probe automation
#each wafer map needs a corresponding config file

import numpy as np

#number of dice on each row (at least 1 element)
x=np.array([5,9,11,13,13,15,15,15,15,15,15,13,13,11,9,5])
# row offset relative to row 0
w=np.array([0,2,3,4,4,5,5,5,5,5,5,4,4,3,2,0])
row_size=x.size-1 #number of rows

#check if a row starts with single arrays (SA) "0" or corssbar (CB) "1"
odd_check=np.array([1,0,0,0,1,1,0,1,0,1,0,0,1,1,1,0,0])

#check for alignment marks
#align_marks=np.array([0,0,[1,23], 0,0,0,0,[2,7,12],0,0,0,0,0,[1,9]])

#subdice initialized array with coordinates x-y (col_sub, row_sub)
col_sub=np.array([3,5])
row_sub=np.array([3,4])

#selected dice coordiantes x-y (col-row)
#row=np.array([0,1,1,2,2,2,3,3,3,4,4,4,5,5,5])
#col=np.array([3,6,8,6,8,10,8,10,12,7,9,11,9,11,13])





#we measure Rs from largest width and largest length, bottom-left elecrode on microscope
#starting with devices with wordline: w1, w2, w3,...wn or length L1, L2, L3, etc
#Therefore length coefficient (L_ratio) is ratio between Li/Lmax, L1/Lmax, L2/Lmax etc.
#these values are calculated in "Electrode lengths.xlsx" file in Automation ArC1 folder
L_ratios=np.array([0.159090909,0.215909091,0.272727273,0.329545455,0.272727273,0.443181818,0.386363636,0.556818182,\
                    0.5,0.674242424,0.613636364,0.784090909,0.727272727,0.897727273,0.840909091,1,1,\
                    0.954545455,0.897727273,0.840909091,0.784090909,0.727272727,0.674242424,0.613636364,\
                    0.556818182,0.5,0.443181818,0.386363636,0.329545455,0.272727273,0.215909091,1])


#width ratio of electrode for every device size starting from S1, S2, S3...etc. 
#In order, device sizes are:  1, 2, 5, 10, 20, 30, 40, 50, 60um
#in this array the width ratio (or width coefficient) is S1/S9, S1/S8, S1/S7...etc. 
W_ratios=np.array([0.016666667,0.02,0.025,0.033333333,0.05,0.1,0.2,0.5,1])

#selected Dice to read
D=np.array([])
#4,12,14,21,23,25,34,36,38,46,48,50,61,63,65,75,77,79,81,91,95
row = np.array([])
col = np.array([])
row=row.astype(int)
col=col.astype(int)

row_old = np.array([])
col_old = np.array([])
row_old=row_old.astype(int)
col_old=col_old.astype(int)

row_sum = np.array([])
col_sum = np.array([])
row_sum=row_sum.astype(int)
col_sum=col_sum.astype(int)

sx=np.array([3,3,3]) # used to build the wafer submap

col_align=np.array([1,9,2,7,12,1,9])#set the alignment marks on the wafermap
row_align=np.array([2,2,7,7,7,13,13])#set the alignment marks on the wafermap

dies_color=[] #used to differentiate between red white and grey colours)
SA=[]#map with the position of single arrays
crossbar=[] #map with the position of crossbars
sel_dies_values=[]#pass the selected dies from wafer control popup to the testmodule and store them until go is pressed again

device_count=0 #how many subdice were read so far
time_elapsed=0
time_estimated=0

#Index, Subindex
index_x=9000 #die x-axis index
index_y=9000 #die y-axis index
subindex_x=3000 #subdie x-axis index
subindex_y=3000 #subdie y-axis index

#Chuck velocity velocity
z_velocity=50 #velocity of the chuck moving in the Z direction in %
xy_velocity=50 #velocity of the chuck moving in the XY direction in %

#Default Z distances for contact and separation
contact_val=746
alignment_val=200
separation_val=1000

#moving times
sleep_time=0.1 		#time for reading values
time_separation=0.5 #time for doing the separation or contact move
time_move_slow=4 	#time for moving in x-y direction (slower)
time_move_medium=2  #time for moving in x-y direction (medium)
time_move_fast=1    #time for moving in x-y direction (fast)
read_time=0 		#time for reading data

#skip odd dice #0-no skip, 1-skip
skip_odd=0

#relative index units in which chuck x and y moved from reference
moved_x=0
moved_y=0
move_limit=0

#reference position relatively to the wafer map defined in x and w
Xr=0
Yr=0
valuesAll=[]
rate=0
rate2=0
#current_x_D=0
#current_y_D=0
#current_x_s=0
#current_y_s=0