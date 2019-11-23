# voice flight following
Periodically read the name of the closest city to your aircraft. Also reads key aircraft instrumentation.
For a compiled version, see the Releases section.

## Requirements
* You will need a free account on [Geonames](http://www.geonames.org). Once you create the account, go into your account settings and enable API access.
* Python  - 3.7 32 bit
* pywin32
## Installation
* Get the latest python 3.7 ([Python releases](https://www.python.org/downloads/))
* Install the latest pywin32 release ([pywin32 releases](https://github.com/mhammond/pywin32/releases))
    * filename: `pywin32-xxx.win32-py2.7.exe`
    * Install with the installer, not using pip!


## Usage
* Start your sim and start a flight.
* Start the script "FlightFollowing.py". Alternatively, run the FlightFollowing.exe file found in the releases section.
* the first time the script is run, it will generate a FlightFollowing.ini file in the same directory where it was run. This file should be edited to add your geonames username. The script will not run until this information is added.
* You should hear the name of the closest city to your aircraft location

## Bugs and issues
* Please report bugs via the github issues tab.
    * It is usefull to attach the logfile from "root/logs".
    
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
