#!/usr/bin/python3
# part of the MK14 emulator in python
# it handles the creation and operation of the GUI interface 
#  

# declare the colors are using the combination of “red”, “blue” and “green” color’s hexadecimal value to obtain colors 
# such as for white #fff, for black  #000000, etc 
# which can be in string specification for the proportion of color in hexadecimal value 
# which can be 4, 8 or 12 bit per color.

import tkinter as tk
from functools import partial

# not sure if this is the correct way to do declare these variables :)
global hiddencolor
hiddencolor = 'white' 
global showcolor
showcolor = 'red'

class SevenSegDigit:

    # this class handles 1 7 segment digit
    
    
    # Order 7 segments clockwise from top left, with crossbar last.
    # Coordinates of each segment are (x0, y0, x1, y1) 
    # given as offsets from top left measured in segment lengths.
    
    offsets = (
        (0, 0, 1, 0),  # top
        (1, 0, 1, 1),  # upper right
        (1, 1, 1, 2),  # lower right
        (0, 2, 1, 2),  # bottom
        (0, 1, 0, 2),  # lower left
        (0, 0, 0, 1),  # upper left
        (0, 1, 1, 1),  # middle
    )

    # Segments used for each digit; 0, 1 = off, on.
    digits = (
        (1, 1, 1, 1, 1, 1, 0),  # 0
        (0, 1, 1, 0, 0, 0, 0),  # 1
        (1, 1, 0, 1, 1, 0, 1),  # 2
        (1, 1, 1, 1, 0, 0, 1),  # 3
        (0, 1, 1, 0, 0, 1, 1),  # 4
        (1, 0, 1, 1, 0, 1, 1),  # 5
        (1, 0, 1, 1, 1, 1, 1),  # 6
        (1, 1, 1, 0, 0, 0, 0),  # 7
        (1, 1, 1, 1, 1, 1, 1),  # 8
        (1, 1, 1, 1, 0, 1, 1),  # 9
        (1, 1, 1, 0, 1, 1, 1),  # 10=A
        (0, 0, 1, 1, 1, 1, 1),  # 11=b
        (1, 0, 0, 1, 1, 1, 0),  # 12=C
        (0, 1, 1, 1, 1, 0, 1),  # 13=d
        (1, 0, 0, 1, 1, 1, 1),  # 14=E
        (1, 0, 0, 0, 1, 1, 1),  # 15=F
    )

    #
    # create the digit by drawing all the segments and 
    # turning them off 
    #  originally by hiding them
    #  try changing colour
    #
    def __init__(self, canvas, *, x=10, y=10, length=20, width=3):
        self.canvas = canvas
        l = length
        self.segs = []
        for x0, y0, x1, y1 in self.offsets:
            self.segs.append(canvas.create_line(
                x + x0*l, y + y0*l, x + x1*l, y + y1*l,
                width=width, state = 'hidden' , fill=showcolor))
            #self.segs.append(canvas.create_line(
            #    x + x0*l, y + y0*l, x + x1*l, y + y1*l,
            #    width=width, state = 'normal' , fill=hiddencolor))

    def show(self, num):
        for iid, on in zip(self.segs, self.digits[num]):
            self.canvas.itemconfigure(iid, state = 'normal' if on else 'hidden')
            #self.canvas.itemconfigure(iid, fill = showcolor if on else hiddencolor)

    def dispBits(self, bits):
        bitMask = 1
        for i in range(len(self.segs)):
            bitOn = (bits & bitMask) != 0
            bitMask = bitMask << 1
            self.canvas.itemconfigure(self.segs[i], state = 'normal' if bitOn else 'hidden')
            #self.canvas.itemconfigure(self.segs[i], fill = showcolor if bitOn else hiddencolor)
            
    
class MK14_UI:
# added 0
    persistenceOfVisionCycles = 10000

    def __init__(self, mk14MemoryMap):
        """
            Create window
             setup 7seg digits
             setup buttons
             needs memoryMap to handle display and keyboard
        """
        self.tkRoot = tk.Tk()
        self.tkRoot.title("MK14")
        self.tkRoot.protocol("WM_DELETE_WINDOW", self.onCloseWindow)
        self.genDigits(8)
        self.genButtons()
        self.memMap = mk14MemoryMap
        self.closing = False

    def service(self):
        """
            call this routine to allow display to cycle etc

        """
        self.tkRoot.update_idletasks()
        self.tkRoot.update()
        self.displayFromMK14MemMap()
        return self.closing

    def onCloseWindow(self):
        self.closing = True
        
    def close(self):
        self.tkRoot.destroy()

    def click(self, btn):
        # test the button command click
        s = "Button %s clicked" % btn
        print ("clicked", btn)
        #self.tkRoot.title(s)

    def release(self, btn, event):
        print ("released", btn)
        self.memMap.setButton(btn, False)

    def press(self, btn, event):
        print ("pressed", btn)
        self.memMap.setButton(btn, True)
    
    def genButtons(self):
        # create a labeled frame for the keypad buttons
        # relief='groove' and labelanchor='nw' are default
        lf = tk.LabelFrame(self.tkRoot, text="", bd=3 , bg='white')
        lf.pack(padx=15, pady=10)
        # typical calculator button layout
        btn_list = [
        'Go','Mem','Abort', 'a',
        '7',   '8',  '9'  ,  'b',
        '4',   '5',  '6'  ,  'c',
        '1',   '2',  '3'  ,  'd',
        'Term','0',  'f'  ,   'e' ]
        # create and position all buttons with a for-loop
        # r, c used for row, column grid values
        r = 1
        c = 0
        n = 0
        # list(range()) needed for Python3
        btn = list(range(len(btn_list)))
        for label in btn_list:
            # attaches the buttons to functions to record press and release
            # partial takes care of function and argument
            cmd = partial(self.click, label)    # called when button pressed
            rel = partial(self.release, label)  # called when button released
            pres = partial(self.press, label)   # called when button pressed
            # create the button
            btn[n] = tk.Button(lf, text=label, width=5, command=cmd, bg="white")
            btn[n].bind("<Button-1>", pres)
            btn[n].bind("<ButtonRelease-1>", rel)
            # position the button
            btn[n].grid(row=r, column=c)
            # increment button index
            n += 1
            # update row/column position
            c += 1
            if c > 3:
                c = 0
                r += 1

    def genDigits(self, numDigits):
        screen = tk.Canvas(self.tkRoot, width=270, height=60, bg='white')
        screen.pack(padx=15, pady=10, fill=tk.X)
        self.digits = []
        for i in range(numDigits):
            self.digits.append(SevenSegDigit(screen, x=10+i*33))

    def displayFromMK14MemMap(self):
        """
            sets all the 7segments based on values in memMap
        """
        curCycles = self.memMap.getCyclesFn()
        for i in range(8):
            bits, cycles = self.memMap.getDisplaySegments(i)
            # debug print
            # print( cycles)
            self.digits[7-i].dispBits(bits)
#   not sure why ??????? so removed test
#            if curCycles < cycles + self.persistenceOfVisionCycles:
#                self.digits[7-i].dispBits(bits)
#            else:
#                self.digits[7-i].dispBits(bits)
            

# Test code
if __name__ == '__main__':
    def testUpdateUI():
        global n
        for i in range(8):
            mk14ui.digits[i].show(n)
        n = (n+1) % 16
        mk14ui.tkRoot.after(1000, testUpdateUI)
    n = 0
    mk14ui = MK14_UI()
    mk14ui.tkRoot.after(1000, testUpdateUI)
    closing = False
    while not closing:
        closing = mk14ui.service()
    mk14ui.close()
    
