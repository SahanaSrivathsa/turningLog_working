from sys import argv
from getCurrentInfo import *
import pandas as pd
import tkinter, tkinter.constants, tkinter.filedialog,tkinter.messagebox,tkinter.ttk
import os
import numpy as np
import datetime
from PIL import Image, ImageDraw, ImageFont, ImageTk

path = os.getcwd()
 

window = Tk(className="bla")

img_path=path + "\\Images\\"+"vHC.png"
image =Image.open(img_path)    
canvas = tkinter.Canvas(window, width=image.size[0], height=image.size[1])
canvas.pack()
image_tk = ImageTk.PhotoImage(image)
canvas.create_image(image.size[0]//2, image.size[1]//2, image=image_tk)

def callback(event):
    print ("clicked at: ", event.x, event.y)

canvas.bind("<Button-1>", callback)
mainloop()