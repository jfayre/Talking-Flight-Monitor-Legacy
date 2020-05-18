# Talking Flight Monitor (TFM)
An accessibility layer for Microsoft FSX and Lockhede Martin Prepar3d.

## downloading
* [download the latest version](https://www.bvipilots.net/files/addons/tfm-setup.exe)
## features
* reads closest city to the aircraft based on simulator GPS position
* reads many  aircraft instruments and switches automatically
* sonification of key aircraft parameters, such as pitch and bank.
* Sonification of flight director to aide in manual flight
* Reads SimConnect message windows, such as the ones displayed by GSX and Pro ATC/x
* reads Radar Contact ATC menus
* allows control of the aircraft autopilot through a simple interace
* provides many hotkeys for querying aircraft instruments on demand

## Requirements
In order to use this software, you will need either [Microsoft Flight Simulator X](https://store.steampowered.com/app/314160/Microsoft_Flight_Simulator_X_Steam_Edition/), or [Lockheed Martin Prepar3d](https://www.prepar3d.com/).

In order to read the nearest city to your aircraft, you will need a free [GeoNames](http://www.geonames.org) account. Once you create the account, enable web access under your profile. 

You will need the latest version of Pete Dowson's [FSUIPC module](http://www.fsuipc.com). If you are using Microsoft FSX, you need version 4. 
Prepar3d requires version 5. You do not need to purchase a registration for Talking Flight Monitor to work. 
## Quick Start
* Install Talking Flight Monitor by running the installer you downloaded.
* Start your simulator  and start a flight.
* Start Talking Flight Monitor from your desktop.
* The first time it is run, you will be prompted for your Geonames username.
* You should now hear the name of the closest city to your aircraft location.
## configuring the program
Under the Application pull-down menu, select Settings to bring up the settings dialog. You can configure all aspects of Talking Flight Monitor through this dialog. Here is a brief description of each setting.
### General tab
* Geonames username: This is where you can change your Geonames username
* Use SAPI for speech output: Choose to use either SAPI or your screen reader voice
* SAPI speech rate: adjust the rate of SAPI speech. ange is from 1 to 10.
* Enable flight following: enable reading of closest city to your aircraft
* Enable reading of instrumentation: automatically reads various aircraft instruments.
* Read SimConnect messages: automatically reads in-simulator pop-up messages from various add-ons such as gSX, Pro ATC/X, etc.
* Enable GPWS callouts: Ground proximity warning system. provides audible indication of key altitudes when landing.
* Enable ILS: Reads information related to ILS when landing, such as glide slope and localiser.
* Announce groundspeed while on ground: reads groundspeed while taxiing and before takeoff.
* Use metric measurements: Announce distances in Kilometers. Altitudes will always be in feet.
### Timing tab
Adjusts various timing intervals. Options are self-explanitory.

### Hotkeys
There are several hotkeys for use when Flight Following is running. The keys are set up as global, so you don't need to be in the Flight Following window to use them. All hotkeys can be changed from this tab.

The keys use a layered aproach. First press the command key, which is Right Square Bracket by default. Then press the desired command. 
The currently available keys are:
* ]: enters command mode (use before all other keys)
* numbers 1 through 0: read info for individual fuel tanks
* a: read altitude above sea level (ASL).
* shift+a: toggle GPWS (ground proximity warning system) announcements
* b: fuel burn rate (in pounds per hour)
* c: read nearest city
* d: read distance and time to destination
* f: fuel report
* Shift+f: toggle announcement of flap angle
* Ctrl+F: audible flight director (see below)
* g: read  altitude above ground (AGL)
* h: read heading
* Shift+i: toggle reading of ILS info such as localiser and glideslope
* m: mach speed
* Ctrl+m: read pitch and bank angle periodically
* o: read outside ambient temperature
* r: read the last SimConnect message displayed.
* shift+r: mute simconnect messages
* s: read indicated airspeed
* t: read true airspeed
* shift+t: toggle announcement of aircraft trim
* v: vertical speed
* w: read next waypoint
* [ (left bracket): audible aircraft attitude indication (see below)
* shift+p: Toggle announcements of autopilot parameters
* i: read wind information
* control+h: toggle runway guidance mode


## audible attitude indications
Flight Following contains four modes that allow you to hear the pitch and bank of your aircraft.
### attitude mode
In "Attitude mode", you will hear a constant tone in the center channel to indicate pitch. Pitch down and pitch up are represented by slightly different sounding tones. The higher the tone, the higher your aircraft pitch.
Bank is represented by a beeping tone in either the right or left stereo channel to indicate the direction of bank. The higher the tone, the higher your bank angle.
### flight director mode
In Flight Director mode, the tones are identical to attitude mode, but the tones indicate the direction you need to turn to follow the flight director.
### manual flight mode
In Manual Flight mode, the pitch and bank angle are read every few seconds. The interval is adjustable in the settings dialog.
### runway guidance mode
Runway guidance mode is designed to help you hold a constant heading on takeoff or landing. When you turn on runway guidance, the current heading of your aircraft is recorded. You will then hear tones in the left or right stereo channel to let you know if you are going off course.

## controling autopilot and radios
The Talking Flight Monitor window contains several edit fields that allow you to control the aircraft's autopilot and com radios directly. To change a setting, just type the value you want into the edit box and press Enter.

## experimental A2A aircraft support
TFM now contains experimental support for the payware aircraft from A2A Simulations. Initially, the Beachcraft Bonanza is supported, with plans to add support for the C182 Skylane and the Piper Cherokee in the future.
You are able to check various aircraft instruments, as well as control a few aircraft systems.
### enabling A2A support
The A2A aircraft support requires a registered version of FSUIPC. 
To install the A2A support:
1. In your TFM install folder, there is a folder called "scripts". Copy the tfm_bonanza.lua file from  this folder into your FSUIPC folder. This should be C:\program files\Lockheed Martin\Prepar3D v4\Modules
2. Add the following to the end of your FSUIPC5.ini file, which is in the same folder where you placed the lua file. Note that the file is called fsuipc6.ini if you are using fSUIPC 6:
```
[Auto.Bonanza]
1=Lua tfm_bonanza
```
### hotkeys
When TFM detects you are running a supported A2A aircraft, the following hotkeys will be enabled. These also follow a similar layered command mode as the rest of TFM. The command key is the left square bracket. 
Note that these keys are not part of the TFM settings dialog yet. The dialog will be updated once the A2A support is finalized. For now, the keys can be changed by editing the tfm.ini file.
* [: command key
* 1: engine cylinder head temperature
* 2: engine exhaust gas temperature
* 3: engine RPM
* 4: oil temperature
* 5: oil pressure
* 6: manifold pressure
* 7: Ammeter
* 8: volt meter
* a: toggle cabin air circulation fan
* d: check or increase windshield defroster setting (keep pressing d to adjust by 10 percent increments, press left bracket again when done)
* shift+d: check or decrease windshield defroster setting (keep pressing d to adjust by 10 percent increments, press left bracket again when done)
* f: fuel tank levels
* shift+f: fuel flow
* h: check or increase cabin heat setting (keep pressing h to adjust by 10 percent increments, press left bracket again when done)
* shift+h: check or decrease cabin heat setting (keep pressing shift+h to adjust by 10 percent increments, press left bracket again when done)
* l: toggle left tip tank fuel pump
* r: toggle right tip tank fuel pump
* t: read cabin temperature
* w: open and close cabin window

## Running from Source
* Get the latest python 3.7 ([Python releases](https://www.python.org/downloads/))
* Install the latest pywin32 release ([pywin32 releases](https://github.com/mhammond/pywin32/releases))
    * filename: `pywin32-xxx.win32-py3.7.exe`
    * Install with the installer, not using pip!
* Run the following in the root of the source directory:
```
pip install -r requirements.txt
```


## Building a Binary Version
This requires PyInstaller to be installed. Install it like so:
```
pip install pyinstaller
```
Once PyInstaller is installed, execute the following from the root of the checkout:
```
pyinstaller tfm.spec
```
Disregard the warning about UPX not being present.


## Bugs and issues
* Please report bugs via the github issues tab.
* It is useful to attach the error.log file to any issues.
    
### Known limitations
* The city given does not take into account the heading of your aircraft. So, the nearest city may be behind you.
* Offline access is not implemented yet. It may be added in the future.


## contributors and credits
* Thanks to Tyler Rodick for his assistance with this project. This is my first major coding project, and it's helpful to have someone fixing my occasional oversight.
* Thanks also to Manuel Cortez, who wrote the keyboard handling code that TFM uses.
