-- companion script for TFM v1.2
-- by Jason Fayre
-- adds support for the A2A Bonanza aircraft
-- read panel variables into offsets
function battery(varname, value)
    ipc.writeUB(0x66c0, value)
end
event.Lvar("Battery1Switch",1000,"battery")
function tt_left_pump(varname, value)
    ipc.writeUB(0x66c1, value)
end
event.Lvar("TipTankLeftPumpSwitch", 1000, "tt_left_pump")
function tt_right_pump(varname, value)
    ipc.writeUB(0x66c2, value)
end
event.Lvar("TipTankRightPumpSwitch", 1000, "tt_right_pump")
function fsel (varname, value)
    ipc.writeUB(0x66c3, value)
end
event.Lvar("FSelBonanzaState", 1000, "fsel")
function tt_available(varname, value)
    ipc.writeUB(0x66c4, value)
end
event.Lvar("TipTanksPresent", 2000, "tt_available")
function window(varname, value)
    ipc.writeUB(0x66c5, value)
end
event.Lvar("WindowLeft", 1000, "window")
function fan(varname, value)
    ipc.writeUB(0x66c6, value)
end
event.Lvar ("VentCabinFanSwitch", 1000, "fan")
function heat(varname, value)
    ipc.writeUB(0x66c7, value)
end
event.Lvar ("CabinTempControl", 1000, "heat")
function defrost (varname, value)
    ipc.writeUB(0x66c8, value)
end
event.Lvar ("WindowDefrosterControlKnob", 1000, "defrost")
function s1(varname, value)
    ipc.writeFLT(0x4200, value)
end







event.Lvar("Seat1Character", 2000, "s1")