#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
TV Garden Plugin - About Screen
Shows plugin information, credits and version
"""

from enigma import eTimer
from Screens.Screen import Screen
from Components.Label import Label
from Components.ActionMap import ActionMap
from Components.ScrollLabel import ScrollLabel

from ..helpers import log
from .. import _ , PLUGIN_VERSION
from ..utils.cache import CacheManager
from ..utils.config import PluginConfig


class TVGardenAbout(Screen):
    skin = """
        <screen name="TVGardenAbout" position="center,center" size="900,650" title="About TV Garden" backgroundColor="#1a1a2e" flags="wfNoBorder">
            <!-- Background -->
            <ePixmap pixmap="skin_default/buttons/red.png" position="380,590" size="140,40" alphatest="blend" />
            <ePixmap name="bg" position="0,0" size="900,650" alphatest="blend" zPosition="-2" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/TVGarden/images/hd/background.png" scale="1" />
            <!-- Header -->
            <widget name="title" position="30,20" size="840,60" font="Regular;32" halign="center" valign="center" foregroundColor="#ffffff" transparent="1" />
            <!-- Content Area -->
            <widget name="scrolltext" position="40,100" size="820,470" font="Regular;22" halign="left" valign="top" foregroundColor="#e0e0e0" transparent="1" />
            <!-- Footer -->
            <widget name="version" position="40,580" size="400,30" font="Regular;20" halign="left" valign="center" foregroundColor="#00aaff" transparent="1" />
            <widget source="key_red" render="Label" position="380,590" size="140,40" font="Regular;20" halign="center" valign="center" transparent="1" />
            <!-- Decorative elements -->
            <eLabel backgroundColor="#001a2336" cornerRadius="20" position="25,90" size="850,490" zPosition="-1" />
            <eLabel backgroundColor="#00000060" cornerRadius="10" position="30,95" size="840,480" zPosition="-1" />
        </screen>
    """

    def __init__(self, session):
        self.config = PluginConfig()
        dynamic_skin = self.config.load_skin("TVGardenAbout", self.skin)
        self.skin = dynamic_skin

        Screen.__init__(self, session)
        self["title"] = Label(_("TV Garden Plugin"))
        self["scrolltext"] = ScrollLabel()
        self["version"] = Label("")
        self["key_red"] = Label(_("Close"))
        self["actions"] = ActionMap(["TVGardenActions", "DirectionActions", "ColorActions", "OkCancelActions"], {
            "cancel": self.close,
            "exit": self.close,
            "back": self.close,
            "red": self.close,
            "ok": self.close,
            "up": self.pageUp,
            "down": self.pageDown,
            "left": self.pageUp,
            "right": self.pageDown,
            "channelUp": self.pageUp,
            "channelDown": self.pageDown,
        }, -2)

        self.setTitle(_("About TV Garden"))
        self.onLayoutFinish.append(self.load_content)

    def load_content(self):
        """Load about content with dynamic stats"""
        try:
            # Get stats
            cache = CacheManager()
            # config = self.config

            # Try to get countries count
            countries_count = "Loading..."
            try:
                metadata = cache.get_countries_metadata()
                countries_count = str(len([c for c in metadata.values() if c.get('hasChannels', False)]))
            except:
                countries_count = "150+"

            # Get cache info
            cache_info = "Active"
            # cache_size = "N/A"

            # Build about text
            about_text = self.generate_about_text(
                countries_count=countries_count,
                cache_info=cache_info
            )

            self["scrolltext"].setText(about_text)
            self["version"].setText("Version: %s" % PLUGIN_VERSION)

            # Auto-scroll after 3 seconds
            self.scroll_timer = eTimer()
            self.scroll_timer.timeout.get().append(self.auto_scroll)
            self.scroll_timer.start(3000, False)

        except Exception as e:
            log.error("Error loading content: %s" % e, module="About")
            self["scrolltext"].setText(_("Error loading information"))

    def generate_about_text(self, countries_count="150+", cache_info="Active"):
        """Generate formatted about text"""
        return """
══════════════════════════════════════
    TV GARDEN PLUGIN
    Complete IPTV Solution for Enigma2
══════════════════════════════════════

VERSION: %s
STATUS: ● FULLY OPERATIONAL

━━━━━━━━━━━━━━━ CORE FEATURES ━━━━━━━━━━━━━━━━
• Global Coverage: %s Countries
• Content Variety: 29 Categories
• Channel Library: 50,000+ Streams
• Real-time Search with Virtual Keyboard
• Smart Caching System: %s
• Auto-Skin Detection (HD/FHD/WQHD)
• Favorites Management with Bouquet Export
• DRM/Problematic Stream Filtering
• Configurable Channel Limits

━━━━━━━━━━━━━━━ KEY CONTROLS ━━━━━━━━━━━━━━━━
[ BROWSER ]
  OK / GREEN      ► Play Selected Channel
  EXIT / RED      ◄ Back / Exit
  YELLOW          ⚙ Context Menu (Remove/Export)
  BLUE            📤 Export Favorites to Bouquet
  MENU            ⚙ Context Menu

[ FAVORITES BROWSER ]
  OK / GREEN      ► Play Selected Channel
  EXIT / RED      ◄ Back / Exit
  YELLOW          ⚙ Options (Remove/Info/Export)
  BLUE            📤 Export ALL to Enigma2 Bouquet
  ↑↓←→            ↕ Navigate Channels

[ PLAYER ]
  CHANNEL +/-     ↕ Zap Between Channels
  OK              ℹ Show Channel Info
  RED             ★ Toggle Favorite
  GREEN           📋 Show Channel List
  EXIT            ✖ Close Player

━━━━━━━━━━━━━━ BOUQUET EXPORT ━━━━━━━━━━━━━━━
• Export favorites to Enigma2 native bouquet
• Automatic bouquet.tv integration
• Supports single & bulk channel export
• Creates: userbouquet.tvgarden_TVGarden_Favorites.tv
• Tag-based identification (tvgarden)
• Easy removal via Options menu
• Requires Enigma2 restart after export

━━━━━━━━━━━━━━ SEARCH FEATURES ━━━━━━━━━━━━━━━
• Instant Results While Typing
• Virtual Keyboard Support
• Search in Names & Descriptions
• Multi-language Search
• Configurable Result Limits
• Smart Filtering (YouTube/DRM skipped)

━━━━━━━━━━━━━ TECHNICAL SPECS ━━━━━━━━━━━━━━━━
• Python 2.7+ / 3.x Compatible
• Memory Efficient (~50MB RAM)
• Player Engines: GStreamer / ExtePlayer3
• Connection Retry with Timeout
• Automatic Cache Management
• Skin System with Resolution Detection
• Bouquet Integration with Enigma2 EPG

━━━━━━━━━━━━━━ DATA SOURCE ━━━━━━━━━━━━━━━━━━
TV Garden Channel List Project
Maintained by Belfagor2005

━━━━━━━━━━━━━━━ CREDITS ━━━━━━━━━━━━━━━━━━━━━━
• Original Concept: Lululla
• Data Source: Belfagor2005
• Plugin Development: TV Garden Team
• Bouquet Export Feature: Community Request
• Testing Community: Enigma2 Users Worldwide

━━━━━━━━━━━━━━━━ NOTES ━━━━━━━━━━━━━━━━━━━━━━
BOUQUET EXPORT TIPS:
1. Export favorites from Favorites Browser (BLUE)
2. Single channel export via Options (YELLOW)
3. Restart Enigma2 to see bouquet in channel list
4. Bouquet file: /etc/enigma2/userbouquet.tvgarden_*.tv

For support, bug reports or feature requests,
please visit the GitHub repository.

Enjoy streaming with TV Garden! 📺
""" % (PLUGIN_VERSION, countries_count, cache_info)

    def pageUp(self):
        """Scroll page up"""
        self["scrolltext"].pageUp()

    def pageDown(self):
        """Scroll page down"""
        self["scrolltext"].pageDown()

    def auto_scroll(self):
        """Auto-scroll text slowly"""
        self["scrolltext"].pageDown()
        # Continue scrolling every 5 seconds
        self.scroll_timer.start(5000, False)

    def close(self):
        """Close screen"""
        if hasattr(self, 'scroll_timer'):
            self.scroll_timer.stop()
        Screen.close(self)
