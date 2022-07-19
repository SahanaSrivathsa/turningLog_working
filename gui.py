from getCurrentInfo import *
import pandas as pd
import tkinter, tkinter.constants, tkinter.filedialog,tkinter.messagebox,tkinter.ttk
import os
import numpy as np
import datetime
import math
from PIL import Image, ImageDraw, ImageFont
################################################################################################################################################
########### PARAMETERS ###########

#Paths to Directories
path = os.getcwd()
screenshot_dir = "C:\\Users\\sahanasrivathsa\\Videos\\Captures"
images_dir=path + "\\Images\\"
#ephysnotes_dir=
HC_img_path = images_dir+"vHC.png"
ACC_angle_path=images_dir+"ACC_angled.png"
ACC_straight_path=images_dir+"ACC.png"

# #Defining the angle
# theta=math.radians(12)
# sin_theta=math.sin(theta)
# cos_theta=math.cos(theta)

#Initializing Lists/Arrays for rat params
turns= [0] * 18
tetrodes = ['TT1','TT2','TT3','TT4','TT5','TT6','TT7','TT8','TT9','TT10','TT11','TT12','TT13','TT14','TT15','TT16','RF','RR']
tt_list=['tt1','tt2','tt3','tt4','tt5','tt6','tt7','tt8','tt9','tt10','tt11','tt12','tt13','tt14','tt15','tt16','rf','rr']
directions_array=['N', 'NW', 'W', 'SW', 'S', 'SE', 'E', 'NE']
temp_pos=[None]*len(tt_list)
updated_depths=[None]*len(tt_list)

#Initializing Empty arrays
turnsFull=[]
turnsEighths=[]
newPos=[]
cellUnits=[]
lfpTheta=[]
lfpSWR=[]
noise=[]
ref=[]
Notes=[]
   
#Font and colors for tetrodes plotting onto paxinos images
font_path = "C:\\Windows\\Fonts\\ARLRDBD.TTF"
color_array= [(85,26,139),(39,64,139), (96,123,139), (46,139,87), (48,128,20),(238,154,0), (255,128,0),(205,51,51), (139,37,0),  (139,131,134) ]

#Distance conversion for ACC and HC images
HC_increment = 61 #1mm scale in image
ACC_increment = 73 #1mm scale in image

#Initial Starting Coordinates for each Image of Paxinos
HC_xcoord=302
HC_ycoord=108
ACC_xcoord=33
ACC_ycoord=75
ACC_ang_xcoord=55
ACC_ang_ycoord=75

################################################################################################################################################
################# Loading and saving functions  #################
def get_rat():
    """
    Retrieves previous information about the specified rat
    """
    ratForm = Tk()
    ratForm.title("Choose Rat")

    Label(ratForm, text='RAT:', font=('Helvetica', 14, "bold")).grid(row=0, column=0)
    rat = Entry(ratForm, width=5)
    rat.grid(row=0, column=1)
    Label(ratForm, text='DATE {YYYY-MM-DD}:', font=('Helvetica',14, "bold")).grid(row=1, column=0)
    date = Entry(ratForm, width=10)
    date.grid(row=1,column=1,pady=10)
    date.insert(0, datetime.datetime.today().strftime('%Y-%m-%d'))
    
    Button(ratForm, text='CONFIRM', command=ratForm.quit).grid(row=2, column=2, sticky=W, pady=4)

    mainloop()
    return (rat.get(),date.get())
    

def save_turn_data():
    """
    Save the inputed data into CSV files. Also appends to tetrode turning metadata file.
    """
    currentFile = path + "/" + rat+ '/current_' + rat + '.csv' 
    #metadataFile=ephysnotes_dir + rat + "/" + 'ephys_notes.csv'
    newpath= path + "/" + rat +"/" + date
    if not os.path.exists(newpath):
        os.makedirs(newpath)

    #Daily Log of Turning Info   
    logFile = newpath + '/' + rat + '_'+date+'.csv'
    
    with open(currentFile,'w') as current:
        with open(logFile,'w') as log:
            current.write('TT,Direction,Total Turns,Depth,Updated\n')
            log.write('TT,Old Depth,Old Direction,Turns,New Direction,Total Turns,New Depth,Units,Theta,SWR,Noise,Reference_AD,Notes\n')
            for tet in range(0,18):
                #Get all the current entries
                turnsFull[tet]=ttTurns[tet].get()
                turnsEighths[tet]=ttEighths[tet].get()
                newPos[tet]=ttPos[tet].get()
                cellUnits[tet] = ttUnits[tet].get()
                lfpTheta[tet]=ttTheta[tet].get()
                lfpSWR[tet]=ttSWR[tet].get()
                noise[tet]=ttNoise[tet].get()
                ref[tet]=ttRef[tet].get()
                Notes[tet]=ttNotes[tet].get()
   
                if turnsEighths[tet] == '':
                    turnsEighths[tet] = 0
                if turnsFull[tet] == '':
                    turnsFull[tet] = 0  
                if newPos[tet] == '':
                    newPos[tet] = positions[tet]  
                turns[tet]=(int(turnsFull[tet])*8)+int(turnsEighths[tet])
                newTotal = total(totTurns[tet],turns[tet])
                if newPos[tet] == 'O':
                    newDepth= 0
                else:
                    newDepth = turnDepth(newTotal)
                current.write('{0},{1},{2},{3},{4},{5}\n'.format(tetrodes[tet],newPos[tet],newTotal,newDepth,date))
                log.write('{0},{1},{2},{3},{4},{5},{6},{7},{8},{9},{10},{11},{12}\n'.format(tetrodes[tet],org_depths[tet],positions[tet],turns[tet],
                                                                 newPos[tet],newTotal,newDepth,cellUnits[tet],lfpTheta[tet],lfpSWR[tet],noise[tet],ref[tet],Notes[tet]))
    master.quit()

################# Functions restricting/validating the entry types  #################
def allowed_turns(input):
    """
    Limits the turns to integers (prevents error)
    """
    if input in ('','0','-'): 
        return True
    elif int(input):
        return True
    else:
        return False

def commas_present(input):
    """
    Removes all commas from notes to allow csv to be read. 
    """
    if ',' in input:
        return False
    else:
        return True
def yes_no(input):
    """
    Limits the Yes no inputs to Y/N 
    """
    if input in ('Y','N'): 
        return True
    else:
        return False

def change_color(c):
    """
    Changes color of the widget if necessary
    """
    widget_list=[master,l2]
    for wid in widget_list:
        wid.configure(bg = c)

################# Functions computing parameters  #################

def calc_turns(oldDir,newDir,directions_array):
    """
    Calculates the number of turns(or eighth turns) when direction is entered
    """
    if newDir == '':
        newDir = oldDir
    if oldDir == 'O':
        return 0
    else:    
        oldIndex = directions_array.index(oldDir)
        newIndex = directions_array.index(newDir)
        delta = newIndex - oldIndex
        if delta < 0:
            return str(8+delta)
        else:
            return str(delta)

def calc_dir(oldDir,turnsEighths):
    """
    Calculates the Direction/Position when no. of turns (or eighth turns) is entered
    """
    if turnsEighths == '':
        turnsEighths = 0
    directions_down = ['N', 'NW', 'W', 'SW', 'S', 'SE', 'E', 'NE']
    if oldDir == 'O':
        return 'O'
    else:
        oldIndex = directions_down.index(oldDir)
        newIndex = (oldIndex + int(turnsEighths)%8)%8
        return directions_down[newIndex]


def checkTTdir():
    """
    Changes the order of directions on TT list based on whether you are turning up or down (based on toggle button t_btn)
    """
    if t_btn.cget('text')== 'Up':
        directions_array=['N', 'NE', 'E', 'SE', 'S', 'SW', 'W', 'NW']
    else:
        directions_array=['N', 'NW', 'W', 'SW', 'S', 'SE', 'E', 'NE']
    return directions_array


# def checkACCangle():
#     """
#     Checks if the bundle is angled on not (based on toggle button ang_btn)
#     """
#     if ang_btn.cget('text')== 'Angled':
#         angle=True
#     else:
#         angle=False
#     return angle
    
def update_tt_depth(tt_id):
    """
    Updates the Tetrode depth based on entered values of position or turns
    """
    directions_array=checkTTdir()
    idx = tt_list.index(tt_id)

    #If No. of Full turns not entered it enters 0. 
    if eval('%sTurnsFull.get()'%(tt_id)) == "":
        eval('%sTurnsFull.insert(0,0)'%(tt_id))
    
    #If both Turns and Pos are filled then it deletes the one that was not last modified and refills it with new value
    if (eval('%sTurns.get()'%(tt_id))!= "" and eval('%sPos.get()'%(tt_id))!=""):
        if (str(master.focus_lastfor()) == '.!entry%d'%(idx+19) or str(master.focus_lastfor()) == '.!entry%d'%(idx+1) or str(master.focus_lastfor()) == '.!entry' ):
            eval('%sPos.delete(0,END)'%(tt_id)) #Deletes pos if turns was last modified
        elif str(master.focus_lastfor()) == '.!entry%d'%(idx+37):
            eval('%sTurns.delete(0,END)'%(tt_id)) # Deletes turns if pos was last modified
    
    #If Turns is empty, fills it with position value
    if not eval('%sTurns.get()'%(tt_id)):
        if not eval('%sPos.get()'%(tt_id)):
            eval('%sPos.insert(0, positions[idx])'%(tt_id))
        if directions_array ==['N', 'NE', 'E', 'SE', 'S', 'SW', 'W', 'NW']:
            turn_ct = eval('calc_turns(positions[idx],%sPos.get(),directions_array)'%(tt_id))
            turn_ct=str(-int(turn_ct))
            eval('%sTurns.insert(0,turn_ct)'%(tt_id))
        else:
            eval('%sTurns.insert(0,calc_turns(positions[idx],%sPos.get(),directions_array))'%(tt_id,tt_id))   
        temp_pos[idx] =eval('%sPos.get()'%(tt_id))
        updated_depths[idx] = depths[idx] + (float(eval('%sTurns.get()'%(tt_id))) + (float(eval('%sTurnsFull.get()'%(tt_id)))*8))* 31.25
    
    #If position is empty fills with turns value
    elif not eval('%sPos.get()'%(tt_id)):
        updated_depths[idx] = depths[idx] + (float(eval('%sTurns.get()'%(tt_id)))+(float(eval('%sTurnsFull.get()'%(tt_id)))*8)) * 31.25
        eval('%sPos.insert(0, calc_dir(positions[idx],%sTurns.get()))'%(tt_id,tt_id))
        temp_pos[idx] = eval('%sPos.get()'%(tt_id))
    if updated_depths[idx]<depths[idx]:
        col='blue' #BLUE Indicates that the tetrode was turned up
    else:
        col='red' #RED Indicates that the tetrode was turned down

    #Makes sure depth doesn't change for dead tetrodes.
    if  positions[idx] == "O":
        updated_depths[idx]=0

    # #Updates depth for angled bundle along D-V axis
    # angle=checkACCangle()
    # if angle:
    #     update_tt_depth[idx]=cos_theta*update_tt_depth[idx]
        
    Label(master, text=temp_pos[idx],font=('Helvetica',14),width = 5,fg=col).grid(row=idx+1,column=3)
    Label(master, text=updated_depths[idx],font=('Helvetica',14),width = 8,fg=col).grid(row=idx+1,column=1)

def fill_dir():
    """
    Based on tetrode position all unfilled directions are filled up. This is necessary to run before saving for the CSV file to read correctly the next time.
    """
    for i in tt_list:
        idx=tt_list.index(i)
        if len(eval('%sPos.get()'%(i))) != 0:
            if eval('%sPos.get()'%(i)) != calc_dir(positions[idx],eval('%sTurns.get()'%(i))):
                MsgBox = tkinter.messagebox.askquestion ('ERROR IN POSITION','Do you want to keep current Position for %s?'%(i),icon = 'warning')
                if MsgBox == 'yes':
                    eval('%sTurns.delete(0, END)'%(i))
                    eval('%sTurns.insert(0, calc_turns(positions[idx],%sPos.get(),directions_array))'%(i,i))
                else:
                    eval('%sPos.delete(0, END)'%(i))
                    eval('%sPos.insert(0,calc_dir(positions[idx],%sTurns.get()))'%(i,i))
        else: 
            eval('%sPos.insert(0, calc_dir(positions[idx],%sTurns.get()))'%(i,i))
        if positions[idx] == "O":
                    eval('%sPos.insert(0,"O")'%(i))

def fill_turns():
    """
    Based on tetrode turns all unfilled turns are filled up. This is necessary to run before saving for the CSV file to read correctly the next time.
    """
    for i in tt_list:
        idx=tt_list.index(i)
        if len(eval('%sTurns.get()'%(i))) != 0:
            if eval('%sPos.get()'%(i)) != calc_dir(positions[idx],eval('%sTurns.get()'%(i))):
                if positions[idx] == "O":
                    eval('%sPos.insert(0,"O")'%(i))
                MsgBox = tkinter.messagebox.askquestion ('ERROR IN TURNS','Do you want to keep current Turn Count for %s?'%(i),icon = 'warning')
                if MsgBox == 'no':
                    eval('%sTurns.delete(0, END)'%(i))
                    eval('%sTurns.insert(0, calc_turns(positions[idx],%sPos.get(),directions_array))'%(i,i))
                else:
                    eval('%sPos.delete(0, END)'%(i))
                    eval('%sPos.insert(0,calc_dir(positions[idx],%sTurns.get()))'%(i,i))
        else: 
            eval('%sTurns.insert(0, calc_turns(positions[idx],%sPos.get(),directions_array))'%(i,i))
        if len(eval('%sTurnsFull.get()'%(i)))==0:
            eval('%sTurnsFull.insert(0,0)'%(i))


################# Functions for image processing and saving  #################

def attach_img():
    """
    Function to easily attach screenshots taken during turning and place them in the correct folder
    """
    imgname =  tkinter.filedialog.askopenfilename(initialdir = screenshot_dir,title = "Select file",filetypes = (("png files", "*.png"),("jpeg files","*.jpg")))
    newpath= path + "/" + rat +"/" + date
    if not os.path.exists(newpath):
        os.makedirs(newpath)
    new_name = tkinter.filedialog.asksaveasfilename(defaultextension = '.png',initialdir = newpath,title = "Select file",filetypes = (("png files", "*.png"),("jpeg files","*.jpg")))
    os.rename(imgname, new_name)

def view_tetrodes_HC():
    '''
    Opens Paxinos image of vHC and plots the tetrode depth and saves it image for every session
    '''
     #img_path=images_dir+"vHC.png"
    HC=Image.open(HC_img_path)    
    draw = ImageDraw.Draw(HC, mode="RGBA")
    for i in range(8,17):
        if updated_depths[i] != None:
            dep=round((updated_depths[i]/1000),2)
            tt_depth = np.floor((updated_depths[i]/1000)*HC_increment)
        else:
            dep=round((depths[i]/1000),2)
            tt_depth = np.floor((depths[i]/1000)*HC_increment)
        if tt_depth == 0:
            dep=0
        draw.line((HC_xcoord+((i-8)*12), HC_ycoord,HC_xcoord+((i-8)*12), HC_ycoord+tt_depth), width = 4, fill = color_array[i-8])
        font = ImageFont.truetype(font_path,size=24)
        if i != 16:
            draw.text((702, 107+(i*24)),"TT%d: %1.2f"%(i+1,dep),fill =color_array[i-8],font=font)
        else:
            draw.text((702, 107+(i*24)),"RF: %1.2f"%(dep),fill =color_array[i-8],font=font)

    HC.show()
    HC.save(path + "\\" + rat +"\\" + date+'\\'+"HC_TETRODES.png")
    del draw

def view_tetrodes_ACC():
    '''
    Opens Paxinos image of ACC and plots the tetrode depth and saves it image for every session
    '''
    #img_path=images_dir+"ACC.png"
    # angle=checkACCangle
    # if angle:
    #     ACC_img_path = ACC_angle_path
    # else:
    ACC_img_path = ACC_straight_path

    ACC =Image.open(ACC_img_path)    
    draw = ImageDraw.Draw(ACC, mode="RGBA")
    numlist=[0,1,2,3,4,5,6,7,17]
    
    
    for i in numlist:
        if updated_depths[i] != None:
            dep=round((updated_depths[i]/1000),2)
            tt_depth = np.floor((updated_depths[i]/1000)*ACC_increment)
        else:
            dep=round((depths[i]/1000),2)
            tt_depth = np.floor((depths[i]/1000)*ACC_increment)
        if tt_depth == 0:
            dep=0
        if i!=17:
            draw.line((ACC_xcoord+(i*10), ACC_ycoord ,ACC_xcoord+(i*10), ACC_ycoord+tt_depth), width = 4, fill = color_array[i])
            font = ImageFont.truetype(font_path,size=25)
            draw.text((624, 280+((i)*25)),"TT%d: %1.2f"%(i+1,dep),fill =color_array[i],font=font)
        else:
            draw.line((ACC_xcoord+((i-8)*10), ACC_ycoord ,ACC_xcoord+((i-8)*10), ACC_ycoord+tt_depth), width = 4, fill = color_array[i-8])
            font = ImageFont.truetype(font_path,size=25)
            draw.text((624, 280+((i-8)*25)),"RR: %1.2f"%(dep),fill =color_array[i-8],font=font)
    # else:
    #         for i in numlist:
    #             if updated_depths[i] != None:
    #                 dep=round((updated_depths[i]/1000),2)
    #                 tt_depth = np.floor((updated_depths[i]/1000)*ACC_increment*cos_theta)
    #                 tt_depth_x =np.floor((updated_depths[i]/1000)*ACC_increment*sin_theta)
    #             else:
    #                 dep=round((depths[i]/1000),2)
    #                 tt_depth = np.floor((depths[i]/1000)*ACC_increment*cos_theta)
    #                 tt_depth_x =np.floor((depths[i]/1000)*ACC_increment*sin_theta)
    #             if tt_depth == 0:
    #                 dep=0
    #             if i!=17:
    #                 draw.line((ACC_ang_xcoord+(i*10), ACC_ang_ycoord ,ACC_ang_xcoord+(i*10)-tt_depth_x, ACC_ang_ycoord +tt_depth), width = 4, fill = color_array[i])
    #                 font = ImageFont.truetype(font_path,size=25)
    #                 draw.text((624, 280+((i)*25)),"TT%d: %1.2f"%(i+1,dep),fill =color_array[i],font=font)
    #             else:
    #                 draw.line((ACC_ang_xcoord+((i-8)*10), ACC_ang_ycoord  ,ACC_ang_xcoord+((i-8)*10)-tt_depth_x, ACC_ang_ycoord +tt_depth*cos_theta), width = 4, fill = color_array[i-8])
    #                 font = ImageFont.truetype(font_path,size=25)
    #                 draw.text((624, 280+((i-8)*25)),"RR: %1.2f"%(dep),fill =color_array[i-8],font=font)


    ACC.show()
    ACC.save(path + "\\" + rat +"\\" + date+"\\"+"ACC_TETRODES.png")
    del draw
###############################################################################################################################################################################
# RUNNING THE FUNCTIONS FOR INITIALIZING THE DATA

#Retrieving previous data
rat,date = get_rat()
depths,positions,totTurns = getCurrent(path,rat,date)
org_depths=depths

#Setting up  the form
master = Tk()
master.title("Turning Log "+date)
master.geometry('1200x800')
var = BooleanVar()

#Restricting allowed directions
valid_directions = master.register(allowed_directions)
valid_turns = master.register(allowed_turns)
valid_comma=master.register(commas_present)
valid_yes=master.register(yes_no)


###############################################################################################################################################################################
#DISPLAY CODE 

################## COLUMN 0 ###############################
for tLabel in range(0,18):
    
    l=[]
    l.append(Label(master, text=tetrodes[tLabel],font=('Helvetica',16, "bold")).grid(row=tLabel+1,column=0))
    #tkinter.ttk.Separator(master, orient="horizontal").grid(row=tLabel+1,sticky='ew',column=1,columnspan=10)

################## COLUMN 1 Current Depth ###############################
l2=Label(master, text='Current \n Depth(\u03BCm)',font=('Helvetica',15, "bold"),anchor="center").grid(row=0, column=1)
for t in range(0,18):
    Label(master, text=depths[t],font=('Helvetica',14),anchor="center").grid(row=t+1,column=1)

################## COLUMN 2 Original Position ###############################
Label(master, text='Original \n Position',font=('Helvetica',15, "bold"),anchor="center").grid(row=0, column=2)
for tt in range(0,18):
    Label(master, text=positions[tt],font=('Helvetica',14),anchor="center").grid(row=tt+1,column=2)

################## COLUMN 3 Current Position ###############################
Label(master, text='Current \n Position',font=('Helvetica',15, "bold"),anchor="center").grid(row=0, column=3)
for tt in range(0,18):
    Label(master, text=positions[tt],font=('Helvetica',14),anchor="center").grid(row=tt+1,column=3)

################## COLUMN 4 No of Full turns ###############################
Label(master, text='Full \n Turns',font=('Helvetica',15, "bold"),anchor="center").grid(row=0, column=4)
ttTurns=[]
for i in tt_list:
    idx=tt_list.index(i)
    eval('%sTurnsFull'%(i)) = Entry(master, width=3,validate = 'key',validatecommand = (valid_turns,'%P'))
    eval('%sTurnsFull'%(i).grid(row=idx+1, column=4))
    ttTurns.append(unit)

################## COLUMN 5 No of Eighths ###############################
Label(master, text='Eighth \n Turns',font=('Helvetica',15, "bold")).grid(row=0, column=5)
ttEighths=[]
for i in tt_list:
    idx=tt_list.index(i)
    unit= Entry(master, width=3,validate = 'key',validatecommand = (valid_turns,'%P'))
    unit.grid(row=idx+1, column=5)
    ttEighths.append(unit)

################# COLUMN 6 New Direction ###############################
Label(master, text='New \n Position',font=('Helvetica',15, "bold"),anchor="center").grid(row=0, column=6)
ttPos=[]
for i in tt_list:
    idx=tt_list.index(i)
    unit= Entry(master, width=3,validate = 'key',validatecommand = (valid_directions,'%P'))
    unit.grid(row=idx+1, column=6)
    ttPos.append(unit)


################## COLUMN 7 Update Buttons ###############################
Label(master, text='Update \n Depth',font=('Helvetica',15, "bold")).grid(row=0, column=7)
for i in tt_list:
    idx=tt_list.index(i)
    #cb[idx]=Checkbutton(master, text="Turn Up", variable=vars[idx],onvalue = 1, offvalue = 0).grid(row=idx+1,column=8,sticky=W,pady=4)
    Button(master, text=tetrodes[idx], command=lambda i=i: update_tt_depth(i)).grid(row=idx+1, column=7, sticky=N, pady=5)



################# COLUMN 8 Cell Units ###############################
Label(master, text='Cell \n Units',font=('Helvetica',15, "bold"),anchor="center").grid(row=0, column=8)
ttUnits=[]
for i in tt_list:
    idx=tt_list.index(i)
    unit= Entry(master, width=3,validate = 'key',validatecommand = (valid_turns,'%P'))
    unit.grid(row=idx+1, column=8)
    ttUnits.append(unit)

################# COLUMN 9 Theta ###############################
Label(master, text='Theta',font=('Helvetica',15, "bold"),anchor="center").grid(row=0, column=9)
ttTheta=[]
for i in tt_list:
    idx=tt_list.index(i)
    unit= Entry(master, width=3,validate = 'key',validatecommand = (valid_yes,'%P'))
    unit.grid(row=idx+1, column=9)
    ttTheta.append(unit)

################# COLUMN 10 SWR ###############################
Label(master, text='SWR',font=('Helvetica',15, "bold"),anchor="center").grid(row=0, column=10)
ttSWR=[]
for i in tt_list:
    idx=tt_list.index(i)
    unit= Entry(master, width=3,validate = 'key',validatecommand = (valid_yes,'%P'))
    unit.grid(row=idx+1, column=10)
    ttTheta.append(unit)

################# COLUMN 11 Noise ###############################
Label(master, text='Noise',font=('Helvetica',15, "bold"),anchor="center").grid(row=0, column=11)
ttNoise=[]
for i in tt_list:
    idx=tt_list.index(i)
    unit= Entry(master, width=3,validate = 'key',validatecommand = (valid_yes,'%P'))
    unit.grid(row=idx+1, column=11)
    ttTheta.append(unit)

################# COLUMN 12 Reference ###############################
Label(master, text='Ref',font=('Helvetica',15, "bold"),anchor="center").grid(row=0, column=12)
ttRef=[]
for i in tt_list:
    idx=tt_list.index(i)
    unit= Entry(master, width=3,validate = 'key',validatecommand = (valid_comma,'%P'))
    unit.grid(row=idx+1, column=12)
    ttTheta.append(unit)

################# COLUMN 13 Notes ###############################
Label(master, text='Notes',font=('Helvetica',15, "bold"),anchor="center").grid(row=0, column=13)
ttNotes=[]
for i in tt_list:
    idx=tt_list.index(i)
    unit= Entry(master, width=15,validate = 'key',validatecommand = (valid_comma,'%P'))
    unit.grid(row=idx+1, column=13)
    ttNotes.append(unit)


############################################################### BUTTONS ########################################################################################

 ############################### TOGGLE BUTTONS ###############################
# UP-DOWN BUTTON
def toggle(tog=[0]):
    '''
    Toggle Button for turning tetrodes up/down
    '''
    tog[0] = not tog[0]
    if tog[0]:
        t_btn.config(text='Up')
        t_btn.config(relief="raised")
        t_btn.config(bg='red')
        change_color('lightcyan')

    else:
        t_btn.config(text='Down')
        t_btn.config(relief="sunken")
        t_btn.config(bg=org_color)
        change_color(bg_master )

#Initializes the up-down toggle button 
t_btn = Button(master,text="Down", width=12, command=toggle,relief="raised")
t_btn.grid(row=22, column=2, pady=10, padx =8 )
org_color = t_btn.cget("background")
bg_master=master.cget('background')

#########################################################
#Angled button Code not being used anymore

# #BUNDLE CONFIG -ANGLED STRAIGHT BUTTON
# def config(tog2=[0]):
#     tog2[0] = not tog2[0]
#     if tog2[0]:
#         ang_btn.config(text='Angled')
#         ang_btn.config(relief="raised")
#         ang_btn.config(bg='green')
        

#     else:
#         ang_btn.config(text='Straight')
#         ang_btn.config(relief="sunken")
#         ang_btn.config(bg=org_color)

# #Initializes the angled bundle button 
# ang_btn = Button(master,text="Straight", width=12, command=config,relief="raised")
# ang_btn.grid(row=22, column=1, pady=10, padx =8 )



 ############################### OTHER BUTTONS ###############################
Button (master, text='Submit', command=save_turn_data,anchor="center").grid(row=22, column=9, pady=8)
Button (master, text='Fill \n Turns', command=fill_turns,anchor="center").grid(row=22, column=4, pady=8)
Button(master,text='Fill \n Directions', command=fill_dir,anchor="center").grid(row=22,column=5,pady=8)
Button(master,text='Attach \n Image', command=attach_img,anchor="center").grid(row=22,column=6,pady=8)
Button(master,text='View Tetrodes \n Hippocampus', command=view_tetrodes_HC,anchor="center").grid(row=22,column=7,pady=8)
Button(master,text='View Tetrodes \n ACC', command=view_tetrodes_ACC,anchor="center").grid(row=22,column=8,pady=8)




mainloop()
master.withdraw()