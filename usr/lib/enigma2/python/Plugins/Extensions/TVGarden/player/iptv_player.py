#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
TV Garden Plugin - IPTV Player
Advanced player with channel zapping
Based on TV Garden Project
"""

from enigma import (
    eServiceReference,
    iPlayableService,
    eTimer,
    # ePicLoad,
    # loadPNG,
)
from Components.ActionMap import ActionMap
from Components.ServiceEventTracker import ServiceEventTracker, InfoBarBase

from Screens.MessageBox import MessageBox
from Screens.Screen import Screen
from Screens.InfoBarGenerics import (
    # InfoBarSubtitleSupport,
    # InfoBarMenu,
    InfoBarSeek,
    InfoBarAudioSelection,
    InfoBarNotifications,
)

# Local imports
from ..helpers import log
# from ..base import BaseBrowser
# from ..channels import ChannelsBrowser
# from ..utils.cache import CacheManager


class TvInfoBarShowHide():
    """ InfoBar show/hide control, accepts toggleShow and hide actions, might start
    fancy animations. """
    STATE_HIDDEN = 0
    STATE_HIDING = 1
    STATE_SHOWING = 2
    STATE_SHOWN = 3
    FLAG_CENTER_DVB_SUBS = 2048
    skipToggleShow = False

    def __init__(self):
        self["ShowHideActions"] = ActionMap(
            ["InfobarShowHideActions"],
            {
                "toggleShow": self.OkPressed,
                "hide": self.hide
            },
            0
        )
        self.__event_tracker = ServiceEventTracker(
            screen=self, eventmap={
                iPlayableService.evStart: self.serviceStarted})
        self.__state = self.STATE_SHOWN
        self.__locked = 0
        self.hideTimer = eTimer()
        try:
            self.hideTimer_conn = self.hideTimer.timeout.connect(
                self.doTimerHide)
        except BaseException:
            self.hideTimer.callback.append(self.doTimerHide)
        self.hideTimer.start(3000, True)
        self.onShow.append(self.__onShow)
        self.onHide.append(self.__onHide)

    def OkPressed(self):
        self.toggleShow()

    def __onShow(self):
        self.__state = self.STATE_SHOWN
        self.startHideTimer()

    def __onHide(self):
        self.__state = self.STATE_HIDDEN

    def serviceStarted(self):
        if self.execing:
            self.doShow()

    def startHideTimer(self):
        if self.__state == self.STATE_SHOWN and not self.__locked:
            self.hideTimer.stop()
            self.hideTimer.start(3000, True)
        elif hasattr(self, "pvrStateDialog"):
            self.hideTimer.stop()
        self.skipToggleShow = False

    def doShow(self):
        self.hideTimer.stop()
        self.show()
        self.startHideTimer()

    def doTimerHide(self):
        self.hideTimer.stop()
        if self.__state == self.STATE_SHOWN:
            self.hide()

    def toggleShow(self):
        if self.skipToggleShow:
            self.skipToggleShow = False
            return
        if self.__state == self.STATE_HIDDEN:
            self.show()
            self.hideTimer.stop()
        else:
            self.hide()
            self.startHideTimer()

    def lockShow(self):
        try:
            self.__locked += 1
        except BaseException:
            self.__locked = 0
        if self.execing:
            self.show()
            self.hideTimer.stop()
            self.skipToggleShow = False

    def unlockShow(self):
        try:
            self.__locked -= 1
        except BaseException:
            self.__locked = 0
        if self.__locked < 0:
            self.__locked = 0
        if self.execing:
            self.startHideTimer()


class TVGardenPlayer(InfoBarBase, InfoBarSeek, InfoBarAudioSelection, InfoBarNotifications, TvInfoBarShowHide, Screen):
    STATE_IDLE = 0
    STATE_PLAYING = 1
    STATE_PAUSED = 2
    ENABLE_RESUME_SUPPORT = True

    def __init__(self, session, service, channel_list=None, current_index=0):
        Screen.__init__(self, session)
        self.session = session
        self.skinName = 'MoviePlayer'

        InfoBarBase.__init__(self)
        InfoBarSeek.__init__(self)
        InfoBarAudioSelection.__init__(self)
        InfoBarNotifications.__init__(self)
        TvInfoBarShowHide.__init__(self)

        self.channel_list = channel_list if channel_list else []
        self.current_index = current_index
        self.itemscount = len(self.channel_list)

        log.debug("INIT: Got %d channels, starting at index %d" % (self.itemscount, self.current_index), module="Player")
        if self.channel_list:
            current_ch = self.channel_list[self.current_index]
            log.debug("Current channel: %s" % current_ch.get('name'), module="Player")
            log.debug("Current URL: %s" % (current_ch.get('stream_url') or current_ch.get('url')), module="Player")

        self.srefInit = self.session.nav.getCurrentlyPlayingServiceReference()
        self['actions'] = ActionMap(
            [
                'MoviePlayerActions',
                'MovieSelectionActions',
                'MediaPlayerActions',
                'EPGSelectActions',
                'OkCancelActions',
                'InfobarShowHideActions',
                'InfobarActions',
                'DirectionActions',
                'InfobarSeekActions'
            ],
            {
                "stop": self.leave_player,
                "cancel": self.leave_player,
                "channelDown": self.previous_channel,
                "channelUp": self.next_channel,
                "down": self.previous_channel,
                "up": self.next_channel,
                "back": self.leave_player,
                "info": self.show_channel_info,
            },
            -1
        )

        self.onFirstExecBegin.append(self.start_stream)
        self.onClose.append(self.cleanup)

    def start_stream(self):
        """Start playing the current channel with error handling"""
        if not self.channel_list:
            log.error("No channel list!", module="Player")
            return

        current_channel = self.channel_list[self.current_index]
        stream_url = current_channel.get('stream_url') or current_channel.get('url')
        channel_name = current_channel.get('name', 'TV Garden')

        if not stream_url:
            log.error("No stream URL for channel %d" % self.current_index, module="Player")
            return

        log.info("Playing channel %d: %s" % (self.current_index, channel_name), module="Player")
        log.debug("URL: %s..." % stream_url[:80], module="Player")

        # Check if the URL may be problematic
        if self.is_problematic_stream(stream_url):
            log.warning("Stream might be problematic", module="Player")
            self.show_stream_warning(channel_name)

        try:
            # Create service reference
            url_encoded = stream_url.replace(":", "%3a")
            name_encoded = channel_name.replace(":", "%3a")

            ref_str = (
                "4097:0:1:0:0:0:0:0:0:0:"
                + url_encoded
                + ":"
                + name_encoded
            )

            log.debug("ServiceRef string: " + ref_str, module="Player")

            sref = eServiceReference(ref_str)
            sref.setName(channel_name)

            # Start service with timeout
            self.session.nav.playService(sref)
            self.current_service = sref

            # Start a timer to check whether the stream plays correctly
            self.start_stream_check_timer()

        except Exception as error:
            log.error("ERROR starting stream: " + str(error), module="Player")
            self.show_error_message("Cannot play: " + channel_name)

    def is_problematic_stream(self, url):
        """Check whether a stream URL may cause playback issues."""
        url_lower = url.lower()

        # Warning signs that usually indicate problematic streams
        warning_signs = [
            "moveonjoy.com",   # Site known to cause crashes
            "akamaihd.net",    # Often uses DRM
            "drm",
            "widevine",
            "playready",
            ".mpd",
            "/dash/",
            "encryption",
            "key",
            "license"
        ]

        return any(sign in url_lower for sign in warning_signs)

    def show_stream_warning(self, channel_name):
        """Show warning about potentially problematic stream"""
        message = f"Warning: {channel_name}\n\nThis stream might use encryption or DRM that is not supported by your receiver.\n\nTry another channel."
        self.session.open(MessageBox, message, MessageBox.TYPE_WARNING)

    def start_stream_check_timer(self):
        """Start timer to check if stream is actually playing"""
        self.stream_check_timer = eTimer()
        self.stream_check_timer.callback.append(self.check_stream_status)
        self.stream_check_timer.start(3000, True)  # Check after 3 seconds

    def check_stream_status(self):
        """Check whether the stream is actually playing."""
        try:
            service = self.session.nav.getCurrentService()
            if service:
                info = service.info()
                if info:
                    # If we can retrieve info, the stream is likely working
                    log.info("Stream appears to be playing correctly", module="Player")
                    return
        except Exception:
            pass

        log.warning("Stream might have failed to start", module="Player")

    def next_channel(self):
        """Switch to the next channel with audio fix"""
        if self.itemscount <= 1:
            return

        # Calculate the new index
        new_index = (self.current_index + 1) % self.itemscount
        log.debug("Next channel: %d -> %d" % (self.current_index, new_index), module="Player")

        # Get new channel info
        new_channel = self.channel_list[new_index]
        stream_url = new_channel.get('stream_url') or new_channel.get('url')
        channel_name = new_channel.get('name', 'TV Garden')

        if not stream_url:
            log.error("No stream URL for channel %d" % new_index, module="Player")
            return

        # Create new service reference
        url_encoded = stream_url.replace(":", "%3a")
        name_encoded = channel_name.replace(":", "%3a")
        ref_str = "4097:0:1:0:0:0:0:0:0:0:%s:%s" % (url_encoded, name_encoded)

        log.info("Switching to: %s" % channel_name, module="Player")

        # Play new service
        sref = eServiceReference(ref_str)
        sref.setName(channel_name)
        self.session.nav.playService(sref)

        # Update current index
        self.current_index = new_index

        # Reset audio tracks after 1 second
        self.audio_reset_timer = eTimer()
        self.audio_reset_timer.callback.append(self.reset_audio_tracks)
        self.audio_reset_timer.start(1000, True)  # 1 second

    def previous_channel(self):
        """Switch to the previous channel with audio fix"""
        if self.itemscount <= 1:
            return

        # Calculate new index
        new_index = (self.current_index - 1) % self.itemscount
        log.debug("Previous channel: %d -> %d" % (self.current_index, new_index), module="Player")

        # Get new channel info
        new_channel = self.channel_list[new_index]
        stream_url = new_channel.get('stream_url') or new_channel.get('url')
        channel_name = new_channel.get('name', 'TV Garden')

        if not stream_url:
            log.error("No stream URL for channel %d" % new_index, module="Player")
            return

        # Create new service reference
        url_encoded = stream_url.replace(":", "%3a")
        name_encoded = channel_name.replace(":", "%3a")
        ref_str = "4097:0:1:0:0:0:0:0:0:0:%s:%s" % (url_encoded, name_encoded)

        log.info("Switching to: %s" % channel_name, module="Player")

        # Play new service
        sref = eServiceReference(ref_str)
        sref.setName(channel_name)
        self.session.nav.playService(sref)

        # Update current index
        self.current_index = new_index

        # Reset audio tracks after 1 second
        self.audio_reset_timer = eTimer()
        self.audio_reset_timer.callback.append(self.reset_audio_tracks)
        self.audio_reset_timer.start(1000, True)  # 1 second

    def reset_audio_tracks(self):
        """Reset audio tracks when changing channels"""
        log.debug("Resetting audio tracks...", module="Player")

        try:
            service = self.session.nav.getCurrentService()
            if service:
                audio = service.audioTracks()
                if audio:
                    # Get current track info
                    current_track = audio.getCurrentTrack()
                    num_tracks = audio.getNumberOfTracks()

                    log.debug("Audio tracks: %d, current: %d" % (num_tracks, current_track), module="Player")

                    if num_tracks > 0:
                        # Force reset to track 0
                        audio.selectTrack(0)

                        # Get track info for debugging
                        track_info = audio.getTrackInfo(0)
                        if track_info:
                            description = track_info.getDescription()
                            language = track_info.getLanguage()
                            log.debug("Selected track 0: %s (%s)" % (description, language), module="Player")

                        # Force update audio settings
                        # self.audioSelection()

                        log.debug("Audio tracks reset successfully", module="Player")
                    else:
                        log.debug("No audio tracks available", module="Player")
        except Exception as e:
            log.error("Error resetting audio: %s" % e, module="Player")

    def show_channel_info(self):
        """Display information for the current channel."""
        if self.channel_list and 0 <= self.current_index < len(self.channel_list):
            channel = self.channel_list[self.current_index]
            info = f"Canale: {channel.get('name', 'N/A')}\n"
            info += f"Indice: {self.current_index + 1}/{self.itemscount}\n"

            if channel.get('country'):
                info += f"Paese: {channel.get('country')}\n"
            if channel.get('language'):
                info += f"Lingua: {channel.get('language')}\n"

            url = channel.get('stream_url') or channel.get('url', 'N/A')
            info += f"URL: {url[:60]}..." if len(url) > 60 else f"URL: {url}"

            self.session.open(MessageBox, info, MessageBox.TYPE_INFO)

    def cleanup(self):
        """Clean up resources."""
        if hasattr(self, 'refreshTimer'):
            self.refreshTimer.stop()

        # Restore initial service
        if self.srefInit:
            self.session.nav.stopService()
            self.session.nav.playService(self.srefInit)

    def leave_player(self):
        """Exit the player."""
        self.cleanup()
        self.close()
