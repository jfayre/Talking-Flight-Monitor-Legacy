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
event.Lvar("TipTanksPresent", 3000, "tt_available")
function defrost (varname, value)
    ipc.writeUB(0x66c8, value)
end
-- event.Lvar ("WindowDefrosterControlKnob", 1000, "defrost")
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
function fuel_tl (offset, value)
    if value == 0 then
        return
    end
    ipc.writeLvar("FuelLeftTipTank", value)
    ipc.sleep(250)
end
event.intercept(0x4208, "FLT", "fuel_tl")
function fuel_tr (offset, value)
    if value == 0 then
        return
    end
    ipc.writeLvar("FuelRightTipTank", value)
    ipc.sleep(250)
end
event.intercept(0x420c, "FLT", "fuel_tr")
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
function toggle_fan(flag)
    var = "VentCabinFanSwitch"
    local f = ipc.readLvar(var)
    if f == 0 then
        ipc.writeLvar(var, 1)
        f = 1
    else
        ipc.writeLvar(var, 0)
        f = 0
    end
    ipc.writeUB(0x66c6, f)
end
event.flag(0, "toggle_fan")
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
    local f = ipc.readLvar("FSelBonanzaState")
    f = f + 1
    if f > 2 then 
        f = 0
    end
    ipc.writeLvar("FSelBonanzaState", f)
    ipc.writeUB(0x66c3, f)
end
event.flag(2, "fuel_selector")

function left_pump()
    local var = "TipTankLeftPumpSwitch"
    local val = ipc.readLvar(var)
    if val == 0 then
        ipc.writeLvar(var, 1)
        val = 1
    else
        ipc.writeLvar(var, 0)
        val = 0
    end
    ipc.writeUB(0x66c1, val)
end
event.flag(3, "left_pump")

function right_pump()
    local var = "TipTankRightPumpSwitch"
    local val = ipc.readLvar(var)
    if val == 0 then
        ipc.writeLvar(var, 1)
        val = 1
    else
        ipc.writeLvar(var, 0)
        val = 0
    end
    ipc.writeUB(0x66c2, val)
end
event.flag(4, "right_pump")

function heat_inc()
    local t = ipc.readLvar("CabinTempControl")
    t = t + 10
    if t > 100 then t = 100 end
    ipc.writeLvar("CabinTempControl", t)
    ipc.writeUB(0x66c7, t)
end
event.flag(5, "heat_inc")

function heat_dec()
    local t = ipc.readLvar("CabinTempControl")
    t = t - 10
    if t < 0 then t = 0 end
    ipc.writeLvar("CabinTempControl", t)
    ipc.writeUB(0x66c7, t)
end
event.flag(6, "heat_dec")
function defrost_inc()
    local t = ipc.readLvar("WindowDefrosterControlKnob")
    t = t + 10
    if t > 100 then t = 100 end
    ipc.writeLvar("WindowDefrosterControlKnob", t)
    ipc.writeUB(0x66c8, t)
end
event.flag(7, "defrost_inc")

function defrost_dec()
    local t = ipc.readLvar("WindowDefrosterControlKnob")
    t = t - 10
    if t < 0 then t = 0 end
    ipc.writeLvar("WindowDefrosterControlKnob", t)
    ipc.writeUB(0x66c8, t)
end
event.flag(8, "defrost_dec")

function fan_speed()
    local s = ipc.readLvar("VentCabinOverheadFreshAirControl")
    s = s + 1
    if s >4 then s = 0 end
    ipc.writeLvar("VentCabinOverheadFreshAirControl", s)
end
event.flag(9, "fan_speed")
