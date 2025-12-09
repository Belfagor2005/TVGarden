#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
TV Garden Plugin - Favorites Browser
Browse and manage favorite channels
Based on TV Garden Project
"""

from sys import stderr
from Components.ActionMap import ActionMap
from Components.MenuList import MenuList
from Components.Label import Label
from enigma import eServiceReference
from Screens.MessageBox import MessageBox

from .base import BaseBrowser
from ..utils.config import PluginConfig
from ..player.iptv_player import TVGardenPlayer
from ..utils.favorites import FavoritesManager
from ..utils.cache import CacheManager
from ..helpers import is_valid_stream_url
from .. import _


class FavoritesBrowser(BaseBrowser):
    """Browse and manage favorite channels"""

    skin = """
        <screen name="FavoritesBrowser" position="center,center" size="1280,720" title="TV Garden" backgroundColor="#1a1a2e" flags="wfNoBorder">
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
        dynamic_skin = self.config.load_skin("FavoritesBrowser", self.skin)
        self.skin = dynamic_skin

        BaseBrowser.__init__(self, session)
        self.session = session
        self.fav_manager = FavoritesManager()
        self.cache = CacheManager()
        self.menu_channels = []
        self.current_channel = None
        self["menu"] = MenuList([])
        self["status"] = Label(_("Loading favorites..."))
        self["key_red"] = Label(_("Back"))
        self["key_green"] = Label(_("Play"))
        self["key_yellow"] = Label(_("Remove"))
        self["key_blue"] = Label(_("Clear All"))
        self["actions"] = ActionMap(["TVGardenActions", "OkCancelActions", "ColorActions", "DirectionActions"], {
            "cancel": self.exit,
            "ok": self.play_channel,
            "red": self.exit,
            "green": self.play_channel,
            "yellow": self.remove_favorite,
            "blue": self.clear_all,
            "up": self.up,
            "down": self.down,
            "left": self.left,
            "right": self.right,
        }, -2)
        self.onFirstExecBegin.append(self.load_favorites)

    def load_favorites(self):
        """Load favorites from file"""
        try:
            favorites = self.fav_manager.get_all()
            print(f"[FavoritesBrowser] Loaded {len(favorites)} favorites", file=stderr)

            menu_items = []
            self.menu_channels = []

            for idx, channel in enumerate(favorites):
                name = channel.get('name', f'Favorite {idx + 1}')

                # Extract stream URL
                stream_url = channel.get('stream_url') or channel.get('url')

                # Validate URL
                if stream_url and is_valid_stream_url(stream_url):
                    # Add extra info for display
                    extra_info = []
                    if channel.get('country'):
                        extra_info.append(channel['country'])
                    if channel.get('category'):
                        extra_info.append(channel['category'])

                    display_name = name
                    if extra_info:
                        display_name += f" [{', '.join(extra_info)}]"

                    # Create channel object
                    channel_data = {
                        'name': name,
                        'url': stream_url,
                        'stream_url': stream_url,
                        'logo': channel.get('logo') or channel.get('icon'),
                        'id': channel.get('id', f'fav_{idx}'),
                        'description': channel.get('description', ''),
                        'group': channel.get('group', ''),
                        'language': channel.get('language', ''),
                        'country': channel.get('country', ''),
                        'is_youtube': False
                    }

                    menu_items.append((display_name, idx))
                    self.menu_channels.append(channel_data)

            self["menu"].setList(menu_items)

            if menu_items:
                self["status"].setText(_("%d favorite channels") % len(menu_items))
                # Select first item
                if self.menu_channels:
                    self.current_channel = self.menu_channels[0]
            else:
                self["status"].setText(_("No favorite channels"))
                self.current_channel = None

        except Exception as e:
            print(f"[FavoritesBrowser] Error loading favorites: {e}", file=stderr)
            self["status"].setText(_("Error loading favorites"))

    def get_current_channel(self):
        """Get currently selected channel"""
        menu_idx = self["menu"].getSelectedIndex()
        if menu_idx is not None and 0 <= menu_idx < len(self.menu_channels):
            return self.menu_channels[menu_idx], menu_idx

        return None, -1

    def play_channel(self):
        """Play selected favorite channel"""
        channel, channel_idx = self.get_current_channel()
        if not channel:
            self["status"].setText(_("No channel selected"))
            return

        stream_url = channel.get('stream_url') or channel.get('url')
        if not stream_url:
            self["status"].setText(_("No stream URL available"))
            return

        try:
            # Create service reference
            url_encoded = stream_url.replace(":", "%3a")
            name_encoded = channel['name'].replace(":", "%3a")
            ref_str = f"4097:0:0:0:0:0:0:0:0:0:{url_encoded}:{name_encoded}"

            service_ref = eServiceReference(ref_str)
            service_ref.setName(channel['name'])

            # Open player with favorites list
            print(f"[FavoritesBrowser] Playing: {channel['name']}", file=stderr)
            self.session.open(TVGardenPlayer, service_ref, self.menu_channels, channel_idx)

        except Exception as e:
            print(f"[FavoritesBrowser] Player error: {e}", file=stderr)
            self.session.open(MessageBox,
                              _("Error opening player"),
                              MessageBox.TYPE_ERROR)

    def remove_favorite(self):
        """Remove the selected channel from favorites."""
        channel, index = self.get_current_channel()

        if channel:
            if self.fav_manager.remove(channel):
                print("[DEBUG] Type of index in remove_favorite: %s" % type(index))
                self["status"].setText(_("Removed from favorites"))
            else:
                self["status"].setText("Error removing favorite")
        else:
            self["status"].setText("No channel selected")

    def clear_all(self):
        """Clear all favorites"""
        if self.fav_manager.clear_all():
            self["status"].setText(_("All favorites cleared"))
            self["menu"].setList([])
            self.menu_channels = []
            self.current_channel = None
        else:
            self["status"].setText(_("Error clearing favorites"))

    def up(self):
        """Handle up key"""
        self["menu"].up()

    def down(self):
        """Handle down key"""
        self["menu"].down()

    def left(self):
        """Handle left key"""
        self["menu"].pageUp()

    def right(self):
        """Handle right key"""
        self["menu"].pageDown()

    def exit(self):
        """Exit browser"""
        self.close()
