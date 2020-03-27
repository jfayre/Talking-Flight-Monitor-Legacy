-- read panel variables into offsets
function battery(varname, value)
    ipc.writeUB(0x66c0, value)
end
function tt_left_pump(varname, value)
    ipc.writeUB(0x66c1, value)
end
function tt_right_pump(varname, value)
    ipc.writeUB(0x66c2, value)
end
function fsel (varname, value)
    ipc.writeUB(0x66c3, value)
end
function tt_available(varname, value)
    ipc.writeUB(0x66c4, value)
end
event.Lvar("Battery1Switch",1000,"battery")
event.Lvar("TipTankLeftPumpSwitch", 1000, "tt_left_pump")
event.Lvar("TipTankRightPumpSwitch", 1000, "tt_right_pump")
event.Lvar("FSelBonanzaState", 1000, "fsel")
event.Lvar("TipTanksPresent", 2000, "tt_available")