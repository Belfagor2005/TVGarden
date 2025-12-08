#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
TV Garden Plugin - Helpers Module
Based on TV Garden Project by Lululla
Data Source: TV Garden Project
"""

from os import remove, makedirs
from os.path import join, exists
from sys import stderr
from datetime import datetime
from Tools.Directories import resolveFilename, SCOPE_PLUGINS, fileExists
from enigma import getDesktop
from . import PLUGIN_NAME, PLUGIN_PATH  # , _, PLUGIN_VERSION, PLUGIN_ICON


# Helper to load skin
def load_skin_file(skin_name):
    """Load skin file for current resolution"""
    skin_file = join(SKIN_PATH, f"{skin_name}.xml")
    
    # Fallback to HD if skin not found for current resolution
    if not fileExists(skin_file):
        skin_file = join(DEFAULT_SKIN_PATH, f"{skin_name}.xml")
    
    # Read skin content
    if fileExists(skin_file):
        try:
            with open(skin_file, 'r') as f:
                return f.read()
        except:
            pass
    
    return None


# ============ DETECT SCREEN RESOLUTION ============
def get_screen_resolution():
    """Get current screen resolution"""
    desktop = getDesktop(0)
    return desktop.size()


def get_resolution_type():
    """Get resolution type: hd, fhd, wqhd"""
    width = get_screen_resolution().width()
    
    if width >= 2560:
        return 'wqhd'
    elif width >= 1920:
        return 'fhd'
    else:  # 1280x720 or smaller
        return 'hd'


# ============ SKIN TEMPLATES ============
def get_skin_template(screen_name):
    """Get skin template for a screen"""
    templates = {
        'main': """
<screen name="TVGardenMain" position="center,center" size="{width},{height}" title="TV Garden">
    <ePixmap pixmap="{images_path}/background.png" position="0,0" size="{width},{height}" zPosition="-1" />
    <widget name="menu" position="50,80" size="{menu_width},{menu_height}" backgroundColor="#1a1a2e" />
    <widget name="status" position="50,{status_y}" size="{menu_width},30" font="Regular;18" halign="center" />
</screen>
""",
        'countries': """
<screen name="CountriesBrowser" position="center,center" size="{width},{height}" title="Countries">
    <widget name="menu" position="50,80" size="{menu_width},{menu_height}" backgroundColor="#16213e" />
    <widget name="flag" position="{flag_x},{flag_y}" size="120,80" alphatest="blend" />
</screen>
"""
    }
    
    # Calculate dimensions based on resolution
    width = get_screen_resolution().width()
    height = get_screen_resolution().height()
    
    if RESOLUTION_TYPE == 'wqhd':
        menu_width = width - 100
        menu_height = height - 200
        status_y = height - 60
        flag_x = width - 180
        flag_y = 100
    elif RESOLUTION_TYPE == 'fhd':
        menu_width = width - 100
        menu_height = height - 200
        status_y = height - 60
        flag_x = width - 180
        flag_y = 100
    else:  # hd
        menu_width = width - 60
        menu_height = height - 160
        status_y = height - 50
        flag_x = width - 140
        flag_y = 80
    
    template = templates.get(screen_name, '')
    return template.format(
        width=width,
        height=height,
        menu_width=menu_width,
        menu_height=menu_height,
        status_y=status_y,
        flag_x=flag_x,
        flag_y=flag_y,
        images_path=IMAGES_PATH
    )


def get_plugin_path():
    """Get absolute path to plugin directory"""
    return resolveFilename(SCOPE_PLUGINS, f"Extensions/{PLUGIN_NAME}")


def get_icons_path():
    """Get path to icons directory"""
    return join(get_plugin_path(), "icons")


def get_skins_path():
    """Get path to skins directory"""
    return join(get_plugin_path(), "skins")


def get_config_path():
    """Get path to config directory"""
    return "/etc/enigma2/tvgarden"


# Determine skin path based on resolution
RESOLUTION_TYPE = get_resolution_type()
SKIN_PATH = join(PLUGIN_PATH, "skin", RESOLUTION_TYPE)
IMAGES_PATH = join(PLUGIN_PATH, "images", RESOLUTION_TYPE)

# Fallback paths
DEFAULT_SKIN_PATH = join(PLUGIN_PATH, "skin", "hd")
DEFAULT_IMAGES_PATH = join(PLUGIN_PATH, "images", "hd")

REPO_BASE = "https://raw.githubusercontent.com/Belfagor2005/tv-garden-channel-list/main"


def get_metadata_url():
    return "https://raw.githubusercontent.com/Belfagor2005/tv-garden-channel-list/main/channels/raw/countries_metadata.json"


def get_country_url(country_code):
    return f"https://raw.githubusercontent.com/Belfagor2005/tv-garden-channel-list/main/channels/raw/countries/{country_code.lower()}.json"


def get_category_url(category_id):
    return f"https://raw.githubusercontent.com/Belfagor2005/tv-garden-channel-list/main/channels/raw/categories/{category_id}.json"


def get_categories_url():
    return "https://api.github.com/repos/Belfagor2005/tv-garden-channel-list/contents/channels/raw/categories"


def get_flag_url(country_code, size=80):
    """Get URL for country flag"""
    return f"https://flagcdn.com/w{size}/{country_code.lower()}.png"


CATEGORIES = [
    {'id': 'all-channels', 'name': 'All Channels'},
    {'id': 'animation', 'name': 'Animation'},
    {'id': 'auto', 'name': 'Auto'},
    {'id': 'business', 'name': 'Business'},
    {'id': 'classic', 'name': 'Classic'},
    {'id': 'comedy', 'name': 'Comedy'},
    {'id': 'cooking', 'name': 'Cooking'},
    {'id': 'culture', 'name': 'Culture'},
    {'id': 'documentary', 'name': 'Documentary'},
    {'id': 'education', 'name': 'Education'},
    {'id': 'entertainment', 'name': 'Entertainment'},
    {'id': 'family', 'name': 'Family'},
    {'id': 'general', 'name': 'General'},
    {'id': 'kids', 'name': 'Kids'},
    {'id': 'legislative', 'name': 'Legislative'},
    {'id': 'lifestyle', 'name': 'Lifestyle'},
    {'id': 'movies', 'name': 'Movies'},
    {'id': 'music', 'name': 'Music'},
    {'id': 'news', 'name': 'News'},
    {'id': 'outdoor', 'name': 'Outdoor'},
    {'id': 'public', 'name': 'Public'},
    {'id': 'relax', 'name': 'Relax'},
    {'id': 'religious', 'name': 'Religious'},
    {'id': 'science', 'name': 'Science'},
    {'id': 'series', 'name': 'Series'},
    {'id': 'shop', 'name': 'Shop'},
    {'id': 'show', 'name': 'Show'},
    {'id': 'sports', 'name': 'Sports'},
    {'id': 'top-news', 'name': 'Top News'},
    {'id': 'travel', 'name': 'Travel'},
    {'id': 'weather', 'name': 'Weather'}
]


def get_category_name(category_id):
    """Get display name for category ID"""
    for cat in CATEGORIES:
        if cat['id'] == category_id:
            return cat['name']
    return category_id


def safe_get(dictionary, keys, default=None):
    """Safely get nested dictionary value"""
    current = dictionary
    for key in keys:
        if isinstance(current, dict) and key in current:
            current = current[key]
        else:
            return default
    return current


def format_channel_count(count):
    """Format channel count for display"""
    if count == 0:
        return "No channels"
    elif count == 1:
        return "1 channel"
    else:
        return f"{count} channels"


def is_valid_stream_url(url):
    """Check if URL looks like a valid stream for Enigma2"""
    if not url or not isinstance(url, str):
        return False
    
    url = url.strip()
    
    valid_prefixes = ('http://', 'https://', 'rtmp://', 'rtsp://')
    
    if not any(url.startswith(prefix) for prefix in valid_prefixes):
        return False
    
    supported_patterns = ('.m3u8', '.mp4', '.ts', '.avi', '.mkv', '.flv', 'mpegts')
    
    url_lower = url.lower()
    for pattern in supported_patterns:
        if pattern in url_lower:
            return True

    if url.startswith(('http://', 'https://')):
        return True
    
    return False


# ============ DEFAULT CONFIG ============
DEFAULT_CONFIG = {
    "skin": "default",
    "player": "exteplayer3",
    "cache_ttl": 3600,
    "max_channels_page": 50,
    "show_flags": True,
    "show_icons": True,
    "auto_update": True,
    "parental_lock": False,
    "parental_pin": "0000",
    "volume": 80,
    "timeout": 10,
    "retries": 3,
    "favorite_countries": [],
    "favorite_categories": [],
    "last_country": None,
    "last_category": None
}


# ============ LOGGING ============
LOG_PATH_DIR = "/tmp/tvgarden_cache"
LOG_PATH = join(LOG_PATH_DIR, "tvgarden.log")

if not exists(LOG_PATH_DIR):
    makedirs(LOG_PATH_DIR)
print(f"[LOG_PATH] Initialized at {LOG_PATH}", file=stderr)


def init_log():
    """Delete old log on startup and create a new empty one."""
    try:
        if exists(LOG_PATH):
            remove(LOG_PATH)
        # create an empty file
        open(LOG_PATH, "w").close()
    except Exception as e:
        print("Error initialize log:", e)


def log(message, level="INFO"):
    """Simple logging function"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_line = f"[{timestamp}] [{level}] TVGarden: {message}\n"

    try:
        with open(LOG_PATH, "a") as f:
            f.write(log_line)
    except:
        pass

    print(f"TVGarden: {message}")
