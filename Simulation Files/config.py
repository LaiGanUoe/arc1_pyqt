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

#selected Dice to read
D=np.array([4,12,14,21,23,25,34,36,38,46,48,50,61,63,65])

row = np.array([])
col = np.array([])
row=row.astype(int)
col=col.astype(int)
sum=0
for j in range(D.size):
    for i in range(x.size):
        sum=sum+x[i]
        if sum>=D[j]:
            row=np.append(row, int(i))
            col=np.append(col, int(x[i]-(sum-D[j])-1))
            sum=0
            break

#Index, Subindex
index_x=9000 #die x-axis index
index_y=9000 #die y-axis index
subindex_x=3000 #subdie x-axis index
subindex_y=3000 #subdie y-axis index

#Chuck velocity velocity
z_velocity=100 #velocity of the chuck moving in the Z direction in %
xy_velocity=100 #velocity of the chuck moving in the XY direction in %

#Default Z distances for contact and separation
contact_val=746
alignment_val=200
separation_val=500

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


#current_x_D=0
#current_y_D=0
#current_x_s=0
#current_y_s=0