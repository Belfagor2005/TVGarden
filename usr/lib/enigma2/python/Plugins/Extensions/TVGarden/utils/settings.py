#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
TV Garden Plugin - Settings Screen
Plugin configuration interface
Based on TV Garden Project
"""

from Screens.Screen import Screen
from Components.ActionMap import ActionMap
from Components.Label import Label
from Components.ConfigList import ConfigListScreen
from Components.config import (
    ConfigInteger,
    ConfigSelection,
    ConfigYesNo,
    ConfigText,
    getConfigListEntry
)

from .. import _
from .config import get_config


class TVGardenSettings(ConfigListScreen, Screen):
    """Settings screen using Enigma2's config system"""

    skin = """
        <screen name="TVGardenSettings" position="center,center" size="1280,720" title="TV Garden Settings" backgroundColor="#1a1a2e" flags="wfNoBorder">
            <ePixmap pixmap="skin_default/buttons/red.png" position="33,650" size="140,40" alphatest="blend" />
            <ePixmap pixmap="skin_default/buttons/green.png" position="174,650" size="140,40" alphatest="blend" />
            <ePixmap name="" position="0,0" size="1280,720" alphatest="blend" zPosition="-1" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/TVGarden/images/hd/background.png" scale="1" />
            <ePixmap name="" position="1039,531" size="200,80" alphatest="blend" zPosition="1" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/TVGarden/icons/logo.png" scale="1" transparent="1"/>
            <widget source="key_red" render="Label" position="33,649" zPosition="1" size="140,40" font="Regular;20" halign="center" valign="center" transparent="1" />
            <widget source="key_green" render="Label" position="174,650" zPosition="1" size="140,40" font="Regular;20" halign="center" valign="center" transparent="1" />
            <widget name="config" position="28,116" size="680,474" scrollbarMode="showOnDemand" backgroundColor="#16213e" />
            <widget name="status" position="603,643" size="648,50" font="Regular; 22" halign="center" foregroundColor="#3333ff" transparent="1" />
            <eLabel backgroundColor="#001a2336" cornerRadius="30" position="5,639" size="1270,60" zPosition="-80" />
            <eLabel name="" position="24,101" size="694,502" zPosition="-1" cornerRadius="18" backgroundColor="#00171a1c" foregroundColor="#00171a1c" />
            <widget source="session.VideoPicture" render="Pig" position="739,140" zPosition="19" size="520,308" backgroundColor="transparent" transparent="0" cornerRadius="14" />
        </screen>
    """

    def __init__(self, session):
        
        self.config = get_config()
        
        dynamic_skin = self.config.load_skin("TVGardenSettings", self.skin)
        self.skin = dynamic_skin
        
        Screen.__init__(self, session)
        ConfigListScreen.__init__(self, [], session=session)

        self.setTitle(_("TV Garden Settings"))
        self.setupConfig()
        self["key_red"] = Label(_("Back"))
        self["key_green"] = Label(_("Save"))
        self["status"] = Label(_("Set options"))
        self["actions"] = ActionMap(
            ["SetupActions", "ColorActions"],
            {
                "cancel": self.cancel,
                "save": self.save,
                "ok": self.save,
            }, -2
        )
    
    def setupConfig(self):
        """Setup configuration entries"""
        self.config_entries = []
        
        # Player settings
        self.config_entries.append([
            _("Player"), "player",
            ConfigSelection(
                default=self.config.get("player", "auto"),
                choices=[
                    ("auto", _("Auto")),
                    ("exteplayer3", _("ExtePlayer3")),
                    ("gstplayer", _("GStreamer"))
                ]
            )
        ])
        
        self.config_entries.append([
            _("Volume"), "volume",
            ConfigInteger(default=self.config.get("volume", 80), limits=(0, 100))
        ])
        
        self.config_entries.append([
            _("Timeout (seconds)"), "timeout",
            ConfigInteger(default=self.config.get("timeout", 10), limits=(5, 60))
        ])
        
        self.config_entries.append([
            _("Retries"), "retries",
            ConfigInteger(default=self.config.get("retries", 3), limits=(1, 10))
        ])
        
        # Cache settings
        self.config_entries.append([
            _("Cache TTL (hours)"), "cache_ttl",
            ConfigInteger(default=self.config.get("cache_ttl", 3600) // 3600, limits=(1, 24))
        ])
        
        self.config_entries.append([
            _("Cache Size"), "cache_size",
            ConfigInteger(default=self.config.get("cache_size", 100), limits=(10, 1000))
        ])
        
        # Display settings
        self.config_entries.append([
            _("Skin"), "skin",
            ConfigSelection(
                default=self.config.get("skin", "auto"),
                choices=[
                    ("auto", _("Auto")),
                    ("hd", _("HD")),
                    ("fhd", _("FHD")),
                    ("wqhd", _("WQHD"))
                ]
            )
        ])
        
        self.config_entries.append([
            _("Show Flags"), "show_flags",
            ConfigYesNo(default=self.config.get("show_flags", True))
        ])
        
        self.config_entries.append([
            _("Show Logos"), "show_logos",
            ConfigYesNo(default=self.config.get("show_logos", True))
        ])
        
        # Browser settings
        self.config_entries.append([
            _("Items per page"), "items_per_page",
            ConfigInteger(default=self.config.get("items_per_page", 20), limits=(10, 100))
        ])
        
        self.config_entries.append([
            _("Default View"), "default_view",
            ConfigSelection(
                default=self.config.get("default_view", "countries"),
                choices=[
                    ("countries", _("Countries")),
                    ("categories", _("Categories")),
                    ("favorites", _("Favorites"))
                ]
            )
        ])
        
        # Favorites
        self.config_entries.append([
            _("Max Favorites"), "max_favorites",
            ConfigInteger(default=self.config.get("max_favorites", 100), limits=(10, 500))
        ])
        
        # Network
        self.config_entries.append([
            _("User Agent"), "user_agent",
            ConfigText(default=self.config.get("user_agent", "TVGarden-Enigma2/1.0"), fixed_size=False)
        ])
        
        # Creazione della lista
        self.list = []
        for entry in self.config_entries:
            name = entry[0]
            config_item = entry[2]
            self.list.append(getConfigListEntry(name, config_item))
        
        self["config"].setList(self.list)
    
    def save(self):
        """Save configuration"""
        for entry in self["config"].list:
            key_name = entry[0].lower().replace(" ", "_")
            
            if entry[1].__class__.__name__ == "ConfigYesNo":
                self.config.set(key_name, entry[1].value)
            elif entry[1].__class__.__name__ == "ConfigSelection":
                self.config.set(key_name, entry[1].value)
            elif entry[1].__class__.__name__ == "ConfigNumber":
                # Special handling for cache TTL
                if "ttl" in key_name:
                    self.config.set("cache_ttl", entry[1].value * 3600)
                else:
                    self.config.set(key_name, entry[1].value)
        
        self.close(True)
    
    def cancel(self):
        """Cancel without saving"""
        self.close(False)
