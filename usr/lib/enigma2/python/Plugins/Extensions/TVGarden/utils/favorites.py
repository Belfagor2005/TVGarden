#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
TV Garden Plugin - Favorites Manager
Manages favorite channels storage
Based on TV Garden Project
"""

import time
from os.path import join, exists
from os import makedirs
from json import load, dump
from hashlib import md5


class FavoritesManager:
    """Manage favorite channels"""
    def __init__(self):
        self.fav_dir = "/etc/enigma2/tvgarden/favorites"
        self.fav_file = join(self.fav_dir, "favorites.json")

        if not exists(self.fav_dir):
            makedirs(self.fav_dir)

        self.favorites = self.load_favorites()
        print(f"[FavoritesManager] Initialized with {len(self.favorites)} favorites")

    def get_all(self):
        """Get all favorites"""
        if hasattr(self, 'favorites'):
            return self.favorites
        else:
            # Fallback
            print("[FavoritesManager] WARNING: self.favorites doesn't exist!")
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
        return md5(f"{name}{group}".encode()).hexdigest()[:16]

    def add(self, channel):
        """Add channel to favorites"""
        channel_id = self.generate_id(channel)
        # Check if already in favorites
        for fav in self.favorites:
            if fav.get('id') == channel_id:
                return False

        # Add timestamp and ID
        channel['id'] = channel_id
        channel['added'] = time.time()

        self.favorites.append(channel)
        return self.save_favorites()

    def remove(self, channel):
        """Remove channel from favorites"""
        channel_id = self.generate_id(channel)

        for i, fav in enumerate(self.favorites):
            if fav.get('id') == channel_id:
                del self.favorites[i]
                return self.save_favorites()
        return False

    def is_favorite(self, channel):
        """Check if channel is in favorites"""
        channel_id = self.generate_id(channel)
        for fav in self.favorites:
            if fav.get('id') == channel_id:
                return True
        return False

    def clear_all(self):
        """Clear all favorites"""
        self.favorites = []
        return self.save_favorites()

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
