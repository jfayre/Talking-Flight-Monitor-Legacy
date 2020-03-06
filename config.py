# -*- coding: cp1252 -*-
import os
import config_utils
import paths
import logging
import platform

log = logging.getLogger("config")

MAINFILE = "tfm.ini"
MAINSPEC = "tfm.defaults"
app = None


def setup ():
 global app
 log.debug("Loading app settings...")
 app = config_utils.load_config(os.path.join(paths.config_path(), MAINFILE), os.path.join(paths.app_path(), MAINSPEC))
 