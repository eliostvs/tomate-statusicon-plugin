from __future__ import unicode_literals

import pytest
from mock import Mock, patch, call
from tomate.constant import State
from tomate.event import Events
from tomate.graph import graph
from tomate.view import TrayIcon


def setup_function(function):
    graph.providers.clear()

    graph.register_instance('tomate.view', Mock())
    graph.register_instance('trayicon.menu', Mock())

    Events.Session.receivers.clear()
    Events.Timer.receivers.clear()
    Events.View.receivers.clear()


def method_called(result):
    return result[0][0]


@pytest.fixture()
@patch('statusicon_plugin.Gtk.StatusIcon')
def plugin(StatusIcon):
    from statusicon_plugin import StatusIconPlugin

    return StatusIconPlugin()


def test_should_update_icon_when_timer_changed(plugin):
    plugin.update_icon(time_ratio=0.5)
    plugin.status_icon.set_from_icon_name.assert_called_with('tomate-50')

    plugin.update_icon(time_ratio=0.9)
    plugin.status_icon.set_from_icon_name.assert_called_with('tomate-90')


def test_should_show_status_icon(plugin):
    plugin.show()

    plugin.status_icon.set_visible.assert_has_calls([call(False), call(True)])


def test_should_hide_status_icon(plugin):
    plugin.hide()

    plugin.status_icon.set_visible.assert_has_calls([call(False), call(False)])


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

    result = Events.Timer.send(State.changed)

    assert len(result) == 1
    assert plugin.update_icon == method_called(result)


def test_should_call_show_when_session_started(plugin):
    plugin.activate()

    result = Events.Session.send(State.started)

    assert len(result) == 1
    assert plugin.show == method_called(result)


def test_should_call_hide_when_timer_finished(plugin):
    plugin.activate()

    result = Events.Session.send(State.finished)

    assert len(result) == 1
    assert plugin.hide == method_called(result)


def test_should_call_hide_when_timer_stopped(plugin):
    plugin.activate()

    result = Events.Session.send(State.stopped)

    assert len(result) == 1


def test_should_call_menu_pop(plugin):
    plugin._popup_menu(None, None)

    plugin.menu.widget.popup.assert_called_once_with(None, None, None, None, 0, 0L)
