#!/usr/bin/env python3

import os

import yaml
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QAction, QFileDialog, QToolButton

from .resources import *
from .ve import UiBuilder


def classFactory(iface):
    """Load VariableEditor class

    :param iface: A QGIS interface instance
    :type iface: QgsInterface
    """
    return VariableEditor(iface)


class VariableEditor:
    """Add the plugin ToolButton in the QGIS plugin toolbar

    :param iface: A QGIS interface instance
    :type iface: QgsInterface
    """
    def __init__(self, iface):
        self.iface = iface
        self._ui = None

    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI
        """
        self.conf_path = os.path.join(os.path.dirname(__file__), "settings.yml")
        self.mbp = QToolButton()
        self.mbp.setPopupMode(QToolButton.MenuButtonPopup)
        icon_openui = ":/icons/mIconVariableEditor.svg"
        icon_confui = ":/icons/settings.svg"
        self.ac_openui = QAction(QIcon(icon_openui), "Open")
        self.ac_confui = QAction(QIcon(icon_confui), "Configure")
        self.mbp.addActions([self.ac_openui, self.ac_confui])
        self.mbp.setDefaultAction(self.ac_openui)
        self.plugin_action = self.iface.addToolBarWidget(self.mbp)
        # signals
        self.ac_confui.triggered.connect(self.configure)
        self.ac_openui.triggered.connect(self.openui)

    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI
        """
        self.iface.removeToolBarIcon(self.plugin_action)
        del self.plugin_action

    def configure(self) -> str:
        """Configure the user UI file path
        """
        self.rw_config("w")

    def ui_path(self) -> str:
        """File dialog for ask the user UI file path
        """
        ui_file, _ = QFileDialog.getOpenFileName(
            None, "Open UI file", os.path.abspath(os.sep), "UI Files (*.ui)"
        )
        return ui_file

    def rw_config(self, mode: str) -> str:
        """Read or write YAML configuration file
        :param mode: "r" for read, "w" for write
        """
        try:
            with open(self.conf_path, mode) as conf_yaml:
                if mode == "r":
                    config = yaml.load(conf_yaml, Loader=yaml.SafeLoader)
                elif mode == "w":
                    yaml.dump({"ui_path": self.ui_path()}, conf_yaml)
        except FileNotFoundError:
            with open(self.conf_path, "w") as conf_yaml:
                yaml.dump({"ui_path": self.ui_path()}, conf_yaml)
        finally:
            with open(self.conf_path, "r") as conf_yaml:
                config = yaml.load(conf_yaml, Loader=yaml.SafeLoader)

        return config["ui_path"]

    def openui(self):
        """Open the user UI file path.
        If there is no path configured, ask for this path
        """
        ui_path = self.rw_config("r")

        if ui_path:
            self._ui = UiBuilder(ui_path)
        else:
            self.configure()
