# Talking Flight Monitor (TFM)
Periodically read the name of the closest city to your aircraft. Also reads key aircraft instrumentation.
For a compiled version, see the Releases section.
## features
* reads closest city to the aircraft based on simulator GPS position
* reads many  aircraft instruments and switches automatically
* sonification of key aircraft parameters, such as pitch and bank.
* Sonification of flight director to aide in manual flight
* Reads SimConnect message windows, such as the ones displayed by GSX and Pro ATC/x
* reads Radar Contact menus


## Usage
In order to read the nearest city to your aircraft, you will need a free [GeoNames](http://www.geonames.org) account. Once you create the account, enable web access under your profile. 
You will need the latest version of FSUIPC 5 for SimConnect messages to work. This also requires Prepar 3d version 4.5.
* Start your simulator  and start a flight.
* Start the script "FlightFollowing.py". Alternatively, run the FlightFollowing.exe file found in the releases section.
* the first time the script is run, it will generate a FlightFollowing.ini file in the same directory where it was run. This file should be edited to add your geonames username. The script will not run until this information is added.
* You should hear the name of the closest city to your aircraft location, as well as various instrument status messages.

### Hotkeys
There are several hotkeys for use when Flight Following is running. The keys are set up as global, so you don't need to be in the Flight Following window to use them. All hotkeys can be changed by editing the FlightFollowing.ini file.
Note that you need to be running Flight Following as an administrator for the global hotkeys to register properly. The packaged executable from the Releases section does this for you.
The keys use a layered aproach. First press the command key, which is Right Square Bracket by default. Then press the desired command. 
The currently available keys are:
* ]: enters command mode (use before all other keys)
* a: read altitude above sea level (ASL).
* shift+a: toggle GPWS (ground proximity warning system) announcements
* c: read nearest city
* d: read distance and time to destination
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

### audible attitude indications
Flight Following contains three modes that allow you to hear the pitch and bank of your aircraft.
In "Attitude mode", you will hear a constant tone in the center channel to indicate pitch. Pitch down and pitch up are represented by different sounding tones. Bank is represented by a beeping tone in either the right or left channel to indicate the direction of bank. The higher the tone, the higher your bank angle.
In Flight Director mode, the tones are identical to attitude mode, but the tones indicate the direction you need to turn to follow the flight director.
In Manual Flight mode, the pitch and bank angle are read every few seconds. The interval is adjustable in the ini file.



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
pyinstaller flightFollowing.spec
```
If you want a version that does not automatically run as administrator, run this instead:
```
pyinstaller flightFollowing-no_Admin.spec
```
Disregard the warning about UPX not being present.


## Bugs and issues
* Please report bugs via the github issues tab.
    * It is useful to attach the error.log file to any issues.
    
### Known limitations
* The city given does not take into account the heading of your aircraft. So, the nearest city may be behind you.
* Offline access is not implemented yet. It may be added in the future.
