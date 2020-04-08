

class MK14_MEMMAP:

    def __init__(self, getCyclesFn):
        self.getCyclesFn = getCyclesFn
        self.stdRam = [0] * 256     # standard ram
        self.extRam = [0] * 256     # extended ram
        self.ioRam = [0] *128       # Ram in the IO chip
        self.display = [0] * 8
        self.dispSetCycTime = [0] * 8
        self.btnMap = [0xff] * 8
        self.rom = [0] * 512        # Rom 

    def getDisplaySegments(self, n):
        """
            returns the status of a display byte - for mk14ui 
        """
        return (self.display[n], self.dispSetCycTime[n])

    def doButtonMap(self, addr, bit, isPressed):
        """
            sets the bitmap line 
        """
        if isPressed:
            mask = (1 << bit) ^ 0xff
            self.btnMap[addr] &= mask
        else:
            mask = 1 << bit
            self.btnMap[addr] |= mask
#        print("ButtonAddr", addr, self.btnMap[addr], isPressed)


    def setButton(self, buttonStr, isPressed):
        """
            sets bit stuff based on button pressed outside in mk14ui 
        """
        if buttonStr == "ABT":
            self.doButtonMap(4, 5, isPressed)
        elif buttonStr == "TRM":
            self.doButtonMap(7, 5, isPressed)
        elif buttonStr == "MEM":
            self.doButtonMap(3, 5, isPressed)
        elif buttonStr == "GO":
            self.doButtonMap(2, 5, isPressed)
        else:
            buttonCode = int(buttonStr, 16)
            if buttonCode < 8:
                self.doButtonMap(buttonCode, 7, isPressed)
            elif buttonCode < 10:
                self.doButtonMap(buttonCode-8, 6, isPressed)
            elif buttonCode < 0x0e:
                self.doButtonMap(buttonCode - 10, 4, isPressed)
            else:
                self.doButtonMap(buttonCode - 10 + 2, 4, isPressed)

    def read(self, addr):
        """
            read from memory
            addr - address to read from 
            returns byte
        """
        page = addr & 0xf00
        if page == 0xf00:
            #   F00-FFF  256 bytes RAM (Standard)
            # return self.stdRam[addr - 0xf00]
            # DA March 2020 changed to use and 
            return self.stdRam[addr & 0xff]
        if page == 0xb00:
            #   B00-BFF  256 bytes RAM (Extended) DA March 2020 added extended ram
            # return self.extRam[addr - 0xb00]
            # DA March 2020 changed to use and 
            return self.extRam[addr & 0xff]

        elif page == 0x900 or page == 0xd00:
            # 0x900 and 0xd00 are display and keyboard memory areas
            if addr & 0x0f <= 0x07:
            #       print("Read keyboard", addr, "rslt", self.btnMap[addr & 0x07])
                return self.btnMap[addr & 0x07]
            else:
                return 0xff
        elif page < 0x800:
            # DA March 2020 changed from 0x900 to 0x800 
            # 000 - 7FF  is rom repeated 4 times
            return self.rom[addr & 0x01ff]
        else:
            # DA March 2020 - add the RAM IO memory and IO stuff
            # should be the RAM IO are 
            # 0x800 0xa00 0xc00 0xe00
            if addr & 0xff <= 0x7f:
                #  128 bytes of ram
                return self.ioRam[addr & 0x7f]
            else:
                return 0
                #  need to handle the IO device stuff.
                # print("Read address unknown", format(addr, "04x"))
        return 0

    def write(self, addr, val, overwriteROM = False):
        """
           write to memory and other areas
           
        """
        page = addr & 0xf00
        if page == 0xf00:
            #   F00-FFF  256 bytes RAM (Standard)
            # self.stdRam[addr - 0xf00] = val & 0xff
            # DA March 2020 change do use bit and to get array entry number
            self.stdRam[addr & 0xff] = val & 0xff
        elif page==0xb00:
            # DA March 2020 added extended 
            #   B00-BFF  256 bytes RAM (Extended) DA March 2020 added extended ram
            # self.stdRam[addr - 0xf00] = val & 0xff
            self.extRam[addr & 0xff] = val & 0xff

        elif page == 0x900 or page == 0xd00:
            # 0x900 and 0xd00 are display and keyboard memory areas
            if addr & 0x0f <= 0x07:
                self.display[addr & 0x07] = val
                self.dispSetCycTime[addr & 0x07] = self.getCyclesFn()
    #            print("Disp: ", end="")
    #            for i in range(8):
    #                print(format(self.display[7-i],"02x"),"",end="")
    #            print()
        elif page < 0x800:
            # DA March 2020 changed from 0x900 to 0x800 
            # 000 - 7FF  is rom repeated 4 times
            # DA March 2020 - added write protect test
            if overwriteROM:
                self.rom[addr & 0x01ff] = val & 0xff
            else:
                print("ROM write attempt ", format(addr, "04x"))
        
        else:
            # DA March 2020 - add the RAM IO memory and IO stuff
            # should be the RAM IO are 
            # 0x800 0xa00 0xc00 0xe00
            if addr & 0xff <= 0x7f:
                #  128 bytes of ram
                self.ioRam[addr & 0x7f] = val & 0xff
            else:
                print ("IO data")
                #  need to handle the IO device stuff.
            # print("Write address unknown", format(addr, "04x"))

    def init(self, initialList):
        """
            Initialise the memory 
            Args
                initialList - defines the contents to write to memory
                          each entry has an address element
                                     followed by a data element 
                                        which is a number of bytes
        """

        for memBlock in initialList:
            # get the details of the data to be stored
            blkAddr = memBlock[0]
            blkData = memBlock[1]
            for i in range(len(blkData)):
                # store byte - set overwriteROM to allow ROM to be set.
                self.write(blkAddr+i, blkData[i], True)

