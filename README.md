# TV Garden Plugin for Enigma2

![](https://komarev.com/ghpvc/?username=Belfagor2005&label=Repository%20Views&color=blueviolet)
[![Python package](https://github.com/Belfagor2005/TVGarden/actions/workflows/pylint.yml/badge.svg)](https://github.com/Belfagor2005/TVGarden/actions/workflows/pylint.yml)
[![TV Garden](https://img.shields.io/badge/TVGarden-00aaff.svg)](https://github.com/Belfagor2005/tv-garden-channel-list)
[![Enigma2](https://img.shields.io/badge/Enigma2-Plugin-ff6600.svg)](https://www.enigma2.net)
[![Python](https://img.shields.io/badge/Python-2.7%2B-blue.svg)](https://www.python.org)
[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![GitHub stars](https://img.shields.io/github/stars/Belfagor2005/TVGarden?style=social)](https://github.com/Belfagor2005/TVGarden/stargazers)

**Professional IPTV Streaming Solution** for Enigma2 receivers with access to **50,000+ channels** from **150+ countries** across **29 categories**. Featuring **performance optimization**, **hardware acceleration**, and **native Enigma2 bouquet export**.

---

## 📺 Screenshots

<table>
  <tr>
    <td align="center">
      <img src="https://raw.githubusercontent.com/Belfagor2005/TVGarden/main/screen/screen1.png" height="220">
    </td>
    <td align="center">
      <img src="https://raw.githubusercontent.com/Belfagor2005/TVGarden/main/screen/screen2.png" height="220">
    </td>
    <td align="center">
      <img src="https://raw.githubusercontent.com/Belfagor2005/TVGarden/main/screen/screen3.png" height="220">
    </td>
  </tr>
  <tr>
    <td align="center">
      <img src="https://raw.githubusercontent.com/Belfagor2005/TVGarden/main/screen/screen4.png" height="220">
    </td>
    <td align="center">
      <img src="https://raw.githubusercontent.com/Belfagor2005/TVGarden/main/screen/screen5.png" height="220">
    </td>
    <td align="center">
      <img src="https://raw.githubusercontent.com/Belfagor2005/TVGarden/main/screen/screen6.png" height="220">
    </td>
  </tr>
</table>

---

## ✨ Key Features

### 🚀 Performance Optimization
- **Hardware Acceleration** - Toggle for H.264/H.265 streams
- **Buffer Size Control** - 512KB to 8MB configurable buffer
- **Smart Player Selection** - Auto, ExtePlayer3, or GStreamer
- **Connection Optimization** - Timeout & retry system

### 🌍 Global Content Access
- **150+ Countries** with national flags display
- **29 Content Categories** (News, Sports, Movies, Music, Kids, etc.)
- **50,000+ Channels** regularly updated

### ⚙️ Advanced Technology
- **Professional Configuration System** - 47+ configurable parameters
- **Smart Caching** - TTL + gzip compression + automatic refresh
- **Auto-Skin Detection** - HD/FHD/WQHD resolution support
- **File Logging System** - With rotation and size limits

### 🔄 Integration & Export
- **Enigma2 Bouquet Export** - Direct integration with channel list
- **Configurable Export** - Bouquet name prefix, max channels, auto-refresh
- **Favorites Management** - Unlimited storage with backup/restore
- **Settings Backup** - Automatic configuration backup system
- **Dual Export System** - Single-file simplicity or multi-file hierarchical performance
- **Smart Channel Splitting** - Countries with >500 channels automatically split into multiple bouquet files

### 🛡️ Reliability & Safety
- **DRM/Crash Protection** - Filtered problematic streams
- **Connection Stability** - Retry attempts with timeout handling
- **Offline Cache** - Previously viewed content available
- **Automatic Updates** - Configurable update checking

### 🔍 Enhanced User Experience
- **Channel Zapping** - CH+/CH- navigation between channels
- **Real-time Search** - Virtual keyboard across all channels
- **Performance Stats** - HW acceleration and buffer info in player
- **Multi-language** - International interface support

---

## 📊 Technical Specifications

| Component | Specification |
|-----------|--------------|
| **Total Channels** | 50,000+ |
| **Countries** | 150+ |
| **Categories** | 29 |
| **Configuration Parameters** | 47+ |
| **Player Engines** | Auto/ExtePlayer3/GStreamer |
| **Buffer Size Range** | 512KB - 8MB |
| **Cache Size** | Configurable (default: 100 items) |
| **Cache TTL** | 1-24 hours (configurable) |
| **Memory Usage** | ~50MB |
| **Load Time (cached)** | <5 seconds |
| **Stream Compatibility** | ~70% success rate |
| **Python Compatibility** | 2.7+ (Enigma2 optimized) |
| **Log File Management** | Size limits + rotation |

---

## ⚙️ Configuration System

### Player Settings
```ini
player = auto               # auto/exteplayer3/gstplayer
volume = 80                 # 0-100%
timeout = 10                # Connection timeout (seconds)
retries = 3                 # Connection retry attempts
```

### Performance Settings
```ini
use_hardware_acceleration = true  # Enable HW acceleration
buffer_size = 2048                # Buffer size in KB (512-8192)
```

### Display Settings
```ini
skin = auto                # auto/hd/fhd/wqhd
show_flags = true          # Show country flags
show_logos = true          # Show channel logos
items_per_page = 20        # Items per browser page
```

### Cache Settings
```ini
cache_enabled = true       # Enable caching
cache_ttl = 3600          # Cache TTL in seconds
cache_size = 100          # Maximum cache items
auto_refresh = true       # Automatic cache refresh
```

### Export Settings
```ini
export_enabled = true     # Enable bouquet export
bouquet_name_prefix = TVGarden  # Bouquet name prefix
max_channels_for_bouquet = 100  # Max channels per bouquet
auto_refresh_bouquet = false    # Auto-refresh bouquet
confirm_before_export = true    # Confirm before exporting
```

### Browser Settings
```ini
max_channels = 500        # Max channels per country (0=all)
default_view = countries  # countries/categories/favorites
```

### Logging Settings
```ini
log_level = INFO          # DEBUG/INFO/WARNING/ERROR/CRITICAL
log_to_file = true        # Enable file logging
log_max_size = 1048576    # Max log file size in bytes
log_backup_count = 3      # Number of backup log files
```

---

## 🎮 Usage Guide

### Navigation Controls

**Browser Controls:**
```
OK / GREEN      - Play selected channel
EXIT / RED      - Back / Exit
YELLOW          - Context menu (Remove/Export)
BLUE            - Export favorites to bouquet
MENU            - Context menu
```

**Favorites Browser:**
```
OK / GREEN      - Play selected channel
EXIT / RED      - Back / Exit
YELLOW          - Options (Remove/Info/Export)
BLUE            - Export ALL to Enigma2 bouquet
ARROWS          - Navigate channels
```

**Player Controls:**
```
CHANNEL +/-     - Zap between channels
OK              - Show channel info + performance stats
RED             - Toggle favorite
GREEN           - Show channel list
EXIT            - Close player
```

### Performance Tips
1. **Buffer Size**: 2MB-4MB for stable connections
2. **HW Acceleration**: ON for H.264/H.265 streams
3. **Connection Timeout**: 10-15 seconds optimal
4. **Max Channels per Country**: 250-500 for faster loading
5. **Cache TTL**: 4-8 hours for balance between freshness and performance

### Bouquet Export Workflow
1. Add channels to favorites using YELLOW button
2. Navigate to Favorites browser
3. Press BLUE button to export all favorites
4. Configure export options (name, max channels)
5. Restart Enigma2 to see bouquet in channel list
6. Access at: `/etc/enigma2/userbouquet.tvgarden_*.tv`

---

## 📥 Installation

### Method 1: IPK Package (Recommended)
```bash
# Download and install via script
wget -q --no-check-certificate "https://raw.githubusercontent.com/Belfagor2005/TVGarden/main/installer.sh" -O - | /bin/sh

# Or install via opkg
opkg update
opkg install enigma2-plugin-extensions-tvgarden

# Restart Enigma2
reboot
```

### Method 2: Manual Installation
```bash
# Clone repository
git clone https://github.com/Belfagor2005/TVGarden.git
cd TVGarden

# Copy to plugins directory
cp -r plugin/ /usr/lib/enigma2/python/Plugins/Extensions/TVGarden/

# Restart Enigma2
reboot
```

---

## 🔧 Technical Architecture

### File Structure
```
TVGarden/
├── __init__.py
├── plugin.py
├── helpers.py
├── browser/
│   ├── __init__.py
│   ├── about.py
│   ├── base.py
│   ├── categories.py
│   ├── channels.py
│   ├── countries.py
│   ├── favorites.py
│   └── search.py
├── player/
│   ├── __init__.py
│   └── iptv_player.py
├── utils/
│   ├── __init__.py
│   ├── cache.py
│   ├── config.py
│   ├── favorites.py
│   ├── settings.py
│   ├── update_manager.py
│   └── updater.py
├── skins/
│   ├── wqhd/
│   ├── fhd/
│   └── hd/
├── icons/
│   ├── plugin.png
│   ├── logo.png
│   ├── redbutton.png
│   ├── greenbutton.png
│   ├── yellowbutton.png
│   ├── bluebutton.png
│   ├── kofi.png
│   └── paypal.png
├── locale/
│   ├── it/
│   ├── en/
│   └── ...
├── install.sh
└── README.md
```

### Performance Features Implementation
- **Hardware Acceleration**: Automatic detection for H.264/H.265 streams
- **Buffer Management**: Configurable buffer size applied to service reference
- **Player Optimization**: Performance settings integrated into player initialization
- **Configuration Validation**: All 47 parameters validated and sanitized

---

## 📈 Performance Metrics

### Loading Performance
- **Cold Start**: 8-12 seconds (initial cache population)
- **Warm Start**: 3-5 seconds (cached data available)
- **Channel Switch**: <2 seconds
- **Search Results**: <1 second

### Resource Utilization
- **Memory Usage**: 45-60MB during active playback
- **CPU Load**: 5-15% average with HW acceleration
- **Network Bandwidth**: ~2MB per category load
- **Cache Efficiency**: 85-95% hit rate after initial load

### Hardware Acceleration Support
- **Formats Supported**: MP4, TS, MKV, AVI containers
- **Codecs Supported**: H.264, H.265, MPEG-2, MPEG-4
- **Auto-detection**: Based on stream URL analysis
- **Fallback System**: Automatic fallback to software decoding

---

## 🔍 Search System

### Features
- **Real-time Typing** - Instant results as you type
- **Virtual Keyboard** - Full text input support
- **Smart Filtering** - YouTube/DRM content automatically filtered
- **Multi-field Search** - Searches name, description, and category
- **Performance Optimized** - 100 result limit for speed

### Usage
1. Select "Search" from main menu
2. Use virtual keyboard to enter search terms
3. Results appear instantly with country/category tags
4. Select channel to play or add to favorites

---

## ⭐ Favorites & Export System

### Features
- **Unlimited Storage** (configurable maximum)
- **JSON Backup/Restore** - Full favorites backup
- **Bouquet Export** - Native Enigma2 integration
- **Timestamp Tracking** - Recently added first display
- **Duplicate Prevention** - Automatic deduplication
- **Export Configuration** - Customizable bouquet settings

### Storage Format
```json
{
  "favorites": [
    {
      "id": "unique_hash",
      "name": "Channel Name",
      "url": "stream_url",
      "country": "Country Code",
      "category": "Category",
      "added": "2025-12-13T14:30:00Z"
    }
  ]
}
```

### Bouquet Export Options
- **Name Prefix**: Customize bouquet name (default: TVGarden)
- **Max Channels**: Limit channels per bouquet (50-1000)
- **Auto-refresh**: Automatically update bouquet on changes
- **Confirmation**: Prompt before exporting for safety

---

## 🐛 Troubleshooting & Debugging

### Common Issues

| Issue | Solution |
|-------|----------|
| **Channels not loading** | Check internet, clear cache, restart plugin |
| **Player won't start** | Verify GStreamer/ExtePlayer3 installation |
| **Search not working** | Clear cache, check GitHub API access |
| **High memory usage** | Reduce cache size, limit concurrent streams |
| **Slow performance** | Enable HW acceleration, adjust buffer size |

### Debug Mode
Enable in settings or via console:
```bash
# View real-time logs
tail -f /tmp/enigma2.log | grep -i tvgarden

# Enable debug logging
echo "DEBUG: 1" > /tmp/tvgarden_debug
```

### Cache Management
```bash
# Clear cache manually
rm -rf /tmp/tvgarden_cache/*

# Check cache statistics
ls -la /tmp/tvgarden_cache/

# Monitor cache usage
du -sh /tmp/tvgarden_cache/
```

### Performance Diagnostics
1. Check HW acceleration status in channel info (OK button)
2. Monitor buffer usage in player statistics
3. Adjust buffer size based on connection stability
4. Test different player engines (Auto/ExtePlayer3/GStreamer)

---

## 🤝 Contributing

We welcome contributions from the community!

### How to Contribute
1. **Report Issues** - Use GitHub Issues with logs and steps to reproduce
2. **Submit Features** - Create detailed feature requests
3. **Code Contributions** - Fork repository and submit pull requests
4. **Translation Help** - Add/update language files in `locale/` directory

### Development Setup
```bash
# Clone repository
git clone https://github.com/Belfagor2005/TVGarden.git
cd TVGarden

# Set up development environment
pip install -r requirements.txt

# Run tests
python -m pytest tests/
```

### Translation Guidelines
1. Edit files in `locale/{language}/LC_MESSAGES/`
2. Test translations in Enigma2 environment
3. Submit pull request with updated language files

---

## 📚 API & Integration

### Plugin Hooks
```python
# Access TV Garden functionality from other plugins
from Plugins.Extensions.TVGarden.utils.config import get_config
from Plugins.Extensions.TVGarden.player.iptv_player import TVGardenPlayer

# Get configuration
config = get_config()
player_type = config.get("player", "auto")

# Open player with custom channel list
channel_list = [...]
self.session.open(TVGardenPlayer, channel_list=channel_list)
```

### Configuration API
```python
# Access and modify configuration
config = get_config()

# Get setting
buffer_size = config.get("buffer_size", 2048)

# Update setting
config.set("buffer_size", 4096)
config.save_config()
```

### Cache API
```python
from Plugins.Extensions.TVGarden.utils.cache import CacheManager

# Access cache system
cache = CacheManager()
channels = cache.get_category_channels('news', force_refresh=False)
```

---

## 📄 License

```
TV Garden Plugin for Enigma2
Copyright (C) 2025 TV Garden Development Team

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
- **Data Source**: [Belfagor2005 TV Garden Channel List](https://github.com/Belfagor2005/tv-garden-channel-list)
- **Plugin Development**: TV Garden Development Team
- **Performance Optimization**: Recent development cycle
- **Testing & Feedback**: Enigma2 community worldwide

### Technical Credits
- **Enigma2 Framework** - Plugin infrastructure
- **GStreamer/ExtePlayer3** - Multimedia playback engines
- **Python Community** - Libraries and tools
- **Open Source Projects** - Inspiration and code sharing

### Special Thanks
- All contributors and code reviewers
- Beta testers and bug reporters
- Documentation contributors
- Community translators

---

## 📞 Support & Resources

### Documentation
- **User Guide**: Complete usage instructions
- **Technical Docs**: API reference and integration guide
- **Troubleshooting**: Common issues and solutions

### Support Channels
- **GitHub Issues**: [Report bugs/request features](https://github.com/Belfagor2005/TVGarden/issues)
- **Releases**: [Latest versions and changelog](https://github.com/Belfagor2005/TVGarden/releases)
- **Wiki**: [Documentation and guides](https://github.com/Belfagor2005/TVGarden/wiki)

### Community
- Join discussions with other Enigma2 users
- Share configuration tips and performance optimizations
- Contribute to plugin improvement

---

**Enjoy optimized streaming with TV Garden!** 📺⚡

*Last Updated: 2025-12-13* | *Version: 1.4*

### What's New in v1.5:
- ✅ **Hardware Acceleration** - Configurable HW acceleration for H.264/H.265
- ✅ **Buffer Size Control** - 512KB to 8MB configurable buffer
- ✅ **Performance Optimization** - 47+ configuration parameters
- ✅ **Enhanced Settings UI** - Organized sections with dynamic display
- ✅ **Professional Configuration** - Complete settings validation system
- ✅ **Log File Management** - Size limits and rotation
- ✅ **Player Integration** - Performance settings applied during playback
- ✅ **About Screen Update** - Complete feature listing
- ✅ **Dual Bouquet Export System** - Single-file simplicity or multi-file hierarchical performance
- ✅ **Smart Channel Splitting** - Countries with >500 channels automatically split into multiple bouquet files
- ✅ **Hierarchical Bouquet Architecture** - Parent container with country-specific sub-bouquets
- ✅ **Enhanced Export Menu** - New options for single/multi-file export in Favorites browser
- ✅ **Complete Bouquet Management** - Tag-based removal of all bouquet files (.tvgarden_*)
- ✅ **Performance-Optimized Structure** - Max 500 channels per file ensures fast Enigma2 loading
