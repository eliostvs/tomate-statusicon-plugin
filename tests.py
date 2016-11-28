from __future__ import unicode_literals

import pytest
from mock import Mock, patch
from tomate.constant import State
from tomate.event import Events
from tomate.graph import graph
from tomate.view import TrayIcon


def setup_function(function):
    graph.providers.clear()

    graph.register_instance('tomate.session', Mock())
    graph.register_instance('trayicon.menu', Mock())

    Events['Session'].receivers.clear()
    Events['Timer'].receivers.clear()
    Events['View'].receivers.clear()


def method_called(result):
    return result[0][0]


@pytest.fixture()
def session():
    return graph.get('tomate.session')


@pytest.fixture()
@patch('statusicon_plugin.Gtk.StatusIcon')
def plugin(StatusIcon):
    from statusicon_plugin import StatusIconPlugin

    return StatusIconPlugin()


def test_should_update_icon_when_timer_changed(plugin):
    plugin.update_icon(time_ratio=0.5)
    plugin.widget.set_from_icon_name.assert_called_with('tomate-50')

    plugin.update_icon(time_ratio=0.9)
    plugin.widget.set_from_icon_name.assert_called_with('tomate-90')


def test_should_show_widget_when_plugin_shows(plugin):
    plugin.show()

    plugin.widget.set_visible.assert_called_once_with(True)


def test_should_hide_widget_when_plugin_hides(plugin):
    plugin.hide()

    plugin.widget.set_visible.assert_called_once_with(False)


def test_should_register_tray_icon_provider(plugin):
    plugin.activate()

    assert TrayIcon in graph.providers.keys()
    assert graph.get(TrayIcon) == plugin


def test_should_unregister_tray_icon_provider(plugin):
    graph.register_instance(TrayIcon, plugin)

    plugin.deactivate()

    assert TrayIcon not in graph.providers.keys()


def test_should_call_update_icon_when_time_changed(plugin):
    plugin.activate()

    result = Events['Timer'].send(State.changed)

    assert len(result) == 1
    assert plugin.update_icon == method_called(result)


def test_should_call_show_when_session_started(plugin):
    plugin.activate()

    result = Events['Session'].send(State.started)

    assert len(result) == 1
    assert plugin.show == method_called(result)


def test_should_call_hide_when_timer_finished(plugin):
    plugin.activate()

    result = Events['Session'].send(State.finished)

    assert len(result) == 1
    assert plugin.hide == method_called(result)


def test_should_call_hide_when_timer_stopped(plugin):
    plugin.activate()

    result = Events['Session'].send(State.stopped)

    assert len(result) == 1


def test_should_call_menu_pop(plugin):
    plugin._popup_menu(None, None)

    plugin.menu.widget.popup.assert_called_once_with(None, None, None, None, 0, 0)


@patch('statusicon_plugin.connect_events')
def test_should_connect_menu_events_when_plugin_activate(connect_events, plugin):
    plugin.activate()

    connect_events.assert_called_once_with(plugin.menu)


@patch('statusicon_plugin.disconnect_events')
def test_should_disconnect_menu_events_when_plugin_deactivate(disconnect_events, plugin):
    plugin.activate()

    plugin.deactivate()

    disconnect_events.assert_called_once_with(plugin.menu)


def test_should_hide_widget_when_plugin_deactivate(plugin):
    plugin.widget = Mock()
    plugin.activate()
    plugin.widget.reset_mock()

    plugin.deactivate()

    plugin.widget.set_visible.assert_called_once_with(False)


def test_should_show_widget_when_plugin_activate(plugin):
    plugin.widget = Mock()

    plugin.activate()

    plugin.widget.set_visible.assert_called_once_with(True)


def test_should_set_idle_icon_when_plugin_hides(plugin):
    plugin.hide()

    plugin.widget.set_from_icon_name.assert_called_with('tomate-idle')


def test_plugin_should_hide_when_session_is_not_running(session, plugin):
    session.is_running.return_value = False

    plugin.activate()

    plugin.widget.set_visible.assert_called_once_with(False)


def test_plugin_should_show_when_session_is_running(session, plugin):
    session.is_running.return_value = True

    plugin.activate()

    plugin.widget.set_visible.assert_called_once_with(True)
