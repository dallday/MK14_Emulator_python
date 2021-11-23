# MK14_Emulator_python
A MK14 emulator written in Python thanks to Rob Dobson


This emulator is based on Rob's MK14PyEm project
https://github.com/robdobsn/MK14PyEm

It fixes the issue with the instruction fetch sequence, and the jump when the offset is oxFF.
The display is also handles in the same way that the MK14 does in that the 7 segments are multiplexed rather than being fixed.

ToDo :- to handle the keys in the same way as the original MK14 does.
        at present you need to click on the buttons as the computer keyboard does not work for it
        to make the instruction execute at the correct speed as per the original SC/MP
	to provide an interrupt process\ 
ToDo :- make the keyboard like the MK14 one.\
ToDo :- add a reset button to return to the monitor.\

Hopefully the comments in the code will help you follow how it works.

Syntax is 
	python3 MK14.py [hexfile]\
	[hexfile] is an optional file to load in the Intel HEX format.

Use "python3 MK14.py" to load and run the MK14 monitor program\
      select 0f12 and press Go to run duck shoot.
      
Use "python3 MK14.py message.hex" to load the monitor, and the message program and then run the monitor\
     select 0f20 and press Go to run the message program

Use "python3 MK14DuckShoot.py"  to load and run the MK14 duckshoot. The monitor is loaded but this will start in the duckshoot program.
 

 The various files
 
 	MK14.py          runs the MK14 monitor program, if no hex file specified loads Duckshoot.
	MK14_V2.py 	 runs in debug mode with (maybe ?) a different version of the MK14 monitor program.
	MK14DuckShoot.py Loads and starts the Duck shoot from the MK14 manual. 
	ins8060cpu.py 	 provides the emulate the SC/MP propcessor.
	mk14memmap.py 	 provides the emulation of the Memory Map for the MK14.
	mk14ui.py 	 handles the 7 segment display and the keyboard.
	message.hex	 The program to display a message on the screen.

I suspect both monitor programs are version 2 of the monitor that starts with 0000 00 on reset.


Thanks to Rob for the original idea.
