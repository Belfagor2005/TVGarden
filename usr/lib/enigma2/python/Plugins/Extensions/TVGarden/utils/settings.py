#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
TV Garden Plugin - Settings Screen
Plugin configuration interface
Based on TV Garden Project
"""

from os.path import exists
from Screens.MessageBox import MessageBox
from Screens.Screen import Screen
from Screens.TextBox import TextBox
from Components.ActionMap import ActionMap
from Components.Label import Label
from Components.ConfigList import ConfigListScreen
from Components.config import (
    ConfigInteger,
    ConfigSelection,
    ConfigYesNo,
    ConfigText,
    ConfigNothing,
    # ConfigAction,
    getConfigListEntry
)
from .. import _
from .config import get_config
from ..helpers import log


class LogViewerScreen(TextBox):
    skin = """
        <screen name="LogViewerScreen" position="center,center" size="1280,720" title="TV Garden Logs" backgroundColor="#1a1a2e" flags="wfNoBorder">
            <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/TVGarden/icons/redbutton.png" position="32,688" size="140,6" alphatest="blend" zPosition="1" transparent="1" />
            <ePixmap name="" position="0,0" size="1280,720" alphatest="blend" zPosition="-1" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/TVGarden/images/hd/background.png" scale="1" />
            <ePixmap name="" position="1041,628" size="200,80" alphatest="blend" zPosition="1" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/TVGarden/icons/logo.png" scale="1" transparent="1" />
            <widget source="key_red" render="Label" position="33,649" zPosition="1" size="140,40" font="Regular;20" halign="center" valign="center" transparent="1" />
            <widget name="text" position="28,45" size="1220,570" font="Console;24" itemHeight="50" backgroundColor="#16213e" transparent="0" />
            <eLabel backgroundColor="#001a2336" cornerRadius="30" position="5,639" size="1270,60" zPosition="-80" />
            <eLabel name="" position="19,36" size="1235,585" zPosition="-1" cornerRadius="18" backgroundColor="#00171a1c" foregroundColor="#00171a1c" />
        </screen>
    """

    def __init__(self, session, max_lines=100):
        # Get log contents
        log_contents = log.get_log_contents(max_lines=max_lines)

        if not log_contents or "Log file not found" in log_contents:
            log_contents = _("Log file is empty or not found")

        # Initialize TextBox with log contents
        TextBox.__init__(self, session, text=log_contents, title=_("TV Garden Logs"))

        self["key_red"] = Label(_("Close"))
        self["actions"] = ActionMap(
            [
                "SetupActions",
                "ColorActions",
                "DirectionActions"
            ],
            {
                "cancel": self.close,
                "red": self.close,
                "ok": self.close,
                "up": self.pageUp,
                "down": self.pageDown,
                "left": self.pageUp,
                "right": self.pageDown,
                "pageUp": self.pageUp,
                "pageDown": self.pageDown,
            }, -2
        )

    def pageUp(self):
        """Scroll up"""
        self["text"].pageUp()

    def pageDown(self):
        """Scroll down"""
        self["text"].pageDown()

    def close(self):
        """Close the log viewer"""
        TextBox.close(self)


class TVGardenSettings(ConfigListScreen, Screen):
    """Settings screen using Enigma2's config system"""

    skin = """
        <screen name="TVGardenSettings" position="center,center" size="1280,720" title="TV Garden Settings" backgroundColor="#1a1a2e" flags="wfNoBorder">
            <ePixmap pixmap="skin_default/buttons/red.png" position="33,650" size="140,40" alphatest="blend" />
            <ePixmap pixmap="skin_default/buttons/green.png" position="174,650" size="140,40" alphatest="blend" />
            <ePixmap name="" position="0,0" size="1280,720" alphatest="blend" zPosition="-1" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/TVGarden/images/hd/background.png" scale="1" />
            <ePixmap name="" position="1039,531" size="200,80" alphatest="blend" zPosition="1" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/TVGarden/icons/logo.png" scale="1" transparent="1"/>
            <widget source="key_red" render="Label" position="33,649" zPosition="1" size="140,40" font="Regular;20" halign="center" valign="center" transparent="1" />
            <widget source="key_green" render="Label" position="174,650" zPosition="1" size="140,40" font="Regular;20" halign="center" valign="center" transparent="1" />
            <widget name="config" position="28,116" size="680,474" scrollbarMode="showOnDemand" backgroundColor="#16213e" />
            <widget name="status" position="603,643" size="648,50" font="Regular; 22" halign="center" foregroundColor="#3333ff" transparent="1" />
            <eLabel backgroundColor="#001a2336" cornerRadius="30" position="5,639" size="1270,60" zPosition="-80" />
            <eLabel name="" position="24,101" size="694,502" zPosition="-1" cornerRadius="18" backgroundColor="#00171a1c" foregroundColor="#00171a1c" />
            <widget source="session.VideoPicture" render="Pig" position="739,140" zPosition="19" size="520,308" backgroundColor="transparent" transparent="0" cornerRadius="14" />
        </screen>
    """

    def __init__(self, session):

        self.config = get_config()

        dynamic_skin = self.config.load_skin("TVGardenSettings", self.skin)
        self.skin = dynamic_skin

        Screen.__init__(self, session)
        ConfigListScreen.__init__(self, [], session=session)

        self.setTitle(_("TV Garden Settings"))
        self.setupConfig()
        self["key_red"] = Label(_("Back"))
        self["key_green"] = Label(_("Save"))
        self["status"] = Label(_("Set options"))
        self["actions"] = ActionMap(
            ["SetupActions", "ColorActions"],
            {
                "cancel": self.cancel,
                "save": self.save,
                "ok": self.handle_ok,
            }, -2
        )

    def handle_ok(self):
        """Handle OK button based on current selection"""
        current = self["config"].getCurrent()
        if not current:
            return

        display_name = current[0]
        config_item = current[1]

        log.debug("OK pressed on: %s" % display_name, module="Settings")

        if display_name == _("View Log File"):
            self._execute_view_logs()
            self._reset_action_selections()
            return
        elif display_name == _("Clear Log Files Now"):
            self.clear_logs()
            self._reset_action_selections()
            return
        elif isinstance(config_item, ConfigNothing):
            return

    def setupConfig(self):
        """Setup configuration entries"""
        self.config_entries = []

        # Player settings
        self.config_entries.append([
            _("Player"), "player",
            ConfigSelection(
                default=self.config.get("player", "auto"),
                choices=[
                    ("auto", _("Auto")),
                    ("exteplayer3", _("ExtePlayer3")),
                    ("gstplayer", _("GStreamer"))
                ]
            )
        ])

        self.config_entries.append([
            _("Volume"), "volume",
            ConfigInteger(default=self.config.get("volume", 80), limits=(0, 100))
        ])

        self.config_entries.append([
            _("Timeout (seconds)"), "timeout",
            ConfigInteger(default=self.config.get("timeout", 10), limits=(5, 60))
        ])

        self.config_entries.append([
            _("Retries"), "retries",
            ConfigInteger(default=self.config.get("retries", 3), limits=(1, 10))
        ])

        # Cache settings
        self.config_entries.append([
            _("Cache TTL (hours)"), "cache_ttl",
            ConfigInteger(default=self.config.get("cache_ttl", 3600) // 3600, limits=(1, 24))
        ])

        self.config_entries.append([
            _("Cache Size"), "cache_size",
            ConfigInteger(default=self.config.get("cache_size", 100), limits=(10, 1000))
        ])

        # Display settings
        self.config_entries.append([
            _("Skin"), "skin",
            ConfigSelection(
                default=self.config.get("skin", "auto"),
                choices=[
                    ("auto", _("Auto")),
                    ("hd", _("HD")),
                    ("fhd", _("FHD")),
                    ("wqhd", _("WQHD"))
                ]
            )
        ])

        self.config_entries.append([
            _("Show Flags"), "show_flags",
            ConfigYesNo(default=self.config.get("show_flags", True))
        ])

        self.config_entries.append([
            _("Show Logos"), "show_logos",
            ConfigYesNo(default=self.config.get("show_logos", True))
        ])

        # Browser settings
        self.config_entries.append([
            _("Items per page"), "items_per_page",
            ConfigInteger(default=self.config.get("items_per_page", 20), limits=(10, 100))
        ])

        # Max channels settings (all_channels)
        self.config_entries.append([
            _("Max channels per country"), "max_channels",
            ConfigSelection(
                default=self.config.get("max_channels", 500),
                choices=[
                    (100, _("100 channels")),
                    (250, _("250 channels")),
                    (500, _("500 channels")),
                    (1000, _("1000 channels")),
                    (0, _("All channels"))
                ]
            )
        ])

        # default view
        self.config_entries.append([
            _("Default View"), "default_view",
            ConfigSelection(
                default=self.config.get("default_view", "countries"),
                choices=[
                    ("countries", _("Countries")),
                    ("categories", _("Categories")),
                    ("favorites", _("Favorites"))
                ]
            )
        ])

        # Favorites
        self.config_entries.append([
            _("Max Favorites"), "max_favorites",
            ConfigInteger(default=self.config.get("max_favorites", 100), limits=(10, 500))
        ])

        # Network
        self.config_entries.append([
            _("User Agent"), "user_agent",
            ConfigText(default=self.config.get("user_agent", "TVGarden-Enigma2/1.0"), fixed_size=False)
        ])

        # ============ LOGGING SETTINGS ============
        self.config_entries.append(getConfigListEntry(
            _("=== Logging Settings ==="),
            ConfigNothing()
        ))

        self.config_entries.append([
            _("Log Level"), "log_level",
            ConfigSelection(
                default=self.config.get("log_level", "INFO"),
                choices=[
                    ("DEBUG", _("Debug (most verbose)")),
                    ("INFO", _("Info (normal)")),
                    ("WARNING", _("Warning")),
                    ("ERROR", _("Error only")),
                    ("CRITICAL", _("Critical only"))
                ]
            )
        ])

        self.config_entries.append([
            _("Log to File"), "log_to_file",
            ConfigYesNo(default=self.config.get("log_to_file", True))
        ])

        self.config_entries.append([
            _("Max Log Size (MB)"), "log_max_size",
            ConfigInteger(
                default=self.config.get("log_max_size", 1048576) // 1048576,  # bytes to MB
                limits=(1, 10)
            )
        ])

        self.config_entries.append([
            _("Log Backup Files"), "log_backup_count",
            ConfigInteger(default=self.config.get("log_backup_count", 3), limits=(1, 10))
        ])

        self.config_entries.append(getConfigListEntry(
            _("--- Log Maintenance ---"),
            ConfigNothing()
        ))

        self.config_entries.append([
            _("View Log File"), "view_log_action",
            ConfigSelection(
                choices=[("open", _("Press OK to view logs"))],
                default="open"
            )
        ])

        self.config_entries.append([
            _("Clear Log Files Now"), "clear_logs_action",
            ConfigSelection(
                choices=[("clear", _("Press OK to clear logs"))],
                default="clear"
            )
        ])

        # ============ CONFIGURATION LIST CREATION ============
        self.list = []
        for entry in self.config_entries:
            name = entry[0]
            # FIX: Takes the last element instead of the third (entry[2])
            # Because some entries have different structure:
            # - Normal configs: [name, key, config_item] -> 3 elements
            # - ConfigNothing/ConfigAction: getConfigListEntry(name, config_item) -> 2 elements
            config_item = entry[-1]  # Always takes the last element
            self.list.append(getConfigListEntry(name, config_item))

        self["config"].setList(self.list)

    def clear_logs(self):
        """Clear log files"""
        try:
            self.session.openWithCallback(
                self._clear_logs_callback,
                MessageBox,
                _("Are you sure you want to clear all log files?"),
                MessageBox.TYPE_YESNO
            )
        except Exception as e:
            self["status"].setText(_("Error: {}").format(str(e)))

    def _clear_logs_callback(self, result):
        """Callback dopo clear logs"""
        if result:
            try:
                log.clear_logs()
                self["status"].setText(_("Logs cleared"))
                self.session.open(
                    MessageBox,
                    _("Log files cleared successfully"),
                    MessageBox.TYPE_INFO,
                    timeout=3
                )
            except Exception as e:
                self.session.open(
                    MessageBox,
                    _("Error clearing logs: {}").format(str(e)),
                    MessageBox.TYPE_ERROR
                )

    def _execute_view_logs(self):
        """Execute view logs directly"""
        try:
            self.session.open(LogViewerScreen)
        except Exception as e:
            log.error("Error opening log viewer: %s" % e, module="Settings")

    def apply_logging_settings(self):
        """Apply logging settings immediately"""
        try:
            log_level = self.config.get("log_level", "INFO")
            log.set_level(log_level)
            log_to_file = self.config.get("log_to_file", True)
            log.enable_file_logging(log_to_file)
            log.info(f"Logging settings applied: level={log_level}, file={log_to_file}", "Settings")
        except Exception as e:
            log.error("Failed to apply logging settings: %s" % e, module="Settings")

    def _reset_action_selections(self):
        """Reset action selections to default"""
        for i, entry in enumerate(self["config"].list):
            display_name = entry[0]
            config_item = entry[1]

            if display_name in [_("View Log File"), _("Clear Log Files Now")]:
                if hasattr(config_item, 'value'):
                    config_item.value = config_item.choices[0][0] if config_item.choices else ""

        self["config"].invalidateCurrent()

    def save(self):
        log.debug("Starting save...", module="Settings")
        name_to_key = {
            _("Player"): "player",
            _("Volume"): "volume",
            _("Timeout (seconds)"): "timeout",
            _("Retries"): "retries",
            _("Cache TTL (hours)"): "cache_ttl",
            _("Cache Size"): "cache_size",
            _("Skin"): "skin",
            _("Show Flags"): "show_flags",
            _("Show Logos"): "show_logos",
            _("Items per page"): "items_per_page",
            _("Max channels per country"): "max_channels",
            _("Default View"): "default_view",
            _("Max Favorites"): "max_favorites",
            _("User Agent"): "user_agent",
            _("Log Level"): "log_level",
            _("Log to File"): "log_to_file",
            _("Max Log Size (MB)"): "log_max_size",
            _("Log Backup Files"): "log_backup_count",
            _("View Log File"): "view_log_action",
            _("Clear Log Files Now"): "clear_logs_action",
        }

        # STEP 1: Check if we're handling an action
        current = self["config"].getCurrent()
        if current:
            display_name = current[0]
            config_key = name_to_key.get(display_name)

            if config_key == "view_log_action":
                self._execute_view_logs()
                self._reset_action_selections()
                return
            elif config_key == "clear_logs_action":
                self.clear_logs()
                self._reset_action_selections()
                return

        # STEP 2: Normal save (only if not an action)
        for entry in self["config"].list:
            display_name = entry[0]
            config_item = entry[1]

            # Skip separators and actions
            if isinstance(config_item, ConfigNothing):
                continue

            # Skip our fake action items (they shouldn't be saved)
            if display_name in [_("View Log File"), _("Clear Log Files Now")]:
                continue

            config_key = name_to_key.get(display_name)
            if not config_key:
                log.warning("No key found for: '%s'" % display_name, module="Settings")
                continue

            value = config_item.value
            log.debug("Saving: %s = %s (type: %s)" % (config_key, value, type(value)), module="Settings")

            if config_key == "log_max_size":
                log.debug("log_max_size raw value: %s (type: %s)" % (value, type(value)), module="Settings")

                try:
                    mb_value = int(value)

                    # Limit to a reasonable value (e.g. max 100MB)
                    if mb_value < 1:
                        mb_value = 1
                    elif mb_value > 100:
                        mb_value = 100

                    bytes_value = mb_value * 1048576  # 1MB = 1,048,576 bytes
                    log.debug("Converting %d MB to %d bytes" % (mb_value, bytes_value), module="Settings")

                    self.config.set("log_max_size", bytes_value)
                except Exception as e:
                    log.error("Error converting log_max_size '%s': %s" % (value, e), module="Settings")
                    self.config.set("log_max_size", 1048576)  # Default 1MB
            elif config_key == "cache_ttl":
                self.config.set("cache_ttl", int(value) * 3600)
            elif config_key == "max_channels":
                try:
                    int_value = int(value)
                    self.config.set("max_channels", int_value)
                    log.debug("Saved max_channels as: %d" % int_value, module="Settings")
                except Exception as e:
                    log.error("Could not convert max_channels '%s': %s" % (value, e), module="Settings")
                    self.config.set("max_channels", 500)
            else:
                self.config.set(config_key, value)

        # STEP 3: Apply and save
        self.apply_logging_settings()

        if self.config.save_config():
            log.info("Config saved successfully to disk", module="Settings")
        else:
            log.error("Failed to save config to disk!", module="Settings")

        # STEP 4: Verify and close
        saved_max = self.config.get("max_channels", 500)
        log.debug("VERIFIED - max_channels in config: %d" % saved_max, module="Settings")

        try:
            import json
            config_file = "/etc/enigma2/tvgarden/config.json"
            if exists(config_file):
                with open(config_file, 'r') as f:
                    file_content = json.load(f)
                log.debug("File content - max_channels: %s" % file_content.get('max_channels', 'NOT FOUND'), module="Settings")
        except Exception as e:
            log.error("Could not read config file: %s" % e, module="Settings")

        self.close(True)

    def cancel(self):
        """Cancel without saving"""
        self.close(False)
