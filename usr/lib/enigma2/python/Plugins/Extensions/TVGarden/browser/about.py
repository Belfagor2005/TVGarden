#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
TV Garden Plugin - About Screen
Shows plugin information, credits and version
"""
from __future__ import print_function
from enigma import eTimer
from Screens.Screen import Screen
from Components.Label import Label
from Components.ActionMap import ActionMap
from Components.ScrollLabel import ScrollLabel

from ..helpers import log
from .. import _, PLUGIN_VERSION
from ..utils.cache import CacheManager
from ..utils.config import PluginConfig


class TVGardenAbout(Screen):
    skin = """
        <screen name="TVGardenAbout" position="center,center" size="1280,720" title="TV Garden" backgroundColor="#1a1a2e" flags="wfNoBorder">
            <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/TVGarden/icons/redbutton.png" position="32,688" size="140,6" zPosition="1" transparent="1" alphatest="blend"/>
            <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/TVGarden/icons/kofi.png" position="740,460" size="130,130" scale="1" transparent="1" alphatest="blend"/>
            <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/TVGarden/icons/paypal.png" position="877,460" size="130,130" scale="1" transparent="1" alphatest="blend"/>
            <ePixmap name="" position="0,0" size="1280,720" zPosition="-1" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/TVGarden/images/hd/background.png" scale="1" alphatest="blend"/>
            <ePixmap name="" position="1039,531" size="200,80" zPosition="1" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/TVGarden/icons/logo.png" scale="1" transparent="1" alphatest="blend"/>
            <widget source="key_red" render="Label" position="33,649" zPosition="1" size="140,40" font="Regular;20" foregroundColor="#3333ff" halign="center" valign="center" transparent="1" alphatest="blend"/>
            <widget name="scrolltext" position="28,116" size="680,474" font="Regular;22" halign="left" valign="top" foregroundColor="#e0e0e0" transparent="1"/>
            <widget name="version" position="603,643" size="648,50" font="Regular; 22" halign="center" foregroundColor="#3333ff" transparent="1" alphatest="blend"/>
            <eLabel backgroundColor="#001a2336" cornerRadius="30" position="5,639" size="1270,60" zPosition="-80"/>
            <eLabel name="" position="24,101" size="694,502" zPosition="-1" cornerRadius="18" backgroundColor="#00171a1c" foregroundColor="#00171a1c"/>
            <widget source="session.VideoPicture" render="Pig" position="739,140" zPosition="19" size="520,308" backgroundColor="transparent" transparent="0" cornerRadius="14"/>
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

            # Auto-scroll after 5 seconds
            self.scroll_timer = eTimer()
            try:
                self.scroll_timer_conn = self.scroll_timer.timeout.connect(self.auto_scroll)
            except AttributeError:
                self.scroll_timer.callback.append(self.auto_scroll)
            self.scroll_timer.start(5000, False)

        except Exception as e:
            log.error("Error loading content: %s" % e, module="About")
            self["scrolltext"].setText(_("Error loading information"))

    def generate_about_text(self, countries_count="150+", cache_info="Active"):
        """Generate formatted about text"""
        return """
            ═══════════════════════════════════════════════
                         TV GARDEN PLUGIN
                    Complete IPTV Solution for Enigma2
            ═══════════════════════════════════════════════

            VERSION: %s
            STATUS: ● FULLY OPERATIONAL WITH PERFORMANCE OPTIMIZATION

            ━━━━━━━━━━━━━━━━━━ CORE FEATURES ━━━━━━━━━━━━━━━━━━
            • Global Coverage: %s Countries
            • Content Variety: 29 Categories
            • Channel Library: 50,000+ Streams
            • Real-time Search with Virtual Keyboard
            • Smart Caching System: %s
            • Auto-Skin Detection (HD/FHD/WQHD)
            • Favorites Management with Bouquet Export
            • DRM/Problematic Stream Filtering
            • Configurable Channel Limits
            • Hardware Acceleration Support
            • Configurable Buffer Size (512KB - 8MB)

            ━━━━━━━━━━━━━━━━━━ NEW: HIERARCHICAL BOUQUET EXPORT ━━━━━━━━━━━━━━━━━━
            • SINGLE-FILE EXPORT: All channels in one bouquet (traditional)
            • MULTI-FILE EXPORT: Hierarchical structure for better performance
            • SMART SPLITTING: Countries with ≤500 channels → single file
            • AUTO-PARTITION: Countries with >500 channels → multiple files
            • CONTAINER SYSTEM: Parent bouquet with sub-bouquet references
            • ENHANCED PERFORMANCE: Faster loading, no Enigma2 slowdown
            • COMPATIBLE: Works with all Enigma2 receivers

            ━━━━━━━━━━━━━━━━━ PERFORMANCE SETTINGS ━━━━━━━━━━━━━━━━━━
            • Hardware Acceleration Toggle (On/Off)
            • Buffer Size Control: 512KB, 1MB, 2MB, 4MB, 8MB
            • Smart HW Accel Detection (H.264, H.265, MPEG-2/4)
            • Automatic Format Detection for Optimization
            • Player Selection: Auto, ExtePlayer3, GStreamer

            ━━━━━━━━━━━━━━━━━ KEY CONTROLS ━━━━━━━━━━━━━━━━━━
            [ BROWSER ]
              OK / GREEN      > Play Selected Channel
              EXIT / RED      < Back / Exit
              YELLOW          [ ] Context Menu (Remove/Export)
              BLUE            [X] Export Favorites to Bouquet
              MENU            [ ] Context Menu

            [ FAVORITES BROWSER ]
              OK / GREEN      > Play Selected Channel
              EXIT / RED      < Back / Exit
              YELLOW          [ ] Options (Remove/Info/Export)
              BLUE            [X] Export ALL to Enigma2 Bouquet
              UP/DOWN         ^/v Navigate Channels

            [ YELLOW BUTTON OPTIONS MENU ]
              View Channel Info      - Detailed channel information
              Remove from Favorites  - Remove selected channel
              Clear All Favorites    - Clear all favorite channels
              Export to Enigma2 Bouquet - Export single channel
              Export ALL Database (Single File) - All channels in one bouquet
              Export ALL Database (Multi-File)  - New hierarchical structure
              Remove Bouquet from Enigma2 - Complete bouquet removal

            [ PLAYER ]
              CHANNEL +/-     ^/v Zap Between Channels
              OK              [i] Show Channel Info + Performance Stats
              RED             [*] Toggle Favorite
              GREEN           [#] Show Channel List
              EXIT            [X] Close Player

            ━━━━━━━━━━━━━━━━━ BOUQUET EXPORT SYSTEM ━━━━━━━━━━━━━━━━━━
            • EXPORT OPTIONS:
              - Single channel export (via Options menu)
              - All favorites export (Blue button in Favorites)
              - Complete database export - SINGLE FILE
              - Complete database export - MULTI-FILE (NEW!)

            • BOUQUET STRUCTURE:
              SINGLE-FILE: userbouquet.tvgarden_TVGarden_Favorites.tv
              MULTI-FILE:  userbouquet.tvgarden_complete_container.tv (parent)
                           subbouquet.tvgarden_italy.tv (child - ≤500 channels)
                           subbouquet.tvgarden_us_part1.tv (child - >500 channels)

            • AUTOMATIC INTEGRATION:
              - Added to bouquets.tv automatically
              - Tag-based identification (tvgarden)
              - Auto-reload after export
              - Preserves existing bouquet order

            • REMOVAL SYSTEM:
              - Removes ALL bouquet files with .tvgarden_ tag
              - Cleans bouquets.tv references
              - Preserves other bouquet files
              - Automatic reload after removal

            ━━━━━━━━━━━━━━━━━ SEARCH FEATURES ━━━━━━━━━━━━━━━━━━
            • Instant Results While Typing
            • Virtual Keyboard Support
            • Search in Names & Descriptions
            • Multi-language Search
            • Configurable Result Limits (100-1000 channels)
            • Smart Filtering (YouTube/DRM skipped)

            ━━━━━━━━━━━━━━━━━ TECHNICAL SPECS ━━━━━━━━━━━━━━━━━━
            • Python 2.7+ Compatible (Enigma2 Optimized)
            • Memory Efficient (~50MB RAM)
            • Player Engines: GStreamer / ExtePlayer3 / Auto
            • Connection Timeout & Retry System (3-10 attempts)
            • Automatic Cache Management (TTL: 1-24 hours)
            • Advanced Logging System (DEBUG to CRITICAL)
            • Log File Management with Rotation & Size Limits
            • Skin System with Resolution Detection
            • Bouquet Integration with Enigma2 EPG
            • 47 Configurable Parameters via Settings Screen
            • Configuration Backup & Restore System

            ━━━━━━━━━━━━━━━━━ CONFIGURATION SYSTEM ━━━━━━━━━━━━━━━━━━
            • Player Settings: Player, Volume, Timeout, Retries
            • Display Settings: Skin, Flags, Logos, Items per Page
            • Browser Settings: Max Channels, Default View
            • Cache Settings: TTL, Size, Auto-refresh
            • Export Settings: Enabled, Auto-refresh, Max Channels
            • Network Settings: User Agent, Connection Timeout
            • Logging Settings: Level, File Logging, Size, Backups
            • Performance Settings: HW Acceleration, Buffer Size
            • Update Settings: Auto-update, Channel, Interval
            • Session Settings: Last Viewed, Watch Time, Statistics

            ━━━━━━━━━━━━━━━━━ DATA SOURCE ━━━━━━━━━━━━━━━━━━━━
            TV Garden Channel List Project
            Maintained by Belfagor2005

            ━━━━━━━━━━━━━━━━━ CREDITS ━━━━━━━━━━━━━━━━━━━━━━━━
            • Original Concept: Lululla
            • Data Source: Belfagor2005
            • Plugin Development: TV Garden Team
            • Bouquet Export Feature: Community Request
            • Performance Optimization: Recent Update
            • Hierarchical Export: Inspired by Vavoo Plugin Architecture
            • Testing Community: Enigma2 Users Worldwide

            ━━━━━━━━━━━━━━━━━ PERFORMANCE TIPS ━━━━━━━━━━━━━━━━━━━━
            RECOMMENDED SETTINGS FOR SMOOTH PLAYBACK:
            1. Buffer Size: 2MB-4MB for stable connections
            2. HW Acceleration: ON for H.264/H.265 streams
            3. Connection Timeout: 10-15 seconds
            4. Max Channels per Country: 250-500 for faster loading
            5. Cache TTL: 4-8 hours for balance

            BOUQUET EXPORT TIPS:
            1. SINGLE-FILE EXPORT: Best for small channel lists (<1000 channels)
            2. MULTI-FILE EXPORT: Recommended for complete database export
            3. File location: /etc/enigma2/
            4. Tag pattern: *.tvgarden_* (for easy identification)
            5. Parent container: userbouquet.tvgarden_complete_container.tv
            6. Child bouquets: subbouquet.tvgarden_[country].tv

            HIERARCHICAL STRUCTURE BENEFITS:
            • FASTER LOADING: Each file has max 500 channels
            • BETTER ORGANIZATION: Countries separated in individual files
            • EASY NAVIGATION: Parent container provides overview
            • OPTIMAL PERFORMANCE: No Enigma2 slowdown with large lists

            LOGGING & TROUBLESHOOTING:
            • Log Level: INFO for normal use, DEBUG for troubleshooting
            • Log to File: ON for persistent logs
            • Max Log Size: 1MB-5MB recommended
            • View logs via Settings → "View Log File"
            • Clear logs via Settings → "Clear Log Files Now"

            TROUBLESHOOTING BOUQUET EXPORT:
            1. If bouquets don't appear: Restart Enigma2
            2. To remove all bouquets: Use "Remove Bouquet" option
            3. Check file permissions in /etc/enigma2/
            4. Verify bouquets.tv contains TV Garden references

            For support, bug reports or feature requests,
            please visit the GitHub repository.

            Enjoy optimized streaming with TV Garden!
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
