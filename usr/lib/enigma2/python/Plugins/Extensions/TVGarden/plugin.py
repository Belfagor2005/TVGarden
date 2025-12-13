#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
###########################################################
#                                                         #
#  TV Garden Plugin for Enigma2                           #
#  Version: 1.4                                           #
#  Created by Enigma2 Developer Lulualla                  #
#  Based on TV Garden Project by Lululla                  #
#  Data Source: Belfagor2005 fork                         #
#                                                         #
#  Repository:                                            #
#  https://github.com/Belfagor2005/tv-garden-channel-list #
#                                                         #
#  PLUGIN FEATURES:                                       #
#  • Global: 150+ countries with flags                    #
#  • Content: 29 categories, 50,000+ channels             #
#  • Caching: Smart TTL + gzip compression                #
#  • Player: Advanced with channel zapping                #
#  • Favorites: Export to Enigma2 bouquets                #
#  • Search: Fast virtual keyboard search                 #
#  • Skins: Auto-detection (HD/FHD/WQHD)                  #
#  • Safety: DRM/crash stream filtering                   #
#  • Performance: HW acceleration + buffer control        #
#  • Logging: File logging with rotation                  #
#  • Updates: Auto-check with notifications               #
#                                                         #
#  PERFORMANCE OPTIMIZATION:                              #
#  • Hardware acceleration for H.264/H.265                #
#  • Configurable buffer size (512KB-8MB)                 #
#  • Smart player selection (Auto/ExtePlayer3/GStreamer)  #
#  • Connection timeout & retry system                    #
#  • Memory efficient (~50MB RAM usage)                   #
#                                                         #
#  BOUQUET EXPORT SYSTEM:                                 #
#  • Export favorites to native Enigma2 bouquets          #
#  • Configurable bouquet name prefix                     #
#  • Max channels per bouquet limit                       #
#  • Auto-refresh bouquet option                          #
#  • Single/Bulk export capabilities                      #
#  • Requires Enigma2 restart after export                #
#                                                         #
#  CONFIGURATION SYSTEM:                                  #
#  • 47+ configurable parameters                          #
#  • Organized settings categories:                       #
#    - Player: Volume, Timeout, Retries                   #
#    - Display: Skin, Flags, Logos, Items per page        #
#    - Browser: Max channels, Default view                #
#    - Cache: TTL, Size, Auto-refresh                     #
#    - Export: Enabled, Auto-refresh, Max channels        #
#    - Network: User agent, Connection timeout            #
#    - Logging: Level, File logging, Size, Backups        #
#    - Performance: HW acceleration, Buffer size          #
#    - Updates: Auto-update, Channel, Interval            #
#                                                         #
#  KEY CONTROLS:                                          #
#  [ BROWSER ]                                            #
#    OK/GREEN    - Play selected channel                  #
#    EXIT/RED    - Back / Exit                            #
#    YELLOW      - Context menu (Remove/Export)           #
#    BLUE        - Export favorites to bouquet            #
#    MENU        - Context menu                           #
#                                                         #
#  [ FAVORITES BROWSER ]                                  #
#    OK/GREEN    - Play selected channel                  #
#    EXIT/RED    - Back / Exit                            #
#    YELLOW      - Options (Remove/Info/Export)           #
#    BLUE        - Export ALL to Enigma2 bouquet          #
#    ARROWS      - Navigate channels                      #
#                                                         #
#  [ PLAYER ]                                             #
#    CHANNEL +/- - Zap between channels                   #
#    OK          - Show channel info + performance stats  #
#    RED         - Toggle favorite                        #
#    GREEN       - Show channel list                      #
#    EXIT        - Close player                           #
#                                                         #
#  TECHNICAL DETAILS:                                     #
#  • Python 2.7+ compatible (Enigma2 optimized)           #
#  • Player engines: GStreamer / ExtePlayer3 / Auto       #
#  • HLS stream support with adaptive bitrate             #
#  • Automatic cache management                           #
#  • Configuration backup & restore                       #
#  • Skin system with resolution detection                #
#  • Bouquet integration with Enigma2 EPG                 #
#                                                         #
#  STATISTICS:                                            #
#  • 50,000+ channels available                           #
#  • ~70% stream compatibility rate                       #
#  • <5 sec loading time (cached)                         #
#  • 47 configuration parameters                          #
#  • 150+ countries supported                             #
#  • 29 content categories                                #
#                                                         #
#  CREDITS & THANKS:                                      #
#  • Original TV Garden concept: Lululla                  #
#  • Repository fork & maintenance: Belfagor2005          #
#  • Plugin development: TV Garden Team                   #
#  • Performance optimization: Recent updates             #
#  • Enigma2 community for testing & feedback             #
#  • All open-source contributors                         #
#                                                         #
#  NOTE: This plugin is for educational purposes only.    #
#  Please respect content rights and usage policies.      #
#                                                         #
#  Last Updated: 2025-12-13                               #
#  Performance Update: HW acceleration + buffer control   #
###########################################################
"""

from __future__ import absolute_import, print_function
from os.path import dirname
from sys import path

from Components.ActionMap import ActionMap
from Components.Label import Label
from Components.MenuList import MenuList

from Screens.Screen import Screen
from Screens.MessageBox import MessageBox

from . import _, PLUGIN_VERSION, PLUGIN_ICON  # , PLUGIN_NAME, PLUGIN_PATH
from .helpers import log, simple_log
from .browser.about import TVGardenAbout
from .browser.countries import CountriesBrowser
from .browser.categories import CategoriesBrowser
from .browser.favorites import FavoritesBrowser
from .browser.search import SearchBrowser
from .utils.cache import CacheManager
from .utils.config import PluginConfig
from .utils.update_manager import UpdateManager
from .utils.updater import PluginUpdater


# Add plugin path to sys.path for imports
plugin_path = dirname(__file__)
if plugin_path not in path:
    path.insert(0, plugin_path)


simple_log("START PLUGIN TVGARDEN BY LULULLA - TEST")

MODULES_LOADED = False
MODULES_LOADED = all([
    CountriesBrowser is not None,
    CategoriesBrowser is not None,
    FavoritesBrowser is not None,
    PluginConfig is not None,
    CacheManager is not None
])


if MODULES_LOADED:
    simple_log("✓ All modules loaded successfully")
else:
    simple_log("✗ Some modules failed to load", "WARNING")
    simple_log("  CountriesBrowser: %s" % (CountriesBrowser is not None))
    simple_log("  CategoriesBrowser: %s" % (CategoriesBrowser is not None))
    simple_log("  FavoritesBrowser: %s" % (FavoritesBrowser is not None))
    simple_log("  PluginConfig: %s" % (PluginConfig is not None))
    simple_log("  CacheManager: %s" % (CacheManager is not None))


class TVGardenMain(Screen):
    """Main menu screen"""

    skin = """
        <screen name="TVGardenMain" position="center,center" size="1280,720" title="TV Garden" backgroundColor="#1a1a2e" flags="wfNoBorder">
            <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/TVGarden/icons/redbutton.png" position="32,688" size="140,6" zPosition="1" transparent="1" alphatest="blend"/>
            <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/TVGarden/icons/greenbutton.png" position="176,688" size="140,6" zPosition="1" transparent="1" alphatest="blend"/>
            <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/TVGarden/icons/yellowbutton.png" position="314,688" size="140,6" zPosition="1" transparent="1" alphatest="blend"/>
            <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/TVGarden/icons/bluebutton.png" position="458,688" size="140,6" zPosition="1" transparent="1" alphatest="blend"/>
            <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/TVGarden/icons/kofi.png" position="740,460" size="130,130" scale="1" transparent="1" alphatest="blend"/>
            <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/TVGarden/icons/paypal.png" position="877,460" size="130,130" scale="1" transparent="1" alphatest="blend"/>
            <ePixmap name="" position="0,0" size="1280,720" zPosition="-1" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/TVGarden/images/hd/background.png" scale="1" alphatest="blend"/>
            <ePixmap name="" position="1039,531" size="200,80" zPosition="1" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/TVGarden/icons/logo.png" scale="1" transparent="1" alphatest="blend"/>
            <widget source="key_red" render="Label" position="33,649" zPosition="1" size="140,40" font="Regular;20" foregroundColor="#3333ff" halign="center" valign="center" transparent="1" alphatest="blend"/>
            <widget source="key_green" render="Label" position="174,650" zPosition="1" size="140,40" font="Regular;20" foregroundColor="#3333ff" halign="center" valign="center" transparent="1" alphatest="blend"/>
            <widget source="key_yellow" render="Label" position="315,650" zPosition="1" size="140,40" font="Regular;20" foregroundColor="#3333ff" halign="center" valign="center" transparent="1" alphatest="blend"/>
            <widget source="key_blue" render="Label" position="455,650" zPosition="1" size="140,40" font="Regular;20" foregroundColor="#3333ff" halign="center" valign="center" transparent="1" alphatest="blend"/>
            <widget name="menu" position="28,116" size="680,474" scrollbarMode="showOnDemand" backgroundColor="#16213e"/>
            <widget name="status" position="603,643" size="648,50" font="Regular; 22" halign="center" foregroundColor="#3333ff" transparent="1" alphatest="blend"/>
            <eLabel backgroundColor="#001a2336" cornerRadius="30" position="5,639" size="1270,60" zPosition="-80"/>
            <eLabel name="" position="24,101" size="694,502" zPosition="-1" cornerRadius="18" backgroundColor="#00171a1c" foregroundColor="#00171a1c"/>
            <widget source="session.VideoPicture" render="Pig" position="739,140" zPosition="19" size="520,308" backgroundColor="transparent" transparent="0" cornerRadius="14"/>
        </screen>
        """

    def __init__(self, session):

        self.config = PluginConfig()
        dynamic_skin = self.config.load_skin("TVGardenMain", self.skin)
        self.skin = dynamic_skin

        Screen.__init__(self, session)
        self.session = session
        self["status"] = Label("TV Garden %s | Ready" % PLUGIN_VERSION)

        self.cache = CacheManager()
        self.menu_items = [
            (_("Browse by Country"), "countries", _("Browse channels by country")),
            (_("Browse by Category"), "categories", _("Browse channels by category")),
            (_("Favorites"), "favorites", _("Your favorite channels")),
            (_("Search"), "search", _("Search channels by name")),
            (_("Check for Updates"), "updates", _("Check for plugin updates")),
            (_("Settings"), "settings", _("Plugin settings and configuration")),
            (_("About"), "about", _("About TV Garden plugin"))
        ]

        self["menu"] = MenuList(self.menu_items)
        self["status"] = Label(
            "TV Garden v.%s | Cache: %d items" % (PLUGIN_VERSION, self.cache.get_size())
        )

        self["key_red"] = Label(_("Exit"))
        self["key_green"] = Label(_("Select"))
        self["key_yellow"] = Label(_("Refresh"))
        self["key_blue"] = Label(_("Settings"))

        self["actions"] = ActionMap(["TVGardenActions", "ColorActions", "SetupActions", "MenuActions"], {
            "cancel": self.exit,
            "ok": self.select_item,
            "red": self.exit,
            "green": self.select_item,
            "yellow": self.refresh_data,
            "blue": self.open_settings,
            "menu": self.open_settings,
        }, -2)

    def select_item(self):
        """Handle menu item selection"""
        selection = self["menu"].getCurrent()
        if selection:
            action = selection[1]

            if action == "countries":
                self.session.open(CountriesBrowser)
            elif action == "categories":
                self.session.open(CategoriesBrowser)
            elif action == "favorites":
                self.session.open(FavoritesBrowser)
            elif action == "search":
                self.open_search()
            elif action == "settings":
                self.open_settings()
            elif action == "updates":
                self.check_for_updates()
            elif action == "about":
                self.show_about()

    def open_search(self):
        """Open search screen"""
        self.session.open(SearchBrowser)

    def open_settings(self):
        """Open settings screen"""
        from .utils.settings import TVGardenSettings
        self.session.open(TVGardenSettings)

    def refresh_data(self):
        """Refresh cache and metadata - VERSIONE CORRETTA"""
        self["status"].setText(_("Refreshing data..."))

        try:
            self.cache.clear_all()

            countries_data = self.cache.get_countries_metadata(force_refresh=True)

            cache_size = self.cache.get_size()

            new_status = "TV Garden v.%s | Cache: %d items" % (PLUGIN_VERSION, cache_size)
            self["status"].setText(new_status)

            self.session.open(
                MessageBox,
                _("Refresh completed!\nLoaded %d countries") % len(countries_data),
                MessageBox.TYPE_INFO
            )

        except Exception as e:
            error_msg = _("Refresh failed: %s") % str(e)
            self["status"].setText(error_msg)
            log.error("Refresh error: %s" % str(e), module="Main")

    def check_for_updates(self):
        """Check for plugin updates - VERSIONE CENTRALIZZATA"""
        log.debug("check_for_updates called from main menu", module="Main")

        # Test diretto per vedere se il problema è in UpdateManager
        try:
            log.debug("Creating UpdateManager instance...", module="Main")
            updater = PluginUpdater()
            log.debug("PluginUpdater created successfully", module="Main")

            # Test diretto della funzione
            latest = updater.get_latest_version()
            log.debug("Direct test - Latest version: %s" % latest, module="Main")

            # Ora usa UpdateManager
            UpdateManager.check_for_updates(self.session, self["status"])

        except Exception as e:
            log.error("Direct test error: %s" % e, module="Main")
            self["status"].setText(_("Update check error"))
            self.session.open(MessageBox,
                              _("Error: %s") % str(e),
                              MessageBox.TYPE_ERROR)

    def show_about_fallback(self):
        about_text = """
            TV GARDEN v%s | Cache: %d items

            * Global: 150+ countries, 29 categories
            * Streams: 50K+, HW Acceleration
            * Buffer: 512KB-8MB, Export bouquet
            * Search: Virtual keyboard, Smart filter

            CONTROLS:
            - PLAYER: CH+/−=Zap, OK=Info+Stats
            - FAVORITES: BLUE=Export bouquet
            - SETTINGS: 47+ options, Log viewer

            PERFORMANCE:
            - HW Accel for H.264/H.265
            - Buffer size configurable
            - Smart stream filtering

            BOUQUET EXPORT:
            - To Enigma2 native bouquet
            - Configurable name & channels
            - Auto-refresh option

            STATUS: FULLY OPERATIONAL
            SETTINGS: 47 parameters
            LOGS: File + Rotation active
            """ % (PLUGIN_VERSION, self.cache.get_size())
    
        self.session.open(MessageBox, about_text.strip(), MessageBox.TYPE_INFO)

    def show_about(self):
        """Show about screen"""
        try:
            self.session.open(TVGardenAbout)
        except ImportError:
            # Fallback to MessageBox
            self.show_about_fallback()

    def exit(self):
        """Exit plugin"""
        self.cache.clear_all()
        self.close()


def menu(menuid, **kwargs):
    """Plugin menu integration"""
    if menuid == "mainmenu":
        return [(_("TV Garden"), main, "tv_garden", 46)]
    return []


def main(session, **kwargs):
    try:
        return session.open(TVGardenMain)
    except Exception as e:
        import traceback
        import time
        log_path = "/tmp/tvgarden_crash.log"
        with open(log_path, "a") as f:
            f.write("=" * 50 + "\n")
            f.write(time.ctime() + "\n")
            f.write("CRASH on init TVGardenMain\n")
            f.write(str(e) + "\n")
            f.write(traceback.format_exc())
            f.write("\n" + "=" * 50 + "\n")
        # Tenta almeno di mostrare un messaggio di errore
        from Screens.MessageBox import MessageBox
        error_msg = "TVGarden Crash: " + str(e)
        session.open(MessageBox, error_msg, MessageBox.TYPE_ERROR)
        return None


def Plugins(**kwargs):
    """Plugin descriptor list"""
    from Plugins.Plugin import PluginDescriptor
    from .utils.config import get_config
    config = get_config()
    log_level = config.get("log_level", "INFO")
    log_to_file = config.get("log_to_file", True)
    log.set_level(log_level)
    log.enable_file_logging(log_to_file)
    log.info("TV Garden Plugin started", "Main")

    description = _("Access free IPTV channels from around the world")
    plugin_descriptor = PluginDescriptor(
        name="TV Garden",
        description=description,
        where=PluginDescriptor.WHERE_PLUGINMENU,
        icon=PLUGIN_ICON,
        fnc=main
    )

    # Also add to extensions menu
    extensions_descriptor = PluginDescriptor(
        name="TV Garden",
        description=description,
        where=PluginDescriptor.WHERE_EXTENSIONSMENU,
        fnc=main
    )

    return [plugin_descriptor, extensions_descriptor]
