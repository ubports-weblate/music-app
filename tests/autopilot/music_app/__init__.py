# -*- Mode: Python; coding: utf-8; indent-tabs-mode: nil; tab-width: 4 -*-
# Copyright 2013, 2014 Canonical
#
# This program is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License version 3, as published
# by the Free Software Foundation.

"""music-app tests and emulators - top level package."""
from ubuntuuitoolkit import MainView, UbuntuUIToolkitCustomProxyObjectBase


class MusicAppException(Exception):
    """Exception raised when there's an error in the Music App."""


def click_object(func):
    """Wrapper which clicks the returned object"""
    def func_wrapper(self, *args, **kwargs):
        return self.pointing_device.click_object(func(self, *args, **kwargs))

    return func_wrapper


def ensure_now_playing_full(func):
    """Wrapper which ensures the now playing is full before clicking"""
    def func_wrapper(self, *args, **kwargs):
        if self.isListView:
            self.click_toggle_view()

        return func(self, *args, **kwargs)

    return func_wrapper


def ensure_now_playing_list(func):
    """Wrapper which ensures the now playing is list before clicking"""
    def func_wrapper(self, *args, **kwargs):
        if not self.isListView:
            self.click_toggle_view()

        return func(self, *args, **kwargs)

    return func_wrapper


class MusicApp(object):
    """Autopilot helper object for the Music application."""

    def __init__(self, app_proxy):
        self.app = app_proxy
        self.main_view = self.app.wait_select_single(MainView)
        self.player = self.app.select_single(Player, objectName='player')

    def get_add_to_playlist_page(self):
        return self.app.wait_select_single(MusicAddToPlaylist,
                                           objectName="addToPlaylistPage")

    def get_albums_page(self):
        self.main_view.switch_to_tab('albumsTab')

        return self.main_view.wait_select_single(
            Page11, objectName='albumsPage')

    def get_albums_artist_page(self):
        return self.main_view.wait_select_single(
            AlbumsPage, objectName='albumsArtistPage')

    def get_artists_page(self):
        self.main_view.switch_to_tab('artistsTab')

        return self.main_view.wait_select_single(
            Page11, objectName='artistsPage')

    def get_new_playlist_dialog(self):
        return self.main_view.wait_select_single(
            Dialog, objectName="dialogNewPlaylist")

    def get_now_playing_page(self):
        return self.app.wait_select_single(MusicNowPlaying,
                                           objectName="nowPlayingPage")

    def get_playlists_page(self):
        self.main_view.switch_to_tab('playlistsTab')

        return self.main_view.wait_select_single(
            MusicPlaylists, objectName='playlistsPage')

    def get_queue_count(self):
        return self.main_view.select_single("LibraryListModel",
                                            objectName="trackQueue").count

    def get_songs_page(self):
        return self.app.wait_select_single(SongsPage, objectName="songsPage")

    def get_toolbar(self):
        return self.app.wait_select_single(MusicToolbar,
                                           objectName="musicToolbarObject")

    def get_tracks_page(self):
        """Open the Tracks tab.

        :return: The autopilot custom proxy object for the TracksPage.

        """
        self.main_view.switch_to_tab('tracksTab')

        return self.main_view.wait_select_single(
            Page11, objectName='tracksPage')

    @property
    def loaded(self):
        return (not self.main_view.select_single("ActivityIndicator",
                objectName="LoadingSpinner").running and
                self.main_view.select_single("*", "allSongsModel").populated)

    def populate_queue(self):
        tracksPage = self.get_tracks_page()  # switch to track tab

        # get and click to play first track
        track = tracksPage.get_track(0)
        self.app.pointing_device.click_object(track)

        tracksPage.visible.wait_for(False)  # wait until page has hidden

        # TODO: when using bottom edge wait for .isReady on tracksPage

        # wait for now playing page to be visible
        self.get_now_playing_page().visible.wait_for(True)


class Page(UbuntuUIToolkitCustomProxyObjectBase):
    """Autopilot helper for Pages."""
    def __init__(self, *args):
        super(Page, self).__init__(*args)
        # XXX we need a better way to keep reference to the main view.
        # --elopio - 2014-01-31
        self.main_view = self.get_root_instance().select_single(MainView)


class MusicPage(Page):
    def __init__(self, *args):
        super(Page, self).__init__(*args)


class MusicAlbums(MusicPage):
    """ Autopilot helper for the albums page """
    def __init__(self, *args):
        super(MusicPage, self).__init__(*args)

        self.visible.wait_for(True)

    @click_object
    def click_album(self, i):
        return (self.wait_select_single("*",
                objectName="albumsPageGridItem" + str(i)))


class MusicArtists(MusicPage):
    """ Autopilot helper for the artists page """
    def __init__(self, *args):
        super(MusicPage, self).__init__(*args)

        self.visible.wait_for(True)

    @click_object
    def click_artist(self, i):
        return (self.wait_select_single("Card",
                objectName="artistsPageGridItem" + str(i)))


class MusicTracks(MusicPage):
    """ Autopilot helper for the tracks page """
    def __init__(self, *args):
        super(MusicPage, self).__init__(*args)

        self.visible.wait_for(True)

    def get_track(self, i):
        return (self.wait_select_single(ListItemWithActions,
                objectName="tracksPageListItem" + str(i)))


class MusicPlaylists(MusicPage):
    """ Autopilot helper for the playlists page """
    def __init__(self, *args):
        super(MusicPage, self).__init__(*args)

        self.visible.wait_for(True)

    def get_count(self):
        return self.wait_select_single(
            "CardView", objectName="playlistsCardView").count


class MusicaddtoPlaylist(MusicPage):
    """ Autopilot helper for add to playlist page """
    def __init__(self, *args):
        super(MusicPage, self).__init__(*args)

        self.visible.wait_for(True)

    def click_new_playlist_action(self):
        self.main_view.get_header().click_action_button("newPlaylistButton")

    @click_object
    def click_playlist(self, i):
        return self.get_playlist(i)

    def get_count(self):  # careful not to conflict until Page11 is fixed
        return self.wait_select_single(
            "CardView", objectName="addToPlaylistCardView").count

    def get_playlist(self, i):
        return (self.wait_select_single("Card",
                objectName="addToPlaylistCardItem" + str(i)))


class Page11(MusicAlbums, MusicArtists, MusicTracks):
    """
    FIXME: Represents MusicTracks MusicArtists MusicAlbums
    due to bug 1341671 and bug 1337004 they all appear as Page11
    Therefore this class 'contains' all of them for now
    Once the bugs are fixed Page11 should be swapped for MusicTracks etc
    """
    def __init__(self, *args):
        super(MusicAlbums, self).__init__(*args)
        super(MusicArtists, self).__init__(*args)
        super(MusicTracks, self).__init__(*args)


class Player(UbuntuUIToolkitCustomProxyObjectBase):
    """Autopilot helper for Player"""


class MusicNowPlaying(MusicPage):
    """ Autopilot helper for now playing page """
    def __init__(self, *args):
        super(MusicPage, self).__init__(*args)

        root = self.get_root_instance()
        self.player = root.select_single(Player, objectName="player")

        self.visible.wait_for(True)

    @ensure_now_playing_full
    @click_object
    def click_forward_button(self):
        return self.wait_select_single("*", objectName="forwardShape")

    @ensure_now_playing_full
    @click_object
    def click_play_button(self):
        return self.wait_select_single("*", objectName="playShape")

    @ensure_now_playing_full
    @click_object
    def click_previous_button(self):
        return self.wait_select_single("*", objectName="previousShape")

    @ensure_now_playing_full
    @click_object
    def click_repeat_button(self):
        return self.wait_select_single("*", objectName="repeatShape")

    @ensure_now_playing_full
    @click_object
    def click_shuffle_button(self):
        return self.wait_select_single("*", objectName="shuffleShape")

    def click_toggle_view(self):
        self.main_view.get_header().click_action_button("toggleView")

    def get_count(self):
        return self.select_single("QQuickListView",
                                  objectName="nowPlayingQueueList").count

    def go_back(self):
        """Use custom back button to go back"""
        self.main_view.get_header().click_custom_back_button()

    @ensure_now_playing_list
    def get_track(self, i):
        return (self.wait_select_single(ListItemWithActions,
                objectName="nowPlayingListItem" + str(i)))

    @ensure_now_playing_full
    def seek_to(self, percentage):
        progress_bar = self.wait_select_single(
            "*", objectName="progressSliderShape")

        x1, y1, width, height = progress_bar.globalRect
        y1 += height // 2

        x2 = x1 + int(width * percentage / 100)

        self.pointing_device.drag(x1, y1, x2, y1)

    def set_repeat(self, state):
        if self.player.repeat != state:
            self.click_repeat_button()

        self.player.repeat.wait_for(state)

    def set_shuffle(self, state):
        if self.player.shuffle != state:
            self.click_shuffle_button()

        self.player.shuffle.wait_for(state)


class AlbumsPage(MusicPage):
    """ Autopilot helper for the albums page """
    def __init__(self, *args):
        super(MusicPage, self).__init__(*args)

        self.visible.wait_for(True)

    @click_object
    def click_artist(self, i):
        return self.wait_select_single("Card",
                                       objectName="albumsPageGridItem"
                                       + str(i))

    def get_artist(self):
        return self.wait_select_single("Label", objectName="artistLabel").text


class SongsPage(MusicPage):
    """ Autopilot helper for the songs page """
    def __init__(self, *args):
        super(MusicPage, self).__init__(*args)

        self.visible.wait_for(True)

    @click_object
    def click_track(self, i):
        return self.get_track(i)

    def get_header_artist_label(self):
        return self.wait_select_single("Label",
                                       objectName="songsPageHeaderAlbumArtist")

    def get_track(self, i):
        return (self.wait_select_single(ListItemWithActions,
                objectName="songsPageListItem" + str(i)))


class MusicToolbar(UbuntuUIToolkitCustomProxyObjectBase):
    """Autopilot helper for the toolbar"""
    def __init__(self, *args):
        super(MusicToolbar, self).__init__(*args)

    @click_object
    def click_play_button(self):
        return self.wait_select_single("*", objectName="playShape")

    @click_object
    def click_jump_to_now_playing(self):
        return self.wait_select_single("*", objectName="jumpNowPlaying")

    def switch_to_now_playing(self):
        self.click_jump_to_now_playing()

        root = self.get_root_instance()
        now_playing_page = root.wait_select_single(MusicNowPlaying,
                                                   objectName="nowPlayingPage")

        now_playing_page.visible.wait_for(True)


class ListItemWithActions(UbuntuUIToolkitCustomProxyObjectBase):
    @click_object
    def click_add_to_playlist_action(self):
        return self.wait_select_single(objectName="addToPlaylistAction")

    @click_object
    def click_add_to_queue_action(self):
        return self.wait_select_single(objectName="addToQueueAction")

    @click_object
    def confirm_removal(self):
        return self.wait_select_single(objectName="swipeDeleteAction")

    def get_label_text(self, name):
        return self.wait_select_single(objectName=name).text

    def swipe_reveal_actions(self):
        x, y, width, height = self.globalRect
        start_x = x + (width * 0.8)
        stop_x = x + (width * 0.2)
        start_y = stop_y = y + (height // 2)

        self.pointing_device.drag(start_x, start_y, stop_x, stop_y)

        self.swipping.wait_for(False)

    def swipe_to_delete(self):
        x, y, width, height = self.globalRect
        start_x = x + (width * 0.2)
        stop_x = x + (width * 0.8)
        start_y = stop_y = y + (height // 2)

        self.pointing_device.drag(start_x, start_y, stop_x, stop_y)

        self.swipping.wait_for(False)


class Dialog(UbuntuUIToolkitCustomProxyObjectBase):
    @click_object
    def click_new_playlist_dialog_create_button(self):
        return self.wait_select_single(
            "Button", objectName="newPlaylistDialogCreateButton")

    def type_new_playlist_dialog_name(self, text):
        self.wait_select_single(
            "TextField", objectName="playlistNameTextField").write(text)


class MainView(MainView):
    """Autopilot custom proxy object for the MainView."""
    retry_delay = 0.2

    def __init__(self, *args):
        super(MainView, self).__init__(*args)
        self.visible.wait_for(True)

        # wait for activity indicator to stop spinning
        spinner = self.wait_select_single("ActivityIndicator",
                                          objectName="LoadingSpinner")
        spinner.running.wait_for(False)
