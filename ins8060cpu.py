
# This is an emulator for INS8060 using python
#
# It was taken from one provided on github
#  https://github.com/robdobsn/MK14PyEm
#
#  first fix was to change the opcode fetch 
#    to increment program counter first and then get op code
#    using the 12 bit add
#
#  changed the indexed code as we don't need to fix the program counter opcode
#
#  halt instruction :-
#      The halt instruction actually should work by 
#        The instruction decode and control logic inhibits the incrementation of the program counter
#        so the halt opcode is read again 
#        on the second read it generates the HFLG line 
#          This is output on DB7 of the data lines at the same time as the high address bits are output 
#            This is whilst the NADS is low
#        At present just do the one instruction. 
#
# David Allday Feb 2020
# 

# use the MK14 version of the memory mapping

import mk14memmap

class CPU_INS8060:

    secondByte = ""    # fix so I can print 2nd byte in an opcode

    def __init__(self, initRAMList, initIP = 0, debugOn = False, debugRam = None):
        """  initialise cpu
           Args:
             initRAMList - defines data to be loaded into RAM
             initIP  - initial Program Counter (IP or P0 )
                      where to start running from - note: first opcode is at address + 1
             debugOn - set to True to get debug messages 
             debugRam - an array to define ram to be display with the debug messages
                       e.g. {"base":0xf1f,"count":1}
           Returns:
           Raises:

        """ 
        self.debugRam = debugRam
        self.debugOn = debugOn
        self.reset(initRAMList, initIP)

    def reset(self, initRAMList, initIP):
        """  reset the cpu values
           Args:
             initRAMList - defines data to be loaded into RAM
             initIP  - initial Program Counter (IP or P0 ) 
                     where to start running from - note: first opcode is at address + 1
           Returns:
           Raises:
        
        """  

        if self.debugOn:
            print("")
            print("Reset")
        # self.halted = False
        self.acc = 0    # accumulator
        self.ext = 0    # extension 
        self.stat = 0   # status flag
        self.cycles = 0  # ???
        self.ptrs = [initIP,0,0,0]  # program counter plus counters 1, 2 and 3
        # 
        self.mem = mk14memmap.MK14_MEMMAP(self.getCycles)
        if self.debugOn:
            print(initRAMList)
        self.mem.init(initRAMList)
        # if debug mode show registers
        self.showReg("")

    def getCycles(self):
        return self.cycles

    def run(self, start = None):
        """ execute a load of opcodes from optional start point
           Args:
               start - the address to start from 
                       i.e initial Program Counter (IP or P0 ) 
                     where to start running from - note: first opcode is at address + 1
        """
        if start != None:
            self.ptrs[0] = start
        self.execSome(8192)
        # ???? check for exit button and exit if so

    def service(self):
        """  execute next 10 opcodes
        """
        self.execSome(10)

    def getMemMap(self):
        """ returns pointer to the memory class in use
        """
        return self.mem
    
    def fetchIP(self):
        """  fetch the next opcode using the Programme counter
             add 1 to the program counter ( pointer 0 )
             Note add only to the first 12 bits of address
                  leaving the top 4 bits unchanged.
        """ 
        # from what the manual says we should increment counter before reading opcode? DA
        self.ptrs[0] = self.addr12bit(self.ptrs[0],1)
        op = self.mem.read(self.ptrs[0])
        # add should be using 12 bits process ? DA
        # removed: self.ptrs[0] += 1
        return op

    def showReg(self, debugStr):
        """  debug code to show registers and optionally some memory
              
        """
        if self.debugOn:
            # print accumulator, extention and status byte
            # end="" means no line feed after each print statement
            print(debugStr, format(self.acc, '02x'), \
                  format(self.ext, '02x'), format(self.stat, '02x'),\
                  end = "")
            # print the 4 index pointers
            print("", format(self.ptrs[0], '04x'), format(self.ptrs[1], '04x'),\
                  format(self.ptrs[2], '04x'), format(self.ptrs[3], '04x'),\
                  end = "")
            # print out some memory
            #   needs debugRam to have base and count entries
            if self.debugRam != None:
                print(" @" + format(self.debugRam["base"], "04x") + " ", end="")
                for i in range(self.debugRam["count"]):
                    print(format(self.mem.read(self.debugRam["base"]+i), "02x"), "", end="")
            # print a new line
            print()

    def execSome(self, numInstr):
        """  execute a number of opcodes
            
        """
        # Check that CPU has not halted
        #  removed the halted stuff 
        #if self.halted:
        #    return

        # Run in a loop until yield or halt
        # DA March 2020 - changed halt processing
        # 
        while (True):
            opcode = self.fetchIP()
            self.secondByte="  "
            debugIpAddr = self.ptrs[0] # program counter points at opcode after fetch

            if self.debugOn:
                print("IP", format(debugIpAddr, "04x"), "OP", format(opcode, "02x"), end="")
            debugStr = self.processOpcode(opcode)
            if self.debugOn:
                print("", self.secondByte, end ="")
                print("", '{:<14}'.format(debugStr), end="")
            self.showReg("")

#            if bHalt:
#                self.halted = True
#                if self.debugOn:
#                    print ("Halt executed")
#                    print("Stopping at HALT")
#                break

            numInstr -= 1
            if numInstr <= 0:
#                if self.debugOn:
#                    print("Yielding ... Done numInstrs")
                break

    def addr12bit(self, ptr, ofs):
        """ add to the first 12 bits of a pointer
           Args:
             ptr - current value of the pointer
             ofs - offset to add
           Returns:
             new value of the pointer
           Raises:
        """
        return ((ptr+ofs) & 0xFFF) | (ptr & 0xF000)
        
    def indexed(self, ptrIdx):
        """
           add data byte to the relevant pointer 
           Note - if data byte value is 0x80 the we should use the value in the value in extention register 

           used for an indexed or relative instruction
               not used for jump instructions
           Args:
             ptrIdx says which pointer is to be used.
           Returns:
             returns the address to be used.
           Raises:
        """
        offset = self.fetchIP()
        # debug code
        self.secondByte=format(offset, "02x")
#     debug line 
#        print("IDX", format(offset, "02x"), "ptrIdx", ptrIdx, "ptr", format(self.ptrs[ptrIdx], "04x"))
        if offset == 0x80:    # offset byte is -128 then use ext register
                              # note this should not be used for a jump address
            offset = self.ext
        elif offset & 0x80 != 0:    # offset is negative subtract from 256
            offset = offset - 256
        ptr = self.ptrs[ptrIdx]      # get which pointer is being used
        # we dont need to fix it as the pointer is now added to before fetching value
        # so the p0 or program counter is still pointing at the offset byte
        # removed: if ptrIdx == 0:  # IP has already incremented so fix this
        # removed:     ptr -= 1
        # DA feb 2020

        # add using just the first 12 bits of the pointer
        addr = self.addr12bit(ptr, offset)

        return addr

    def jumpIndexed(self, ptrIdx):
        """ an indexed or relative jump instruction
            it does not use the ext register if #80
            DA feb 2020
           Args:
             ptrIdx says which pointer is to be used.
           Returns:
             returns the address to be used.
           Raises:
        """
        offset = self.fetchIP()
        self.secondByte=format(offset, "02x")
        # debug print statement
        # print("IDX", format(offset, "02x"), "ptrIdx", ptrIdx, "ptr", format(self.ptrs[ptrIdx], "04x"))
        if offset & 0x80 != 0:    # offset is negative subtract from 256
            offset = offset - 256
        ptr = self.ptrs[ptrIdx]      # get which pointer is being used
        # we dont need to fix it as the pointer is now added to before fetching value
        # so the p0 or program counter is still pointing at the offset byte
        # removed: if ptrIdx == 0:  # IP has already incremented so fix this
        # removed:     ptr -= 1
        # DA feb 2020
        addr = self.addr12bit(ptr, offset)
        return addr

    def autoIndexed(self, ptrIdx):
        """
         an auto indexed instruction
         This is like the indexing mode except that the pointer register is pre-decremented or post-incremented by the displacement.
          - if the displacement is -2 the pointer register has 2 subtracted before the data is fetched,
           if it is +2 it has 2 added after.

          returns address to use to fetch data

        """
        oOffset = self.fetchIP()
        offset = oOffset
        self.secondByte=format(offset, "02x")

        if offset == 0x80:     # offset byte is -128 then use ext register
            offset = self.ext
        elif offset & 0x80 != 0:     # offset is negative subtract from 256
            offset = offset - 256
        if offset < 0:  # negative - adjust pointer before fetch
            self.ptrs[ptrIdx] = self.addr12bit(self.ptrs[ptrIdx], offset)
        addr = self.ptrs[ptrIdx]
        if offset > 0: # positive - adjust pointer after fetch
            self.ptrs[ptrIdx] = self.addr12bit(self.ptrs[ptrIdx], offset)
        # debug print line
        #    print("@IX", format(oOffset, "02x"), format(offset, "02x"), "ptrIdx", ptrIdx, "ptr", format(self.ptrs[ptrIdx], "04x"))
        return addr

    def inRange(self, val, start, leng):
        """   
          used to check if the opcode is one of a group
        """
        return val >= start and val < start+leng

    def sign(self, n):
        """
            return sign of a byte
            
        """
        return n & 0x80

    # Do add treating each nibble as a number from 0 to 9
    #  and set the flags   
    def decimalAdd(self, in1, in2):
        # spit the bytes into nibbles
        dOnes = (in1 & 0x0f) + (in2 & 0x0f)
        dTens = (in1 & 0xf0) + (in2 & 0xf0)
        # check if carry flag is set
        dOnes += 1 if (self.stat & 0x80 != 0) else 0
        # clear carry flag
        self.stat &= 0x7f
        if dOnes > 9:
            dOnes = dOnes - 10
            dTens += 0x10
        if dTens > 0x90:
            # tens nibble has overflowed
            # reduce it by 10 
            dTens -= 0xa0
            # set carry flag
            self.stat |= 0x80
        # create the return byte
        outVal = dTens + dOnes
        if self.debugOn:
            print("DecAdd", format(in1,"02x"), format(in2,"02x"), dOnes, dTens, outVal & 0xff)
        # return just the byte value 
        return outVal & 0xff

    def binaryAdd(self, in1, in2):
        """
         add 2 "bytes" using standard binary and set the flags
         todo DA is this maths correct for 2s compliment ?
         add the 2 bytes plus 1 if the carry flag set
        """ 
        outVal = in1 + in2 + (1 if (self.stat & 0x80 != 0) else 0)
        self.stat = self.stat & 0x3f # clear CYL and OV
        if outVal > 0xff:
            # number too big set the carry flag
            self.stat |= 0x80
        if self.sign(in1) == self.sign(in2) and self.sign(in1) != self.sign(outVal):
            # if the inputs had the same sign set the overflow flag if the sign has changed
            # todo DA does this work if the both large negative
            self.stat |= 0x40
        return outVal & 0xff

    
    def complimentaryAdd(self, in1, in2):
        """
            xor the first byte before doing an add
        """
        return self.binaryAdd(in1 ^ 0xff, in2)

    def doALU(self, opType, idxType, sourceVal, ptrIdx):
        debugStr = ""
        # Handle store
        if opType == 0x08: # opcodes are 0xc8..0xcf
            self.cycles += 18
            if idxType <= 3:
                addr = self.indexed(ptrIdx)
                debugStr += "ST " + format(addr, "04x") + ", " + format(self.acc, "02x")
                self.mem.write(addr, self.acc)
            else:
                addr = self.autoIndexed(ptrIdx)
                debugStr += "ST@ " + format(addr, "04x") + ", " + format(self.acc, "02x")
                self.mem.write(addr, self.acc)
            return debugStr
        # Other ops require a "memory" value
        if idxType <= 3:
            addr = self.indexed(ptrIdx)
            mem = self.mem.read(addr)
            self.cycles += 18
            debugStr += " " + format(addr, "04x") + " => " + format(mem, "02x")
        elif idxType == 4:
            mem = self.fetchIP()
            self.secondByte=format(mem, "02x")
            self.cycles += 10
            debugStr += "I " + format(mem, "02x")
        elif idxType <= 7:
            addr = self.autoIndexed(ptrIdx)
            mem = self.mem.read(addr)
            self.cycles += 18
            debugStr += "@ " + format(addr, "04x") + " => " + format(mem, "02x")
        else:
            mem = self.ext
            self.cycles += 6
            debugStr += "E " + format(mem, "02x")
        # Perform the operation
        if opType == 0x00: # opcodes are 0xc0..0xc7
            self.acc = mem
            debugStr = "LD" + debugStr
        elif opType == 0x10:
            self.acc = mem & self.acc
            debugStr = "AND" + debugStr
        elif opType == 0x18:
            self.acc = mem | self.acc
            debugStr = "OR" + debugStr
        elif opType == 0x20:
            self.acc = mem ^ self.acc
            debugStr = "XOR" + debugStr
        elif opType == 0x28:
            self.acc = self.decimalAdd(mem, self.acc)
            self.cycles += 5
            debugStr = "DAD" + debugStr
        elif opType == 0x30:
            self.acc = self.binaryAdd(mem, self.acc)
            self.cycles += 1
            debugStr = "ADD" + debugStr
        elif opType == 0x38:
            self.acc = self.complimentaryAdd(mem, self.acc)        
            self.cycles += 2
            debugStr = "CAD" + debugStr
        return debugStr
        
    def processOpcode(self, opcode):
        # bHalt = False  #removed halt stuff as that is not how it works
        debugStr = ""
        # print("opcode",format(opcode,"02x"))
        # ALU operations 0xc0 .. 0xff
        if self.inRange(opcode, 0xc0, 0x40):
            idxType = opcode & 0x07
            opType = opcode & 0x38
            debugStr = self.doALU(opType, idxType, self.acc, opcode&0x03)
        # ALU operations 0x40, 0x48, 0x50, .. 0x78
        elif self.inRange(opcode & 0x78, 0x40, 0x40) and opcode & 0x87 == 0:
            idxType = 8
            opType = opcode & 0x38
            debugStr = self.doALU(opType, idxType, self.acc, opcode&0x03)
        # XPAL and XPAH
        elif self.inRange(opcode, 0x30, 8):
            ptr = self.ptrs[opcode&0x03]
            ptr &= 0xff00 if opcode < 0x34 else 0xff
            ptr |= self.acc if opcode < 0x34 else (self.acc << 8)
            self.ptrs[opcode&0x03] = ptr
            self.acc = ptr & 0xff
            self.cycles += 8
            debugStr = "XPAL" if opcode < 0x34 else "XPAH"
            debugStr += str(opcode&0x03)
        # XPPC
        elif self.inRange(opcode, 0x3c, 4):
            ptr = self.ptrs[opcode&0x03]
            self.ptrs[opcode&0x03] = self.ptrs[0]
            self.ptrs[0] = ptr
            self.cycles += 7
            debugStr = "XPPC" + str(opcode&0x03)
        # Jumps
        elif self.inRange(opcode, 0x90, 16):
            jump = False
            if opcode < 0x94:
                jump = True
                debugStr = "JMP"
            elif opcode < 0x98:
                if self.acc & 0x80 == 0:
                    jump = True
                    debugStr = "JP True"
                else:
                    debugStr = "JP False"
            elif opcode < 0x9c:
                if self.acc == 0:
                    jump = True
                    debugStr = "JZ True"
                else:
                    debugStr = "JZ False"
            else:
                if self.acc != 0:
                    jump = True
                    debugStr = "JNZ True"
                else:
                    debugStr = "JNZ False"
            if jump:
                # opcode fetch is done by the indexed routine
                # removed the +1 as the program counter will be added to before fetching the next instruction
                # self.ptrs[0] = self.indexed(opcode&0x03) + 1
                # cannot use this routine as will use the ext register if value #80 - DA Feb 2020 
                # self.ptrs[0] = self.indexed(opcode&0x03)
                self.ptrs[0] = self.jumpIndexed(opcode&0x03)
                debugStr += " >>" + format(self.ptrs[0],"04x")
            else:
                # not jumping so skip over the 2nd byte
                # this will actually be pointing at the second byte but will add 1 before getting opcode
                #  actualy fetch second byte for the display
                offset = self.fetchIP()
                self.secondByte=format(offset, "02x")
                # do above instead of just moving on pointer
                # also should really do a 12 bit add
                #self.ptrs[0] += 1
            self.cycles += 11
        # ILD
        elif self.inRange(opcode, 0xa8, 4):
            ptr = self.indexed(opcode&0x03)
            self.acc = (self.mem.read(ptr) + 1) & 0xff
            self.mem.write(ptr, self.acc)
            self.cycles += 22
            debugStr = "ILD"
            debugStr += str(opcode&0x03)
        # DLD
        elif self.inRange(opcode, 0xb8, 4):
            ptr = self.indexed(opcode&0x03)
            self.acc = (self.mem.read(ptr) - 1) & 0xff
            self.mem.write(ptr, self.acc)
            self.cycles += 22
            debugStr = "DLD"
            debugStr += str(opcode&0x03)
        # DLY
        elif opcode == 0x8f:
            n = self.fetchIP()
            self.secondByte=format(n, "02x")
            leng = n & 0xff
            leng = 13 + 2 * self.acc + 2 * n + 512 * n
            self.acc = 0xff
            self.cycles += leng
            debugStr = "DLY"
        # XAE
        elif opcode == 0x01:
            n = self.acc
            self.acc = self.ext
            self.ext = n
            self.cycles += 1
            debugStr = "XAE"
        # SIO
        elif opcode == 0x19:
            self.ext = (self.ext >> 1) & 0x7f
            self.cycles += 5
            debugStr = "SIO"
        # SR
        elif opcode == 0x1c:
            self.acc = (self.acc >> 1) & 0x7f
            self.cycles += 5
            debugStr = "SR"
        # SRL
        elif opcode == 0x1d:
            self.acc = ((self.acc >> 1) & 0x7f) | (self.stat & 0x80)
            self.cycles += 5
            debugStr = "SRL"
        # RR
        elif opcode == 0x1e:
            self.acc = ((self.acc >> 1) & 0x7f) | (0x80 if (self.acc & 0x01 == 1) else 0)
            self.cycles += 5
            debugStr = "RR"
        # RRL
        elif opcode == 0x1f:
            n = self.acc
            self.acc = ((self.acc >> 1) & 0x7f) | (0x80 if (self.stat & 0x80 != 0) else 0)
            self.stat = (self.stat & 0x7f) | (0x80 if (n & 0x01 == 1) else 0)
            self.cycles += 5
            debugStr = "RRL"
        # HALT
        elif opcode == 0x00:
            # bHalt = True
            self.cycles += 8
        # CCL
        elif opcode == 0x02:
            self.stat &= 0x7f
            self.cycles += 5
            debugStr = "CCL"
        # SCL
        elif opcode == 0x03:
            self.stat |= 0x80
            self.cycles += 5
            debugStr = "SCL"
        # DINT
        elif opcode == 0x03:
            self.stat &= 0xf7
            self.cycles += 6
            debugStr = "DINT"
        # IEN
        elif opcode == 0x03:
            self.stat |= 0x08
            self.cycles += 6
            debugStr = "IEN"
        # CSA
        elif opcode == 0x06:
            self.acc = self.stat
            self.cycles += 5
            debugStr = "CSA"
        # CAS
        elif opcode == 0x07:
            self.stat = self.acc & 0xcf
            self.cycles += 5
            debugStr = "CAS"
        # NOP
        elif opcode == 0x08:
            self.cycles += 1
            debugStr = "NOP"
        # Unknown
        else:
            debugStr = "UNKNOWN " + format(opcode, "02x")

        return (debugStr)

# end of code

