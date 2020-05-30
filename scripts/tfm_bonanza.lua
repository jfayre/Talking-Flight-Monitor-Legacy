-- companion script for TFM v1.2
-- by Jason Fayre
-- adds support for the A2A Bonanza aircraft
-- read panel variables into offsets
function battery(varname, value)
    ipc.writeUB(0x66c0, value)
end
-- event.Lvar("Battery1Switch",1000,"battery")
function tt_left_pump(varname, value)
    ipc.writeUB(0x66c1, value)
end
-- event.Lvar("TipTankLeftPumpSwitch", 1000, "tt_left_pump")
function tt_right_pump(varname, value)
    ipc.writeUB(0x66c2, value)
end
-- event.Lvar("TipTankRightPumpSwitch", 1000, "tt_right_pump")
function fsel (varname, value)
    ipc.writeUB(0x66c3, value)
end
-- event.Lvar("FSelBonanzaState", 1000, "fsel")
function tt_available(varname, value)
    ipc.writeUB(0x66c4, value)
end
-- event.Lvar("TipTanksPresent", 2000, "tt_available")
function window(varname, value)
    ipc.writeUB(0x66c5, value)
end
-- event.Lvar("WindowLeft", 1000, "window")
function fan(varname, value)
    ipc.writeUB(0x66c6, value)
end
-- event.Lvar ("VentCabinFanSwitch", 1000, "fan")
function heat(varname, value)
    ipc.writeUB(0x66c7, value)
end
-- event.Lvar ("CabinTempControl", 1000, "heat")
function defrost (varname, value)
    ipc.writeUB(0x66c8, value)
end
-- event.Lvar ("WindowDefrosterControlKnob", 1000, "defrost")

function fuel_wl (offset, value)
    if value == 0 then
        return
    end
    ipc.writeLvar("FuelLeftWingTank", value)
    ipc.sleep(250)
end
event.offset(0x4200, "FLT", "fuel_wl")
function fuel_wr (offset, value)
    if value == 0 then
        return
end

    ipc.writeLvar("FuelRightWingTank", value)
    ipc.sleep(250)
end
event.offset(0x4204, "FLT", "fuel_wr")
function fuel_tl (offset, value)
    if value == 0 then
        return
    end
    ipc.writeLvar("FuelLeftTipTank", value)
    ipc.sleep(250)
end
event.offset(0x4208, "FLT", "fuel_tl")
function fuel_tr (offset, value)
    if value == 0 then
        return
    end
    ipc.writeLvar("FuelRightTipTank", value)
    ipc.sleep(250)
end
event.offset(0x420c, "FLT", "fuel_tr")
function oil(offset, value)
    if value == 0 then
        return
    end
    -- value = math.floor(value*10)/10
    ipc.log("writing oil: " .. value)
    ipc.writeLvar("Eng1_OilQuantity", value)
    -- ipc.sleep()
    ipc.writeLvar("SystemCondSelectFSX", 46)
    --ipc.sleep(500)
    ipc.writeLvar("SystemCondValueFSX", value)
end
event.offset(0x4230, "DBL", "oil")
function seat1(offset, value)
    if value > 0 then
        ipc.writeLvar("Seat1Character", 1)
        ipc.sleep(100)
        ipc.writeLvar("Character1Weight", value)
        ipc.sleep(100)
    else
        ipc.writeLvar("Seat1Character", 0)
        ipc.sleep(100)
        ipc.writeLvar("Seat2Character", 0)
        ipc.sleep(100)
        ipc.writeLvar("Seat3Character", 0)
        ipc.sleep(100)
        ipc.writeLvar("Seat4Character", 0)
    end
end
event.offset(0x4214, "UW", "seat1")
function seat2(offset, value)
    if value > 0 then
        ipc.writeLvar("Seat2Character", 2)
        ipc.sleep(100)
        ipc.writeLvar("Character2Weight", value)
        ipc.sleep(100)
    else
        ipc.writeLvar("Seat2Character", 0)
    end
end
event.offset(0x4216, "UW", "seat2")
function seat3(offset, value)
    if value > 0 then
        ipc.writeLvar("Seat3Character", 3)
        ipc.sleep(100)
        ipc.writeLvar("Character3Weight", value)
        ipc.sleep(100)
    else
        ipc.writeLvar("Seat3Character", 0)
    end
end
event.offset(0x4218, "UW", "seat3")
function seat4(offset, value)
    if value > 0 then
        ipc.writeLvar("Seat4Character", 4)
        ipc.sleep(100)
        ipc.writeLvar("Character4Weight", value)
        ipc.sleep(100)
    else
        ipc.writeLvar("Seat4Character", 0)
    end
end
event.offset(0x4220, "UW", "seat4")
function payload_weight(varname, value)
    ipc.writeUW(0x4222, value)
end
event.Lvar("PayloadWeight", 3000, "payload_weight")



