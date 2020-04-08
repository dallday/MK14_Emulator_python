#
#
#  python emulation of the MK14 playing duckshoot
#
#

import mk14ui
import ins8060cpu


def hexVal(inStr, pos, len):
    return int(inStr[pos:pos + len], 16)


def fromHexLines(hexLines):
    memOut = []
    for hexLine in hexLines:
        leng = hexVal(hexLine, 1, 2)
        if leng > 0:
            addr = hexVal(hexLine, 3, 4)
            memVals = []
            for i in range(leng):
                memVals.append(hexVal(hexLine, 9 + i * 2, 2))
            memOut.append([addr, memVals])
    return memOut

hexLines = [
    ":180F1200C40D35C40031C401C8F4C410C8F1C400C8EEC40801C0E71EB2",
    ":180F2A00C8E49404C4619002C400C9808F01C0D89C0EC180E4FF980811",
    ":160F4200C8CEC0CAE480C8C64003FC0194D6B8BF98C8C40790CEDD"
]
memVals = fromHexLines(hexLines)

# to use with debug working
#cpu = ins8060cpu.CPU_INS8060(memVals, 0xf11, True, {"base":0xf0f,"count":3})
# to use without debug
cpu = ins8060cpu.CPU_INS8060(memVals, 0xf11, False)

#mk14UI.tkRoot.after(1000, testUpdateUI)
mk14UI = mk14ui.MK14_UI(cpu.getMemMap())

closing = False
while not closing:
    cpu.service()
    closing = mk14UI.service()
mk14UI.close()
