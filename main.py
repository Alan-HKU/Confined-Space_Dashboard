import sys
import os

from modules import *
from widgets import *
from funciton import *


widgets = None


class MainWindow(QMainWindow):
    def __init__(self):
        os.environ["QT_FONT_DPI"] = "100"
        QMainWindow.__init__(self)

        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        global widgets
        widgets = self.ui

        Settings.ENABLE_CUSTOM_TITLE_BAR = True

        title       = "密閉空間監測系統"
        description = "密閉空間監測系統"
        self.setWindowTitle(title)
        widgets.titleRightInfo.setText(description)

        UIFunctions.uiDefinitions(self)

        # Left menu navigation
        widgets.btn_home.clicked.connect(self.buttonClick)

        self.show()

        widgets.stackedWidget.setCurrentWidget(widgets.home)
        widgets.btn_home.setStyleSheet(
            UIFunctions.selectMenu(widgets.btn_home.styleSheet())
        )

    def buttonClick(self):
        btn     = self.sender()
        btnName = btn.objectName()

        page_map = {
            "btn_home":    widgets.home,
            "btn_widgets": getattr(widgets, "widgets", None),
            "btn_new":     getattr(widgets, "new_page", None),
        }

        if btnName in page_map and page_map[btnName] is not None:
            widgets.stackedWidget.setCurrentWidget(page_map[btnName])
            UIFunctions.resetStyle(self, btnName)
            btn.setStyleSheet(UIFunctions.selectMenu(btn.styleSheet()))

    def resizeEvent(self, event):
        UIFunctions.resize_grips(self)

    def mousePressEvent(self, event):
        self.dragPos = event.globalPos()


if __name__ == "__main__":
    all_init()

    os.environ["QT_FONT_DPI"] = get("DPI")

    # QApplication MUST be created before any Qt objects (QSoundEffect, QTimer, etc.)
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon("icon.ico"))

    private_mqtt = mqtt_client_init(
        get("private_broker"), get("private_broker_port"), get("private_topic"),
        role="private"
    )
    print(f"Private MQTT -> {get('private_broker')}:{get('private_broker_port')}  topic={get('private_topic')}")

    public_mqtt = mqtt_client_init(
        get("public_broker"), get("public_broker_port"), get("private_topic"),
        role="public"
    )
    print(f"Public MQTT  -> {get('public_broker')}:{get('public_broker_port')}  topic={get('public_topic')}")

    data_obj = data(public_mqtt)
    gui      = GUI()   # QSoundEffect created here — must be after QApplication

    window = MainWindow()
    window_init(window)

    # GUI refresh (labels, colours)
    timer1 = QTimer()
    timer1.timeout.connect(lambda: gui.update(window, data_obj))
    timer1.start(get("GUIReflashTime"))

    # Data logging
    timer2 = QTimer()
    timer2.timeout.connect(lambda: data_obj.log())
    timer2.start(get("LoggingTime"))

    # Consume MQTT buffer -> update data model
    timer4 = QTimer()
    timer4.timeout.connect(lambda: data_obj.get())
    timer4.start(get("DataReflashTime"))

    # Publish upstream
    timer5 = QTimer()
    timer5.timeout.connect(lambda: data_obj.send(public_mqtt))
    timer5.start(get("MQTTTime"))

    # Rotate display page
    timer6 = QTimer()
    timer6.timeout.connect(lambda: gui.switch_display_device(data_obj))
    timer6.start(get("DisplaySwitchTime"))

    # Bind status indicator
    timer7 = QTimer()
    timer7.timeout.connect(lambda: set_status_bind(window, data_obj))
    timer7.start(get("GUIReflashTime"))

    sys.exit(app.exec())

    