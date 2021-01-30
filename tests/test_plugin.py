from unittest.mock import patch

import pytest

from tomate.pomodoro import State
from tomate.pomodoro.event import Events
from tomate.pomodoro.graph import graph
from tomate.pomodoro.session import Session
from tomate.pomodoro.timer import Payload as TimerPayload
from tomate.ui.widgets import TrayIcon


@pytest.fixture()
def menu(mocker):
    return mocker.Mock()


@pytest.fixture
def session(mocker):
    return mocker.Mock(spec=Session)


@pytest.fixture
def plugin(session, menu):
    graph.providers.clear()

    graph.register_instance("tomate.session", session)
    graph.register_instance("trayicon.menu", menu)

    Events.Session.receivers.clear()
    Events.Timer.receivers.clear()

    from statusicon_plugin import StatusIconPlugin
    return StatusIconPlugin()


def test_should_update_icon_when_timer_changes(plugin):
    plugin.activate()

    payload = TimerPayload(time_left=5, duration=10)
    Events.Timer.send(State.changed, payload=payload)

    assert plugin.widget.get_icon_name() == "tomate-50"


def test_should_show_widget_when_session_starts(plugin):
    plugin.activate()
    plugin.widget.set_visible(False)

    Events.Session.send(State.started)

    assert plugin.widget.get_visible() is True


@pytest.mark.parametrize("event", [State.finished, State.stopped])
def test_should_hide_widget_when_session_ends(event, plugin):
    plugin.activate()
    plugin.widget.set_visible(True)

    Events.Session.send(event)

    assert plugin.widget.get_visible() is False
    assert plugin.widget.get_icon_name() == "tomate-idle"


class TestActivePlugin:
    def test_should_register_tray_icon_provider(self, plugin):
        plugin.activate()

        assert TrayIcon in graph.providers.keys()
        assert graph.get(TrayIcon) == plugin

    def test_should_show_menu_when_session_is_running(self, session, plugin):
        session.is_running.return_value = True
        plugin.widget.set_visible(False)

        plugin.activate()

        assert plugin.widget.get_visible() is True

    def test_should_hide_menu_when_session_is_not_running(self, session, plugin):
        session.is_running.return_value = False
        plugin.widget.set_visible(False)

        plugin.activate()

        assert plugin.widget.get_visible() is False

    @patch("statusicon_plugin.connect_events")
    def test_should_connect_menu_events(self, connect_events, plugin, menu):
        plugin.activate()

        connect_events.assert_called_once_with(menu)


class TestDeactivatePlugin:
    def test_should_unregister_tray_icon_provider(self, plugin):
        graph.register_instance(TrayIcon, plugin)
        plugin.activate()

        plugin.deactivate()

        assert TrayIcon not in graph.providers.keys()

    def test_should_hide_widget_when_plugin_deactivate(self, plugin):
        plugin.activate()
        plugin.widget.set_visible(True)

        plugin.deactivate()

        assert plugin.widget.get_visible() is False

    @patch("statusicon_plugin.disconnect_events")
    def test_should_disconnect_menu_events_when_plugin_deactivate(self, disconnect_events, plugin, menu):
        plugin.activate()

        plugin.deactivate()

        disconnect_events.assert_called_once_with(menu)


@pytest.mark.parametrize("event, params", [("button-press-event", [None]), ("popup-menu", [0, 0])])
def test_should_call_menu_pop(event, params, plugin, menu):
    plugin.widget.emit(event, *params)

    menu.widget.popup.assert_called_once_with(None, None, None, None, 0, 0)
