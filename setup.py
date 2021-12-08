from distutils.core import setup
import py2exe

setup(
    console=['gui.py'],
    options={
        'py2exe':{
            'packages':['pandas','Tkinter']
        }
    }
)