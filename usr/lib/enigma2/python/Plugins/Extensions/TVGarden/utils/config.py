#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
TV Garden Plugin - Config Module
Settings and configuration management
Based on TV Garden Project
"""

from os.path import join, exists
from os import makedirs, chmod
from json import load, dump
from Tools.Directories import fileExists
import shutil
from ..helpers import log
from .. import PLUGIN_PATH


class PluginConfig:
    """Simple JSON configuration manager"""

    def __init__(self):
        # Paths
        self.config_dir = "/etc/enigma2/tvgarden"
        self.config_file = join(self.config_dir, "config.json")
        self.backup_file = join(self.config_dir, "config.json.backup")

        # Create config directory if not exists
        if not exists(self.config_dir):
            makedirs(self.config_dir)

        # Default configuration
        self.defaults = {
            # Player settings
            "player": "exteplayer3",
            "timeout": 10,
            "retries": 3,
            "volume": 80,

            # Display settings
            "skin": "auto",
            "show_flags": True,
            "show_logos": True,
            "show_info": True,

            # Browser settings
            "items_per_page": 20,
            "max_channels": 500,
            "sort_by": "name",
            "default_view": "countries",

            # Cache settings
            "cache_enabled": True,
            "cache_ttl": 3600,
            "cache_size": 100,
            "auto_refresh": True,

            # Parental control
            "parental_lock": False,
            "parental_pin": "0000",
            "blocked_categories": [],

            # Favorites
            "max_favorites": 100,
            "auto_add_favorite": False,

            # Network
            "user_agent": "TVGarden-Enigma2/1.0",
            "use_proxy": False,
            "proxy_url": "",

            # Updates
            "auto_update": True,
            "update_channel": "stable",

            # Last session
            "last_country": None,
            "last_category": None,
            "last_channel": None,
            "last_volume": 80,

            # Statistics
            "stats_enabled": True,
            "watch_time": 0,
            "channels_watched": 0,

            # Logging settings
            "log_level": "INFO",        # DEBUG, INFO, WARNING, ERROR, CRITICAL
            "log_to_file": True,
            "log_max_size": 1048576,  # 1MB in bytes
            "log_backup_count": 3,      # Keep 3 backup files

        }

        # Load or create config
        self.config = self.load_config()

    def load_config(self):
        """Load configuration from JSON file"""
        if fileExists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    loaded_config = load(f)

                # Merge with defaults for missing keys
                config = self.defaults.copy()
                config.update(loaded_config)

                # Validate and fix values
                config = self.validate_config(config)

                return config
            except Exception as e:
                log.error("Error loading config: %s" % e, module="Config")
                return self.restore_backup()

        # Create new config with defaults
        return self.defaults.copy()

    def save_config(self):
        """Save configuration to JSON file"""
        try:
            # Create backup before saving
            if fileExists(self.config_file):
                shutil.copy2(self.config_file, self.backup_file)

            # Save config
            with open(self.config_file, 'w') as f:
                dump(self.config, f, indent=4, sort_keys=True)

            # Set proper permissions
            chmod(self.config_file, 0o644)

            return True
        except Exception as e:
            log.error(f"Error loading config: {e}", module="Config")
            return False

    def validate_config(self, config):
        """Validate and fix configuration values"""
        # Ensure volume is between 0-100
        if 'volume' in config:
            try:
                config['volume'] = max(0, min(100, int(config['volume'])))
            except:
                config['volume'] = 80

        # Ensure timeout is reasonable
        if 'timeout' in config:
            try:
                config['timeout'] = max(5, min(60, int(config['timeout'])))
            except:
                config['timeout'] = 10

        # Ensure skin is valid
        valid_skins = ['auto', 'hd', 'fhd', 'wqhd']
        if config.get('skin') not in valid_skins:
            config['skin'] = 'auto'

        # Ensure player is valid
        valid_players = ['exteplayer3', 'gstplayer', 'auto']
        if config.get('player') not in valid_players:
            config['player'] = 'auto'

        return config

    def restore_backup(self):
        """Restore configuration from backup"""
        if fileExists(self.backup_file):
            try:
                with open(self.backup_file, 'r') as f:
                    return load(f)
            except:
                pass

        # Return defaults if backup also fails
        return self.defaults.copy()

    def get(self, key, default=None):
        """Get config value"""
        return self.config.get(key, default or self.defaults.get(key))

    def set(self, key, value):
        """Set config value and save"""
        self.config[key] = value
        return self.save_config()

    def delete(self, key):
        """Delete config key"""
        if key in self.config:
            del self.config[key]
            return self.save_config()
        return False

    def reset(self):
        """Reset to defaults"""
        self.config = self.defaults.copy()
        return self.save_config()

    def export(self, filepath):
        """Export config to file"""
        try:
            with open(filepath, 'w') as f:
                dump(self.config, f, indent=4)
            return True
        except:
            return False

    def import_config(self, filepath):
        """Import config from file"""
        if fileExists(filepath):
            try:
                with open(filepath, 'r') as f:
                    imported = load(f)

                # Merge with current config
                self.config.update(imported)
                return self.save_config()
            except:
                return False
        return False

    # Convenience methods
    def get_player(self):
        """Get configured player with auto-detection"""
        player = self.get('player', 'auto')
        if player == 'auto':
            try:
                import subprocess
                result = subprocess.run(['which', 'exteplayer3'],
                                        capture_output=True, text=True)
                if result.returncode == 0:
                    return 'exteplayer3'
            except:
                pass
            return 'gstplayer'
        return player

    def get_skin_resolution(self):
        """Get skin resolution name (hd, fhd, wqhd)"""
        skin_setting = self.get('skin', 'auto')

        if skin_setting == 'auto':
            try:
                from enigma import getDesktop
                desktop = getDesktop(0)
                width = desktop.size().width()
                height = desktop.size().height()

                if width >= 2560 or height >= 1440:
                    return "wqhd"
                elif width >= 1920 or height >= 1080:
                    return "fhd"
                elif width >= 1280 or height >= 720:
                    return "hd"
                else:
                    return "sd"
            except:
                return 'hd'

        return skin_setting

    def load_skin(self, screen_name, default_skin):
        """
        Load skin from file or use default from class
        Args:
            screen_name: Name of screen (e.g., "TVGardenMain")
            default_skin: Default skin XML from class
        Returns:
            Skin XML string
        """
        resolution = self.get_skin_resolution()

        skin_file = join(PLUGIN_PATH, f"skins/{resolution}/{screen_name}.xml")

        if fileExists(skin_file):
            try:
                with open(skin_file, 'r', encoding='utf-8') as f:
                    skin_content = f.read()
                log.info(f"Loaded skin from: {skin_file}", module="Config")
                return skin_content
            except Exception as e:
                log.error(f"Error loading skin: {e}", module="Config")

        # Fallback to Class Skin
        log.warning(f"Using class skin for {screen_name}", module="Config")
        return default_skin

    def get_skin_path(self):
        """Get skin path based on config and detection"""
        skin_setting = self.get('skin', 'auto')
        if skin_setting == 'auto':
            try:
                from ..helpers import get_resolution_type
                return get_resolution_type()
            except:
                return 'hd'
        return skin_setting

    def is_category_blocked(self, category_id):
        """Check if category is blocked by parental control"""
        if not self.get('parental_lock', False):
            return False

        blocked = self.get('blocked_categories', [])
        return category_id in blocked

    def add_watch_time(self, seconds):
        """Add watch time to statistics"""
        if self.get('stats_enabled', True):
            current = self.get('watch_time', 0)
            self.set('watch_time', current + seconds)

    def increment_channels_watched(self):
        """Increment channels watched counter"""
        if self.get('stats_enabled', True):
            current = self.get('channels_watched', 0)
            self.set('channels_watched', current + 1)


_config_instance = None


def get_config():
    """Get configuration singleton instance"""
    global _config_instance
    if _config_instance is None:
        _config_instance = PluginConfig()
    return _config_instance
