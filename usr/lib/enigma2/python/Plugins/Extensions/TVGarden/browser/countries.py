#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
TV Garden Plugin - Countries Browser
Browse 150+ countries with flags
Based on TV Garden Project
"""
from __future__ import print_function
import tempfile
from os import unlink
from os.path import exists
from Components.Label import Label
from enigma import ePicLoad, eTimer
from Components.Pixmap import Pixmap
from Components.MenuList import MenuList
from Components.ActionMap import ActionMap
from sys import version_info

from .. import _
from ..helpers import log
from .base import BaseBrowser
from .channels import ChannelsBrowser
from ..utils.cache import CacheManager
from ..utils.config import PluginConfig


if version_info[0] == 3:
    from urllib.request import urlopen, Request
else:
    from urllib2 import urlopen, Request


class CountriesBrowser(BaseBrowser):

    skin = """
        <screen name="CountriesBrowser" position="center,center" size="1280,720" title="TV Garden" backgroundColor="#1a1a2e" flags="wfNoBorder">
            <ePixmap pixmap="skin_default/buttons/red.png" position="33,650" size="140,40" alphatest="blend" />
            <ePixmap pixmap="skin_default/buttons/green.png" position="174,650" size="140,40" alphatest="blend" />
            <ePixmap pixmap="skin_default/buttons/yellow.png" position="315,650" size="140,40" alphatest="blend" />
            <ePixmap name="" position="0,0" size="1280,720" alphatest="blend" zPosition="-1" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/TVGarden/images/hd/background.png" scale="1" />
            <ePixmap name="" position="1039,531" size="200,80" alphatest="blend" zPosition="1" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/TVGarden/icons/logo.png" scale="1" transparent="1"/>
            <widget source="key_red" render="Label" position="33,649" zPosition="1" size="140,40" font="Regular;20" halign="center" valign="center" transparent="1" />
            <widget source="key_green" render="Label" position="174,650" zPosition="1" size="140,40" font="Regular;20" halign="center" valign="center" transparent="1" />
            <widget source="key_yellow" render="Label" position="315,650" zPosition="1" size="140,40" font="Regular;20" halign="center" valign="center" transparent="1" />
            <widget name="menu" position="28,116" size="680,474" scrollbarMode="showOnDemand" backgroundColor="#16213e" />
            <widget name="status" position="603,643" size="648,50" font="Regular; 22" halign="center" foregroundColor="#3333ff" transparent="1" />
            <widget name="flag" position="45,37" size="80,50" alphatest="blend" />
            <eLabel backgroundColor="#001a2336" cornerRadius="30" position="5,639" size="1270,60" zPosition="-80" />
            <eLabel name="" position="24,101" size="694,502" zPosition="-1" cornerRadius="18" backgroundColor="#00171a1c" foregroundColor="#00171a1c" />
            <widget source="session.VideoPicture" render="Pig" position="739,140" zPosition="19" size="520,308" backgroundColor="transparent" transparent="0" cornerRadius="14" />
        </screen>
    """

    def __init__(self, session):
        self.config = PluginConfig()
        dynamic_skin = self.config.load_skin("CountriesBrowser", self.skin)
        self.skin = dynamic_skin

        BaseBrowser.__init__(self, session)
        self.session = session
        self.cache = CacheManager()

        # Initialize before widgets
        self.picload = ePicLoad()
        self.picload_conn = None  # Store connection to prevent garbage collection

        self.countries = []
        self.selected_country = None
        self.current_flag_path = None

        # Menu setup
        self["menu"] = MenuList([], enableWrapAround=True)
        self["menu"].onSelectionChanged.append(self.onSelectionChanged)

        # Widgets
        self["status"] = Label(_("Loading countries..."))
        self["flag"] = Pixmap()
        self["key_red"] = Label(_("Back"))
        self["key_green"] = Label(_("Select"))
        self["key_yellow"] = Label(_("Refresh"))

        # Actions
        self["actions"] = ActionMap(["TVGardenActions", "OkCancelActions", "ColorActions"], {
            "cancel": self.exit,
            "ok": self.select_country,
            "red": self.exit,
            "green": self.select_country,
            "yellow": self.refresh,
            "up": self.up,
            "down": self.down,
            "left": self.left,
            "right": self.right,
        }, -2)

        # Connect picload AFTER widget creation
        self.picload_conn = self.picload.PictureData.get().append(self.update_flag)

        self.onFirstExecBegin.append(self.load_countries)
        self.onClose.append(self.cleanup)

    def cleanup(self):
        """Cleanup resources on close"""
        log.debug("Cleaning up", module="Countries")

        # Flag to prevent double cleanup
        if getattr(self, '_cleaned_up', False):
            return
        self._cleaned_up = True

        # Remove timer callbacks
        if hasattr(self, 'timer') and self.timer:
            try:
                self.timer.callback = []
                self.timer.stop()
            except Exception as e:
                log.debug("Error stopping timer: {}".format(e), module="Countries")
            finally:
                self.timer = None

        if hasattr(self, 'flag_timer') and self.flag_timer:
            try:
                self.flag_timer.callback = []
                self.flag_timer.stop()
            except Exception as e:
                log.debug("Error stopping flag_timer: {}".format(e), module="Countries")
            finally:
                self.flag_timer = None

        # Remove temporary flag file
        if hasattr(self, 'current_flag_path') and self.current_flag_path:
            if exists(self.current_flag_path):
                try:
                    unlink(self.current_flag_path)
                except Exception as e:
                    log.debug("Error deleting temp file: {}".format(e), module="Countries")
            self.current_flag_path = None

        # Remove picload callback
        if hasattr(self, 'picload_conn') and self.picload_conn:
            try:
                if self.picload and hasattr(self.picload, 'PictureData'):
                    if self.picload.PictureData and self.picload.PictureData.get():
                        self.picload.PictureData.get().remove(self.picload_conn)
            except Exception as e:
                log.debug("Error removing picload callback: {}".format(e), module="Countries")
            finally:
                self.picload_conn = None

        # Cleanup picload
        if hasattr(self, 'picload') and self.picload:
            try:
                # Force internal cleanup of ePicLoad
                self.picload.__dict__.clear()
            except:
                pass
            finally:
                self.picload = None

        # Remove menu callback
        try:
            if hasattr(self["menu"], 'onSelectionChanged'):
                self["menu"].onSelectionChanged = []
        except:
            pass

    def load_countries(self):
        """Load countries list from TV Garden repository"""
        try:
            metadata = self.cache.get_countries_metadata()
            log.debug("Metadata received: %d countries" % len(metadata), module="Countries")

            self.countries = []
            for code, info in metadata.items():
                if info.get('hasChannels', False):
                    self.countries.append({
                        'code': code,
                        'name': info.get('country', code),
                        'channels': info.get('channelCount', 0)
                    })

            self.countries.sort(key=lambda x: x['name'])

            # Create menu items
            menu_items = []
            for idx, country in enumerate(self.countries):
                display_text = "%s" % country['name']
                if country['channels'] > 0:
                    display_text += " (%d ch)" % country['channels']
                menu_items.append((display_text, idx))

            self["menu"].setList(menu_items)

            if menu_items:
                self["status"].setText(_("Select a country"))
                # Load initial flag with delay
                self.timer = eTimer()
                self.timer.callback.append(self.load_initial_flag)
                self.timer.start(100, True)  # 100ms delay
            else:
                self["status"].setText(_("No countries with channels found"))

        except Exception as e:
            self["status"].setText(_("Error loading countries"))
            log.error("Error: %s" % e, module="Countries")
            import traceback
            traceback.print_exc()

    def load_initial_flag(self):
        """Load first flag after a short delay"""
        if self.countries:
            self.update_country_selection(0)

    def onSelectionChanged(self):
        """Called when menu selection changes"""
        current_index = self["menu"].getSelectedIndex()
        if current_index is not None:
            self.update_country_selection(current_index)

    def update_country_selection(self, index):
        """Update selection and load flag"""
        if 0 <= index < len(self.countries):
            self.selected_country = self.countries[index]

            # Clear previous flag immediately
            self["flag"].hide()

            # Load new flag with proper error handling
            flag_code = self.selected_country['code'].lower()
            flag_url = "https://flagcdn.com/w80/%s.png" % flag_code

            # Use a timer to prevent rapid consecutive loads
            if hasattr(self, 'flag_timer'):
                self.flag_timer.stop()

            self.flag_timer = eTimer()
            self.flag_timer.callback.append(lambda: self.download_flag_safe(flag_url, flag_code))
            self.flag_timer.start(50, True)  # Small delay

    def download_flag_safe(self, url, country_code):
        """Safe flag download with memory management"""
        try:
            # Cleanup old temp file
            if self.current_flag_path and exists(self.current_flag_path):
                try:
                    unlink(self.current_flag_path)
                except:
                    pass

            # Download flag
            req = Request(url, headers={'User-Agent': 'TVGarden-Enigma2/1.0'})
            with urlopen(req, timeout=3) as response:
                if response.status == 200:
                    flag_data = response.read()

                    # Save to temp file
                    with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as f:
                        f.write(flag_data)
                        temp_path = f.name

                    self.current_flag_path = temp_path

                    # Get ACTUAL widget size from skin
                    try:
                        # Get widget position and size
                        flag_widget = self["flag"]
                        widget_size = flag_widget.instance.size()
                        widget_width = widget_size.width()
                        widget_height = widget_size.height()

                        log.debug("Widget size: %dx%d for %s" % (widget_width, widget_height, country_code), module="Countries")

                        # Use actual widget size or default
                        width = widget_width if widget_width > 0 else 80
                        height = widget_height if widget_height > 0 else 50

                    except:
                        # Fallback to default size
                        width, height = 80, 50
                        log.debug("Using default size for %s" % country_code, module="Countries")

                    # Load with ePicLoad - Use actual widget size
                    # Parameters: (width, height, scaletype, aspectratio, resize, alphablend, background_color)
                    self.picload.setPara((
                        width,       # widget width
                        height,      # widget height
                        1,           # scaletype: 0=No scale, 1=Scale, 2=Keep aspect, 3=Center
                        1,           # aspectratio: 0=ignore, 1=keep
                        False,       # resize: True=resize image to fit
                        1,           # alphablend: 0=no, 1=yes
                        "#00000000"  # transparent background
                    ))

                    # Try sync decode
                    result = self.picload.startDecode(temp_path, 0, 0, False)

                    if result == 0:  # Success
                        ptr = self.picload.getData()
                        if ptr:
                            self["flag"].instance.setPixmap(ptr)
                            self["flag"].show()
                            log.debug("Flag displayed %dx%d for %s" % (width, height, country_code), module="Countries")
                        else:
                            log.warning("No pixmap data for %s" % country_code, module="Countries")
                            self.load_default_flag()
                    else:
                        log.warning("Decode failed for %s" % country_code, module="Countries")
                        self.load_default_flag()
                else:
                    log.warning("HTTP %d for %s" % (response.status, url), module="Countries")
                    self.load_default_flag()

        except Exception as e:
            log.error("Error downloading flag %s: %s" % (country_code, e), module="Countries")
            self.load_default_flag()

    def load_default_flag(self):
        """Load a default/placeholder flag"""
        try:
            # Try to use a simple embedded flag or skip
            self["flag"].hide()
        except:
            pass

    def update_flag(self, picInfo=None):
        """Callback for async picload - use with caution"""
        # This is called when picload finishes async decode
        # We're using sync decode mainly, but keep this for compatibility
        if picInfo:
            log.debug("Async decode finished: %s" % picInfo, module="Countries")

    def select_country(self):
        """Select a country and show its channels"""
        if not self.selected_country:
            self["status"].setText(_("No country selected"))
            return

        log.info("Opening channels for: {}".format(self.selected_country['code']), module="Countries")

        # Cleanup before opening new screen
        if self.current_flag_path and exists(self.current_flag_path):
            try:
                unlink(self.current_flag_path)
            except:
                pass

        # Additional minor cleanup
        if hasattr(self, 'flag_timer') and self.flag_timer:
            try:
                self.flag_timer.stop()
            except:
                pass

        # Open the channel browser
        self.session.open(ChannelsBrowser,
                          country_code=self.selected_country['code'],
                          country_name=self.selected_country['name'])

    def refresh(self):
        """Refresh countries list"""
        self["status"].setText(_("Refreshing..."))
        try:
            self.cache.clear_all()
            self.load_countries()
            self["status"].setText(_("Countries refreshed"))
        except Exception as e:
            self["status"].setText(_("Refresh failed"))
            log.error("Refresh error: %s" % e, module="Countries")

    # Navigation methods - simplified
    def up(self):
        self["menu"].up()

    def down(self):
        self["menu"].down()

    def left(self):
        self["menu"].pageUp()

    def right(self):
        self["menu"].pageDown()

    def exit(self):
        """Exit browser"""
        self.cleanup()
        self.close()
