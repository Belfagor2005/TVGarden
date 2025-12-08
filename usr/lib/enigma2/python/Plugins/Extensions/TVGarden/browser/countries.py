#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
TV Garden Plugin - Countries Browser
Browse 150+ countries with flags
Based on TV Garden Project
"""

# Standard library
import tempfile
from os import unlink
from sys import stderr
from urllib.request import urlopen

# Enigma2 components
from enigma import ePicLoad
from Components.ActionMap import ActionMap
from Components.Label import Label
from Components.MenuList import MenuList
from Components.Pixmap import Pixmap

# Local imports
from .base import BaseBrowser
from ..utils.config import PluginConfig
from .channels import ChannelsBrowser
from ..utils.cache import CacheManager
from .. import _

print("[CATEGORIES.PY] File imported", file=stderr)


class CountriesBrowser(BaseBrowser):
    """Browse channels by country"""

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
        self.countries = []
        self.selected_country = None

        self["menu"] = MenuList([])
        self["status"] = Label(_("Loading countries..."))
        self["flag"] = Pixmap()
        self["key_red"] = Label(_("Back"))
        self["key_green"] = Label(_("Select"))
        self["key_yellow"] = Label(_("Refresh"))
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

        self.picload = ePicLoad()
        self.picload.PictureData.get().append(self.update_flag)
        self.onFirstExecBegin.append(self.load_countries)
        # self.onLayoutFinish.append(self.refresh)

    def onSelectionChanged(self):
        """Called when menu selection changes"""
        current_index = self["menu"].getSelectedIndex()
        if current_index is not None:
            self.update_country_selection(current_index)

    def load_countries(self):
        """Load countries list from TV Garden repository"""
        try:
            metadata = self.cache.get_countries_metadata()
            print(f"[CountriesBrowser] Metadata received: {len(metadata)} countries", file=stderr)

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
                display_text = f"{country['name']}"
                if country['channels'] > 0:
                    display_text += f" ({country['channels']} ch)"
                menu_items.append((display_text, idx))

            self["menu"].setList(menu_items)
            self["menu"].onSelectionChanged.append(self.onSelectionChanged)

            if menu_items:
                self["status"].setText(_("Select a country"))
                self.update_country_selection(0)
            else:
                self["status"].setText(_("No countries with channels found"))

        except Exception as e:
            self["status"].setText(_("Error loading countries"))
            print(f"[CountriesBrowser] Error: {e}", file=stderr)
            import traceback
            traceback.print_exc()

    def refresh(self):
        """Refresh countries list - clear cache and reload"""
        self["status"].setText(_("Refreshing..."))

        try:
            # Clear cache and get fresh data
            self.cache.clear_all()
            self.load_countries()
            self["status"].setText(_("Countries refreshed"))
        except Exception as e:
            self["status"].setText(_("Refresh failed"))
            print(f"[CountriesBrowser] Refresh error: {e}", file=stderr)

    def update_country_selection(self, index):
        """Update selection and load flag"""
        print(f"[CountriesBrowser] update_country_selection index={index}", file=stderr)

        if 0 <= index < len(self.countries):
            self.selected_country = self.countries[index]
            print(f"[CountriesBrowser] Selected: {self.selected_country['code']} - {self.selected_country['name']}", file=stderr)

            # Load country flag
            flag_url = f"https://flagcdn.com/w80/{self.selected_country['code'].lower()}.png"
            if flag_url:
                print(f"[DEBUG] Loading flag: {flag_url[:50]}...", file=stderr)
                self.download_flag(flag_url)
            else:
                print("[DEBUG] No flag available", file=stderr)
                self["flag"].hide()
        else:
            print(f"[CountriesBrowser] ERROR: Index {index} out of range (0-{len(self.countries) - 1})", file=stderr)

    def download_flag(self, url):
        """Download and display country flag"""
        try:
            print(f"[CountriesBrowser] Downloading flag: {url}", file=stderr)
            with urlopen(url, timeout=5) as response:
                flag_data = response.read()

                # Save to temp file
                with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as f:
                    f.write(flag_data)
                    temp_path = f.name

                # Load with ePicLoad
                self.picload.setPara((80, 50, 1, 1, False, 1, "#00000000"))
                self.picload.startDecode(temp_path)

                # Cleanup
                unlink(temp_path)

        except Exception as e:
            print(f"[CountriesBrowser] Error downloading flag: {e}", file=stderr)
            self["flag"].hide()

    def update_flag(self, picInfo=None):
        """Update flag pixmap"""
        print(f"[CountriesBrowser] update_flag called, picInfo: {picInfo}", file=stderr)
        ptr = self.picload.getData()
        print(f"[CountriesBrowser] ePicLoad ptr: {ptr}", file=stderr)
        if ptr:
            self["flag"].instance.setScale(1)
            self["flag"].instance.setPixmap(ptr)
            self["flag"].show()
            print("[CountriesBrowser] Flag displayed", file=stderr)
        else:
            self["flag"].hide()
            print("[CountriesBrowser] No flag data, hiding", file=stderr)

    def select_country(self):
        """Select country and show channels"""
        if not self.selected_country:
            self["status"].setText(_("No country selected"))
            return

        print(f"[CountriesBrowser] Opening channels for: {self.selected_country['code']} ({self.selected_country['name']})", file=stderr)

        self.session.open(ChannelsBrowser,
                          country_code=self.selected_country['code'],
                          country_name=self.selected_country['name'])

    def up(self):
        """Handle up key"""
        self["menu"].up()
        current_index = self["menu"].getSelectedIndex()
        print(f"[CountriesBrowser] up() -> index: {current_index}", file=stderr)
        # self.update_country_selection(current_index)

    def down(self):
        """Handle down key"""
        self["menu"].down()
        current_index = self["menu"].getSelectedIndex()
        print(f"[CountriesBrowser] down() -> index: {current_index}", file=stderr)
        # self.update_country_selection(current_index)

    def left(self):
        """Handle left key"""
        self["menu"].pageUp()
        current_index = self["menu"].getSelectedIndex()
        print(f"[CountriesBrowser] left() -> index: {current_index}", file=stderr)
        # self.update_country_selection(current_index)

    def right(self):
        """Handle right key"""
        self["menu"].pageDown()
        current_index = self["menu"].getSelectedIndex()
        print(f"[CountriesBrowser] right() -> index: {current_index}", file=stderr)
        # self.update_country_selection(current_index)

    def exit(self):
        """Exit browser"""
        self.close()
