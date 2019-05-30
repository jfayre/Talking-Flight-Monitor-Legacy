#!/usr/bin/python
# -*- coding: iso-8859-15 -*-
#==============================================================================
# VaLogger - My custom logger class for VoiceAtis
# Copyright (C) 2018  Oliver Clemens
# 
# This program is free software: you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free Software
# Foundation, either version 3 of the License, or (at your option) any later
# version.
# 
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
# details.
# 
# You should have received a copy of the GNU General Public License along with
# this program.  If not, see <https://www.gnu.org/licenses/>.
#==============================================================================

import os
import sys
import ctypes
import struct
import time

class VaLogger(object):
    
    STD_OUTPUT_HANDLE = -11
    COLORS = {
#               'D'    : 0x0001,  # blue
              'D'   : 0x0002,   # green
              'E'     : 0x0004, # red
              'W'  : 0x0006,    # yellow
              }

 
    def __init__(self,*args,**optional):
        # Process paths.
        if len(args):
            self.logDir = args[0]
            self.logFile = os.path.join(self.logDir,time.strftime('%y%m%d-%H%M%S.log'))
        else:
            self.logFile = None
        
        # Process optional input.
        # Format
        self.logFormat = optional.get('Format','%H:%M:%S')
        self.consoleFormat = optional.get('Format','%H:%M:%S')
        
        self.logFormat = optional.get('LogFormat',self.logFormat)
        self.consoleFormat = optional.get('ConsoleFormat',self.consoleFormat)
        
        # Level
        self.logLevel = optional.get('LogLevel','debug')
        self.consoleLevel = optional.get('ConsoleLevel','info')
        
        # Color
        self.colorize = optional.get('Color',False)
        
        # Init logfile.
        if self.logFile is not None:
            try:
                if not os.path.isdir(self.logDir): 
                    os.makedirs(self.logDir)
                with open(self.logFile,'w'):
                    os.utime(self.logFile, None)
            except:
                self.logFile = None
        
        # Init color.
        self._initColor()
        
    def debug(self,message):
        if self.consoleLevel == 'debug':
            self._log2Console('D', message)
        if self.logLevel == 'debug':
            self._log2File('D', message)
    
    def info(self,message):
        levelList = ['debug','info']
        if self.consoleLevel in levelList:
            self._log2Console('I', message)
        if self.logLevel in levelList:
            self._log2File('I', message)
    
    def warning(self,message):
        levelList = ['debug','info','warning']
        if self.consoleLevel in levelList:
            self._log2Console('W', message)
        if self.logLevel in levelList:
            self._log2File('W', message)
        
    def error(self,message):
        self._log2Console('E', message)
        self._log2File('E', message)
        sys.exit('Error at execution. Terminated.')
    
    def setLevel(self,**optional):
        self.logLevel = optional.get('LogLevel',self.logLevel)
        self.consoleLevel = optional.get('ConsoleLevel',self.consoleLevel)
    
    def _log2Console(self,idChar,message):
        if idChar != 'I':
            self._setColor(idChar)
        print(time.strftime('{} - {} - {}'.format(self.consoleFormat,idChar,message)))
        self._resetColor()
    
    
    def _log2File(self,idChar,message):
        if self.logFile is not None:
            with open(self.logFile,'a') as logFile:  # @UnusedVariable
                logFile.write(time.strftime('{} - {} - {}\n'.format(self.consoleFormat,idChar,message)))       
    
    
    def _setColor(self,color):
        if None not in [self.colorHandle,self.colorReset] and self.colorize:
            ctypes.windll.kernel32.SetConsoleTextAttribute(self.colorHandle, self.COLORS[color])  # @UndefinedVariable
        
        
    def _resetColor(self):
        if None not in [self.colorHandle,self.colorReset]:
            ctypes.windll.kernel32.SetConsoleTextAttribute(self.colorHandle, self.colorReset)  # @UndefinedVariable
    
    
    def _initColor(self):
        try:
            # Get color handle.
            self.colorHandle = ctypes.windll.kernel32.GetStdHandle(self.STD_OUTPUT_HANDLE)  # @UndefinedVariable
            
            # Get csbi attributes.
            csbi = ctypes.create_string_buffer(22)
            res = ctypes.windll.kernel32.GetConsoleScreenBufferInfo(self.colorHandle, csbi)  # @UndefinedVariable
            assert res
            
            (bufx, bufy, curx, cury, wattr,                                                 # @UnusedVariable
            left, top, right, bottom, maxx, maxy) = struct.unpack("hhhhHhhhhhh", csbi.raw)  # @UnusedVariable
            self.colorReset = wattr
        except:
            self.colorHandle = None
            self.colorReset = None