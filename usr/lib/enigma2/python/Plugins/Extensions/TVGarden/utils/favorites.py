#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
TV Garden Plugin - Favorites Manager
Manages favorite channels storage
Based on TV Garden Project
"""

import time
from os import makedirs, remove, system
from os.path import exists, join
from json import load, dump
from hashlib import md5
from shutil import copy2
from ..helpers import log
from .. import _


class FavoritesManager:
    """Manage favorite channels"""
    def __init__(self):
        self.fav_dir = "/etc/enigma2/tvgarden/favorites"
        self.fav_file = join(self.fav_dir, "favorites.json")

        if not exists(self.fav_dir):
            makedirs(self.fav_dir)

        self.favorites = self.load_favorites()
        log.info("Initialized with %d favorites" % len(self.favorites), module="Favorites")

    def get_all(self):
        """Get all favorites"""
        if hasattr(self, 'favorites'):
            return self.favorites
        else:
            # Fallback
            log.warning("self.favorites doesn't exist!", module="Favorites")
            return []

    def load_favorites(self):
        """Load favorites from file"""
        if exists(self.fav_file):
            try:
                with open(self.fav_file, 'r') as f:
                    return load(f)
            except:
                return []
        return []

    def save_favorites(self):
        """Save favorites to file"""
        try:
            with open(self.fav_file, 'w') as f:
                dump(self.favorites, f, indent=2)
            return True
        except:
            return False

    def generate_id(self, channel):
        """Generate unique ID for channel"""
        # Use stream URL as base for ID
        stream_url = channel.get('stream_url', '')
        if stream_url:
            return md5(stream_url.encode()).hexdigest()[:16]

        # Fallback to name and other attributes
        name = channel.get('name', '')
        group = channel.get('group', '')
        return md5("%s%s" % (name, group).encode()).hexdigest()[:16]

    def add(self, channel):
        """Add channel to favorites"""
        if self.is_favorite(channel):
            return False, _("Already in favorites")

        channel_id = self.generate_id(channel)
        channel_name = channel.get('name', 'Unknown')

        channel['id'] = channel_id
        channel['added'] = time.time()

        self.favorites.append(channel)

        if self.save_favorites():
            log.info("✓ Added to favorites: %s" % channel_name, module="Favorites")
            return True, _("Added to favorites: %s") % channel_name
        else:
            log.error("✗ Failed to save favorites: %s" % channel_name, module="Favorites")
            return False, _("Error saving favorites")

    def remove(self, channel):
        """Remove channel from favorites"""
        channel_id = self.generate_id(channel)
        channel_name = channel.get('name', 'Unknown')

        for i, fav in enumerate(self.favorites):
            if fav.get('id') == channel_id:
                del self.favorites[i]
                if self.save_favorites():
                    log.info("✓ Removed from favorites: %s" % channel_name, module="Favorites")
                    return True, _("Removed from favorites: %s") % channel_name
                else:
                    log.error("✗ Failed to save after removal: %s" % channel_name, module="Favorites")
                    return False, _("Error saving favorites")

        return False, _("Channel not found in favorites")

    def is_favorite(self, channel):
        """Check if channel is already in favorites - OTTIMIZZATO"""
        if not channel:
            return False

        channel_url = channel.get('stream_url') or channel.get('url')
        if channel_url and self.is_url_in_favorites(channel_url):
            return True

        channel_id = self.generate_id(channel)
        for fav in self.favorites:
            if fav.get('id') == channel_id:
                return True

        return False

    def is_url_in_favorites(self, url):
        """Check if specific URL is already in favorites"""
        if not url:
            return False

        for fav in self.favorites:
            fav_url = fav.get('stream_url') or fav.get('url')
            if fav_url and fav_url == url:
                return True

        return False

    def search(self, query):
        """Search in favorites"""
        query = query.lower()
        results = []
        for fav in self.favorites:
            name = fav.get('name', '').lower()
            group = fav.get('group', '').lower()
            desc = fav.get('description', '').lower()

            if query in name or query in group or query in desc:
                results.append(fav)
        return results

    def _create_bouquet_files(self):
        """Create actual bouquet files - LULULLA STYLE"""
        try:
            bouquet_name = "TVGarden"
            tag = "tvgarden"
            userbouquet_file = "/etc/enigma2/userbouquet.%s_%s.tv" % (tag, bouquet_name)

            with open(userbouquet_file, "w") as f:
                # LULULLA STYLE HEADER
                f.write("#NAME TV Garden Favorites\n")
                f.write("#SERVICE 1:64:0:0:0:0:0:0:0:0:::--- | TV Garden Favorites by Lululla | ---\n")
                f.write("#DESCRIPTION --- | TV Garden Favorites by Lululla | ---\n\n")

                for idx, channel in enumerate(self.favorites, 1):
                    name = channel.get('name', 'Channel %d' % idx)
                    stream_url = channel.get('stream_url') or channel.get('url', '')

                    if not stream_url:
                        continue

                    url_encoded = stream_url.replace(":", "%3a")
                    name_encoded = name.replace(":", "%3a")

                    # ONE service line per channel
                    service_line = '#SERVICE 4097:0:1:0:0:0:0:0:0:0:%s:%s\n' % (url_encoded, name_encoded)
                    f.write(service_line)
                    f.write('#DESCRIPTION %s\n\n' % name)

            return True

        except Exception as e:
            log.error("Error: %s" % e, module="Favorites")
            return False

    def export_to_bouquet(self, channels=None, bouquet_name="tvgarden_favorites"):
        """Export channels to Enigma2 bouquet file - FIXED FORMAT"""
        try:
            if channels is None:
                channels = self.favorites

            if not channels or len(channels) == 0:
                return False, _("No channels to export")

            tag = "tvgarden"
            userbouquet_file = "/etc/enigma2/userbouquet.%s_%s.tv" % (tag, bouquet_name)

            with open(userbouquet_file, "w") as f:
                f.write("#NAME TV Garden Favorites\n")
                f.write("#SERVICE 1:64:0:0:0:0:0:0:0:0::--- | TV Garden Favorites by Lululla | ---\n")
                f.write("#DESCRIPTION --- | TV Garden Favorites by Lululla | ---\n")

                valid_count = 0
                for idx, channel in enumerate(channels, 1):
                    name = channel.get('name', 'Channel %d' % idx)
                    stream_url = channel.get('stream_url') or channel.get('url', '')

                    if not stream_url:
                        continue

                    # Encoding
                    url_encoded = stream_url.replace(":", "%3a")
                    name_encoded = name.replace(":", "%3a")

                    # Use 4097:0:1:0:0:0:0:0:0:0 format
                    service_line = '#SERVICE 4097:0:1:0:0:0:0:0:0:0:%s:%s\n' % (url_encoded, name_encoded)
                    f.write(service_line)
                    f.write('#DESCRIPTION %s\n' % name)

                    valid_count += 1

            if valid_count == 0:
                return False, _("No valid stream URLs found")

            # Use existing methods
            self._add_to_bouquets_tv(tag, bouquet_name)
            self._reload_bouquets()

            return True, _("Exported %d channels to bouquet") % valid_count

        except Exception as e:
            log.error("Error: %s" % e, module="Favorites")
            return False, _("Error: %s") % str(e)

    def _reload_bouquets(self):
        """Reload bouquets in Enigma2 - ENHANCED"""
        try:
            from enigma import eDVBDB
            db = eDVBDB.getInstance()
            db.reloadServicelist()
            db.reloadBouquets()

            # Additional delay to ensure reload completes
            time.sleep(1)
            log.info("Bouquets reloaded via eDVBDB", module="Favorites")
            return True

        except Exception as e:
            log.error("eDVBDB reload failed: %s" % e, module="Favorites")

            # Fallback: try shell command
            try:
                system("wget -qO - http://127.0.0.1/web/servicelistreload > /dev/null 2>&1")
                log.info("Bouquets reloaded via web interface", module="Favorites")
                return True
            except:
                log.error("All reload methods failed", module="Favorites")
                return False

    def _add_to_bouquets_tv(self, tag, bouquet_name):
        """Add bouquet reference to bouquets.tv - ADD TO END"""
        try:
            bouquet_tv_file = "/etc/enigma2/bouquets.tv"
            bouquet_line = '#SERVICE 1:7:1:0:0:0:0:0:0:0:FROM BOUQUET "userbouquet.%s_%s.tv" ORDER BY bouquet\n' % (tag, bouquet_name)

            if exists(bouquet_tv_file):
                # Read entire file
                with open(bouquet_tv_file, "r") as f:
                    content = f.read()

                # Check if already exists
                if bouquet_line in content:
                    log.info("Bouquet already in bouquets.tv", module="Favorites")
                    return True

                # Check if file ends with newline
                with open(bouquet_tv_file, "rb") as f:
                    f.seek(-1, 2)  # Go to last byte
                    last_char = f.read(1)
                    needs_newline = last_char != b'\n'

                # Append to END of file
                with open(bouquet_tv_file, "a") as f:
                    if needs_newline:
                        f.write("\n")
                    # f.write("# TV Garden Favorites - Added by TV Garden Plugin\n")
                    f.write(bouquet_line)

                log.info("Added bouquet to END of bouquets.tv", module="Favorites")
                return True
            else:
                # Create new bouquets.tv file
                with open(bouquet_tv_file, "w") as f:
                    f.write("#NAME Bouquets (TV)\n")
                    f.write("#SERVICE 1:7:1:0:0:0:0:0:0:0:\n")
                    f.write("\n# TV Garden Favorites\n")
                    f.write(bouquet_line)

                log.info("Created bouquets.tv with TV Garden bouquet", module="Favorites")
                return True

        except Exception as e:
            log.error("Error updating bouquets.tv: %s" % e, module="Favorites")
            return False

    def remove_bouquet(self, bouquet_name="tvgarden_favorites"):
        """Remove bouquet while PRESERVING original order"""
        try:
            tag = "tvgarden"
            removed_files = 0

            # 1. SAFE REMOVAL from bouquets.tv (preserve order)
            bouquet_tv_file = "/etc/enigma2/bouquets.tv"

            if exists(bouquet_tv_file):
                # Backup original
                backup_file = "%s.backup" % bouquet_tv_file
                copy2(bouquet_tv_file, backup_file)

                # Read and filter WITHOUT reordering
                with open(bouquet_tv_file, "r") as f:
                    lines = f.readlines()

                # Find and remove only TV Garden lines
                new_lines = []
                skip_next_empty = False

                for i, line in enumerate(lines):
                    # Skip lines containing our bouquet
                    if 'userbouquet.%s_%s.tv' % (tag, bouquet_name) in line:
                        skip_next_empty = True  # Skip next empty line if exists
                        continue

                    # Skip TV Garden comment lines
                    if "TV Garden" in line and "Favorites" in line:
                        continue

                    # Skip empty line after removed bouquet
                    if skip_next_empty and line.strip() == "":
                        skip_next_empty = False
                        continue

                    new_lines.append(line)

                # Write back preserving original order of other bouquets
                if len(new_lines) != len(lines):
                    with open(bouquet_tv_file, "w") as f:
                        f.writelines(new_lines)
                    log.info("Removed TV Garden from bouquets.tv (order preserved)", module="Favorites")

            # 2. Remove bouquet files
            files_to_remove = [
                "/etc/enigma2/userbouquet.%s_%s.tv" % (tag, bouquet_name),
                "/etc/enigma2/userbouquet.%s_%s.del" % (tag, bouquet_name),
                "/etc/enigma2/userbouquet.%s_%s.radio" % (tag, bouquet_name)
            ]

            for file in files_to_remove:
                if exists(file):
                    remove(file)
                    removed_files += 1
                    log.info("Removed: %s" % file, module="Favorites")

            # 3. SOFT RELOAD (not full reloadBouquets!)
            self._reload_bouquets()

            return True, _("Bouquet removed. %d files deleted. Order preserved.") % removed_files

        except Exception as e:
            log.error("Error removing bouquet: %s" % e, module="Favorites")
            return False, _("Error: %s") % str(e)

    def export_single_channel(self, channel, bouquet_name="tvgarden_favorites"):
        """Export single channel to bouquet - LULULLA STYLE"""
        try:
            tag = "tvgarden"
            userbouquet_file = "/etc/enigma2/userbouquet.%s_%s.tv" % (tag, bouquet_name)

            name = channel.get('name', 'TV Garden Channel')
            stream_url = channel.get('stream_url') or channel.get('url', '')

            if not stream_url:
                return False, _("No stream URL")

            # Check if file exists to read first line
            file_exists = exists(userbouquet_file)
            file_mode = "a" if file_exists else "w"

            with open(userbouquet_file, file_mode) as f:
                # If new file, add Lululla style header
                if file_mode == "w":
                    f.write("#NAME TV Garden Favorites\n")
                    f.write("#SERVICE 1:64:0:0:0:0:0:0:0:0::--- | TV Garden Favorites by Lululla | ---\n")
                    f.write("#DESCRIPTION --- | TV Garden Favorites by Lululla | ---\n")
                # Add channel
                url_encoded = stream_url.replace(":", "%3a")
                name_encoded = name.replace(":", "%3a")

                service_line = '#SERVICE 4097:0:1:0:0:0:0:0:0:0:%s:%s\n' % (url_encoded, name_encoded)
                f.write(service_line)
                f.write('#DESCRIPTION %s\n' % name)

            # Use existing methods
            self._add_to_bouquets_tv(tag, bouquet_name)
            self._reload_bouquets()

            return True, _("Channel added to bouquet")

        except Exception as e:
            log.error("Error: %s" % e, module="Favorites")
            return False, _("Error: %s") % str(e)

    def clear_all(self):
        """Clear all favorites"""
        count = len(self.favorites)
        self.favorites = []
        if self.save_favorites():
            log.info("✓ Cleared all favorites (%d)" % count, module="Favorites")
            return True, _("Cleared %d favorites") % count
        else:
            log.error("✗ Failed to clear favorites", module="Favorites")
            return False, _("Error clearing favorites")
