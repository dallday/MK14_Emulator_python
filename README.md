# MK14_Emulator_python
A MK14 emulator written in Python thanks to Rob Dobson

***************  The Go button does not work in the emulator - seems I have not quite got it right *****************

This emulator is based on Rob's MK14PyEm project
https://github.com/robdobsn/MK14PyEm

It fixes the issue with the instruction fetch sequence, and the jump when the offset is oxFF.
The display is also handles in the same way that the MK14 does in that the 7 segments are multiplexed rather than being fixed.

ToDo :- to handle the keys in the same way as the original MK14 did.
        to make the instruction execute at the correct speed as per the original SC/MP

Hopefully the comments in the code will help you follow how it works.

To run use 
 python3 MK14DuckShoot.py
        to run the MK14 duckshoot
 python3 MK14.py
        to run the MK14 monitor program - GO does not seem to work correctly.
        

Thanks to Rob for the original idea.
