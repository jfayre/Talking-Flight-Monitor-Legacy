-- companion script for TFM v1.3
	-- by Jason Fayre
-- adds support for the A2A C182 aircraft
-- scan for available hotkey slots starting at offset 0x3210
-- each slot is 4 bytes
-- byte 1: key code
-- byte 2: shift keys
-- bytes 3 and 4 are flags
ipc.log("scanning for available hotkey slots")
offset = 0x3210
count = 0
keys = {}
key = 1
for i = 1, 56, 1 do
    offset = 0x3210 + count
    shift = ipc.readUB(offset + 1)
    if ipc.readUD(offset) == 0 or shift == 16 or shift == 17 then 
        -- we found a free slot
        keys[key] = {offset = offset, flag = offset+ 3}
        key = key + 1
    end
count = count + 4
end
-- constants for keys
key_a = 65  
key_b = 66
key_c = 67
key_d = 68
key_e = 69
key_f = 70
key_g = 71
key_h = 72
key_i = 73
key_j = 74
key_k = 75
key_l = 76
key_m = 77
key_n = 78
key_o = 79
key_p = 80
key_q = 81
key_r = 82
key_s = 83
key_t = 84
key_u = 85
key_v = 86
key_w = 87
key_x = 88
key_y = 89
key_z= 90
mod_tab = 16
mod_shift_tab = 17

function set_key(slot, shift, key)
    ipc.writeStruct(keys[slot].offset, "2UB", key, shift)
end
-- set flag to let tfm know that the script is running
ipc.writeUB(0x66c7, 1)

-- define hotkeys

-- defroster increase, tab+d
set_key(3, mod_tab, key_d)
function defrost_inc(offset, value)
    if value == 0 then return end
    local t = ipc.readLvar("WindowDefrosterControlKnob")
    t = t + 10
    if t > 100 then t = 100 end
    ipc.writeLvar("WindowDefrosterControlKnob", t)
    ipc.writeUB(0x66c4, t)
    ipc.writeUB(keys[3].flag,0)
end
event.offset(keys[3].flag, "UB", "defrost_inc")

-- defroster decrease, shift+tab+d
set_key(4, mod_shift_tab, key_d)
function defrost_dec(offset, value)
    if value == 0 then return end
    local t = ipc.readLvar("WindowDefrosterControlKnob")
    t = t - 10
    if t < 0 then t = 0 end
    ipc.writeLvar("WindowDefrosterControlKnob", t)
    ipc.writeUB(0x66c4, t)
    ipc.writeUB(keys[4].flag,0)
end
event.offset(keys[4].flag, "UB", "defrost_dec")


-- fuel selector, tab+f
set_key(5, mod_tab, key_f)
function fuel_selector(offset, value)
    if value == 0 then return end
    local f = ipc.readLvar("FSelC182State")
    f = f + 1
    if f > 3 then 
        f = 0
    end
    ipc.writeLvar("FSelC182State", f)
    ipc.writeUB(keys[5].flag,0)
end
event.offset(keys[5].flag, "UB", "fuel_selector")

-- cabin heat increase, tab+h
set_key(6, mod_tab, key_h)
function heat_inc(offset, value)
    if value == 0 then return end
    local t = ipc.readLvar("CabinTempControl")
    t = t + 10
    if t > 100 then t = 100 end
    ipc.writeLvar("CabinTempControl", t)
    ipc.writeUB(0x66c3, t)
    ipc.writeUB(keys[6].flag,0)
end
event.offset(keys[6].flag, "UB", "heat_inc")

-- cabin heat decrease, tab+shift+h
set_key(7, mod_shift_tab, key_h)
function heat_dec(offset, value)
    if value == 0 then return end
    local t = ipc.readLvar("CabinTempControl")
    t = t - 10
    if t < 0 then t = 0 end
    ipc.writeLvar("CabinTempControl", t)
    ipc.writeUB(0x66c3, t)
    ipc.writeUB(keys[7].flag,0)
end
event.offset(keys[7].flag, "UB", "heat_dec")

-- windows
set_key(10, mod_tab, key_w)
function toggle_window(offset, value)
    if value == 0 then return end
    local wnd = ipc.readLvar("WindowLeft")
if wnd == 0 then
    ipc.writeLvar("WindowLeft", 1)
else
    ipc.writeLvar("WindowLeft", 0)
end
ipc.writeUB(keys[10].flag, 0)
end
event.offset(keys[10].flag, "UB", "toggle_window")

-- read panel variables into offsets
function battery(varname, value)
    ipc.writeUB(0x66c0, value)
end
event.Lvar("Battery1Switch",1000,"battery")
function alternator(varname, value)
    ipc.writeUB(0x66c5, value)
end
event.Lvar("Eng1_GeneratorSwitch",1000,"alternator")

function read_fsel(varname, value)
    ipc.writeUB(0x66c1, f)
end
event.lvar("FSelC182State", 1000, "read_fsel")
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

set_key(11, mod_tab, key_p)
function annunciator(offset, value)
    -- reset tfm annunciator offset
    ipc.writeDBL(0x4230, 0)
    lights = {}
    light_offset = 0x4230
    vars = {
            'VacRLight',
            'VacRLightBlinking',
            'VacLLight',
            'VacLLightBlinking',
            'VacLight',
            'VacLightBlinking',
            'OilPressLight',
            'OilPressLightBlinking',
            'FuelLLight',
            'FuelLLightBlinking',
            'FuelLight',
            'FuelRLight',
            'FuelRLightBlinking',
            'PitchTrimLight',
            'PitchTrimLightBlinking',
            'VoltsLight',
            'VoltsLightBlinking'}
    for i, v in ipairs(vars) do
        lights[v] = ipc.readLvar(v)
        ipc.log(v .. " " .. lights[v])
    end
    if lights["VacLLight"] == 1 or lights['VacLLightBlinking'] == 1 then
        ipc.writeUB(0x4230, 1)
    end
    if lights["VacRLight"] == 1 or lights['VacRLightBlinking'] == 1 then
        ipc.writeUB(0x4231, 1)
    end
    if lights["VacLight"] == 1 or lights['VacLightBlinking'] == 1 then
        ipc.writeUB(0x4232, 1)
    end
    if lights["FuelLLight"] == 1 or lights['FuelLLightBlinking'] == 1 then
        ipc.writeUB(0x4233, 1)
    end
    if lights["FuelRLight"] == 1 or lights['FuelRLightBlinking'] == 1 then
        ipc.writeUB(0x4234, 1)
    end
    if lights["OilPressLight"] == 1 or lights['OilPressLightBlinking'] == 1 then
        ipc.writeUB(0x4235, 1)
    end
    if lights["VoltsLight"] == 1 or lights['VoltsLightBlinking'] == 1 then
        ipc.writeUB(0x4236, 1)
    end
    if lights["PitchTrimLight"] == 1 or lights['PitchTrimLightBlinking'] == 1 then
        ipc.writeUB(0x4237, 1)
    end

end
event.intercept(0x4238, "UB", "annunciator")

-- complete overhaul
function repair_all(offset, value)
    if value == 0 then return end
    ipc.log ("complete overhaul")
    ipc.writeLvar("SystemCondSelectFSX", 100)
    ipc.writeLvar("SystemCondValueFSX", 0)
    ipc.writeLvar("Eng1_DamageFlagOvertorque", 0)
    ipc.writeLvar("Eng1_DamageFlagHighCAT", 0)
    ipc.writeLvar("Eng1_DamageFlagNoADI", 0)
    ipc.writeLvar("Eng1_DamageFlagHighCHT", 0)
    ipc.writeLvar("Eng1_WearFlag", 0)
    ipc.writeLvar("Eng1_SuddenDamageFlag", 0)
    ipc.writeLvar("Eng1_ShockCoolingFlag", 0)
    ipc.writeLvar("RandStatic1", 0)
    ipc.writeLvar("RandStatic1b", 0)
    ipc.writeLvar("RandStatic1c", 0)
    ipc.writeLvar("RandStatic1d", 0)
    ipc.writeLvar("E1H", 0)
    ipc.writeLvar("E1S", 0)
    ipc.writeLvar("Prop1Strike", 0)
    ipc.writeLvar("ExtendLeftGear", 1)
    ipc.writeLvar("ExtendRightGear", 1)
    ipc.writeLvar("RepairClickSound", 1)
    ipc.writeLvar("CompleteOverhaulButton", 1)

end
event.intercept(0x4240, "UB", "repair_all")
