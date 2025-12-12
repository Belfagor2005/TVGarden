#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
TV Garden Plugin - Cache Module
Smart caching with TTL + gzip
Based on TV Garden Project
"""
from __future__ import print_function
import time
import hashlib
import gzip
from os.path import join, exists, getmtime
from os import listdir, remove, makedirs
from json import load, loads, dump
from sys import version_info

if version_info[0] == 3:
    from urllib.request import urlopen, Request
else:
    from urllib2 import urlopen, Request


try:
    from ..helpers import (
        get_metadata_url,
        get_country_url,
        get_category_url,
        get_categories_url,
        log
    )
except ImportError as e:
    print('Error import helpers:', str(e))

    def log(message, level="INFO", module=""):
        print("[%s] [%s] TVGarden: %s" % (level, module, message))

    def get_metadata_url():
        return "https://raw.githubusercontent.com/Belfagor2005/tv-garden-channel-list/main/channels/raw/countries_metadata.json"

    def get_country_url(code):
        return "https://raw.githubusercontent.com/Belfagor2005/tv-garden-channel-list/main/channels/raw/countries/%s.json" % code.lower()

    def get_category_url(cat_id):
        return "https://raw.githubusercontent.com/Belfagor2005/tv-garden-channel-list/main/channels/raw/categories/%s.json" % cat_id

    def get_categories_url():
        return "https://api.github.com/repos/Belfagor2005/tv-garden-channel-list/contents/channels/raw/categories"


class CacheManager:
    """Smart cache manager with TTL support"""

    def __init__(self):
        self.cache_dir = "/tmp/tvgarden_cache"
        self.cache_data = {}

        if not exists(self.cache_dir):
            makedirs(self.cache_dir)
        log.info("Initialized at %s" % self.cache_dir, module="Cache")

    def _get_cache_key(self, url):
        """Generate cache key from URL"""
        return hashlib.md5(url.encode()).hexdigest()

    def _get_cache_path(self, key):
        """Get cache file path"""
        return join(self.cache_dir, "%s.json.gz" % key)

    def _is_cache_valid(self, cache_path, ttl=3600):
        """Check if cache is still valid"""
        if not exists(cache_path):
            return False

        file_age = time.time() - getmtime(cache_path)
        return file_age < ttl

    def _get_cached(self, cache_key):
        """Get data from cache - nuovo metodo mancante"""
        cache_path = self._get_cache_path(cache_key)
        if exists(cache_path):
            try:
                with gzip.open(cache_path, 'rt', encoding='utf-8') as f:
                    return load(f)
            except Exception as e:
                log.error("Error reading %s: %s" % (cache_key, e), module="Cache")
        return None

    def _set_cached(self, cache_key, data):
        """Save data to cache - nuovo metodo mancante"""
        cache_path = self._get_cache_path(cache_key)
        try:
            with gzip.open(cache_path, 'wt', encoding='utf-8') as f:
                dump(data, f)
            return True
        except Exception as e:
            log.error("Error saving %s: %s" % (cache_key, e), module="Cache")
            return False

    def _fetch_url(self, url):
        """Fetch URL - nuovo metodo mancante"""
        try:
            headers = {'User-Agent': 'TVGarden-Enigma2-Plugin/1.0'}
            req = Request(url, headers=headers)

            with urlopen(req, timeout=15) as response:
                data = response.read()

                try:
                    return loads(data.decode('utf-8'))
                except:
                    # Try gzip decompression
                    try:
                        return loads(gzip.decompress(data).decode('utf-8'))
                    except:
                        raise ValueError("Failed to decode response")
        except Exception as e:
            log.error("Error fetching %s: %s" % (url, e), module="Cache")
            raise

    def fetch_url(self, url, force_refresh=False, ttl=3600):
        """Fetch URL with caching support (metodo vecchio ma usato da get_country_channels)"""
        cache_key = self._get_cache_key(url)
        cache_path = self._get_cache_path(cache_key)

        if not force_refresh and self._is_cache_valid(cache_path, ttl):
            try:
                with gzip.open(cache_path, 'rt', encoding='utf-8') as f:
                    return load(f)
            except:
                pass

        try:
            result = self._fetch_url(url)
            # Cache the result
            self._set_cached(cache_key, result)
            return result
        except Exception as e:
            log.error("Error in fetch_url: %s" % e, module="Cache")
            raise

    def _get_default_categories(self):
        """Default categories if GitHub API fails"""
        return [
            {'id': 'all-channels', 'name': 'All Channels'},
            {'id': 'animation', 'name': 'Animation'},
            {'id': 'general', 'name': 'General'},
            {'id': 'news', 'name': 'News'},
            {'id': 'entertainment', 'name': 'Entertainment'},
            {'id': 'music', 'name': 'Music'},
            {'id': 'sports', 'name': 'Sports'},
            {'id': 'movies', 'name': 'Movies'},
            {'id': 'kids', 'name': 'Kids'},
            {'id': 'documentary', 'name': 'Documentary'},
        ]

    def get_available_categories(self):
        """Get list of available categories from GitHub directory"""
        categories_url = get_categories_url()
        try:
            # Use cache if it already exists
            cache_key = "available_categories"
            if cache_key in self.cache_data:
                return self.cache_data[cache_key]

            # Download file list from GitHub directory
            with urlopen(categories_url, timeout=10) as response:
                data = load(response)

            # Extract .json filenames
            categories = []
            for item in data:
                if item['name'].endswith('.json'):
                    category_id = item['name'].replace('.json', '')
                    name = category_id.replace('-', ' ').title()
                    categories.append({'id': category_id, 'name': name})

            # Save to cache
            self.cache_data[cache_key] = categories
            self._save_cache()

            log.info("Found %d categories from GitHub" % len(categories), module="Cache")
            return categories

        except Exception as e:
            log.error("Error getting categories: %s" % e, module="Cache")
            # Fallback to hardcoded list
            return self._get_default_categories()

    def get_category_channels(self, category_id, force_refresh=False):
        """Get channels for a specific category, handling multiple JSON formats."""
        cache_key = "cat_%s" % category_id
        channels = self._get_cached(cache_key)

        if channels is not None and not force_refresh:
            return channels

        try:
            url = get_category_url(category_id)
            log.debug("Fetching category %s from %s" % (category_id, url), module="Cache")
            data = self._fetch_url(url)
            log.debug("Raw data type for %s: %s" % (category_id, type(data)), module="Cache")

            # Handle both possible formats
            if isinstance(data, list):
                # Format: Direct list of channels
                channels = data
                log.debug("Data is list with %d items" % len(channels), module="Cache")
            elif isinstance(data, dict):
                # Format: Object with a key containing the list
                log.debug("Data is dict with keys: %s" % list(data.keys()), module="Cache")
                for key in ['channels', 'items', 'streams', 'list']:
                    if key in data and isinstance(data[key], list):
                        channels = data[key]
                        log.debug("Found '%s' key with %d items" % (key, len(channels)), module="Cache")
                        break
                else:
                    channels = []
                    log.debug("No known list key found", module="Cache")
            else:
                channels = []
                log.debug("Unexpected format: %s" % type(data), module="Cache")

            log.debug("Extracted %d channels for %s" % (len(channels), category_id), module="Cache")

            if channels:
                self._set_cached(cache_key, channels)
            return channels

        except Exception as e:
            log.error("Failed to get category %s: %s" % (category_id, e), module="Cache")
            import traceback
            traceback.print_exc()
        return []

    def get_country_channels(self, country_code, force_refresh=False):
        """Get channels for specific country"""
        try:
            url = get_country_url(country_code)
            log.debug("Fetching country %s" % country_code, module="Cache")

            result = self.fetch_url(url, force_refresh)
            log.debug("Fetch successful, type: %s" % type(result), module="Cache")

            return result
        except Exception as e:
            log.error("ERROR fetching country %s: %s" % (country_code, e), module="Cache")
            return []

    def get_countries_metadata(self, force_refresh=False):
        """Get countries metadata"""
        url = get_metadata_url()
        return self.fetch_url(url, force_refresh)

    def clear_all(self):
        """Clear all cache"""
        for file in listdir(self.cache_dir):
            if file.endswith('.json.gz'):
                remove(join(self.cache_dir, file))
        log.info("Cache cleared", module="Cache")
        return True

    def get_size(self):
        """Get cache size in items"""
        count = 0
        for file in listdir(self.cache_dir):
            if file.endswith('.json.gz'):
                count += 1
        return count
