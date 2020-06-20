-- TFM launcher script for a2a aircraft
-- This script is used to launch the other lua scripts, based on loaded aircraft.
function launch(offset, ac)
ipc.log(ac)
if string.find(ac, "Bonanza") then 
    ipc.log("starting bonanza script")
    ipc.runlua("tfm_bonanza.lua") end
if string.find(ac, "Cherokee") then 
    ipc.log("starting Cherokee script")
    ipc.runlua("tfm_cherokee.lua") end
if string.find(ac, "C172") then 
    ipc.log("Starting C172 script")
    ipc.runlua("tfm_c172.lua") end
if string.find(ac, "C182") then 
    ipc.log("Starting c182 script")
    ipc.runlua("tfm_c182.lua") end
end
event.offset(0x3d00, "STR", 255, "launch")
