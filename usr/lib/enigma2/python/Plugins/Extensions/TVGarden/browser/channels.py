#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
TV Garden Plugin - Channels Browser
List and play IPTV channels
Based on TV Garden Project
"""
from __future__ import print_function
import tempfile
from os import unlink
from sys import stderr, version_info
from enigma import (
    ePicLoad,
    eServiceReference,
)
from Components.Label import Label
from Components.Pixmap import Pixmap
from Components.MenuList import MenuList
from Screens.ChoiceBox import ChoiceBox
from Screens.MessageBox import MessageBox
from Components.ActionMap import ActionMap

if version_info[0] == 3:
    from urllib.request import urlopen
else:
    from urllib2 import urlopen


try:
    from ..helpers import is_valid_stream_url, log
except ImportError as e:
    print("[CHANNELS IMPORT ERROR] %s" % e, file=stderr)

    # Fallback functions
    def log(msg, level="INFO"):
        print("[%s] TVGarden: %s" % (level, msg))

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
            <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/TVGarden/icons/redbutton.png" position="32,688" size="140,6" zPosition="1" transparent="1" alphatest="blend" />
            <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/TVGarden/icons/greenbutton.png" position="176,688" size="140,6" zPosition="1" transparent="1" alphatest="blend" />
            <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/TVGarden/icons/yellowbutton.png" position="314,688" size="140,6" zPosition="1" transparent="1" alphatest="blend" />
            <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/TVGarden/icons/bluebutton.png" position="458,688" size="140,6" zPosition="1" transparent="1" alphatest="blend" />
            <ePixmap name="" position="0,0" size="1280,720" zPosition="-1" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/TVGarden/images/hd/background.png" scale="1" alphatest="blend" />
            <ePixmap name="" position="1039,531" size="200,80" zPosition="1" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/TVGarden/icons/logo.png" scale="1" transparent="1" alphatest="blend"/>
            <widget source="key_red" render="Label" position="33,649" zPosition="1" size="140,40" font="Regular;20" foregroundColor="#3333ff" halign="center" valign="center" transparent="1" alphatest="blend" />
            <widget source="key_green" render="Label" position="174,650" zPosition="1" size="140,40" font="Regular;20" foregroundColor="#3333ff" halign="center" valign="center" transparent="1" alphatest="blend" />
            <widget source="key_yellow" render="Label" position="315,650" zPosition="1" size="140,40" font="Regular;20" foregroundColor="#3333ff" halign="center" valign="center" transparent="1" alphatest="blend" />
            <widget source="key_blue" render="Label" position="455,650" zPosition="1" size="140,40" font="Regular;20" foregroundColor="#3333ff" halign="center" valign="center" transparent="1" alphatest="blend" />
            <widget name="menu" position="28,116" size="680,474" scrollbarMode="showOnDemand" backgroundColor="#16213e" />
            <widget name="status" position="603,643" size="648,50" font="Regular; 22" halign="center" foregroundColor="#3333ff" transparent="1" alphatest="blend" />
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
            title = "Channels - %s" % country_name
        elif category_name:
            title = "Channels - %s" % category_name
        self.setTitle(title)

        self.export_enabled = True
        self.auto_refresh_bouquet = False
        self.confirm_before_export = True

        self._load_export_settings()

        self["menu"] = MenuList([])
        self["status"] = Label(_("Loading channels..."))
        self["logo"] = Pixmap()

        if self.export_enabled:
            self["key_blue"] = Label(_("Export"))
        else:
            self["key_blue"] = Label(_("Info"))

        self["key_red"] = Label(_("Back"))
        self["key_green"] = Label(_("Play"))
        self["key_yellow"] = Label(_("Favorite"))

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

    def channel_menu(self):
        """Show channel context menu"""
        menu = [
            (_("Play Channel"), "play"),
            (_("Add to Favorites"), "favorite"),
            (_("Channel Information"), "info"),
        ]
        if self.export_enabled and self.menu_channels:
            menu.append((_("Export Current View"), "export_current"))
            menu.append((_("Export Settings"), "export_settings"))

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
            elif choice[1] == "export_current":
                self.export_current_view()
            elif choice[1] == "export_settings":
                self.export_settings_menu()

    def load_channels(self):
        """Load channels for current context (country or category)"""
        try:
            config = get_config()
            max_channels = config.get("max_channels", 500)

            channels = []
            if self.country_code:
                log.debug("Loading country channels: %s" % self.country_code, module="Channels")
                channels = self.cache.get_country_channels(self.country_code)
            elif self.category_id:
                log.debug("Loading category channels: %s" % self.category_id, module="Channels")
                channels = self.cache.get_category_channels(self.category_id)
            else:
                log.error("ERROR: No country_code or category_id!", module="Channels")
                return

            log.debug("Total channels received: %d" % len(channels), module="Channels")
            log.debug("Max channels limit: %d (0=all)" % max_channels, module="Channels")

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
                    log.debug("Stopped at %d channels (limit: %d)" % (idx, max_channels), module="Channels")
                    skipped_count = len(channels) - idx
                    break

                name = channel.get("name", "Channel %d" % (idx + 1))

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
                        "[CHANNELS DEBUG] ⏭️ Skipping YouTube: %s" % name,
                        file=stderr
                    )
                    continue  # skip this channel

                # 4. Basic URL validation
                if not stream_url:
                    log.warning("✗ No stream URL: %s" % name, module="Channels")
                    continue

                # 5. Advanced validation: playable URL
                if not is_valid_stream_url(stream_url):
                    log.warning("✗ Invalid URL format: %s" % name, module="Channels")
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
                        log.warning("⚠️ Skipping problematic pattern '%s': %s..." % (pattern, name[:30]), module="Channels")
                        problematic_count += 1
                        is_problematic = True
                        break

                if is_problematic:
                    continue

                # 7. Prefer HTTP over HTTPS (more stable on Enigma2)
                stream_url_to_use = stream_url

                # Debug URL type
                if stream_url.startswith("http://"):
                    log.debug("   HTTP URL (good)", module="Channels")
                elif stream_url.startswith("https://"):
                    log.debug("   HTTPS URL (may have issues)", module="Channels")
                elif stream_url.startswith("rtmp://") or stream_url.startswith("rtsp://"):
                    log.debug("   RTMP/RTSP URL (needs gstreamer)", module="Channels")

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
                    "id": channel.get("nanoid", "ch_%d" % idx),
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
                log.debug("✓ Added: %s" % name, module="Channels")

            self["menu"].setList(menu_items)
            self["menu"].onSelectionChanged.append(self.onSelectionChanged)
            if menu_items:
                selected_idx = menu_items[0][1]
                if 0 <= selected_idx < len(self.menu_channels):
                    self.current_channel = self.menu_channels[selected_idx]
                    log.debug("First channel: %s" % self.current_channel['name'], module="Channels")
                    self.update_channel_selection(0)

            # Build status message
            if max_channels > 0 and len(channels) > max_channels:
                msg = _("Showing {shown} of {total} channels")
                status_text = msg.format(
                    shown=min(max_channels, valid_count),
                    total=valid_count + youtube_count + problematic_count
                )
            else:
                status_text = _("Found %d playable channels") % valid_count

            if youtube_count > 0:
                status_text += " " + _("(skipped %d YouTube)") % youtube_count

            if problematic_count > 0:
                status_text += " " + _("(filtered %d problematic)") % problematic_count

            if skipped_count > 0 and max_channels > 0:
                status_text += " " + _("(limited to first %d)") % max_channels

            self["status"].setText(status_text)

            log.info("Playable: %d, Skipped YouTube: %d, Filtered problematic: %d, Config limit: %d, Skipped by limit: %d" %
                     (valid_count, youtube_count, problematic_count, max_channels, skipped_count),
                     module="Channels")

        except Exception as e:
            log.error("load_channels failed: %s" % e, module="Channels")
            import traceback
            traceback.print_exc()
            self["status"].setText(_("Error loading channels"))

    def update_channel_selection(self, index):
        """Update selection and load logo"""
        log.debug("update_channel_selection called with index: %d" % index, module="Channels")
        if 0 <= index < len(self.menu_channels):
            self.current_channel = self.menu_channels[index]
            log.debug("Selected channel: %s" % self.current_channel['name'], module="Channels")
            log.debug("Stream URL: %s" % self.current_channel.get('stream_url', 'NONE'), module="Channels")

            logo_url = self.current_channel.get('logo')
            if logo_url:
                log.debug("Loading logo: %s..." % logo_url[:50], module="Channels")
                self.download_logo(logo_url)
            else:
                log.debug("No logo available", module="Channels")
                self["logo"].hide()
        else:
            log.error("ERROR: Index %d out of range (0-%d)" % (index, len(self.menu_channels) - 1), module="Channels")

    def update_logo(self, picInfo=None):
        """Update logo pixmap"""
        ptr = self.picload.getData()
        if ptr:
            self["logo"].instance.setScale(1)
            self["logo"].instance.setPixmap(ptr)
            self["logo"].show()
            log.debug("logo displayed", module="Channels")
        else:
            self["logo"].hide()
            log.debug("No logo data, hiding", module="Channels")

    def download_logo(self, url):
        """Download and display channel logo"""
        try:
            try:
                response = urlopen(url, timeout=5)
                try:
                    logo_data = response.read()
                finally:
                    response.close()
            except Exception as e:
                log.error("Error downloading logo: %s" % e, module="Channels")
                self["logo"].hide()
                return

            try:
                from os import close
                temp_fd, temp_path = tempfile.mkstemp(suffix='.png')
                close(temp_fd)
                f = None
                try:
                    f = open(temp_path, 'wb')
                    f.write(logo_data)
                finally:
                    if f:
                        f.close()
            except Exception as e:
                log.error("Error creating temp file: %s" % e, module="Channels")
                self["logo"].hide()
                return

            # Load with ePicLoad
            self.picload.setPara((80, 50, 1, 1, False, 1, "#00000000"))
            result = self.picload.startDecode(temp_path)

            if result != 0:
                log.error("Logo decode failed for: %s" % url, module="Channels")

            # Cleanup temp file
            try:
                unlink(temp_path)
            except:
                pass

        except Exception as e:
            log.error("Error downloading logo: %s" % e, module="Channels")
            self["logo"].hide()

    def generate_country_bouquet(self, country_code, channels):
        """Generate bouquet for a specific country"""
        try:
            if not channels:
                return False, "No channels for country: %s" % country_code

            tag = "tvgarden"

            # Use prefix from config
            config = get_config()
            prefix = config.get("bouquet_name_prefix", "TVGarden")

            # Create bouquet name: prefix_countrycode
            bouquet_name = "%s_%s" % (prefix.lower(), country_code.lower())
            userbouquet_file = "/etc/enigma2/userbouquet.%s_%s.tv" % (tag, bouquet_name)

            valid_count = 0
            with open(userbouquet_file, "w") as f:
                # Use prefix in display name
                f.write("#NAME %s - %s\n" % (prefix, country_code.upper()))
                f.write("#SERVICE 1:64:0:0:0:0:0:0:0:0::--- | %s %s | ---\n" % (prefix, country_code.upper()))
                f.write("#DESCRIPTION --- | %s %s | ---\n" % (prefix, country_code.upper()))

                for channel in channels:
                    name = channel.get('name', '')
                    stream_url = channel.get('stream_url') or channel.get('url', '')

                    if not stream_url:
                        continue

                    url_encoded = stream_url.replace(":", "%3a")
                    name_encoded = name.replace(":", "%3a")

                    f.write("#SERVICE 4097:0:1:0:0:0:0:0:0:0:%s:%s\n" % (url_encoded, name_encoded))
                    f.write("#DESCRIPTION %s\n" % name)

                    valid_count += 1

            if valid_count == 0:
                return False, "No valid streams for country: %s" % country_code

            self._add_to_bouquets_tv(tag, bouquet_name)
            self._reload_bouquets()

            return True, "Exported %d channels for %s" % (valid_count, country_code.upper())

        except Exception as e:
            return False, "Error: %s" % str(e)

    def generate_all_countries_bouquet(self):
        """Generate separate bouquets for each country"""
        try:
            cache = CacheManager()

            # Get all countries
            countries_meta = cache.get_countries_metadata()

            results = []
            for country_code in countries_meta.keys():
                # Load channels for this country
                channels = cache.get_country_channels(country_code)

                if channels:
                    success, message = self.generate_country_bouquet(country_code, channels)
                    results.append((country_code, success, message))

            # Also create a bouquet containing all countries
            if results:
                all_channels = []
                for country_code, success, msg in results:
                    if success:
                        channels = cache.get_country_channels(country_code)
                        if channels:
                            all_channels.extend(channels[:10])  # Limit to 10 per country

                if all_channels:
                    self.export_to_bouquet(all_channels, "all_countries")

            return True, "Generated bouquets for %d countries" % len(results)

        except Exception as e:
            return False, "Error generating country bouquets: %s" % str(e)

    def _load_export_settings(self):
        """Load export settings from config"""
        try:
            config = get_config()
            self.export_enabled = config.get("export_enabled", True)
            self.auto_refresh_bouquet = config.get("auto_refresh_bouquet", False)
            self.confirm_before_export = config.get("confirm_before_export", True)
            self.max_channels_for_bouquet = config.get("max_channels_for_bouquet", 100)
            self.bouquet_name_prefix = config.get("bouquet_name_prefix", "TVGarden")

            log.debug("Export settings loaded from config", module="Channels")

        except Exception as e:
            self.export_enabled = True
            self.auto_refresh_bouquet = False
            self.confirm_before_export = True
            self.max_channels_for_bouquet = 100
            self.bouquet_name_prefix = "TVGarden"
            log.error("Error loading export settings: %s" % e, module="Channels")

    def _save_export_settings(self):
        """Save export settings to config"""
        try:
            config = get_config()
            config.set("export_enabled", self.export_enabled)
            config.set("auto_refresh_bouquet", self.auto_refresh_bouquet)
            config.set("confirm_before_export", self.confirm_before_export)
            config.set("max_channels_for_bouquet", self.max_channels_for_bouquet)
            config.set("bouquet_name_prefix", self.bouquet_name_prefix)
            config.save_config()

            log.debug("Export settings saved to config", module="Channels")

        except Exception as e:
            log.error("Error saving export settings: %s" % e, module="Channels")

    def export_settings_menu(self):
        """Export Settings Menu"""
        export_status = _("ENABLED") if self.export_enabled else _("DISABLED")
        refresh_status = _("ON") if self.auto_refresh_bouquet else _("OFF")
        confirm_status = _("ON") if self.confirm_before_export else _("OFF")

        menu = [
            (_("Export: %s") % export_status, "toggle_export"),
            (_("Auto-refresh: %s") % refresh_status, "toggle_refresh"),
            (_("Confirm before export: %s") % confirm_status, "toggle_confirm"),
            (_("Test Export (1 channel)"), "test_export"),
            (_("Back"), "back"),
        ]

        self.session.openWithCallback(self.export_settings_callback, ChoiceBox,
                                      title=_("Export Settings"), list=menu)

    def export_settings_callback(self, choice):
        """Manages settings menu selection"""
        if not choice:
            return

        if choice[1] == "toggle_export":
            self.export_enabled = not self.export_enabled
            if self.export_enabled:
                self["key_blue"] = Label(_("Export"))
            else:
                self["key_blue"] = Label(_("Info"))

            self._save_export_settings()
            self.export_settings_menu()

        elif choice[1] == "toggle_refresh":
            self.auto_refresh_bouquet = not self.auto_refresh_bouquet
            self._save_export_settings()
            self.export_settings_menu()

        elif choice[1] == "toggle_confirm":
            self.confirm_before_export = not self.confirm_before_export
            self._save_export_settings()
            self.export_settings_menu()

        elif choice[1] == "test_export":
            self._test_export_function()

        elif choice[1] == "back":
            self.channel_menu()

    def export_current_view(self):
        """Export current country/category channels"""
        if not self.menu_channels:
            self.session.open(MessageBox, _("No channels to export"),
                              MessageBox.TYPE_INFO, timeout=2)
            return

        # If confirmation is disabled, export directly
        if not self.confirm_before_export:
            self.execute_export()
            return

        # Otherwise ask for confirmation
        if self.country_name:
            display_name = self.country_name
        elif self.category_name:
            base_name = self.category_name.split(' (')[0] if ' (' in self.category_name else self.category_name
            display_name = base_name
        else:
            display_name = _("Channels")

        msg = _("Export {count} channels to bouquet '{name}'?").format(
            count=len(self.menu_channels),
            name=display_name
        )

        self.session.openWithCallback(
            lambda r: self.execute_export() if r else None,
            MessageBox,
            msg,
            MessageBox.TYPE_YESNO
        )

    def execute_export(self):
        """Perform actual export"""
        try:
            # Determine if it's a country or category
            if self.country_code:
                success, msg = self.fav_manager.generate_country_bouquet(
                    self.country_code,
                    self.menu_channels
                )
            elif self.category_id:
                safe_name = self.category_name.split(' (')[0] if ' (' in self.category_name else self.category_name
                safe_name = ''.join(c for c in safe_name if c.isalnum() or c in (' ', '-', '_')).replace(' ', '_')[:30]
                success, msg = self.fav_manager.export_to_bouquet(
                    self.menu_channels,
                    "category_%s" % safe_name.lower()
                )
            else:
                success, msg = self.fav_manager.export_to_bouquet(
                    self.menu_channels,
                    "tvgarden_channels"
                )

            self.session.open(
                MessageBox,
                msg,
                MessageBox.TYPE_INFO if success else MessageBox.TYPE_ERROR,
                timeout=4
            )

        except Exception as e:
            log.error("Export error: %s" % e, module="Channels")
            self.session.open(
                MessageBox,
                _("Export failed: %s") % str(e),
                MessageBox.TYPE_ERROR,
                timeout=4
            )

    def play_channel(self):
        """Play the selected channel."""
        # 1. Get the correct index from the menu
        menu_idx = self["menu"].getSelectedIndex()
        log.debug("Menu index: %d" % menu_idx, module="Channels")

        if menu_idx is None or menu_idx < 0 or menu_idx >= len(self.menu_channels):
            log.error("ERROR: Invalid index %d" % menu_idx, module="Channels")
            return

        # 2. Get the selected channel by index
        selected_channel = self.menu_channels[menu_idx]
        stream_url = selected_channel.get("stream_url") or selected_channel.get("url")

        if not stream_url:
            self["status"].setText(_("No stream URL"))
            return

        # 3. Critical debug info
        log.debug("===== PASSING TO PLAYER =====", module="Channels")
        log.debug("Channel: %s" % selected_channel.get('name'), module="Channels")
        log.debug("Index: %d" % menu_idx, module="Channels")
        log.debug("Total: %d" % len(self.menu_channels), module="Channels")
        log.debug("URL: %s..." % stream_url[:80], module="Channels")

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
        """Toggle favorite with MessageBox"""
        if not self.current_channel:
            return

        channel_name = self.current_channel.get('name', _('Unknown'))

        if self.fav_manager.is_favorite(self.current_channel):
            self.session.openWithCallback(
                lambda r: self._remove_favorite_confirmation(r),
                MessageBox,
                _("Remove '%s' from favorites?") % channel_name,
                MessageBox.TYPE_YESNO
            )
        else:
            success, message = self.fav_manager.add(self.current_channel)
            self.session.open(
                MessageBox,
                message,
                MessageBox.TYPE_INFO if success else MessageBox.TYPE_ERROR,
                timeout=3
            )

    def _remove_favorite_confirmation(self, result):
        """Remove if confirmed"""
        if result and self.current_channel:
            success, message = self.fav_manager.remove(self.current_channel)
            self.session.open(
                MessageBox,
                message,
                MessageBox.TYPE_INFO if success else MessageBox.TYPE_ERROR,
                timeout=3
            )

    def show_info(self):
        """Show channel information"""
        if self.current_channel:
            info = "%s\n\n" % self.current_channel.get('name', 'Unknown')

            desc = self.current_channel.get('description')
            if desc:
                info += "%s\n\n" % desc

            stream_url = self.current_channel.get('stream_url', 'N/A')
            if len(stream_url) > 60:
                info += _("Stream: %s...") % stream_url[:60]
            else:
                info += _("Stream: %s") % stream_url

            self.session.open(MessageBox, info, MessageBox.TYPE_INFO)

    def up(self):
        """Handle up key"""
        self["menu"].up()
        current_index = self["menu"].getSelectedIndex()
        log.debug("Up -> index: %d" % current_index, module="Channels")
        self.update_channel_selection(current_index)

    def down(self):
        """Handle down key"""
        self["menu"].down()
        current_index = self["menu"].getSelectedIndex()
        log.debug("Down -> index: %d" % current_index, module="Channels")
        self.update_channel_selection(current_index)

    def left(self):
        """Handle left key"""
        self["menu"].pageUp()
        current_index = self["menu"].getSelectedIndex()
        log.debug("Left -> index: %d" % current_index, module="Channels")
        self.update_channel_selection(current_index)

    def right(self):
        """Handle right key"""
        self["menu"].pageDown()
        current_index = self["menu"].getSelectedIndex()
        log.debug("Right -> index: %d" % current_index, module="Channels")
        self.update_channel_selection(current_index)

    def exit(self):
        """Exit browser"""
        self.close()
