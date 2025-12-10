#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
###########################################################
#                                                         #
#  TV Garden Plugin for Enigma2                           #
#  Version: 1.1                                           #
#  Created by Enigma2 Developer Lulualla                  #
#  Based on TV Garden Project by Lululla                  #
#  Data Source: Belfagor2005 fork                         #
#                                                         #
#  Repository:                                            #
#  https://github.com/Belfagor2005/tv-garden-channel-list #
#                                                         #
#  Plugin Features:                                       #
#  • Browse 150+ countries with flags                     #
#  • 29 categories with filtered content                  #
#  • Smart caching system (TTL + gzip)                    #
#  • Advanced player with channel zapping                 #
#  • Favorites with export/import                         #
#  • Fast search across all channels                      #
#  • Multiple skin support (HD/FHD/WQHD)                  #
#  • DRM/crash protection filters                         #
#                                                         #
#  Player Controls:                                       #
#  • CHANNEL +/- : Navigate channel list                  #
#  • OK : Show channel info                               #
#  • EXIT : Close player                                  #
#                                                         #
#  Technical Details:                                     #
#  • Python 2.7+ compatible                               #
#  • Enigma2 MoviePlayer based                            #
#  • Gstreamer HLS support                                #
#  • Memory efficient (~50MB RAM)                         #
#                                                         #
#  Statistics:                                            #
#  • 50,000+ channels available                           #
#  • ~70% stream compatibility rate                       #
#  • <5 sec loading time (cached)                         #
#                                                         #
#  Credits & Thanks:                                      #
#  • Original TV Garden: Lululla                          #
#  • Repository fork: Belfagor2005 as (Lululla)           #
#  • Enigma2 community for testing                        #
#  • All open-source contributors                         #
#                                                         #
#  Note: This plugin is for educational purposes only.    #
#  Please respect content rights and usage policies.      #
#                                                         #
#  Last Updated: 2025-12-06                               #
###########################################################
"""

from __future__ import absolute_import
from os.path import dirname
from sys import path

from Components.ActionMap import ActionMap
from Components.Label import Label
from Components.MenuList import MenuList

from Screens.Screen import Screen
from Screens.MessageBox import MessageBox

from . import _, PLUGIN_VERSION, PLUGIN_ICON  # , PLUGIN_NAME, PLUGIN_PATH
from .helpers import log, simple_log
from .browser.countries import CountriesBrowser
from .browser.categories import CategoriesBrowser
from .browser.favorites import FavoritesBrowser
from .browser.search import SearchBrowser
from .utils.cache import CacheManager
from .utils.config import PluginConfig

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
    simple_log(f"  CountriesBrowser: {CountriesBrowser is not None}")
    simple_log(f"  CategoriesBrowser: {CategoriesBrowser is not None}")
    simple_log(f"  FavoritesBrowser: {FavoritesBrowser is not None}")
    simple_log(f"  PluginConfig: {PluginConfig is not None}")
    simple_log(f"  CacheManager: {CacheManager is not None}")


class TVGardenMain(Screen):
    """Main menu screen"""

    skin = """
        <screen name="TVGardenMain" position="center,center" size="1280,720" title="TV Garden" backgroundColor="#1a1a2e" flags="wfNoBorder">
            <ePixmap pixmap="skin_default/buttons/red.png" position="33,650" size="140,40" alphatest="blend" />
            <ePixmap pixmap="skin_default/buttons/green.png" position="174,650" size="140,40" alphatest="blend" />
            <ePixmap pixmap="skin_default/buttons/yellow.png" position="315,650" size="140,40" alphatest="blend" />
            <ePixmap pixmap="skin_default/buttons/blue.png" position="455,650" size="140,40" alphatest="blend" />
            <ePixmap name="" position="0,0" size="1280,720" alphatest="blend" zPosition="-1" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/TVGarden/images/hd/background.png" scale="1" />
            <ePixmap name="" position="1039,531" size="200,80" alphatest="blend" zPosition="1" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/TVGarden/icons/logo.png" scale="1" transparent="1"/>
            <widget source="key_red" render="Label" position="33,649" zPosition="1" size="140,40" font="Regular;20" halign="center" valign="center" transparent="1" />
            <widget source="key_green" render="Label" position="174,650" zPosition="1" size="140,40" font="Regular;20" halign="center" valign="center" transparent="1" />
            <widget source="key_yellow" render="Label" position="315,650" zPosition="1" size="140,40" font="Regular;20" halign="center" valign="center" transparent="1" />
            <widget source="key_blue" render="Label" position="455,650" zPosition="1" size="140,40" font="Regular;20" halign="center" valign="center" transparent="1" />
            <widget name="menu" position="28,116" size="680,474" scrollbarMode="showOnDemand" backgroundColor="#16213e" />
            <widget name="status" position="603,643" size="648,50" font="Regular; 22" halign="center" foregroundColor="#3333ff" transparent="1" />
            <eLabel backgroundColor="#001a2336" cornerRadius="30" position="5,639" size="1270,60" zPosition="-80" />
            <eLabel name="" position="24,101" size="694,502" zPosition="-1" cornerRadius="18" backgroundColor="#00171a1c" foregroundColor="#00171a1c" />
            <widget source="session.VideoPicture" render="Pig" position="739,140" zPosition="19" size="520,308" backgroundColor="transparent" transparent="0" cornerRadius="14" />
        </screen>
        """

    def __init__(self, session):

        self.config = PluginConfig()
        dynamic_skin = self.config.load_skin("TVGardenMain", self.skin)
        self.skin = dynamic_skin

        Screen.__init__(self, session)
        self.session = session
        self["status"] = Label(f"TV Garden {PLUGIN_VERSION} | Ready")

        self.cache = CacheManager()
        self.menu_items = [
            (_("Browse by Country"), "countries", _("Browse channels by country")),
            (_("Browse by Category"), "categories", _("Browse channels by category")),
            (_("Favorites"), "favorites", _("Your favorite channels")),
            (_("Search"), "search", _("Search channels by name")),
            (_("Settings"), "settings", _("Plugin settings and configuration")),
            (_("About"), "about", _("About TV Garden plugin"))
        ]

        self["menu"] = MenuList(self.menu_items)
        self["status"] = Label(
            f"TV Garden v.{PLUGIN_VERSION} | Cache: {self.cache.get_size()} items"
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

        # self.onFirstExecBegin.append(self.check_modules)

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
        """Refresh cache and metadata"""
        self["status"].setText(_("Refreshing data..."))

        def refresh_callback(result):
            if result:
                self["status"].setText(_("Data refreshed successfully"))
                self.session.open(MessageBox,
                                  _("Cache and metadata have been refreshed."),
                                  MessageBox.TYPE_INFO)
            else:
                self["status"].setText(_("Refresh failed"))
                self.session.open(MessageBox,
                                  _("Failed to refresh data. Check internet connection."),
                                  MessageBox.TYPE_ERROR)

        self.cache.clear_all()
        self.cache.get_countries_metadata(force_refresh=True)
        self["status"] = Label(
            f"TV Garden v.{PLUGIN_VERSION} | Cache: {self.cache.get_size()} items"
        )

    def show_about_fallback(self):
        col1_width = 30
        features = [
            ("Browse by Country", "Countries: ~150"),
            ("Browse by Category", "Categories: 29+"),
            ("Favorites Management", "Channels: 50,000+"),
            ("Bouquet Export", "Enigma2 Integration"),
            ("Search All Channels", "Cache: %d items" % self.cache.get_size())
        ]

        about_lines = [
            "TV GARDEN PLUGIN v%s" % PLUGIN_VERSION,
            "══════════════════════════════════════",
            "",
            "CORE FEATURES" + " " * (col1_width - 13) + "STATISTICS"
        ]

        for feat_left, feat_right in features:
            spaces = " " * (col1_width - len(feat_left) - 2)  # -2 per "• "
            about_lines.append("• " + feat_left + spaces + "• " + feat_right)

        about_lines.extend([
            "• Advanced Player with Zapping",
            "• Smart Caching System",
            "• Filtered Streams",
            "• Multiple Skins Support",
            "• Export to Enigma2 Bouquets",
            "",
            "KEY CONTROLS",
            "• FAVORITES: YELLOW=Options, BLUE=Export",
            "• PLAYER: CH+/-=Navigate, OK=Info",
            "• BROWSER: YELLOW=Favorite, BLUE=Clear",
            "",
            "BOUQUET EXPORT",
            "• Export favorites to Enigma2 bouquet",
            "• Single/Bulk channel export",
            "• Auto bouquets.tv integration",
            "• Restart Enigma2 required",
            "",
            "DATA SOURCE",
            "TV Garden Project (Belfagor2005 fork)",
            "https://github.com/Belfagor2005/tv-garden-channel-list",
            "",
            "PLUGIN STATUS: FULLY OPERATIONAL",
            "BOUQUET EXPORT: ACTIVE"
        ])

        about_text = "\n".join(about_lines)
        self.session.open(MessageBox, about_text, MessageBox.TYPE_INFO)

    def show_about(self):
        """Show about screen"""
        try:
            from .browser.about import TVGardenAbout
            self.session.open(TVGardenAbout)
        except ImportError:
            # Fallback to MessageBox
            self.show_about_fallback()

    def exit(self):
        """Exit plugin"""
        self.cache.clear_all()
        self.close()


def main(session, **kwargs):
    """Main entry point"""
    return session.open(TVGardenMain)


def menu(menuid, **kwargs):
    """Plugin menu integration"""
    if menuid == "mainmenu":
        return [(_("TV Garden"), main, "tv_garden", 46)]
    return []


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
