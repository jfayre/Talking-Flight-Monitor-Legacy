-- companion script for TFM v1.2
-- by Jason Fayre
-- adds support for the A2A Cherokee aircraft
-- read panel variables into offsets
function battery(varname, value)
    ipc.writeUB(0x66c0, value)
end
function fsel (varname, value)
    ipc.writeUB(0x66c3, value)
end
function window(varname, value)
    ipc.writeUB(0x66c5, value)
end
function fan(varname, value)
    ipc.writeUB(0x66c6, value)
end
function heat(varname, value)
    ipc.writeUB(0x66c7, value)
end
function defrost (varname, value)
    ipc.writeUB(0x66c8, value)
end
event.Lvar("Battery1Switch",1000,"battery")
event.Lvar("FSelCherokeeState", 1000, "fsel")
event.Lvar("WindowLeft", 1000, "window")
event.Lvar ("VentCabinFanSwitch", 1000, "fan")
event.Lvar ("CabinTempControl", 1000, "heat")
event.Lvar ("WindowDefrosterControlKnob", 1000, "defrost")