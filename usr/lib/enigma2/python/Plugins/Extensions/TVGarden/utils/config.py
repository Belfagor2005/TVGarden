#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
TV Garden Plugin - Config Module
Settings and configuration management
Based on TV Garden Project
"""
from __future__ import print_function
from os.path import join, exists
from os import makedirs, chmod
from json import load, dump
from Tools.Directories import fileExists
import shutil
from .. import USER_AGENT
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
            try:
                makedirs(self.config_dir)
                log.info("Created config directory: %s" % self.config_dir, module="Config")
            except Exception as e:
                log.error("Error creating config directory: %s" % e, module="Config")

        # ============ DEFAULT CONFIGURATION ============
        self.defaults = {
            # ============ PLAYER SETTINGS ============
            "player": "exteplayer3",             # "auto", "exteplayer3", "gstplayer"
            "timeout": 10,                       # Connection timeout in seconds
            "retries": 3,                        # Connection retry attempts
            "volume": 80,                        # Default volume 0-100

            # ============ DISPLAY SETTINGS ============
            "skin": "auto",                      # "auto", "hd", "fhd", "wqhd"
            "show_flags": True,                  # Show country flags
            "show_logos": True,                  # Show channel logos
            "show_info": True,                   # Show channel info
            "items_per_page": 20,                # Items per browser page

            # ============ BROWSER SETTINGS ============
            "max_channels": 500,                 # Max channels per country (0=all)
            "sort_by": "name",                   # Sort channels by
            "default_view": "countries",         # "countries", "categories", "favorites"

            # ============ CACHE SETTINGS ============
            "cache_enabled": True,               # Enable caching
            "cache_ttl": 3600,                   # Cache time-to-live in seconds (1 hour)
            "cache_size": 100,                   # Maximum cache items
            "auto_refresh": True,                # Automatic cache refresh

            # ============ EXPORT SETTINGS ============
            "export_enabled": True,              # Enable bouquet export
            "auto_refresh_bouquet": False,       # Auto-refresh bouquet
            "confirm_before_export": True,       # Confirm before exporting
            "max_channels_for_bouquet": 100,     # Max channels for bouquet
            "bouquet_name_prefix": "TVGarden",   # Bouquet name prefix

            # ============ NETWORK SETTINGS ============
            "user_agent": USER_AGENT,
            "use_proxy": False,
            "proxy_url": "",
            "connection_timeout": 30,            # Network connection timeout

            # ============ LOGGING SETTINGS ============
            "log_level": "INFO",                 # "DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"
            "log_to_file": True,                 # Log to file
            "log_max_size": 1048576,             # Max log file size in bytes (1MB)
            "log_backup_count": 3,               # Number of backup log files

            # ============ UPDATE SETTINGS ============
            "auto_update": True,                 # Automatic updates
            "update_channel": "stable",          # "stable", "beta", "dev"
            "update_check_interval": 86400,      # Check for updates every 24 hours
            "notify_on_update": True,            # Notify when updates available
            "last_update_check": 0,              # Timestamp of last update check

            # ============ FAVORITES SETTINGS ============
            "max_favorites": 100,                # Maximum favorites allowed
            "auto_add_favorite": False,          # Automatically add watched to favorites

            # ============ PERFORMANCE SETTINGS ============
            "use_hardware_acceleration": True,   # Use hardware acceleration
            "buffer_size": 2048,                 # Buffer size in KB

            # ============ DEBUG/DEVELOPMENT ============
            "debug_mode": False,                 # Enable debug mode

            # ============ LAST SESSION ============
            "last_country": None,
            "last_category": None,
            "last_channel": None,
            "last_volume": 80,

            # ============ STATISTICS ============
            "stats_enabled": True,
            "watch_time": 0,                     # Total watch time in seconds
            "channels_watched": 0,               # Number of channels watched
        }

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

                log.info("Configuration loaded successfully from %s" % self.config_file, module="Config")
                return config
            except Exception as e:
                log.error("Error loading config: %s" % e, module="Config")
                return self.restore_backup()

        # Create new config with defaults
        log.info("Creating new configuration with defaults", module="Config")
        return self.validate_config(self.defaults.copy())

    def save_config(self):
        """Save configuration to JSON file"""
        try:
            # Create backup before saving
            if fileExists(self.config_file):
                try:
                    shutil.copy2(self.config_file, self.backup_file)
                    log.debug("Created backup: %s" % self.backup_file, module="Config")
                except Exception as e:
                    log.warning("Could not create backup: %s" % e, module="Config")

            # Validate before saving
            self.config = self.validate_config(self.config)

            # Save config
            with open(self.config_file, 'w') as f:
                dump(self.config, f, indent=4, sort_keys=True)

            # Set proper permissions
            chmod(self.config_file, 0o644)

            log.info("Configuration saved to %s" % self.config_file, module="Config")
            return True
        except Exception as e:
            log.error("Error saving config: %s" % e, module="Config")
            return False

    def validate_config(self, config):
        """Validate and fix configuration values"""
        validated_config = config.copy()

        # Ensure volume is between 0-100
        if 'volume' in validated_config:
            try:
                volume = int(validated_config['volume'])
                if volume < 0:
                    volume = 0
                elif volume > 100:
                    volume = 100
                validated_config['volume'] = volume
            except (ValueError, TypeError):
                validated_config['volume'] = 80

        # Ensure timeout is reasonable
        if 'timeout' in validated_config:
            try:
                timeout = int(validated_config['timeout'])
                if timeout < 5:
                    timeout = 5
                elif timeout > 60:
                    timeout = 60
                validated_config['timeout'] = timeout
            except (ValueError, TypeError):
                validated_config['timeout'] = 10

        # Ensure max_channels_for_bouquet is valid
        if 'max_channels_for_bouquet' in validated_config:
            try:
                val = int(validated_config['max_channels_for_bouquet'])
                if val < 0:
                    val = 100
                validated_config['max_channels_for_bouquet'] = val
            except (ValueError, TypeError):
                validated_config['max_channels_for_bouquet'] = 100

        # Ensure skin is valid
        valid_skins = ['auto', 'hd', 'fhd', 'wqhd', 'sd']
        if validated_config.get('skin') not in valid_skins:
            validated_config['skin'] = 'auto'

        # Ensure player is valid
        valid_players = ['exteplayer3', 'gstplayer', 'auto']
        if validated_config.get('player') not in valid_players:
            validated_config['player'] = 'auto'

        # Ensure log_level is valid
        valid_log_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
        if validated_config.get('log_level') not in valid_log_levels:
            validated_config['log_level'] = 'INFO'

        # Ensure buffer_size is reasonable
        if 'buffer_size' in validated_config:
            try:
                buffer_size = int(validated_config['buffer_size'])
                if buffer_size < 512:
                    buffer_size = 512
                elif buffer_size > 8192:
                    buffer_size = 8192
                validated_config['buffer_size'] = buffer_size
            except (ValueError, TypeError):
                validated_config['buffer_size'] = 2048

        # Ensure log_max_size is reasonable
        if 'log_max_size' in validated_config:
            try:
                val = int(validated_config['log_max_size'])
                if val < 102400:  # Min 100KB
                    val = 102400
                elif val > 10485760:  # Max 10MB
                    val = 10485760
                validated_config['log_max_size'] = val
            except (ValueError, TypeError):
                validated_config['log_max_size'] = 1048576  # 1MB default

        # Ensure log_backup_count is reasonable
        if 'log_backup_count' in validated_config:
            try:
                val = int(validated_config['log_backup_count'])
                if val < 1:
                    val = 1
                elif val > 10:
                    val = 10
                validated_config['log_backup_count'] = val
            except (ValueError, TypeError):
                validated_config['log_backup_count'] = 3

        # Ensure connection_timeout is reasonable
        if 'connection_timeout' in validated_config:
            try:
                timeout = int(validated_config['connection_timeout'])
                if timeout < 10:
                    timeout = 10
                elif timeout > 120:
                    timeout = 120
                validated_config['connection_timeout'] = timeout
            except (ValueError, TypeError):
                validated_config['connection_timeout'] = 30

        # Ensure cache_ttl is reasonable
        if 'cache_ttl' in validated_config:
            try:
                val = int(validated_config['cache_ttl'])
                if val < 60:  # Min 1 minute
                    val = 60
                elif val > 86400:  # Max 24 hours
                    val = 86400
                validated_config['cache_ttl'] = val
            except (ValueError, TypeError):
                validated_config['cache_ttl'] = 3600

        # Ensure cache_size is reasonable
        if 'cache_size' in validated_config:
            try:
                val = int(validated_config['cache_size'])
                if val < 10:
                    val = 10
                elif val > 1000:
                    val = 1000
                validated_config['cache_size'] = val
            except (ValueError, TypeError):
                validated_config['cache_size'] = 100

        return validated_config

    def restore_backup(self):
        """Restore configuration from backup"""
        if fileExists(self.backup_file):
            try:
                with open(self.backup_file, 'r') as f:
                    backup_config = load(f)

                # Validate restored config
                validated_config = self.validate_config(backup_config)

                log.info("Configuration restored from backup: %s" % self.backup_file, module="Config")
                return validated_config
            except Exception as e:
                log.error("Error restoring backup: %s" % e, module="Config")

                # Return defaults if backup also fails
                return self.defaults.copy()
        else:
            log.warning("No backup found, using defaults", module="Config")
            return self.defaults.copy()

    def get(self, key, default=None):
        """Get config value"""
        if key in self.config:
            return self.config[key]
        elif default is not None:
            return default
        else:
            return self.defaults.get(key)

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
            # Ensure directory exists
            export_dir = join(filepath, '..')
            if not exists(export_dir):
                makedirs(export_dir)

            with open(filepath, 'w') as f:
                dump(self.config, f, indent=4)

            log.info("Configuration exported to: %s" % filepath, module="Config")
            return True
        except Exception as e:
            log.error("Error exporting config: %s" % e, module="Config")
            return False

    def import_config(self, filepath):
        """Import config from file"""
        if fileExists(filepath):
            try:
                with open(filepath, 'r') as f:
                    imported = load(f)

                # Validate imported config
                validated_imported = self.validate_config(imported)

                # Merge with current config (keep current values for missing keys)
                for key, value in validated_imported.items():
                    self.config[key] = value

                log.info("Configuration imported from: %s" % filepath, module="Config")
                return self.save_config()
            except Exception as e:
                log.error("Error importing config: %s" % e, module="Config")
                return False
        else:
            log.error("Import file not found: %s" % filepath, module="Config")
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
                else:
                    # Try gstplayer
                    result = subprocess.run(['which', 'gst-launch-1.0'],
                                            capture_output=True, text=True)
                    if result.returncode == 0:
                        return 'gstplayer'
            except Exception as e:
                log.debug("Auto-detection failed: %s" % e, module="Config")
            return 'gstplayer'  # Default fallback
        return player

    def get_skin_resolution(self):
        """Get skin resolution name (hd, fhd, wqhd, sd)"""
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
            except Exception as e:
                log.error("Error detecting resolution: %s" % e, module="Config")
                return 'hd'  # Default fallback

        return skin_setting

    def load_skin(self, screen_name, default_skin):
        """
        Load skin from file or use default from class
        Compatibile Python 2
        """
        resolution = self.get_skin_resolution()

        skin_file = join(PLUGIN_PATH, "skins/%s/%s.xml" % (resolution, screen_name))

        if fileExists(skin_file):
            try:
                # Python 2: NO 'encoding' parameter
                f = open(skin_file, 'r')
                skin_content = f.read()
                f.close()
                
                log.info("Loaded skin from: %s" % skin_file, module="Config")
                return skin_content
            except Exception as e:
                log.error("Error loading skin: %s" % e, module="Config")
                # Fallback to Class Skin
                log.warning("Using class skin for %s due to error" % screen_name, module="Config")
                return default_skin
        else:
            # Fallback to Class Skin
            log.warning("Skin file not found: %s, using class skin for %s" % (skin_file, screen_name), module="Config")
            return default_skin

    def get_skin_path(self):
        """Get skin path based on config and detection"""
        skin_setting = self.get('skin', 'auto')
        if skin_setting == 'auto':
            try:
                from ..helpers import get_resolution_type
                return get_resolution_type()
            except Exception as e:
                log.error("Error getting resolution type: %s" % e, module="Config")
                return 'hd'  # Default fallback
        return skin_setting

    def add_watch_time(self, seconds):
        """Add watch time to statistics"""
        if self.get('stats_enabled', True):
            current = self.get('watch_time', 0)
            self.set('watch_time', current + seconds)
            log.debug("Added %d seconds to watch time, total: %d" % (seconds, current + seconds), module="Config")

    def increment_channels_watched(self):
        """Increment channels watched counter"""
        if self.get('stats_enabled', True):
            current = self.get('channels_watched', 0)
            self.set('channels_watched', current + 1)
            log.debug("Incremented channels watched to: %d" % (current + 1), module="Config")

    def get_connection_timeout(self):
        """Get connection timeout in seconds"""
        return self.get('connection_timeout', 30)

    def get_buffer_size(self):
        """Get buffer size in KB"""
        return self.get('buffer_size', 2048)

    def is_debug_mode(self):
        """Check if debug mode is enabled"""
        return self.get('debug_mode', False)

    def use_hardware_acceleration(self):
        """Check if hardware acceleration should be used"""
        return self.get('use_hardware_acceleration', True)

    def get_all_settings(self):
        """Get all configuration as dictionary"""
        return self.config.copy()

    def get_settings_group(self, group_prefix):
        """
        Get all settings that start with a specific prefix
        Example: get_settings_group("log_") returns all logging settings
        """
        result = {}
        for key, value in self.config.items():
            if key.startswith(group_prefix):
                result[key] = value
        return result

    def update_settings(self, settings_dict, replace_all=False):
        """
        Update multiple settings at once
        Args:
            settings_dict: Dictionary with settings to update
            replace_all: If True, replace entire config with settings_dict
        Returns:
            True if successful, False otherwise
        """
        try:
            if replace_all:
                self.config = settings_dict.copy()
            else:
                for key, value in settings_dict.items():
                    self.config[key] = value
                    
            return self.save_config()
        except Exception as e:
            log.error("Error updating settings: %s" % e, module="Config")
            return False

    def get_version(self):
        """Get configuration version (for future compatibility)"""
        return self.get('config_version', 1)

    def set_version(self, version):
        """Set configuration version"""
        self.config['config_version'] = version
        return self.save_config()


# Singleton instance
_config_instance = None


def get_config():
    """Get configuration singleton instance"""
    global _config_instance
    if _config_instance is None:
        _config_instance = PluginConfig()
    return _config_instance


def reload_config():
    """Reload configuration from disk"""
    if _config_instance is not None:
        _config_instance.config = _config_instance.load_config()
        log.info("Configuration reloaded from disk", module="Config")
    return _config_instance
