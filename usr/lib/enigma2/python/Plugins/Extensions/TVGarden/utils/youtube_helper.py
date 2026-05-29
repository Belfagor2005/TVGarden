# -*- coding: utf-8 -*-

import subprocess
import re
from os.path import exists
from urllib.parse import unquote

from ..helpers import log

"""
TV Garden Plugin - Youtube scraping
Advanced scrapingg
Based on TV Garden Project
"""


def find_ytdlp():
    """Find yt-dlp executable in system"""
    paths = ["/usr/bin/yt-dlp", "/usr/local/bin/yt-dlp"]
    for path in paths:
        if exists(path):
            try:
                result = subprocess.run(
                    [path, "--version"], capture_output=True, timeout=5)
                if result.returncode == 0:
                    log.debug("yt-dlp found: %s" % path, module="YouTube")
                    return path
            except BaseException:
                pass
    log.error(
        "yt-dlp not found. Install with: opkg install yt-dlp",
        module="YouTube")
    return None


def extract_video_id(url):
    patterns = [
        r'(?:https?://)?(?:www\.)?youtube\.com/watch\?v=([^&]+)',
        r'(?:https?://)?youtu\.be/([^?]+)',
        r'(?:https?://)?(?:www\.)?youtube\.com/embed/([^/?]+)',
        r'(?:https?://)?(?:www\.)?youtube-nocookie\.com/embed/([^/?]+)',
        r'(?:https?://)?(?:www\.)?youtube\.com/v/([^/?]+)',
        r'(?:https?://)?(?:www\.)?youtube\.com/shorts/([^/?]+)',
        r'(?:https?://)?(?:www\.)?youtube\.com/live/([^/?]+)',
    ]
    try:
        decoded = unquote(url)
        for pattern in patterns:
            match = re.search(pattern, decoded, re.IGNORECASE)
            if match:
                return match.group(1)
    except Exception as e:
        log.error("Error extracting video ID: %s" % e, module="YouTube")
    return None


def get_stream_with_ytdlp(ytdlp_path, video_id):
    """Get direct stream URL using yt-dlp"""
    youtube_url = "https://www.youtube.com/watch?v=" + video_id
    format_options = [
        ["-g", "-f", "18"],
        ["-g", "-f", "best[ext=mp4]"],
        ["-g", "-f", "22/37"],
        ["-g", "-f", "best[protocol!=m3u8_native]"],
        ["-g", "-f", "best"],
    ]
    for fmt in format_options:
        cmd = [ytdlp_path] + fmt + [youtube_url]
        log.debug("Trying format: %s" % " ".join(fmt), module="YouTube")
        try:
            result = subprocess.run(
                cmd, capture_output=True, text=True, timeout=30)
            if result.returncode == 0:
                stream_url = result.stdout.strip()
                if stream_url.startswith(("http://", "https://")):
                    log.info("YouTube stream obtained: %s..." %
                             stream_url[:80], module="YouTube")
                    return stream_url
        except subprocess.TimeoutExpired:
            log.warning("Timeout for format: %s" % fmt, module="YouTube")
        except Exception as e:
            log.warning("Error with format: %s" % e, module="YouTube")
    return None


def get_youtube_stream(url):
    """Main function: given YouTube URL, return direct stream URL"""
    video_id = extract_video_id(url)
    if not video_id:
        log.error("Cannot extract video ID from %s" % url, module="YouTube")
        return None
    ytdlp = find_ytdlp()
    if not ytdlp:
        return None
    return get_stream_with_ytdlp(ytdlp, video_id)
