#!/usr/bin/env python3

from PyQt5 import uic
from PyQt5.QtCore import QObject
from PyQt5.QtWidgets import (
    QAbstractSlider,
    QAbstractSpinBox,
    QCheckBox,
    QComboBox,
    QLineEdit,
)
from qgis.core import QgsExpressionContextUtils, QgsProject


def createClass(path, parent=None):
    """Create from UI file path an instance of the widget
    """
    ui_class, ui_widget = uic.loadUiType(path)

    class UserUI(ui_class, ui_widget):
        def __init__(self, parent=None):
            super(UserUI, self).__init__(parent)
            self.setupUi(self)

    return UserUI(parent)


class UiBuilder(QObject):
    """Create the UI widget, interface it with QGIS and show it
    """

    def __init__(self, path: str):
        super(UiBuilder, self).__init__()
        if not path:
            raise ValueError("path is None")

        self.prefix = "ve"
        self.var_format = "{0}_{1}"
        self.project = QgsProject.instance()
        self.user_ui = createClass(path)
        proj_variables = QgsExpressionContextUtils.projectScope(self.project)
        # signals and init variables
        ui_objs = self.user_ui.findChildren(QObject)
        for obj in ui_objs:
            name = obj.objectName()
            if name:
                var_name = self.var_format.format(self.prefix, name)
                if isinstance(obj, QCheckBox):
                    if var_name in proj_variables.variableNames():
                        try:
                            value = int(proj_variables.variable(var_name))
                        except ValueError:
                            value = 0
                        finally:
                            obj.setCheckState(value)
                    else:
                        self.store_variable(name, obj.checkState())

                    obj.stateChanged.connect(self.widget_connector)
                elif isinstance(obj, QComboBox):
                    if var_name in proj_variables.variableNames():
                        value = proj_variables.variable(var_name)
                        obj.setCurrentText(value)
                    else:
                        self.store_variable(name, obj.currentText())

                    obj.currentIndexChanged.connect(self.widget_connector)
                elif isinstance(obj, QAbstractSpinBox):
                    if var_name in proj_variables.variableNames():
                        value = proj_variables.variable(var_name)
                        obj.lineEdit().setText(value)
                    else:
                        self.store_variable(name, obj.text())

                    obj.editingFinished.connect(self.widget_connector)
                elif isinstance(obj, QLineEdit):
                    if var_name in proj_variables.variableNames():
                        value = proj_variables.variable(var_name)
                        obj.setText(value)
                    else:
                        self.store_variable(name, obj.text())

                    obj.editingFinished.connect(self.widget_connector)
                elif isinstance(obj, QAbstractSlider):
                    if var_name in proj_variables.variableNames():
                        try:
                            value = int(proj_variables.variable(var_name))
                        except ValueError:
                            value = 0
                        finally:
                            obj.setValue(value)
                    else:
                        self.store_variable(name, obj.value())

                    obj.valueChanged.connect(self.widget_connector)

        self.user_ui.show()

    def widget_connector(self, *args):
        """Receive widget edit signals and store values in the project variables
        """
        obj = self.sender()
        name = obj.objectName()
        if isinstance(obj, QCheckBox):
            value = obj.checkState()
        elif isinstance(obj, QComboBox):
            value = obj.currentText()
        elif isinstance(obj, (QAbstractSpinBox, QLineEdit)):
            value = obj.text()
        elif isinstance(obj, QAbstractSlider):
            value = obj.value()

        self.store_variable(name, value)

    def store_variable(self, name: str, value):
        """Store UI values in the QGIS project variables
        :param name: The name of the variable to store
        :param value: The value of the variable to store
        """
        project = QgsProject.instance()
        QgsExpressionContextUtils.setProjectVariable(
            project, self.var_format.format(self.prefix, name), value
        )
