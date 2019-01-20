from unittest.mock import Mock, patch

import pytest

from tomate.constant import State
from tomate.event import Events
from tomate.graph import graph
from tomate.session import Session
from tomate.timer import TimerPayload
from tomate.view import TrayIcon


def setup_function(function):
    graph.providers.clear()

    graph.register_instance("tomate.session", Mock(spec=Session))
    graph.register_instance("trayicon.menu", Mock())

    Events.Session.receivers.clear()
    Events.Timer.receivers.clear()


@pytest.fixture
def plugin(mocker):
    with mocker.patch("statusicon_plugin.Gtk.StatusIcon"):
        from statusicon_plugin import StatusIconPlugin

        return StatusIconPlugin()


@pytest.fixture
def session():
    return graph.get("tomate.session")


def test_should_update_icon_when_timer_changes(plugin):
    # given
    plugin.activate()
    payload = TimerPayload(time_left=5, duration=10)

    # when
    Events.Timer.send(State.changed, payload=payload)

    # then
    plugin.widget.set_from_icon_name.assert_called_with("tomate-50")


def test_should_show_widget_when_session_starts(plugin):
    # given
    plugin.activate()
    plugin.widget.reset_mock()

    # when
    Events.Session.send(State.started)

    # then
    plugin.widget.set_visible.assert_called_once_with(True)


def test_should_hide_widget_when_session_ends(plugin):
    for event_type in [State.finished, State.stopped]:
        # given
        plugin.activate()
        plugin.widget.reset_mock()

        # when
        Events.Session.send(event_type)

        # then
        plugin.widget.set_visible.assert_called_once_with(False)
        plugin.widget.set_from_icon_name("tomate-idle")


class TestActivePlugin:
    def setup_method(self, method):
        setup_function(method)

    def test_should_register_tray_icon_provider(self, plugin):
        plugin.activate()

        assert TrayIcon in graph.providers.keys()
        assert graph.get(TrayIcon) == plugin

    def test_should_show_menu_when_session_is_running(self, session, plugin):
        session.is_running.return_value = True

        plugin.activate()

        plugin.widget.set_visible.assert_called_once_with(True)

    def test_should_hide_menu_when_session_is_not_running(self, session, plugin):
        session.is_running.return_value = False

        plugin.activate()

        plugin.widget.set_visible.assert_called_once_with(False)

    @patch("statusicon_plugin.connect_events")
    def test_should_connect_menu_events(self, connect_events, plugin):
        # when
        plugin.activate()

        # then
        connect_events.assert_called_once_with(plugin.menu)


class TestDeactivatePlugin:
    def setup_method(self, method):
        setup_function(method)

    def test_should_unregister_tray_icon_provider(self, plugin):
        # given
        graph.register_instance(TrayIcon, plugin)
        plugin.activate()

        # when
        plugin.deactivate()

        # then
        assert TrayIcon not in graph.providers.keys()

    def test_should_hide_widget_when_plugin_deactivate(self, plugin):
        # given
        plugin.activate()
        plugin.widget.reset_mock()

        # when
        plugin.deactivate()

        # then
        plugin.widget.set_visible.assert_called_once_with(False)

    @patch("statusicon_plugin.disconnect_events")
    def test_should_disconnect_menu_events_when_plugin_deactivate(self, disconnect_events, plugin):
        # given
        plugin.activate()

        # when
        plugin.deactivate()

        # then
        disconnect_events.assert_called_once_with(plugin.menu)


def test_should_call_menu_pop(plugin):
    plugin._popup_menu(None, None, None)

    plugin.menu.widget.popup.assert_called_once_with(None, None, None, None, 0, 0)
