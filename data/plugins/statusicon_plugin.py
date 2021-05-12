import logging

import gi
from wiring import Graph

gi.require_version("Gtk", "3.0")

from gi.repository import Gtk

import tomate.pomodoro.plugin as plugin
from tomate.ui import Systray
from tomate.pomodoro import Bus, TimerPayload, suppress_errors, Events, on

logger = logging.getLogger(__name__)


class StatusIconPlugin(plugin.Plugin):
    @suppress_errors
    def __init__(self):
        super().__init__()
        self.menu = None
        self.session = None
        self.widget = self.create_status_icon()

    def configure(self, bus: Bus, graph: Graph) -> None:
        super().configure(bus, graph)
        self.menu = graph.get("tomate.ui.systray.menu")
        self.session = graph.get("tomate.session")

    @suppress_errors
    def activate(self):
        super().activate()
        self.menu.connect(self.bus)
        self.graph.register_instance(Systray, self)
        if self.session.is_running():
            self.show()
        else:
            self.hide()

    @suppress_errors
    def deactivate(self):
        super().deactivate()
        self.menu.disconnect(self.bus)
        self.graph.unregister_provider(Systray)
        self.hide()

    @suppress_errors
    @on(Events.SESSION_START)
    def show(self, **__):
        logger.debug("action=show")
        self.widget.props.visible = True

    @suppress_errors
    @on(Events.SESSION_END, Events.SESSION_INTERRUPT)
    def hide(self, **__):
        logger.debug("action=hide")
        self.widget.set_properties(visible=False, icon_name="tomate-idle")

    @suppress_errors
    @on(Events.TIMER_UPDATE)
    def update_icon(self, payload: TimerPayload):
        icon_name = self.icon_name(payload.elapsed_percent)
        self.widget.props.icon_name = icon_name
        logger.debug("action=set_icon name=%s", icon_name)

    @staticmethod
    def icon_name(percent):
        return "tomate-{:02.0f}".format(percent)

    def create_status_icon(self):
        status_icon = Gtk.StatusIcon.new_from_icon_name("tomate-idle")
        status_icon.set_properties(visible=False, title="TomateStatusIcon")
        status_icon.connect("button-press-event", self.show_popup_menu)
        status_icon.connect("popup-menu", self.show_popup_menu)
        return status_icon

    def show_popup_menu(self, *_):
        self.menu.widget.popup(None, None, None, None, 0, Gtk.get_current_event_time())
