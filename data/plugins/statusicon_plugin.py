import logging

from gi.repository import Gtk
from wiring import implements

from tomate.pomodoro import State
from tomate.pomodoro.event import connect_events, disconnect_events, Events, on
from tomate.pomodoro.graph import graph
from tomate.pomodoro.plugin import Plugin, suppress_errors
from tomate.pomodoro.timer import Payload as TimerPayload
from tomate.ui.widgets import TrayIcon

logger = logging.getLogger(__name__)


@implements(TrayIcon)
class StatusIconPlugin(Plugin):
    @suppress_errors
    def __init__(self):
        super(StatusIconPlugin, self).__init__()

        self.menu = graph.get("trayicon.menu")
        self.session = graph.get("tomate.session")
        self.widget = self.create_widget()

    @suppress_errors
    def activate(self):
        super(StatusIconPlugin, self).activate()

        graph.register_instance(TrayIcon, self)
        connect_events(self.menu)

        self.show_if_session_is_running()

    def show_if_session_is_running(self):
        if self.session.is_running():
            self.show()
        else:
            self.hide()

    @suppress_errors
    def deactivate(self):
        super(StatusIconPlugin, self).deactivate()

        graph.unregister_provider(TrayIcon)
        disconnect_events(self.menu)

        self.hide()

    @suppress_errors
    @on(Events.Session, [State.started])
    def show(self, *ars, **kwargs):
        self.widget.set_visible(True)

        logger.debug("Plugin status icon is showing")

    @suppress_errors
    @on(Events.Session, [State.finished, State.stopped])
    def hide(self, *args, **kwargs):
        self.widget.set_visible(False)
        self.widget.set_from_icon_name("tomate-idle")

        logger.debug("Plugin status icon is hiding")

    @suppress_errors
    @on(Events.Timer, [State.changed])
    def update_icon(self, _, payload: TimerPayload):
        icon_name = self.icon_name_for(payload.elapsed_percent)
        self.widget.set_from_icon_name(icon_name)

        logger.debug("action=set_icon name=%s", icon_name)

    @staticmethod
    def icon_name_for(percent):
        return "tomate-{0:.0f}".format(percent)

    def create_widget(self):
        widget = Gtk.StatusIcon(visible=False)
        widget.set_from_icon_name("tomate-idle")
        widget.set_title("StatusIcon")
        widget.connect("button-press-event", self.show_popup_menu)
        widget.connect("popup-menu", self.show_popup_menu)

        return widget

    def show_popup_menu(self, *_):
        self.menu.widget.popup(None, None, None, None, 0, Gtk.get_current_event_time())
