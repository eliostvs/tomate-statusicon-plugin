import pytest
from blinker import NamedSignal
from gi.repository import Gtk

from tomate.pomodoro.event import Events
from tomate.pomodoro.graph import graph
from tomate.pomodoro.session import Session
from tomate.pomodoro.timer import Payload as TimerPayload
from tomate.ui import Systray, SystrayMenu


@pytest.fixture
def bus():
    return NamedSignal("Test")


@pytest.fixture()
def menu(mocker):
    return mocker.Mock(spec=SystrayMenu, widget=mocker.Mock(spec=Gtk.Menu))


@pytest.fixture
def session(mocker):
    return mocker.Mock(spec=Session)


@pytest.fixture
def subject(bus, menu, session):
    graph.providers.clear()
    graph.register_instance("tomate.bus", bus)
    graph.register_instance("tomate.ui.systray.menu", menu)
    graph.register_instance("tomate.session", session)

    from statusicon_plugin import StatusIconPlugin
    return StatusIconPlugin()


def test_changes_icon_when_timer_change(bus, subject):
    subject.activate()

    bus.send(Events.TIMER_UPDATE, payload=TimerPayload(time_left=5, duration=10))

    assert subject.widget.get_icon_name() == "tomate-50"


def test_shows_when_session_start(bus, subject):
    subject.activate()
    subject.widget.set_visible(False)

    bus.send(Events.SESSION_START)

    assert subject.widget.get_visible() is True


@pytest.mark.parametrize("event", [Events.SESSION_END, Events.SESSION_INTERRUPT])
def test_hides_when_session_end(event, bus, subject):
    subject.activate()
    subject.widget.set_visible(True)

    bus.send(event)

    assert subject.widget.get_visible() is False
    assert subject.widget.get_icon_name() == "tomate-idle"


class TestActivePlugin:
    def test_registers_systray_provider(self, subject):
        subject.activate()

        assert Systray in graph.providers.keys()
        assert graph.get(Systray) == subject

    def test_shows_when_session_is_running(self, session, subject):
        session.is_running.return_value = True
        subject.widget.set_visible(False)

        subject.activate()

        assert subject.widget.get_visible() is True

    def test_hides_when_session_is_not_running(self, session, subject):
        session.is_running.return_value = False
        subject.widget.set_visible(False)

        subject.activate()

        assert subject.widget.get_visible() is False

    def test_connect_menu_events(self, bus, menu, subject):
        subject.activate()

        menu.connect.assert_called_once_with(bus)


class TestDeactivatePlugin:
    def test_unregisters_systray_provider(self, subject):
        graph.register_instance(Systray, subject)
        subject.activate()

        subject.deactivate()

        assert Systray not in graph.providers.keys()

    def test_hide(self, subject):
        subject.activate()
        subject.widget.set_visible(True)

        subject.deactivate()

        assert subject.widget.get_visible() is False

    def test_disconnects_menu_events(self, bus, menu, subject):
        subject.activate()

        subject.deactivate()

        menu.disconnect.assert_called_once_with(bus)


@pytest.mark.parametrize("event, params", [("button-press-event", [None]), ("popup-menu", [0, 0])])
def test_shows_menu_when_clicked(event, params, subject, menu):
    subject.widget.emit(event, *params)

    menu.widget.popup.assert_called_once_with(None, None, None, None, 0, 0)
