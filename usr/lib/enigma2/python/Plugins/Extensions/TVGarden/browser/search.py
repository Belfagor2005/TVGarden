#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
TV Garden Plugin - SearchBrowser
Live search like Vavoo
Data Source: TV Garden Project
"""

from sys import stderr
from Components.ActionMap import ActionMap
from Components.MenuList import MenuList
from Components.Label import Label
from Components.Sources.StaticText import StaticText
from enigma import eServiceReference, eTimer

from Screens.MessageBox import MessageBox
from Screens.VirtualKeyBoard import VirtualKeyBoard

from .base import BaseBrowser
from ..utils.config import PluginConfig
from ..player.iptv_player import TVGardenPlayer
from ..utils.cache import CacheManager
from ..utils.favorites import FavoritesManager
from ..helpers import CATEGORIES, is_valid_stream_url
from .. import _


class SearchBrowser(BaseBrowser):
    skin = """
        <screen name="SearchBrowser" position="center,center" size="1280,720" title="TV Garden" backgroundColor="#1a1a2e" flags="wfNoBorder">
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
            <widget name="search_label" position="30,30" size="420,60" font="Regular; 32" halign="right" valign="center" foregroundColor="#ffffff" />
            <widget name="search_text" position="460,29" size="789,60" font="Regular;32" halign="left" valign="center" backgroundColor="#2d3047" foregroundColor="#ffffff" />
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
        self.cache = CacheManager()
        self.fav_manager = FavoritesManager()

        self.search_query = ""
        self.all_channels = []
        self.filtered_channels = []
        self.menu_channels = []

        self["search_label"] = Label(_("Search:"))
        self["search_text"] = Label("")
        self["menu"] = MenuList([])
        self["status"] = Label(_("Press GREEN for keyboard..."))
        self["key_red"] = StaticText(_("Back"))
        self["key_green"] = StaticText(_("Keyboard"))
        self["key_yellow"] = StaticText(_("Favorite"))
        self["key_blue"] = StaticText(_("Clear"))

        self["actions"] = ActionMap(["TVGardenActions", "OkCancelActions", "ColorActions", "DirectionActions"], {
            "cancel": self.exit,
            "ok": self.play_channel,
            "red": self.exit,
            "green": self.open_keyboard,
            "yellow": self.toggle_favorite,
            "blue": self.clear_search,
            "up": self.up,
            "down": self.down,
            "left": self.left,
            "right": self.right,
        }, -2)

        self.search_timer = eTimer()
        self.search_timer.callback.append(self.perform_search)

        self.onFirstExecBegin.append(self.load_all_channels)

    def load_all_channels(self):
        """Load all channels using dynamic categories"""
        print("[SearchSimple] Loading channels dynamically...", file=stderr)
        self.all_channels = []
        
        try:
            # 1. FIRST try using all-channels.json
            print("[SearchSimple] Trying all-channels.json...", file=stderr)
            all_channels_data = self.cache.get_category_channels("all-channels")
            
            if all_channels_data:
                self.all_channels = all_channels_data
                print("[SearchSimple] ✓ Loaded %d from all-channels.json" % len(self.all_channels), file=stderr)
            else:
                # 2. FALLBACK: use dynamic categories
                print("[SearchSimple] Using dynamic categories...", file=stderr)
                
                # Get available categories
                categories = self.cache.get_available_categories()
                print("[SearchSimple] Found %d available categories" % len(categories), file=stderr)
                
                for category in categories:
                    cat_id = category['id']
                    if cat_id == 'all-channels':  # Already attempted
                        continue
                        
                    try:
                        channels = self.cache.get_category_channels(cat_id)
                        if channels:
                            for channel in channels:
                                channel['category'] = category['name']
                                self.all_channels.append(channel)
                            print("[SearchSimple]   Added %d from %s" % (len(channels), cat_id), file=stderr)
                    except Exception as e:
                        print("[SearchSimple]   Skipped %s: %s" % (cat_id, str(e)[:50]), file=stderr)
                        continue
            
            # Final status
            total = len(self.all_channels)
            if total > 0:
                self["status"].setText(_("Ready - {} channels").format(total))
                print("[SearchSimple] ✓ TOTAL: %d channels ready" % total, file=stderr)
            else:
                self["status"].setText(_("No channels loaded"))
                print("[SearchSimple] ✗ No channels loaded", file=stderr)
                
        except Exception as e:
            print("[SearchSimple] ERROR: %s" % e, file=stderr)
            self["status"].setText(_("Error loading channels"))

    # def load_all_channels(self):
        # """Load all channels once for fast searching"""
        # print("[SearchSimple] Loading all channels...", file=stderr)
        # self.all_channels = []

        # try:
            # # Carica da tutte le categorie
            # for category in CATEGORIES:
                # category_id = category['id']
                # try:
                    # channels = self.cache.get_category_channels(category_id)
                    # for channel in channels:
                        # # Aggiungi info categoria
                        # channel_copy = channel.copy()
                        # channel_copy['category'] = category['name']
                        # self.all_channels.append(channel_copy)
                # except:
                    # pass

            # print(f"[SearchSimple] Loaded {len(self.all_channels)} channels", file=stderr)
            # self["status"].setText(_("Ready - Press GREEN to search"))

        # except Exception as e:
            # print(f"[SearchSimple] Error loading channels: {e}", file=stderr)
            # self["status"].setText(_("Error loading channels"))

    def open_keyboard(self):
        """Open virtual keyboard"""
        self.session.openWithCallback(
            self.keyboard_callback,
            VirtualKeyBoard,
            title=_("Search Channels"),
            text=self.search_query
        )

    def keyboard_callback(self, result):
        """Handle keyboard input"""
        if result is not None:
            self.search_query = result
            self["search_text"].setText(self.search_query)
            self["status"].setText(_("Searching..."))

            self.search_timer.start(300, True)

    def clear_search(self):
        """Clear search"""
        self.search_query = ""
        self["search_text"].setText("")
        self["menu"].setList([])
        self.menu_channels = []
        self["status"].setText(_("Press GREEN for keyboard..."))

    def match_channel(self, channel, query):
        """Check if channel matches search query"""
        # Search in name
        name = channel.get('name', '').lower()
        if query in name:
            return True

        # Search in description
        description = channel.get('description', '').lower()
        if description and query in description:
            return True

        # Search in group/category
        group = channel.get('group', '').lower()
        if group and query in group:
            return True

        return False

    def perform_search(self):
        """Perform the actual search"""
        query = self.search_query.lower()
        print(f"[SearchBrowser] Searching for: '{query}'", file=stderr)

        self.search_results = []
        self.menu_channels = []

        try:
            all_channels = self.cache.get_category_channels("all-channels")
            for channel in all_channels:
                if self.match_channel(channel, query):
                    self.search_results.append(channel)
        except Exception as e:
            print(f"[SearchBrowser] Search error: {e}", file=stderr)

        self.display_search_results()

    """
    # def perform_search(self):
        # query = self.search_query.lower()
        # print(f"[SearchBrowser] Optimized search for: '{query}'", file=stderr)

        # self.search_results = []
        # self.menu_channels = []

        # # STRATEGY 1: First look in the main file "all-channels.json" (FASTER)
        # try:
            # all_channels_data = self.cache.get_category_channels("all-channels")
            # for channel in all_channels_data:
                # if self.match_channel(channel, query):
                    # self.search_results.append(channel)
            # print(f"[SearchBrowser] Found {len(self.search_results)} results in 'all-channels.json'", file=stderr)

        # except Exception as e:
            # print(f"[SearchBrowser] Error with 'all-channels.json': {e}", file=stderr)
            # # STRATEGY 2: Fallback - Search Category Files
            # for category in CATEGORIES:
                # try:
                    # channels = self.cache.get_category_channels(category['id'])
                    # for channel in channels:
                        # if self.match_channel(channel, query):
                            # self.search_results.append(channel)
                # except Exception as e:
                    # print('error on perform_search: ', str(e))
                    # pass

        # self.display_search_results()

    # def perform_search(self):
        # query = self.search_query.lower().strip()

        # if not query or len(query) < 2:
            # self["status"].setText(_("Enter at least 2 characters"))
            # return

        # print(f"[SearchSimple] Searching for: '{query}'", file=stderr)

        # self.filtered_channels = []
        # self.menu_channels = []
        # valid_count = 0

        # for channel in self.all_channels:
            # # Cerca nel nome
            # name = channel.get('name', '').lower()
            # if query in name:
                # # Filtra e valida
                # stream_url = self.extract_stream_url(channel)
                # if stream_url and is_valid_stream_url(stream_url):
                    # channel_data = self.create_channel_data(channel, stream_url)
                    # self.filtered_channels.append(channel)
                    # self.menu_channels.append(channel_data)
                    # valid_count += 1

        # # Mostra risultati
        # menu_items = []
        # for idx, channel_data in enumerate(self.menu_channels):
            # name = channel_data['name']
            # extra = []
            # if channel_data.get('category'):
                # extra.append(channel_data['category'])
            # if channel_data.get('country'):
                # extra.append(channel_data['country'])

            # display = name
            # if extra:
                # display += f" [{', '.join(extra)}]"
            # menu_items.append((display, idx))

        # self["menu"].setList(menu_items)

        # if menu_items:
            # self["status"].setText(_("Found {} channels").format(valid_count))
        # else:
            # self["status"].setText(_("No channels found for: {}").format(query))
    """

    def display_search_results(self):
        """Display search results in menu"""
        print(f"[SearchBrowser] Found {len(self.search_results)} results", file=stderr)

        menu_items = []
        self.menu_channels = []
        valid_count = 0

        for idx, channel in enumerate(self.search_results):
            if idx >= 100:  # Performance limit
                break

            name = channel.get('name', f'Result {idx + 1}')
            stream_url = None

            # Extract URL
            if 'iptv_urls' in channel and channel['iptv_urls']:
                for url in channel['iptv_urls']:
                    if url and url.strip():
                        stream_url = url.strip()
                        break

            # Skip if no valid URL
            if not stream_url:
                continue

            # Validate URL
            if not is_valid_stream_url(stream_url):
                continue

            # Create display name
            extra_info = []
            if channel.get('category'):
                extra_info.append(channel['category'])
            if channel.get('country'):
                extra_info.append(channel['country'])

            display_name = name
            if extra_info:
                display_name += f" [{', '.join(extra_info)}]"

            # Create channel data
            channel_data = {
                'name': name,
                'url': stream_url,
                'stream_url': stream_url,
                'logo': channel.get('logo'),
                'id': channel.get('nanoid', f'srch_{idx}'),
                'description': channel.get('description', ''),
                'group': channel.get('group', ''),
                'language': channel.get('language', ''),
                'country': channel.get('country', ''),
                'is_youtube': False
            }

            menu_items.append((display_name, idx))
            self.menu_channels.append(channel_data)
            valid_count += 1

        # Update UI
        self["menu"].setList(menu_items)

        if menu_items:
            self["status"].setText(_("Found {} channels").format(valid_count))
            if self.menu_channels:
                self.current_channel = self.menu_channels[0]
        else:
            self["status"].setText(_("No channels found for: {}").format(self.search_query))

    def extract_stream_url(self, channel):
        """Extract stream URL from channel"""
        # Check iptv_urls
        if 'iptv_urls' in channel and isinstance(channel['iptv_urls'], list):
            for url in channel['iptv_urls']:
                if isinstance(url, str) and url.strip():
                    return url.strip()

        # Check youtube_urls (skip)
        if 'youtube_urls' in channel and isinstance(channel['youtube_urls'], list):
            for url in channel['youtube_urls']:
                if isinstance(url, str) and url.strip():
                    return None  # Skip YouTube

        return channel.get('url', '')

    def create_channel_data(self, channel, stream_url):
        """Create channel data for player"""
        return {
            'name': channel.get('name', ''),
            'url': stream_url,
            'stream_url': stream_url,
            'logo': channel.get('logo') or channel.get('icon'),
            'id': channel.get('nanoid', ''),
            'description': channel.get('description', ''),
            'group': channel.get('group', '') or channel.get('category', ''),
            'language': channel.get('language', ''),
            'country': channel.get('country', ''),
            'category': channel.get('category', ''),
            'is_youtube': False
        }

    def get_current_channel(self):
        menu_idx = self["menu"].getSelectedIndex()
        if menu_idx is not None and 0 <= menu_idx < len(self.menu_channels):
            return self.menu_channels[menu_idx], menu_idx
        return None, -1

    def play_channel(self):
        """Play selected channel"""
        channel, idx = self.get_current_channel()
        if not channel:
            return

        stream_url = channel.get('stream_url')
        if not stream_url:
            self["status"].setText(_("No stream URL"))
            return

        try:
            url_encoded = stream_url.replace(":", "%3a")
            name_encoded = channel['name'].replace(":", "%3a")
            ref_str = f"4097:0:0:0:0:0:0:0:0:0:{url_encoded}:{name_encoded}"

            service_ref = eServiceReference(ref_str)
            service_ref.setName(channel['name'])

            self.session.open(TVGardenPlayer, service_ref, self.menu_channels, idx)

        except Exception as e:
            print(f"[SearchSimple] Play error: {e}", file=stderr)
            self.session.open(MessageBox, _("Error opening player"), MessageBox.TYPE_ERROR)

    def toggle_favorite(self):
        """Add/remove channel from favorites"""
        channel, channel_idx = self.get_current_channel()
        if channel:
            if self.fav_manager.is_favorite(channel):
                self.fav_manager.remove(channel)
                self["status"].setText(_("Removed from favorites"))
            else:
                self.fav_manager.add(channel)
                self["status"].setText(_("Added to favorites"))

    def up(self):
        self["menu"].up()

    def down(self):
        self["menu"].down()

    def left(self):
        self["menu"].pageUp()

    def right(self):
        self["menu"].pageDown()

    def exit(self):
        if self.search_timer.isActive():
            self.search_timer.stop()
        self.close()
