#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
TV Garden Plugin for Enigma2
Based on TV Garden Project
"""

from Components.Language import language
from Tools.Directories import resolveFilename, SCOPE_PLUGINS
from os import environ
import gettext
import sys

PLUGIN_NAME = "TVGarden"
PLUGIN_VERSION = "1.1"
PLUGIN_PATH = resolveFilename(SCOPE_PLUGINS, f"Extensions/{PLUGIN_NAME}")
PLUGIN_ICON = resolveFilename(SCOPE_PLUGINS, "Extensions/TVGarden/icons/plugin.png")


def localeInit():
    try:
        lang = language.getLanguage()[:2]
        environ["LANGUAGE"] = lang
        gettext.bindtextdomain(PLUGIN_NAME,
                               resolveFilename(SCOPE_PLUGINS, f"Extensions/{PLUGIN_NAME}/locale"))
        gettext.textdomain(PLUGIN_NAME)
    except:
        pass


def _(txt):
    try:
        t = gettext.dgettext(PLUGIN_NAME, txt)
        if t == txt:
            t = gettext.gettext(txt)
        return t
    except:
        return txt


localeInit()
language.addCallback(localeInit)

# Make translation available to all modules
sys.modules[__name__].__dict__['_'] = _
