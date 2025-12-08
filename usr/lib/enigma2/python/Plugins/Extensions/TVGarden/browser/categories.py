#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
TV Garden Plugin - Categories Browser
Browse 29 categories of IPTV channels
Based on TV Garden Project
"""

from Components.ActionMap import ActionMap
from Components.MenuList import MenuList
from Components.Label import Label
from Components.Pixmap import Pixmap
from enigma import eTimer
from sys import stderr

from .base import BaseBrowser
from ..utils.config import PluginConfig
from .channels import ChannelsBrowser
from ..utils.cache import CacheManager
from .. import _

try:
    from ..helpers import CATEGORIES
except ImportError:
    # Fallback
    CATEGORIES = [
        {'id': 'animation',    'name': _('Animation'),      'icon': 'film'},
        {'id': 'auto',         'name': _('Auto'),           'icon': 'car'},
        {'id': 'business',     'name': _('Business'),       'icon': 'briefcase'},
        {'id': 'classic',      'name': _('Classic'),        'icon': 'landmark'},
        {'id': 'comedy',       'name': _('Comedy'),         'icon': 'masks-theater'},
        {'id': 'cooking',      'name': _('Cooking'),        'icon': 'utensils'},
        {'id': 'culture',      'name': _('Culture'),        'icon': 'palette'},
        {'id': 'documentary',  'name': _('Documentary'),    'icon': 'camera-retro'},
        {'id': 'education',    'name': _('Education'),      'icon': 'graduation-cap'},
        {'id': 'entertainment', 'name': _('Entertainment'),  'icon': 'gamepad'},
        {'id': 'family',       'name': _('Family'),         'icon': 'users'},
        {'id': 'general',      'name': _('General'),        'icon': 'tv'},
        {'id': 'history',      'name': _('History'),        'icon': 'scroll'},
        {'id': 'hobby',        'name': _('Hobby'),          'icon': 'puzzle-piece'},
        {'id': 'kids',         'name': _('Kids'),           'icon': 'child-reaching'},
        {'id': 'legislative',  'name': _('Legislative'),    'icon': 'gavel'},
        {'id': 'lifestyle',    'name': _('Lifestyle'),      'icon': 'person-walking'},
        {'id': 'local',        'name': _('Local'),          'icon': 'map-marker-alt'},
        {'id': 'movies',       'name': _('Movies'),         'icon': 'clapperboard'},
        {'id': 'music',        'name': _('Music'),          'icon': 'music'},
        {'id': 'news',         'name': _('News'),           'icon': 'newspaper'},
        {'id': 'politics',     'name': _('Politics'),       'icon': 'landmark-dome'},
        {'id': 'religious',    'name': _('Religious'),      'icon': 'place-of-worship'},
        {'id': 'series',       'name': _('Series'),         'icon': 'photo-film'},
        {'id': 'science',      'name': _('Science'),        'icon': 'flask'},
        {'id': 'shop',         'name': _('Shop'),           'icon': 'shopping-cart'},
        {'id': 'sports',       'name': _('Sports'),         'icon': 'futbol'},
        {'id': 'travel',       'name': _('Travel'),         'icon': 'plane-departure'},
        {'id': 'weather',      'name': _('Weather'),        'icon': 'cloud-sun'}
    ]


class CategoriesBrowser(BaseBrowser):
    """Browse channels by category"""

    skin = """
        <screen name="CategoriesBrowser" position="center,center" size="1280,720" title="TV Garden" backgroundColor="#1a1a2e" flags="wfNoBorder">
            <ePixmap pixmap="skin_default/buttons/red.png" position="33,650" size="140,40" alphatest="blend" />
            <ePixmap pixmap="skin_default/buttons/green.png" position="174,650" size="140,40" alphatest="blend" />
            <ePixmap name="" position="0,0" size="1280,720" alphatest="blend" zPosition="-1" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/TVGarden/images/hd/background.png" scale="1" />
            <ePixmap name="" position="1039,531" size="200,80" alphatest="blend" zPosition="1" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/TVGarden/icons/logo.png" scale="1" transparent="1"/>
            <widget source="key_red" render="Label" position="33,649" zPosition="1" size="140,40" font="Regular;20" halign="center" valign="center" transparent="1" />
            <widget source="key_green" render="Label" position="174,650" zPosition="1" size="140,40" font="Regular;20" halign="center" valign="center" transparent="1" />
            <widget name="menu" position="28,116" size="680,474" scrollbarMode="showOnDemand" backgroundColor="#16213e" />
            <widget name="status" position="603,643" size="648,50" font="Regular; 22" halign="center" foregroundColor="#3333ff" transparent="1" />
            <widget name="icon" position="45,37" size="50,50" alphatest="blend" />
            <eLabel backgroundColor="#001a2336" cornerRadius="30" position="5,639" size="1270,60" zPosition="-80" />
            <eLabel name="" position="24,101" size="694,502" zPosition="-1" cornerRadius="18" backgroundColor="#00171a1c" foregroundColor="#00171a1c" />
            <widget source="session.VideoPicture" render="Pig" position="739,140" zPosition="19" size="520,308" backgroundColor="transparent" transparent="0" cornerRadius="14" />
        </screen>
    """

    def __init__(self, session):
        
        self.config = PluginConfig()
        dynamic_skin = self.config.load_skin("CategoriesBrowser", self.skin)
        self.skin = dynamic_skin   

        BaseBrowser.__init__(self, session)
        self.session = session

        self.cache = CacheManager()
        self.selected_category = None

        self["menu"] = MenuList([])
        self["status"] = Label(_("Loading categories..."))
        self["icon"] = Pixmap()
        self["key_red"] = Label(_("Back"))
        self["key_green"] = Label(_("Select"))
        self["actions"] = ActionMap(["TVGardenActions", "OkCancelActions", "ColorActions"], {
            "cancel": self.exit,
            "ok": self.select_category,
            "red": self.exit,
            "green": self.select_category,
            "up": self.up,
            "down": self.down,
        }, -2)

        print("[CATEGORIES DEBUG] ActionMap configured", file=stderr)
        print(f"[CATEGORIES DEBUG] self['actions']: {self['actions']}", file=stderr)
        self.test_key_press = False
        self.timer = eTimer()
        self.timer.callback.append(self.testOK)
        self.timer.start(3000, True)
        self.onFirstExecBegin.append(self.load_categories)

    def testOK(self):
        """Test method called by timer"""
        print("[CATEGORIES DEBUG] testOK() called!", file=stderr)
        self.select_category()

    def load_categories(self):
        """Load categories list - show only names"""
        menu_items = []
        for category in CATEGORIES:
            # Show name only - we'll get count when selected
            menu_items.append((category['name'], category['id']))
        
        self["menu"].setList(menu_items)
        self["status"].setText(_("Select a category"))

    def select_category(self):
        """Select category"""
        selection = self["menu"].getCurrent()
        if selection:
            category_id = selection[1]
            category_name = selection[0]
            
            print(f"[DEBUG CategoriesBrowser] Selected: {category_id} ({category_name})")
            
            try:
                # Load data
                print(f"[DEBUG] Calling cache.get_category_channels('{category_id}')")
                data = self.cache.get_category_channels(category_id)
                print(f"[DEBUG] Data received, type: {type(data)}")
                
                # Full log for the first 500 characters
                data_str = str(data)
                print(f"[DEBUG] Data sample: {data_str[:300]}...")
                
                # Extract channels
                channels = []
                if isinstance(data, list):
                    channels = data
                    print(f"[DEBUG] Data is list with {len(channels)} items")
                elif isinstance(data, dict):
                    print(f"[DEBUG] Data is dict with keys: {list(data.keys())}")
                    if 'channels' in data:
                        channels = data['channels']
                        print(f"[DEBUG] Found 'channels' key with {len(channels)} items")
                    else:
                        # Search for other keys
                        for key in ['items', 'streams', 'list']:
                            if key in data:
                                channels = data[key]
                                print(f"[DEBUG] Found '{key}' key with {len(channels)} items")
                                break
                
                print(f"[DEBUG] Total channels extracted: {len(channels)}")
                
                if len(channels) > 0:
                    print(f"[DEBUG] Opening ChannelsBrowser with {len(channels)} channels")
                    self.session.open(ChannelsBrowser,
                                      category_id=category_id,
                                      category_name=f"{category_name} ({len(channels)} channels)")
                else:
                    self["status"].setText(_("No channels in this category"))
                    print("[DEBUG] WARNING: Empty channel list!")
                    
            except Exception as e:
                self["status"].setText(_("Error loading category"))
                print(f"[DEBUG] ERROR: {type(e).__name__}: {e}")
                import traceback
                traceback.print_exc()

    def refresh(self):
        """Refresh categories - clear cache"""
        self["status"].setText(_("Refreshing cache..."))
        try:
            self.cache.clear_all()
            self["status"].setText(_("Cache cleared"))
        except:
            self["status"].setText(_("Refresh failed"))

    def exit(self):
        """Exit browser"""
        self.close()
