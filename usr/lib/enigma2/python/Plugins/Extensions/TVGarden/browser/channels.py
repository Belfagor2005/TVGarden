#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
TV Garden Plugin - Channels Browser
List and play IPTV channels
Based on TV Garden Project
"""

import tempfile
from os import unlink
from sys import stderr
from urllib.request import urlopen

from enigma import (
    ePicLoad,
    eServiceReference,
)

from Screens.MessageBox import MessageBox
from Screens.ChoiceBox import ChoiceBox

from Components.ActionMap import ActionMap
from Components.Label import Label
from Components.MenuList import MenuList
from Components.Pixmap import Pixmap

try:
    from ..helpers import is_valid_stream_url, log
except ImportError as e:
    print(f"[CHANNELS IMPORT ERROR] {e}", file=stderr)
    # Fallback functions

    def log(msg, level="INFO"):
        print(f"[{level}] TVGarden: {msg}")

    def is_valid_stream_url(url):
        if not url or not isinstance(url, str):
            return False
        url = url.strip()
        valid_prefixes = ('http://', 'https://', 'rtmp://', 'rtsp://')
        return any(url.startswith(prefix) for prefix in valid_prefixes) or '.m3u8' in url.lower()


from .base import BaseBrowser
from ..utils.config import PluginConfig, get_config
from ..utils.cache import CacheManager
from ..utils.favorites import FavoritesManager
from ..player.iptv_player import TVGardenPlayer
from .. import _


class ChannelsBrowser(BaseBrowser):
    skin = """
        <screen name="CountriesBrowser" position="center,center" size="1280,720" title="TV Garden" backgroundColor="#1a1a2e" flags="wfNoBorder">
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
            <widget name="logo" position="45,37" size="80,50" alphatest="blend" />
            <eLabel backgroundColor="#001a2336" cornerRadius="30" position="5,639" size="1270,60" zPosition="-80" />
            <eLabel name="" position="24,101" size="694,502" zPosition="-1" cornerRadius="18" backgroundColor="#00171a1c" foregroundColor="#00171a1c" />
            <widget source="session.VideoPicture" render="Pig" position="739,140" zPosition="19" size="520,308" backgroundColor="transparent" transparent="0" cornerRadius="14" />
        </screen>
    """

    def __init__(self, session, country_code=None, country_name=None,
                 category_id=None, category_name=None):

        self.config = PluginConfig()
        dynamic_skin = self.config.load_skin("ChannelsBrowser", self.skin)
        self.skin = dynamic_skin

        BaseBrowser.__init__(self, session)
        self.session = session
        self.cache = CacheManager()
        self.channels = []
        self.menu_channels = []
        self.current_channel = None

        self.fav_manager = FavoritesManager()

        self.country_code = country_code
        self.country_name = country_name
        self.category_id = category_id
        self.category_name = category_name

        title = ""
        if country_name:
            title = f"Channels - {country_name}"
        elif category_name:
            title = f"Channels - {category_name}"
        self.setTitle(title)

        self["menu"] = MenuList([])
        self["status"] = Label(_("Loading channels..."))
        self["logo"] = Pixmap()

        self["key_red"] = Label(_("Back"))
        self["key_green"] = Label(_("Play"))
        self["key_yellow"] = Label(_("Favorite"))
        self["key_blue"] = Label(_("Info"))

        self["actions"] = ActionMap(["TVGardenActions", "OkCancelActions", "ColorActions"], {
            "cancel": self.exit,
            "ok": self.play_channel,
            "red": self.exit,
            "green": self.play_channel,
            "yellow": self.toggle_favorite,
            "blue": self.show_info,
            "up": self.up,
            "down": self.down,
            "left": self.left,
            "right": self.right,
            "menu": self.channel_menu,
        }, -2)

        self.picload = ePicLoad()
        self.picload.PictureData.get().append(self.update_logo)
        self.onFirstExecBegin.append(self.load_channels)
        # self.onLayoutFinish.append(self.refresh)

    def onSelectionChanged(self):
        """Called when menu selection changes"""
        current_index = self["menu"].getSelectedIndex()
        if current_index is not None:
            self.update_channel_selection(current_index)

    def load_channels(self):
        """Load channels for current context (country or category)"""
        try:
            config = get_config()
            max_channels = config.get("max_channels", 500)

            channels = []
            if self.country_code:
                print(f"[CHANNELS DEBUG] Loading country channels: {self.country_code}", file=stderr)
                channels = self.cache.get_country_channels(self.country_code)
            elif self.category_id:
                print(f"[CHANNELS DEBUG] Loading category channels: {self.category_id}", file=stderr)
                channels = self.cache.get_category_channels(self.category_id)
            else:
                print("[CHANNELS DEBUG] ERROR: No country_code or category_id!", file=stderr)
                return

            print(f"[CHANNELS DEBUG] Total channels received: {len(channels)}", file=stderr)
            print(f"[CHANNELS DEBUG] Max channels limit: {max_channels} (0=all)", file=stderr)

            # Save the ORIGINAL channels
            self.channels = channels

            # Process channels list
            menu_items = []
            self.menu_channels = []

            youtube_count = 0
            valid_count = 0
            problematic_count = 0
            skipped_count = 0

            for idx, channel in enumerate(channels):
                # Apply configurable limit (0 = all channels)
                if max_channels > 0 and idx >= max_channels:
                    print(
                        f"[CHANNELS DEBUG] Stopped at {idx} channels (limit: {max_channels})",
                        file=stderr
                    )
                    skipped_count = len(channels) - idx
                    break

                name = channel.get("name", f"Channel {idx + 1}")

                stream_url = None
                found_in = None
                is_youtube = False

                # 1. Check iptv_urls
                if (
                    "iptv_urls" in channel
                    and isinstance(channel["iptv_urls"], list)
                    and channel["iptv_urls"]
                ):
                    for url in channel["iptv_urls"]:
                        if isinstance(url, str) and url.strip():
                            stream_url = url.strip()
                            found_in = "iptv_urls"
                            break

                # 2. If not found, check youtube_urls
                if (
                    not stream_url
                    and "youtube_urls" in channel
                    and isinstance(channel["youtube_urls"], list)
                    and channel["youtube_urls"]
                ):
                    for url in channel["youtube_urls"]:
                        if isinstance(url, str) and url.strip():
                            stream_url = url.strip()
                            found_in = "youtube_urls"
                            is_youtube = True
                            break

                # 3. If YouTube → skip for now
                if is_youtube:
                    youtube_count += 1
                    print(
                        f"[CHANNELS DEBUG] ⏭️ Skipping YouTube: {name}",
                        file=stderr
                    )
                    continue  # skip this channel

                # 4. Basic URL validation
                if not stream_url:
                    print(
                        f"[CHANNELS DEBUG] ✗ No stream URL: {name}",
                        file=stderr
                    )
                    continue

                # 5. Advanced validation: playable URL
                if not is_valid_stream_url(stream_url):
                    print(
                        f"[CHANNELS DEBUG] ✗ Invalid URL format: {name}",
                        file=stderr
                    )
                    continue

                # 6. CRITICAL FILTER: skip known problematic hosts/protocols
                stream_lower = stream_url.lower()

                problematic_patterns = [
                    "moveonjoy.com",  # caused crashes in logs
                    ".mpd",           # DASH DRM
                    "/dash/",         # DASH stream
                    "drm",
                    "widevine",       # DRM: Widevine
                    "playready",      # DRM: PlayReady
                    "fairplay",       # DRM: Apple FairPlay
                    "keydelivery",
                    "license.",
                    "encryption",
                    "akamaihd.net",   # often DRM
                    "level3.net"      # problematic CDN
                ]

                is_problematic = False
                for pattern in problematic_patterns:
                    if pattern in stream_lower:
                        print(
                            (f"[CHANNELS DEBUG] ⚠️ Skipping problematic pattern "
                             f"'{pattern}': {name[:30]}..."),
                            file=stderr
                        )
                        problematic_count += 1
                        is_problematic = True
                        break

                if is_problematic:
                    continue

                # 7. Prefer HTTP over HTTPS (more stable on Enigma2)
                stream_url_to_use = stream_url

                # Debug URL type
                if stream_url.startswith("http://"):
                    print("[CHANNELS DEBUG]   HTTP URL (good)", file=stderr)
                elif stream_url.startswith("https://"):
                    print("[CHANNELS DEBUG]   HTTPS URL (may have issues)",
                          file=stderr)
                elif (
                    stream_url.startswith("rtmp://")
                    or stream_url.startswith("rtsp://")
                ):
                    print("[CHANNELS DEBUG]   RTMP/RTSP URL (needs gstreamer)",
                          file=stderr)

                # 8. Build channel object
                channel_data = {
                    "name": name,
                    "url": stream_url_to_use,
                    "stream_url": stream_url_to_use,
                    "logo": (
                        channel.get("logo")
                        or channel.get("icon")
                        or channel.get("image")
                    ),
                    "id": channel.get("nanoid", f"ch_{idx}"),
                    "description": channel.get("description", ""),
                    "group": channel.get("group", ""),
                    "language": channel.get("language", ""),
                    "country": channel.get("country", ""),
                    "found_in": found_in,
                    "original_index": idx,
                    "is_youtube": False,
                }

                menu_items.append((name, idx))
                self.menu_channels.append(channel_data)
                valid_count += 1
                print(f"[CHANNELS DEBUG] ✓ Added: {name}", file=stderr)

            self["menu"].setList(menu_items)
            self["menu"].onSelectionChanged.append(self.onSelectionChanged)
            if menu_items:
                selected_idx = menu_items[0][1]
                if 0 <= selected_idx < len(self.menu_channels):
                    self.current_channel = self.menu_channels[selected_idx]
                    print(f"[CHANNELS DEBUG] First channel: {self.current_channel['name']}", file=stderr)
                    self.update_channel_selection(0)

            # Build status message
            if max_channels > 0 and len(channels) > max_channels:
                status_text = _("Showing {shown} of {total} channels").format(
                    shown=min(max_channels, valid_count),
                    total=valid_count + youtube_count + problematic_count
                )
            else:
                status_text = _("Found {count} playable channels").format(count=valid_count)

            if youtube_count > 0:
                status_text += " " + _("(skipped {count} YouTube)").format(count=youtube_count)

            if problematic_count > 0:
                status_text += " " + _("(filtered {count} problematic)").format(count=problematic_count)

            if skipped_count > 0 and max_channels > 0:
                status_text += " " + _("(limited to first {limit})").format(limit=max_channels)

            self["status"].setText(status_text)

            print(f"[CHANNELS FINAL] Playable: {valid_count}, "
                  f"Skipped YouTube: {youtube_count}, "
                  f"Filtered problematic: {problematic_count}, "
                  f"Config limit: {max_channels}, "
                  f"Skipped by limit: {skipped_count}", file=stderr)

        except Exception as e:
            print(f"[CHANNELS ERROR] load_channels failed: {e}", file=stderr)
            import traceback
            traceback.print_exc()
            self["status"].setText(_("Error loading channels"))

    def update_channel_selection(self, index):
        """Update selection and load logo"""
        print(f"[DEBUG] update_channel_selection called with index: {index}", file=stderr)
        if 0 <= index < len(self.menu_channels):
            self.current_channel = self.menu_channels[index]
            print(f"[DEBUG] Selected channel: {self.current_channel['name']}", file=stderr)
            print(f"[DEBUG] Stream URL: {self.current_channel.get('stream_url', 'NONE')}", file=stderr)

            logo_url = self.current_channel.get('logo')
            if logo_url:
                print(f"[DEBUG] Loading logo: {logo_url[:50]}...", file=stderr)
                self.download_logo(logo_url)
            else:
                print("[DEBUG] No logo available", file=stderr)
                self["logo"].hide()
        else:
            print(f"[ChannelsBrowser] ERROR: Index {index} out of range (0-{len(self.menu_channels) - 1})", file=stderr)

    def download_logo(self, url):
        """Download and display channel logo"""
        try:
            with urlopen(url, timeout=5) as response:
                logo_data = response.read()

                with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as f:
                    f.write(logo_data)
                    temp_path = f.name

                # Load with ePicLoad
                self.picload.setPara((80, 50, 1, 1, False, 1, "#00000000"))
                self.picload.startDecode(temp_path)

                # Cleanup
                unlink(temp_path)

        except Exception as e:
            print(f"[ChannelsBrowser] Error downloading logo: {e}", file=stderr)
            self["logo"].hide()

    def update_logo(self, picInfo=None):
        """Update logo pixmap"""
        ptr = self.picload.getData()
        if ptr:
            self["logo"].instance.setScale(1)
            self["logo"].instance.setPixmap(ptr)
            self["logo"].show()
            print("[ChannelsBrowser] logo displayed", file=stderr)
        else:
            self["logo"].hide()
            print("[ChannelsBrowser] No logo data, hiding", file=stderr)

    def play_channel(self):
        """Play the selected channel."""
        # 1. Get the correct index from the menu
        menu_idx = self["menu"].getSelectedIndex()
        print(f"[PLAY DEBUG] Menu index: {menu_idx}", file=stderr)

        if (
            menu_idx is None
            or menu_idx < 0
            or menu_idx >= len(self.menu_channels)
        ):
            print(
                f"[PLAY DEBUG] ERROR: Invalid index {menu_idx}",
                file=stderr
            )
            return

        # 2. Get the selected channel by index
        selected_channel = self.menu_channels[menu_idx]
        stream_url = (
            selected_channel.get("stream_url")
            or selected_channel.get("url")
        )

        if not stream_url:
            self["status"].setText(_("No stream URL"))
            return

        # 3. Critical debug info
        print("[PLAY DEBUG] ===== PASSING TO PLAYER =====",
              file=stderr)
        print(f"[PLAY DEBUG] Channel: {selected_channel.get('name')}",
              file=stderr)
        print(f"[PLAY DEBUG] Index: {menu_idx}", file=stderr)
        print(f"[PLAY DEBUG] Total: {len(self.menu_channels)}",
              file=stderr)
        print(f"[PLAY DEBUG] URL: {stream_url[:80]}...",
              file=stderr)

        # 4. Create a basic service reference
        service_ref = eServiceReference(4097, 0, stream_url)
        service_ref.setName(selected_channel.get("name", "TV Garden"))

        # 5. Pass to player: service_ref, channel list, index
        self.session.open(
            TVGardenPlayer,
            service_ref,
            self.menu_channels,
            menu_idx
        )

    def toggle_favorite(self):
        """Add/remove channel from favorites"""
        if self.current_channel:
            if self.fav_manager.is_favorite(self.current_channel):
                self.fav_manager.remove(self.current_channel)
                self["status"].setText(_("Removed from favorites"))
            else:
                self.fav_manager.add(self.current_channel)
                self["status"].setText(_("Added to favorites"))

    def show_info(self):
        """Show channel information"""
        if self.current_channel:
            info = f"{self.current_channel.get('name', 'Unknown')}\n\n"

            desc = self.current_channel.get('description')
            if desc:
                info += f"{desc}\n\n"

            stream_url = self.current_channel.get('stream_url', 'N/A')
            info += _("Stream: %s") % (stream_url[:60] + '...' if len(stream_url) > 60 else stream_url)

            self.session.open(MessageBox, info, MessageBox.TYPE_INFO)

    def channel_menu(self):
        """Show channel context menu"""
        menu = [
            (_("Play Channel"), "play"),
            (_("Add to Favorites"), "favorite"),
            (_("Channel Information"), "info"),
            (_("Share Channel"), "share"),
            (_("Report Issue"), "report"),
        ]
        self.session.openWithCallback(self.menu_callback, ChoiceBox,
                                      title=_("Channel Menu"), list=menu)

    def menu_callback(self, choice):
        """Handle menu selection"""
        if choice:
            if choice[1] == "play":
                self.play_channel()
            elif choice[1] == "favorite":
                self.toggle_favorite()
            elif choice[1] == "info":
                self.show_info()

    def up(self):
        """Handle up key"""
        self["menu"].up()
        current_index = self["menu"].getSelectedIndex()
        print(f"[DEBUG] Up -> index: {current_index}", file=stderr)
        self.update_channel_selection(current_index)

    def down(self):
        """Handle down key"""
        self["menu"].down()
        current_index = self["menu"].getSelectedIndex()
        print(f"[DEBUG] Down -> index: {current_index}", file=stderr)
        self.update_channel_selection(current_index)

    def left(self):
        """Handle left key"""
        self["menu"].pageUp()
        current_index = self["menu"].getSelectedIndex()
        print(f"[DEBUG] Left -> index: {current_index}", file=stderr)
        self.update_channel_selection(current_index)

    def right(self):
        """Handle right key"""
        self["menu"].pageDown()
        current_index = self["menu"].getSelectedIndex()
        print(f"[DEBUG] Right -> index: {current_index}", file=stderr)
        self.update_channel_selection(current_index)

    def exit(self):
        """Exit browser"""
        self.close()
