# TV Garden Plugin for Enigma2

![](https://komarev.com/ghpvc/?username=Belfagor2005&label=Repository%20Views&color=blueviolet)
[![Python package](https://github.com/Belfagor2005/TVGarden/actions/workflows/pylint.yml/badge.svg)](https://github.com/Belfagor2005/TVGarden/actions/workflows/pylint.yml)
[![TV Garden](https://img.shields.io/badge/TVGarden-00aaff.svg)](https://github.com/Belfagor2005/tv-garden-channel-list)
[![Enigma2](https://img.shields.io/badge/Enigma2-Plugin-ff6600.svg)](https://www.enigma2.net)
[![Python](https://img.shields.io/badge/Python-3.x-blue.svg)](https://www.python.org)
[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![GitHub stars](https://img.shields.io/github/stars/Belfagor2005/TVGarden?style=social)](https://github.com/Belfagor2005/TVGarden/stargazers)

**Professional IPTV Streaming Solution** for Enigma2 receivers with access to **50,000+ channels** from **150+ countries** and **29 categories**.
---
<img src="[https://raw.githubusercontent.com/Belfagor2005/TVGarden/main/screen/screen1.png](https://raw.githubusercontent.com/Belfagor2005/TVGarden/refs/heads/main/screen/screen1.png)">
<img src="[https://raw.githubusercontent.com/Belfagor2005/TVGarden/main/screen/screen2.png](https://raw.githubusercontent.com/Belfagor2005/TVGarden/refs/heads/main/screen/screen2.png)">
<img src="[https://raw.githubusercontent.com/Belfagor2005/TVGarden/main/screen/screen3.png](https://raw.githubusercontent.com/Belfagor2005/TVGarden/refs/heads/main/screen/screen3.png)">
<img src="[https://raw.githubusercontent.com/Belfagor2005/TVGarden/main/screen/screen4.png](https://raw.githubusercontent.com/Belfagor2005/TVGarden/refs/heads/main/screen/screen4.png)">
<img src="[https://raw.githubusercontent.com/Belfagor2005/TVGarden/main/screen/screen5.png](https://raw.githubusercontent.com/Belfagor2005/TVGarden/refs/heads/main/screen/screen5.png)">
<img src="[https://raw.githubusercontent.com/Belfagor2005/TVGarden/main/screen/screen6.png](https://raw.githubusercontent.com/Belfagor2005/TVGarden/refs/heads/main/screen/screen6.png)">


## 📺 Key Features

### 🌍 Global Coverage
- **150+ Countries** with national flags
- **29 Content Categories** (News, Sports, Movies, Music, Kids, etc.)
- **Local & International** channels

### 🔧 Advanced Technology
- **Smart Caching System** (TTL + gzip compression)
- **GStreamer/ExtePlayer3** multimedia engine
- **Memory Efficient** (~50MB RAM usage)
- **Auto-Skin Detection** (HD/FHD/WQHD)

### 🎮 User Experience
- **Channel Zapping** (CH+/CH- navigation)
- **Real-time Search** across all channels
- **Favorites Management** with export/import
- **Parental Control** with PIN protection
- **Multi-language** interface

### 🛡️ Reliability
- **DRM/Crash Protection** (filtered streams)
- **Connection Retry** with timeout handling
- **Offline Cache** for previously viewed content
- **Automatic Updates** from TV Garden repository

---

## 📊 Technical Specifications

| Component | Specification |
|-----------|--------------|
| **Total Channels** | 50,000+ |
| **Countries** | 150+ |
| **Categories** | 29 |
| **Cache Size** | Configurable (default: 100 items) |
| **Cache TTL** | 1-24 hours (configurable) |
| **Player Engine** | GStreamer / ExtePlayer3 / Auto |
| **Memory Usage** | ~50MB |
| **Load Time** | <5 seconds (cached) |
| **Stream Compatibility** | ~70% success rate |
| **Python Version** | 2.7+ / 3.x compatible |

---

## 📥 Installation

### Method 1: IPK Package (Recommended)
```bash
# Install from Telnet Console
wget -q --no-check-certificate "https://raw.githubusercontent.com/Belfagor2005/TVGarden/main/installer.sh" -O - | /bin/sh

# Install via opkg
opkg install enigma2-plugin-extensions-tvgarden

# Restart Enigma2
reboot
```

### Method 3: Plugin Manager
1. Open **Plugin Browser** on your receiver
2. Select **Download Plugins**
3. Find **TV Garden** in **Extensions** category
4. Click **Install** and restart GUI

---

## ⚙️ Configuration

### Player Settings
```ini
player = auto               # auto/gstreamer/exteplayer3
volume = 80                 # 0-100%
timeout = 10                # Connection timeout (seconds)
retries = 3                 # Connection retry attempts
```

### Cache Settings
```ini
cache_enabled = true        # Enable/disable cache
cache_ttl = 3600           # Cache time-to-live (seconds)
cache_size = 100           # Maximum cache items
auto_refresh = true        # Automatic cache refresh
```

### Display Settings
```ini
skin = auto                # auto/hd/fhd/wqhd
show_flags = true          # Show country flags
show_logos = true          # Show channel logos
items_per_page = 20        # Items per browser page
```

### Parental Control
```ini
parental_lock = false      # Enable parental control
parental_pin = 0000        # 4-digit PIN code
blocked_categories = []    # List of blocked categories
```

---

## 🎮 Usage Guide

### Navigation
- **OK Button**: Select/Play channel
- **CH+ / CH-**: Channel zapping (in player)
- **EXIT**: Return to previous screen
- **MENU**: Context menu/options
- **INFO**: Show channel information

### Main Menu Options
1. **Browse by Country** - Select from 150+ countries with flags
2. **Browse by Category** - 29 content categories
3. **Favorites** - Your saved channels (add with YELLOW button)
4. **Search** - Real-time search across all channels
5. **Settings** - Plugin configuration
6. **About** - Version info and statistics

### Player Controls
- **CHANNEL +/-**: Navigate through channel list
- **OK**: Show extended channel information
- **RED**: Toggle favorite status
- **GREEN**: Show channel list
- **YELLOW**: Show channel info
- **BLUE/EXIT**: Close player

---

## 🔧 Technical Details

### Architecture
```
TVGarden/
├── __init__.py
├── plugin.py
├── helpers.py
├── browser/
│   ├── __init__.py
│   ├── base.py
│   ├── countries.py
│   ├── categories.py
│   ├── channels.py
│   ├── favorites.py
│   └── search.py
├── player/
│   ├── __init__.py
│   └── iptv_player.py
├── utils/
│   ├── config.py
│   ├── cache.py
│   ├── settings.py
│   └── favorites.py
├── skins/
│   ├── default/
│   │   ├── skin.json
│   │   └── main.xml
│   ├── wqhd/
│   ├── fhd/
│   └── hd/
├── icons/
│   ├── plugin.png
│   ├── logo.png
│   ├── country/
│   └── category/
├── locale/
│   ├── it/
│   ├── en/
│   └── ...
├── Makefile
├── install.sh
└── README.md
```

### Data Sources
- **Primary**: [TV Garden Channel List](https://github.com/Belfagor2005/tv-garden-channel-list)
- **Format**: Compressed JSON with gzip support
- **Update Frequency**: Configurable (default: 1 hour)
- **Fallback**: Local cache with TTL expiration

### Cache System
- **Two-layer cache**: Memory + filesystem
- **Gzip compression**: Reduces bandwidth usage
- **TTL management**: Automatic expiration
- **LRU eviction**: Least Recently Used item removal
- **Size limits**: Configurable maximum items

---

## 📈 Performance Metrics

### Loading Times
- **Cold Start**: 8-12 seconds (initial cache)
- **Warm Start**: 3-5 seconds (cached data)
- **Channel Switch**: <2 seconds
- **Search Query**: <1 second (with cache)

### Resource Usage
- **Memory**: 45-60MB during playback
- **CPU**: 5-15% average load
- **Network**: ~2MB per category load
- **Storage**: 10-50MB cache size

### Success Rates
- **Stream Playback**: ~70% working streams
- **Cache Hit Rate**: 85-95% after initial load
- **Search Accuracy**: Near-instant results
- **Country Loading**: 100% metadata success

---

## 🔍 Search Features

### Search Methods
1. **Real-time Typing** - Instant results as you type
2. **Virtual Keyboard** - Full text input support
3. **Smart Filtering** - YouTube/DRM content filtered
4. **Multi-field Search** - Name, description, category

### Search Results
- **Display**: Channel name with country/category tags
- **Sorting**: Relevance + alphabetical
- **Limits**: 100 results maximum (performance)
- **Preview**: Stream URL validation before playback

---

## ⭐ Favorites System

### Features
- **Unlimited Storage** (configurable limit)
- **JSON Export/Import** - Backup and restore
- **Automatic Deduplication** - Unique channel IDs
- **Timestamp Tracking** - Recently added first
- **Search Integration** - Search within favorites

### Storage Format
```json
{
  "favorites": [
    {
      "id": "md5_hash",
      "name": "Channel Name",
      "url": "stream_url",
      "country": "Country Code",
      "category": "Category",
      "added": "timestamp"
    }
  ]
}
```

---

## 🐛 Troubleshooting

### Common Issues & Solutions

| Issue | Solution |
|-------|----------|
| **No channels loading** | Check internet connection, restart plugin |
| **Player doesn't open** | Verify GStreamer installation, check URL format |
| **Search not working** | Clear cache, check GitHub API access |
| **Memory high usage** | Reduce cache size, limit concurrent streams |
| **Slow loading** | Increase cache TTL, use wired connection |

### Debug Mode
Enable debug logging in settings or via SSH:
```bash
# Enable debug logs
echo "TVGarden DEBUG: 1" >> /tmp/enigma2.log

# Monitor logs in real-time
tail -f /tmp/enigma2.log | grep -i tvgarden
```

### Cache Management
```bash
# Clear cache manually
rm -rf /tmp/tvgarden_cache/*

# Check cache size
du -sh /tmp/tvgarden_cache/

# View cache contents
ls -la /tmp/tvgarden_cache/categories/
```

---

## 🤝 Contributing

We welcome contributions! Here's how you can help:

### Reporting Issues
1. Check existing issues on GitHub
2. Provide Enigma2 version and logs
3. Include steps to reproduce
4. Add screenshots if applicable

### Development
1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Submit a pull request

### Translation
Help translate the plugin:
1. Edit files in `locale/` directory
2. Add new language files
3. Test translation in Enigma2
4. Submit translation updates

---

## 📚 Documentation

### API Reference
- **Cache API**: `CacheManager.get_category_channels()`
- **Player API**: `TVGardenPlayer(session, service_ref, channel_list)`
- **Config API**: `PluginConfig.get(key, default)`
- **Favorites API**: `FavoritesManager.add(channel)`

### Plugin Hooks
```python
# Custom integration example
from Plugins.Extensions.TVGarden.browser import CountriesBrowser
from Plugins.Extensions.TVGarden.utils.cache import CacheManager

# Access cached data
cache = CacheManager()
channels = cache.get_category_channels('news')

# Open browser directly
self.session.open(CountriesBrowser)
```

### Skin Development
Create custom skins in `skins/your_skin/`:
```xml
<screen name="TVGardenMain" position="center,center" size="1280,720">
  <!-- Your custom layout -->
</screen>
```

---

## 📄 License

```
TV Garden Plugin for Enigma2
Copyright (C) 2025 Your Name

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program. If not, see <https://www.gnu.org/licenses/>.
```

---

## 🙏 Credits & Acknowledgments

### Core Development
- **Original Concept**: Lululla (TV Garden Project)
- **Data Source**: [Belfagor2005](https://github.com/Belfagor2005/tv-garden-channel-list)
- **Plugin Development**: Your Name/Team
- **Testing Community**: Enigma2 users worldwide

### Technologies Used
- **Enigma2 Python API** - Plugin framework
- **GStreamer** - Multimedia playback
- **Python urllib/json** - Data handling
- **GitHub API** - Dynamic category loading

### Special Thanks
- All contributors and testers
- Open source community
- Enigma2 developers

---

## 📞 Support & Contact

- **GitHub Issues**: [Report bugs/features](https://github.com/Belfagor2005/TVGarden/issues)
- **Documentation**: [Wiki/Guide](https://github.com/Belfagor2005/TVGarden/wiki)
- **Releases**: [Latest versions](https://github.com/Belfagor2005/TVGarden/releases)

---

**Enjoy streaming with TV Garden!** 📺✨

*Last Updated: 2025-12-07* | *Version: 1.0*
