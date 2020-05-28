-- companion script for TFM v1.2
-- by Jason Fayre
-- adds support for the A2A Cherokee aircraft
-- read panel variables into offsets
function battery(varname, value)
    ipc.writeUB(0x66c0, value)
end
function fsel (varname, value)
    ipc.writeUB(0x66c1, value)
end
function window(varname, value)
    ipc.writeUB(0x66c2, value)
end
function heat(varname, value)
    ipc.writeUB(0x66c3, value)
end
function defrost (varname, value)
    ipc.writeUB(0x66c4, value)
end
function carb_heat(varname, value)
    ipc.writeUB(0x66c5, value)
end
function starter(varname, value)
    ipc.sleep(1000)
    ipc.writeLvar("L:Eng1_StarterSwitch",0)
end

event.Lvar("Battery1Switch",1000,"battery")
event.Lvar("FSelCherokeeState", 1000, "fsel")
event.Lvar("WindowLeft", 1000, "window")
-- event.Lvar ("VentCabinFanSwitch", 1000, "fan")
event.Lvar ("CabinTempControl", 1000, "heat")
event.Lvar ("WindowDefrosterControlKnob", 1000, "defrost")
event.Lvar ("Eng1_CarbHeatSwitch", 1000, "carb_heat")
event.Lvar ("Eng1_StarterSwitch", 500, "starter")