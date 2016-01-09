from __future__ import unicode_literals

import logging
from locale import gettext as _

from gi.repository import Gtk
from wiring import implements

import tomate.plugin
from tomate.constant import State
from tomate.event import Events, on
from tomate.graph import graph
from tomate.utils import suppress_errors
from tomate.view import TrayIcon

logger = logging.getLogger(__name__)


@implements(TrayIcon)
class StatusIconPlugin(tomate.plugin.Plugin):

    @suppress_errors
    def __init__(self):
        super(StatusIconPlugin, self).__init__()

        self.view = graph.get('tomate.view')
        self.config = graph.get('tomate.config')

        menu = self._build_menu()
        menu.show_all()

        self.status_icon = self._build_status_icon(menu)

        self.hide()

    def _build_status_icon(self, menu):
        status_icon = Gtk.StatusIcon()
        status_icon.set_from_icon_name('tomate-indicator')
        status_icon.set_title("StatusIcon")
        status_icon.connect("button-press-event", lambda icon, event: menu.popup(None, None, None, None, 0, Gtk.get_current_event_time()))
        status_icon.connect("popup-menu",
                                 lambda icon, button, time: menu.popup(None, None, None, None, button, time))
        return status_icon

    def _build_menu(self):
        menuitem = Gtk.MenuItem(_('Show'), visible=False)
        menuitem.connect('activate', self.on_show_menu_activate)
        menu = Gtk.Menu(halign=Gtk.Align.CENTER)
        menu.add(menuitem)

        return menu

    @suppress_errors
    def on_show_menu_activate(self, widget=None):
        return self.view.show()

    @suppress_errors
    def activate(self):
        super(StatusIconPlugin, self).activate()
        graph.register_instance(TrayIcon, self)

    @suppress_errors
    def deactivate(self):
        super(StatusIconPlugin, self).deactivate()
        graph.unregister_provider(TrayIcon)

    @suppress_errors
    @on(Events.View, [State.hiding])
    def show(self, sener=None, **kwargs):
        self.status_icon.set_visible(True)

        logger.debug('Plugin status icon is showing')

    @suppress_errors
    @on(Events.Session, [State.finished])
    @on(Events.View, [State.showing])
    def hide(self, sender=None, **kwargs):
        self.status_icon.set_visible(False)

        logger.debug('Plugin status icon is hiding')

    @suppress_errors
    @on(Events.Timer, [State.changed])
    def update_icon(self, sender=None, **kwargs):
        percent = int(kwargs.get('time_ratio', 0) * 100)

        if self.rounded_percent(percent) < 99:
            icon_name = self.icon_name_for(percent)
            self.status_icon.set_from_icon_name(icon_name)

            logger.debug('set icon %s', icon_name)

    def rounded_percent(self, percent):
        '''
        The icons show 5% steps, so we have to round.
        '''
        return percent - percent % 5

    def icon_name_for(self, percent):
        return 'tomate-{0:02}'.format(self.rounded_percent(percent))
