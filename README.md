# voice flight following
Periodically read the name of the closest city to your aircraft. Also reads key aircraft instrumentation.
For a compiled version, see the Releases section.
## features
* reads closest city to the aircraft based on simulator GPS position
* reads various aircraft instrumentation
* sonification of key aircraft parameters, such as pitch and bank.
* Sonification of flight director to aide in manual flight
* Reads SimConnect message windows, such as the ones displayed by GSX and Pro ATC/x

## Usage
You will need the latest version of FSUIPC for recent functionality to work. 
* Start your sim and start a flight.
* Start the script "FlightFollowing.py". Alternatively, run the FlightFollowing.exe file found in the releases section.
* the first time the script is run, it will generate a FlightFollowing.ini file in the same directory where it was run. This file should be edited to add your geonames username. The script will not run until this information is added.
* You should hear the name of the closest city to your aircraft location, as well as various instrument status.

### Hotkeys
There are several hotkeys for use when Flight Following is running. The keys are set up as global, so you don't need to be in the Flight Following window to use them. 
Note that you need to be running Flight Following as an administrator for the global hotkeys to register properly. The packaged executable from the Releases section does this for you.
The keys use a layered aproach. First press the command key, which is Right Square Bracket by default. Then press the desired command. 
The currently available keys are:
* ]: enters command mode (use before all other keys)
* a: read altitude above sea level (ASL).
* d: read distance and time to destination
* g: read  altitude above ground (AGL)
* h: read heading
* r: read the last SimConnect message displayed.
* s: read indicated airspeed
* t: read true airspeed
* w: read next waypoint
* Shift+F: audible flight director (see below)
* Shift+M: read pitch and bank angle periodically
* [ (left bracket): audible aircraft attitude indication (see below)
### audible attitude indications
Flight Following contains two modes that allow you to hear the pitch and bank of your aircraft.
In "Attitude mode", you will hear a constant tone in the center channel to indicate pitch. Pitch down and pitch up are represented by different sounding tones. Bank is represented by a beeping tone in either the right or left channel to indicate the direction of bank. The higher the tone, the higher your bank angle.



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
This requires PyInstaller and [UPX](https://upx.github.io) to be installed. Install PyInstaller like so:
```
pip install pyinstaller
```
UPX is distributed as a zip file. Uncompress it and add the unzipped folder to your PATH.
Once PyInstaller and UPX are installed, execute the following from the root of the checkout:
```
pyinstaller flightFollowing.spec
```
If you want a version that does not automatically run as administrator, run this instead:
```
pyinstaller flightFollowing-no_Admin.spec
```


## Bugs and issues
* Please report bugs via the github issues tab.
    * It is useful to attach the error.log file to any issues.
    
### Known limitations
* The city given does not take into account the heading of your aircraft. So, the nearest city may be behind you.
* Offline access is not implemented yet. It may be added in the future.

## Used packages and Copyright

### pyttsx
Text-to-speech package for python. Used to read the parsed ATIS string.

pyttsx Copyright (c) 2009, 2013 Peter Parente

Permission to use, copy, modify, and distribute this software for any
purpose with or without fee is hereby granted, provided that the above
copyright notice and this permission notice appear in all copies.

THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES
WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF
MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR
ANY SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES
WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN
ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF
OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.


### pyuipc - FSUIPC SDK for Python
Used to get the com frequencies, com status, aircraft coordinates from the simulator.

All Copyright - Peter Dowson and István Váradi.


## Changelog
