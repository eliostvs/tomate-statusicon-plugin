from __future__ import unicode_literals

import unittest

from mock import Mock, patch, call

from tomate.graph import graph
from tomate.view import TrayIcon


@patch('statusicon_plugin.Gtk.StatusIcon')
class TestIndicatorPlugin(unittest.TestCase):

    def make_statusicon(self):
        from statusicon_plugin import StatusIconPlugin

        graph.providers.clear()

        graph.register_instance('tomate.config', Mock(**{'get_icon_paths.return_value': ['']}))
        graph.register_instance('tomate.view', Mock())

        return StatusIconPlugin()

    def test_should_update_icon_when_timer_changed(self, fake_status_icon):
        plugin = self.make_statusicon()

        plugin.update_icon(time_ratio=0.5)
        plugin.status_icon.set_from_icon_name.assert_called_with('tomate-50')

        plugin.update_icon(time_ratio=0.9)
        plugin.status_icon.set_from_icon_name.assert_called_with('tomate-90')

    def test_should_show_status_icon(self, fake_stautus_icon):
        plugin = self.make_statusicon()

        plugin.show()

        plugin.status_icon.set_visible.assert_has_calls([call(False), call(True)])

    def test_should_hide_status_icon(self, fake_stautus_icon):
        plugin = self.make_statusicon()

        plugin.hide()

        plugin.status_icon.set_visible.assert_has_calls([call(False), call(False)])

    def test_should_register_tray_icon_provider(self, fake_stautus_icon):
        plugin = self.make_statusicon()

        plugin.activate()

        self.assertIn(TrayIcon, graph.providers.keys())
        self.assertEqual(graph.get(TrayIcon), plugin)

    def test_should_unregister_tray_icon_provider(self, fake_stautus_icon):
        plugin = self.make_statusicon()

        graph.register_instance(TrayIcon, plugin)

        plugin.deactivate()

        self.assertNotIn(TrayIcon, graph.providers.keys())

    def test_should_show_view(self, fake_stautus_icon):
        plugin = self.make_statusicon()

        plugin.on_show_menu_activate()

        plugin.view.show.assert_called_once_with()
