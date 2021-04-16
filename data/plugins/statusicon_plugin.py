import logging

import gi

gi.require_version("Gtk", "3.0")

from gi.repository import Gtk

import tomate.pomodoro.plugin as plugin
from tomate.ui import Systray
from tomate.pomodoro import Bus, TimerPayload, suppress_errors, graph, Events, on

logger = logging.getLogger(__name__)


class StatusIconPlugin(plugin.Plugin):
    @suppress_errors
    def __init__(self):
        super().__init__()
        self.menu = graph.get("tomate.ui.systray.menu")
        self.session = graph.get("tomate.session")
        self.status_icon = self.create_widget()

    def connect(self, bus: Bus) -> None:
        logger.debug("action=connect")
        super().connect(bus)
        self.menu.connect(bus)

    def disconnect(self, bus: Bus) -> None:
        logger.debug("action=disconnect")
        self.menu.disconnect(bus)
        super().disconnect(bus)

    @suppress_errors
    def activate(self):
        super().activate()
        graph.register_instance(Systray, self)

        if self.session.is_running():
            self.show()
        else:
            self.hide()

    @suppress_errors
    def deactivate(self):
        super().deactivate()
        graph.unregister_provider(Systray)
        self.hide()

    @suppress_errors
    @on(Events.SESSION_START)
    def show(self, *_, **__):
        logger.debug("action=show")
        self.status_icon.props.visible = True

    @suppress_errors
    @on(Events.SESSION_END, Events.SESSION_INTERRUPT)
    def hide(self, *_, **__):
        logger.debug("action=hide")
        self.status_icon.props.visible = False
        self.status_icon.set_from_icon_name("tomate-idle")

    @suppress_errors
    @on(Events.TIMER_UPDATE)
    def update_icon(self, _, payload: TimerPayload):
        icon_name = self.icon_name(payload.elapsed_percent)
        self.status_icon.set_from_icon_name(icon_name)
        logger.debug("action=set_icon name=%s", icon_name)

    @staticmethod
    def icon_name(percent):
        return "tomate-{:02.0f}".format(percent)

    def create_widget(self):
        widget = Gtk.StatusIcon(visible=False)
        widget.set_from_icon_name("tomate-idle")
        widget.props.title = "TomateStatusIcon"
        widget.connect("button-press-event", self.show_popup_menu)
        widget.connect("popup-menu", self.show_popup_menu)
        return widget

    def show_popup_menu(self, *_):
        self.menu.widget.popup(None, None, None, None, 0, Gtk.get_current_event_time())
