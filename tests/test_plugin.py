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


@pytest.mark.parametrize(
    "time_left,duration,icon_name",
    [
        (100, 100, "tomate-00"),
        (95, 100, "tomate-05"),
        (90, 100, "tomate-10"),
        (85, 100, "tomate-15"),
        (80, 100, "tomate-20"),
        (75, 100, "tomate-25"),
        (70, 100, "tomate-30"),
        (65, 100, "tomate-35"),
        (60, 100, "tomate-40"),
        (55, 100, "tomate-45"),
        (50, 100, "tomate-50"),
        (45, 100, "tomate-55"),
        (40, 100, "tomate-60"),
        (35, 100, "tomate-65"),
        (30, 100, "tomate-70"),
        (25, 100, "tomate-75"),
        (20, 100, "tomate-80"),
        (10, 100, "tomate-90"),
        (5, 100, "tomate-95"),
    ],
)
def test_changes_icon_when_timer_change(time_left, duration, icon_name, bus, subject):
    subject.activate()

    bus.send(Events.TIMER_UPDATE, payload=TimerPayload(time_left=time_left, duration=duration))

    assert subject.status_icon.get_icon_name() == icon_name


def test_shows_when_session_start(bus, subject):
    subject.activate()
    subject.status_icon.set_visible(False)

    bus.send(Events.SESSION_START)

    assert subject.status_icon.get_visible() is True


@pytest.mark.parametrize("event", [Events.SESSION_END, Events.SESSION_INTERRUPT])
def test_hides_when_session_end(event, bus, subject):
    subject.activate()
    subject.status_icon.set_visible(True)

    bus.send(event)

    assert subject.status_icon.get_visible() is False
    assert subject.status_icon.get_icon_name() == "tomate-idle"


class TestActivePlugin:
    def test_registers_systray_provider(self, subject):
        subject.activate()

        assert Systray in graph.providers.keys()
        assert graph.get(Systray) == subject

    def test_shows_when_session_is_running(self, session, subject):
        session.is_running.return_value = True
        subject.status_icon.set_visible(False)

        subject.activate()

        assert subject.status_icon.get_visible() is True

    def test_hides_when_session_is_not_running(self, session, subject):
        session.is_running.return_value = False
        subject.status_icon.set_visible(False)

        subject.activate()

        assert subject.status_icon.get_visible() is False

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
        subject.status_icon.set_visible(True)

        subject.deactivate()

        assert subject.status_icon.get_visible() is False

    def test_disconnects_menu_events(self, bus, menu, subject):
        subject.activate()

        subject.deactivate()

        menu.disconnect.assert_called_once_with(bus)


@pytest.mark.parametrize("event, params", [("button-press-event", [None]), ("popup-menu", [0, 0])])
def test_shows_menu_when_clicked(event, params, subject, menu):
    subject.status_icon.emit(event, *params)

    menu.widget.popup.assert_called_once_with(None, None, None, None, 0, 0)
