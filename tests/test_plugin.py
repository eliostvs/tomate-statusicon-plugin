import pytest
from gi.repository import Gtk

from tomate.pomodoro import Bus, Events, Session, TimerPayload, graph
from tomate.ui import Systray, SystrayMenu


@pytest.fixture
def bus() -> Bus:
    return Bus()


@pytest.fixture
def menu(mocker):
    return mocker.Mock(spec=SystrayMenu, widget=mocker.Mock(spec=Gtk.Menu))


@pytest.fixture
def session(mocker):
    return mocker.Mock(spec=Session)


@pytest.fixture
def plugin(bus, menu, session):
    from statusicon_plugin import StatusIconPlugin

    graph.providers.clear()
    graph.register_instance("tomate.bus", bus)
    graph.register_instance("tomate.ui.systray.menu", menu)
    graph.register_instance("tomate.session", session)

    instance = StatusIconPlugin()
    instance.connect(bus)
    return instance


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
def test_changes_icon_when_timer_change(time_left, duration, icon_name, bus, plugin):
    plugin.activate()

    bus.send(Events.TIMER_UPDATE, payload=TimerPayload(time_left=time_left, duration=duration))

    assert plugin.status_icon.props.icon_name == icon_name


def test_shows_when_session_start(bus, plugin):
    plugin.activate()
    plugin.status_icon.props.visible = False

    bus.send(Events.SESSION_START)

    assert plugin.status_icon.props.visible is True


@pytest.mark.parametrize("event", [Events.SESSION_END, Events.SESSION_INTERRUPT])
def test_hides_when_session_end(event, bus, plugin):
    plugin.activate()
    plugin.status_icon.props.visible = True

    bus.send(event)

    assert plugin.status_icon.props.visible is False
    assert plugin.status_icon.props.icon_name == "tomate-idle"


class TestActivePlugin:
    def test_registers_systray_provider(self, plugin):
        plugin.activate()

        assert Systray in graph.providers.keys()
        assert graph.get(Systray) == plugin

    def test_shows_when_session_is_running(self, session, plugin):
        session.is_running.return_value = True
        plugin.status_icon.props.visible = False

        plugin.activate()

        assert plugin.status_icon.props.visible is True

    def test_hides_when_session_is_not_running(self, session, plugin):
        session.is_running.return_value = False
        plugin.status_icon.props.visible = False

        plugin.activate()

        assert plugin.status_icon.props.visible is False

    def test_connect_menu_events(self, bus, menu, plugin):
        menu.connect.assert_called_once_with(bus)


class TestDeactivatePlugin:
    def test_unregisters_systray_provider(self, plugin):
        graph.register_instance(Systray, plugin)
        plugin.activate()

        plugin.deactivate()

        assert Systray not in graph.providers.keys()

    def test_hide(self, plugin):
        plugin.activate()
        plugin.status_icon.props.visible = True

        plugin.deactivate()

        assert plugin.status_icon.props.visible is False

    def test_disconnects_menu_events(self, bus, menu, plugin):
        plugin.disconnect(bus)

        menu.disconnect.assert_called_once_with(bus)


@pytest.mark.parametrize("event, params", [("button-press-event", [None]), ("popup-menu", [0, 0])])
def test_shows_menu_when_clicked(event, params, plugin, menu):
    plugin.status_icon.emit(event, *params)

    menu.widget.popup.assert_called_once_with(None, None, None, None, 0, 0)
