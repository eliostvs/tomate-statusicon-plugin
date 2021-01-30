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
def subject(session, menu):
    graph.providers.clear()

    graph.register_instance("tomate.session", session)
    graph.register_instance("trayicon.menu", menu)

    Events.Session.receivers.clear()
    Events.Timer.receivers.clear()

    from statusicon_plugin import StatusIconPlugin
    return StatusIconPlugin()


def test_change_icon_when_timer_change(subject):
    subject.activate()

    payload = TimerPayload(time_left=5, duration=10)
    Events.Timer.send(State.changed, payload=payload)

    assert subject.widget.get_icon_name() == "tomate-50"


def test_show_when_session_start(subject):
    subject.activate()
    subject.widget.set_visible(False)

    Events.Session.send(State.started)

    assert subject.widget.get_visible() is True


@pytest.mark.parametrize("event", [State.finished, State.stopped])
def test_hide_when_session_end(event, subject):
    subject.activate()
    subject.widget.set_visible(True)

    Events.Session.send(event)

    assert subject.widget.get_visible() is False
    assert subject.widget.get_icon_name() == "tomate-idle"


class TestActivePlugin:
    def test_register_trayicon_provider(self, subject):
        subject.activate()

        assert TrayIcon in graph.providers.keys()
        assert graph.get(TrayIcon) == subject

    def test_show_when_session_is_running(self, session, subject):
        session.is_running.return_value = True
        subject.widget.set_visible(False)

        subject.activate()

        assert subject.widget.get_visible() is True

    def test_hide_when_session_is_not_running(self, session, subject):
        session.is_running.return_value = False
        subject.widget.set_visible(False)

        subject.activate()

        assert subject.widget.get_visible() is False

    def test_connect_menu_events(self, subject, menu, mocker):
        connect_events = mocker.patch("statusicon_plugin.connect_events")

        subject.activate()

        connect_events.assert_called_once_with(menu)


class TestDeactivatePlugin:
    def test_unregister_trayicon_provider(self, subject):
        graph.register_instance(TrayIcon, subject)
        subject.activate()

        subject.deactivate()

        assert TrayIcon not in graph.providers.keys()

    def test_hide(self, subject):
        subject.activate()
        subject.widget.set_visible(True)

        subject.deactivate()

        assert subject.widget.get_visible() is False

    def test_disconnect_menu_events(self, subject, menu, mocker):
        disconnect_events = mocker.patch("statusicon_plugin.disconnect_events")
        subject.activate()

        subject.deactivate()

        disconnect_events.assert_called_once_with(menu)


@pytest.mark.parametrize("event, params", [("button-press-event", [None]), ("popup-menu", [0, 0])])
def test_show_menu_when_it_is_clicked(event, params, subject, menu):
    subject.widget.emit(event, *params)

    menu.widget.popup.assert_called_once_with(None, None, None, None, 0, 0)
