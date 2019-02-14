from tkinter import *
from threading import Thread
import time

g=None
def gui():
    global g
    window = Tk()

    g = Canvas(window, width=1910, height=1070)
    g.pack()

    mainloop()

def makeGrid(l,x,y):
    global g
    g.delete(ALL)
    cWidth = g.winfo_width()/(len(l[0])+1)
    cHeight = g.winfo_height()/(len(l)+1)
    i=1
    for row in l:
        Thread(target=threadGrid, args=[row,i,cHeight,cWidth,y,x]).start()
        i+=1

    time.sleep(1)

def threadGrid(row,i,cHeight,cWidth,y,x):
    global g
    j=1
    for v in row:
        g.create_text(i*cWidth,j*cHeight,font=("Purisa", 20),text='X' if x==i-1 and y==j-1 else v)
        j+=1


t=Thread(target=gui)
t.start()
time.sleep(1)
