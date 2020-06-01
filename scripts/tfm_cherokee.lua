-- companion script for TFM v1.3
-- by Jason Fayre
-- adds support for the A2A Cherokee aircraft
-- read panel variables into offsets
function battery(varname, value)
    ipc.writeUB(0x66c0, value)
end
event.Lvar("Battery1Switch",1000,"battery")
-- functions to set fuel quantity.
function fuel_wl (offset, value)
    if value == 0 then
        return
    end
    ipc.writeLvar("FuelLeftWingTank", value)
    ipc.sleep(250)
end
event.intercept(0x4200, "FLT", "fuel_wl")
function fuel_wr (offset, value)
    if value == 0 then
        return
end

    ipc.writeLvar("FuelRightWingTank", value)
    ipc.sleep(250)

end
event.intercept(0x4204, "FLT", "fuel_wr")
function oil(offset, value)
    if value == 0 then
        return
    end
    ipc.log("writing oil: " .. value)
    ipc.writeLvar("Eng1_OilQuantity", value)
    ipc.sleep(100)
    ipc.writeLvar("SystemCondSelectFSX", 46)
    ipc.sleep(100)
    ipc.writeLvar("SystemCondValueFSX", value)
    ipc.sleep(250)
    value = ipc.readLvar("Eng1_OilQuantity")
    ipc.writeDBL(0x4230, value)
end
event.intercept(0x4230, "DBL", "oil")

-- functions for setting passengers and weight
function seat1(offset, value)
    if value > 0 then
        ipc.log("setting seat 1: " .. value)
        ipc.writeLvar("Seat1Character", 1)
        ipc.sleep(100)
        ipc.writeLvar("Character1Weight", value)
        ipc.sleep(100)
    else
        ipc.log("removing pilot and all passengers")
        ipc.writeLvar("Seat1Character", 0)
        ipc.sleep(100)
        ipc.writeLvar("Seat2Character", 0)
        ipc.sleep(100)
        ipc.writeLvar("Seat3Character", 0)
        ipc.sleep(100)
        ipc.writeLvar("Seat4Character", 0)
    end
ipc.writeUW(0x4214, 1)
end
event.intercept(0x4214, "UW", "seat1")
function seat2(offset, value)
    if value > 0 then
        ipc.log("setting seat 2: " .. value)
        ipc.writeLvar("Seat2Character", 2)
        ipc.sleep(100)
        ipc.writeLvar("Character2Weight", value)
        ipc.sleep(100)
    else
        ipc.log("removing passenger 1")
        ipc.writeLvar("Seat2Character", 0)
    end
end
event.intercept(0x4216, "UW", "seat2")
function seat3(offset, value)
    if value > 0 then
        ipc.log("setting seat 3: " .. value)
        ipc.writeLvar("Seat3Character", 3)
        ipc.sleep(100)
        ipc.writeLvar("Character3Weight", value)
        ipc.sleep(100)
    else
        ipc.log("removing passenger 2")
        ipc.writeLvar("Seat3Character", 0)
    end
end
event.intercept(0x4218, "UW", "seat3")
function seat4(offset, value)
    if value > 0 then
        ipc.log("setting seat 4: " .. value)
        ipc.writeLvar("Seat4Character", 4)
        ipc.sleep(100)
        ipc.writeLvar("Character4Weight", value)
        ipc.sleep(100)
    else
        ipc.log("removing passenger 3")
        ipc.writeLvar("Seat4Character", 0)
    end
end
event.intercept(0x4220, "UW", "seat4")
function payload_weight(varname, value)
    ipc.writeUW(0x4222, value)
end
event.Lvar("PayloadWeight", 3000, "payload_weight")

-- functions for aircraft controls. These are controlled by lua flags set by fSUIPC
function toggle_window()
local wnd = ipc.readLvar("WindowLeft")
if wnd == 0 then
    ipc.writeLvar("WindowLeft", 1)
else
    ipc.writeLvar("WindowLeft", 0)
end
end
event.flag(1, "toggle_window")
function fuel_selector()
    local f = ipc.readLvar("FSelCherokeeState")
    f = f + 1
    if f > 2 then 
        f = 0
    end
    ipc.writeLvar("FSelCherokeeState", f)
    ipc.writeUB(0x66c1, f)
end
event.flag(2, "fuel_selector")


function heat_inc()
    local t = ipc.readLvar("CabinTempControl")
    t = t + 10
    if t > 100 then t = 100 end
    ipc.writeLvar("CabinTempControl", t)
    ipc.writeUB(0x66c3, t)
end
event.flag(5, "heat_inc")

function heat_dec()
    local t = ipc.readLvar("CabinTempControl")
    t = t - 10
    if t < 0 then t = 0 end
    ipc.writeLvar("CabinTempControl", t)
    ipc.writeUB(0x66c3, t)
end
event.flag(6, "heat_dec")
function defrost_inc()
    local t = ipc.readLvar("WindowDefrosterControlKnob")
    t = t + 10
    if t > 100 then t = 100 end
    ipc.writeLvar("WindowDefrosterControlKnob", t)
    ipc.writeUB(0x66c4, t)
end
event.flag(7, "defrost_inc")

function defrost_dec()
    local t = ipc.readLvar("WindowDefrosterControlKnob")
    t = t - 10
    if t < 0 then t = 0 end
    ipc.writeLvar("WindowDefrosterControlKnob", t)
    ipc.writeUB(0x66c4, t)
end
event.flag(8, "defrost_dec")
function carb_inc()
    local c = ipc.readLvar("Eng1_CarbHeatSwitch")
    c = c + 10
    if c > 100 then c = 100 end
    ipc.writeLvar("Eng1_CarbHeatSwitch", c)
    ipc.writeUB(0x66c5, c)
end
event.flag(9, "carb_inc")
function carb_dec()
    local c = ipc.readLvar("Eng1_CarbHeatSwitch")
    c = c - 10
    if c < 0 then c = 0 end
    ipc.writeLvar("Eng1_CarbHeatSwitch", c)
    ipc.writeUB(0x66c5, c)
end
event.flag(10, "carb_dec")

