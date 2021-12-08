import pandas as pd
import os
from tkinter import *

tetrodes = ['TT1','TT2','TT3','TT4','TT5','TT6','TT7','TT8','TT9','TT10','TT11','TT12','TT13','TT14','TT15','TT16','RF','RR']

def allowed_directions(input):
    directions = ['N', 'NW', 'W', 'SW', 'S', 'SE', 'E', 'NE','']
    if input in directions:
        return True
    else:
        return False

def getInitial():
    setInitialForm = Tk()
    setInitialForm.title("Turning Log - Set Initial Positions")
    for tLabel in range(0, 18):
        Label(setInitialForm, text=tetrodes[tLabel], font=('Helvetica', 16, "bold")).grid(row=tLabel + 1, column=0)
    Label(setInitialForm, text='Starting Position', font=('Helvetica', 15, "bold")).grid(row=0, column=1)
    validation=setInitialForm.register(allowed_directions)
    tt1Start = Entry(setInitialForm, width=3,validate = 'key',validatecommand = (validation,'%P'))
    tt1Start.grid(row=1, column=1)
    tt2Start = Entry(setInitialForm, width=3,validate = 'key',validatecommand = (validation,'%P'))
    tt2Start.grid(row=2, column=1)
    tt3Start = Entry(setInitialForm, width=3,validate = 'key',validatecommand = (validation,'%P'))
    tt3Start.grid(row=3, column=1)
    tt4Start = Entry(setInitialForm, width=3,validate = 'key',validatecommand = (validation,'%P'))
    tt4Start.grid(row=4, column=1)
    tt5Start = Entry(setInitialForm, width=3,validate = 'key',validatecommand = (validation,'%P'))
    tt5Start.grid(row=5, column=1)
    tt6Start = Entry(setInitialForm, width=3,validate = 'key',validatecommand = (validation,'%P'))
    tt6Start.grid(row=6, column=1)
    tt7Start = Entry(setInitialForm, width=3,validate = 'key',validatecommand = (validation,'%P'))
    tt7Start.grid(row=7, column=1)
    tt8Start = Entry(setInitialForm, width=3,validate = 'key',validatecommand = (validation,'%P'))
    tt8Start.grid(row=8, column=1)
    tt9Start = Entry(setInitialForm, width=3,validate = 'key',validatecommand = (validation,'%P'))
    tt9Start.grid(row=9, column=1)
    tt10Start = Entry(setInitialForm, width=3,validate = 'key',validatecommand = (validation,'%P'))
    tt10Start.grid(row=10,column=1)
    tt11Start = Entry(setInitialForm, width=3,validate = 'key',validatecommand = (validation,'%P'))
    tt11Start.grid(row=11, column=1)
    tt12Start = Entry(setInitialForm, width=3,validate = 'key',validatecommand = (validation,'%P'))
    tt12Start.grid(row=12, column=1)
    tt13Start = Entry(setInitialForm, width=3,validate = 'key',validatecommand = (validation,'%P'))
    tt13Start.grid(row=13, column=1)
    tt14Start = Entry(setInitialForm, width=3,validate = 'key',validatecommand = (validation,'%P'))
    tt14Start.grid(row=14, column=1)
    tt15Start = Entry(setInitialForm, width=3,validate = 'key',validatecommand = (validation,'%P'))
    tt15Start.grid(row=15, column=1)
    tt16Start = Entry(setInitialForm, width=3,validate = 'key',validatecommand = (validation,'%P'))
    tt16Start.grid(row=16, column=1)
    rfStart = Entry(setInitialForm, width=3,validate = 'key',validatecommand = (validation,'%P'))
    rfStart.grid(row=17, column=1)
    rrStart = Entry(setInitialForm, width=3,validate = 'key',validatecommand = (validation,'%P'))
    rrStart.grid(row=18, column=1)
    

    startPos= [tt1Start,tt2Start,tt3Start,tt4Start,tt5Start,tt6Start,tt7Start,tt8Start,tt9Start,tt10Start,
               tt11Start,tt12Start,tt13Start,tt14Start,tt15Start,tt16Start,rfStart,rrStart]
    
    Button(setInitialForm, text='Quit', command=setInitialForm.quit).grid(row=20, column=0, sticky=W, pady=4)
    Button(setInitialForm, text='Submit', command=setInitialForm.quit).grid(row=20, column=2 , sticky=W, pady=4)

    mainloop()
    
    return [l.get() for l in startPos]

#### CHANGE BACK PATH  ###############################
def getCurrent(path,rat,date):
    dir = path + "/" + rat
    file = dir +'/current_'+rat+'.csv'
    
    if not os.path.isdir(dir):
        os.makedirs(dir)
    if os.path.exists(file):
        info = pd.read_csv(file)
    else:
        with open(file,'w') as create:
            create.write('TT,Direction,Total Turns,Depth,Updated\n')
            starting = getInitial()
            for t in range(0,18):
                if starting[t]=='':
                    starting[t] = 'O'
            for tetr in range(0,18):
                create.write('{0},{1},0,0,{2}\n'.format(tetrodes[tetr],starting[tetr],date))
        info = pd.read_csv(file)


    depths = list(info['Depth'])
    positions = list(info['Direction'])
    totalTurns = list(info['Total Turns'])

    return (depths,positions,totalTurns)


def total(past,new):
    return int(past)+int(new)


def turnDepth(totalTurns):
    depth = float(totalTurns) * 31.25
    return int(depth)