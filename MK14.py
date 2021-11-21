
# This is an emulator for MK14 using python
# This loads the monitor rom into Rom space 
# plus can load a hex file by specify it as the parameter

#
# The code was taken from one provided on github
#  https://github.com/robdobsn/MK14PyEm
#
#  first fix was to change start address to x000 
#   as the scmp  increments the program counter first and then get op code
#   
#  The code now multiplexes the 7 segment display like the real MK14 does 
#
# David Allday Mar 2020
#
#  memVals  - defines the contents to write to memory
#            each entry has an address element
#                 followed by a data element 
#                       which is a number of bytes
#           Note: During intial setup (mem.init) the ROM can be written to.
#      
#  David Allday Nov 2021                 


import mk14ui          # mk14 user interface 
import ins8060cpu      # emulates the scmp processor
import sys             # system functions

# The mk14 monitor rom - version 2 probably ???

romCode = (0x0000, [
0,207,255,144,30,55,194,12,51,199,255,192,242,1,192,235,49,192,231,53,192,
231,50,192,227,54,192,228,0,7,192,222,8,5,63,200,217,64,200,215,6,
200,213,53,200,204,49,200,202,196,15,54,200,198,196,0,50,200,194,199,1,
51,202,12,55,202,14,196,0,202,2,202,3,196,1,55,144,109,194,14,144,
179,197,1,1,196,1,203,213,196,1,7,143,8,195,213,80,152,7,143,24,
196,0,7,144,5,196,0,7,143,24,143,32,195,213,243,213,156,224,187,214,
156,215,63,196,8,203,213,6,212,32,152,251,143,28,25,143,28,187,213,156,
242,64,205,1,144,233,198,254,50,3,251,216,201,1,63,8,170,14,144,54,
194,14,53,194,12,49,194,13,201,0,144,52,228,6,152,157,228,5,152,34,
170,12,156,30,144,226,196,255,202,17,202,15,194,14,53,194,12,49,193,0,
202,13,196,63,51,63,144,220,196,26,51,63,144,234,196,255,202,15,194,14,
53,194,12,49,193,0,202,13,196,63,51,63,144,194,196,4,202,9,170,15,
156,6,196,0,202,13,202,17,2,194,13,242,13,202,13,186,9,156,245,194,
13,88,202,13,144,150,63,6,91,79,102,109,125,7,127,103,119,124,57,94,
121,113,196,4,202,9,170,15,156,6,196,0,202,14,202,12,2,194,12,242,
12,202,12,194,14,242,14,202,14,186,9,156,239,194,12,88,202,12,63,196,
1,53,196,11,49,194,13,212,15,1,193,128,202,0,194,13,28,28,28,28,
1,193,128,202,1,3,196,1,53,196,11,49,194,12,212,15,1,193,128,202,
4,194,12,28,28,28,28,1,193,128,202,5,6,212,128,152,9,2,196,0,
202,3,198,2,144,222,198,254,196,0,202,11,196,13,53,196,255,202,16,196,
10,202,9,196,0,202,10,49,170,16,1,194,128,201,128,143,0,193,128,228,
255,156,76,186,9,156,237,194,10,152,10,194,11,156,216,194,10,202,11,144,
210,194,11,152,206,1,64,212,32,156,40,196,128,80,156,27,196,64,80,156,
25,196,15,80,244,7,1,192,128,1,199,2,63,144,169,10,11,12,13,0,
0,14,15,96,144,239,96,244,8,144,234,96,228,4,152,8,63,144,145,88,
202,10,144,175,196,0,55,196,75,51,63])


def hexVal(inStr, pos, len):
    """ Returns the  byte at position + len as a hex value
           Args:
                inStr - string to be processed
                pos  - start postion 
                len  - 
           Returns:
                   Hex values
           Raises:
 
    """
    return int(inStr[pos:pos + len], 16)

def fromHexLines(hexLinesp):
    """ 
        Convert the hexlines format into the mem format used to load memory
    """
    #print ("hexLinesp")
    #print (hexLinesp)
    memOut = []
    for hexLine in hexLinesp:
        # print ("hexline", hexLine)
        leng = hexVal(hexLine, 1, 2)
        if leng > 0:
            addr = hexVal(hexLine, 3, 4)
            memVals = []
            for i in range(leng):
                memVals.append(hexVal(hexLine, 9 + i * 2, 2))
            memOut.append([addr, memVals])
    return memOut

def showMem(mem, addr, leng):
    """
        Debug code
        Display the values in certian memory locations
        Displays the address followed by the next 16 bytes 
        args
            mem - is an object that holds the memory
            addr - where to start from
            leng - number of bytes to list
    """
    for i in range(leng):
        if i % 16 == 0:
            print(format(addr+i, "04x"), "", end="")
        print(format(mem.read(addr+i), "02x"), "", end="")
        if i % 16 == 15:
            print()
    print()


# this is the "Duck Shoot" in hex format

hexLines = [
    ":180F1200C40D35C40031C401C8F4C410C8F1C400C8EEC40801C0E71EB2",
    ":180F2A00C8E49404C4619002C400C9808F01C0D89C0EC180E4FF980811",
    ":160F4200C8CEC0CAE480C8C64003FC0194D6B8BF98C8C40790CEDD"
]


print ('Number of arguments:', len(sys.argv), 'arguments.')
print ('Argument List:', str(sys.argv))

#if __name__ == "__main__":
#    print("Arguments count: " , len(sys.argv))
#    for i, arg in enumerate(sys.argv):
#       print("Argument ", i, "='", {arg}, "'")



if (len(sys.argv) > 1):
    filein = sys.argv[1]
    with open(filein) as fp:
        # readlines reads all the lines of a file into a list 
        # which we can them process line by line
        hexLines=fp.readlines()
        print ("Read ",filein)
        # read would load all the lines of the file as characters ??
        # reading the file does not create the array needed as the code loaded above does
        # only a character stream 


#print ("hexLines")
#print (hexLines)



# convert it into the mem format used
memVals = fromHexLines(hexLines)
# add it to the Rom code
memVals.append(romCode)

# initialise the CPU
#  loads the memory and set the program counter
# use this one to display debug information
#cpu = ins8060cpu.CPU_INS8060(memVals, 0x000, True, {"base":0xf0f,"count":3})
# This initialises the processor and memory map 
cpu = ins8060cpu.CPU_INS8060(memVals, 0x000, False)

# debug to show rom space
# showMem(cpu.getMemMap(), 0, 512)

mk14UI = mk14ui.MK14_UI(cpu.getMemMap())

closing = False
# main loop 
while not closing:
    # print ("Executing 10 statements")
    # execute 10 statements
    cpu.service()
    # sort out display
    closing = mk14UI.service()
    #closing=True # fix
# finished - remove the gui
mk14UI.close()

# end of code

