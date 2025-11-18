# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'main_10.ui'
##
## Created by: Qt User Interface Compiler version 6.6.0
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (
    QCoreApplication,
    QDate,
    QDateTime,
    QLocale,
    QMetaObject,
    QObject,
    QPoint,
    QRect,
    QSize,
    QTime,
    QUrl,
    Qt,
)
from PySide6.QtGui import (
    QBrush,
    QColor,
    QConicalGradient,
    QCursor,
    QFont,
    QFontDatabase,
    QGradient,
    QIcon,
    QImage,
    QKeySequence,
    QLinearGradient,
    QPainter,
    QPalette,
    QPixmap,
    QRadialGradient,
    QTransform,
)
from PySide6.QtWidgets import (
    QApplication,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLayout,
    QMainWindow,
    QPushButton,
    QSizePolicy,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)
from .resources_rc import *


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1281, 756)
        MainWindow.setMinimumSize(QSize(940, 560))
        self.styleSheet = QWidget(MainWindow)
        self.styleSheet.setObjectName("styleSheet")
        font = QFont()
        font.setFamilies(["Segoe UI"])
        font.setPointSize(10)
        font.setBold(False)
        font.setItalic(False)
        self.styleSheet.setFont(font)
        self.styleSheet.setStyleSheet(
            "/* /////////////////////////////////////////////////////////////////////////////////////////////////\n"
            "\n"
            "SET APP STYLESHEET - FULL STYLES HERE\n"
            "DARK THEME - DRACULA COLOR BASED\n"
            "\n"
            "///////////////////////////////////////////////////////////////////////////////////////////////// */\n"
            "\n"
            "QWidget{\n"
            "	color: rgb(221, 221, 221);\n"
            '	font: 10pt "Segoe UI";\n'
            "}\n"
            "\n"
            "/* /////////////////////////////////////////////////////////////////////////////////////////////////\n"
            "Tooltip */\n"
            "QToolTip {\n"
            "	color: #ffffff;\n"
            "	background-color: rgba(33, 37, 43, 180);\n"
            "	border: 1px solid rgb(44, 49, 58);\n"
            "	background-image: none;\n"
            "	background-position: left center;\n"
            "    background-repeat: no-repeat;\n"
            "	border: none;\n"
            "	border-left: 2px solid rgb(255, 121, 198);\n"
            "	text-align: left;\n"
            "	padding-left: 8px;\n"
            "	margin: 0px;\n"
            "}\n"
            "\n"
            "/* /////////////////////////////////////////////////////////////////////////////////////////////////\n"
            "Bg App */\n"
            "#bgApp {	\n"
            "	background"
            "-color: rgb(40, 44, 52);\n"
            "	border: 1px solid rgb(44, 49, 58);\n"
            "}\n"
            "\n"
            "/* /////////////////////////////////////////////////////////////////////////////////////////////////\n"
            "Left Menu */\n"
            "#leftMenuBg {	\n"
            "	background-color: rgb(33, 37, 43);\n"
            "}\n"
            "#topLogo {\n"
            "	background-color: rgb(33, 37, 43);\n"
            "	background-image: url(:/images/images/images/PyDracula.png);\n"
            "	background-position: centered;\n"
            "	background-repeat: no-repeat;\n"
            "}\n"
            '#titleLeftApp { font: 63 12pt "Segoe UI Semibold"; }\n'
            '#titleLeftDescription { font: 8pt "Segoe UI"; color: rgb(189, 147, 249); }\n'
            "\n"
            "/* MENUS */\n"
            "#topMenu .QPushButton {	\n"
            "	background-position: left center;\n"
            "    background-repeat: no-repeat;\n"
            "	border: none;\n"
            "	border-left: 22px solid transparent;\n"
            "	background-color: transparent;\n"
            "	text-align: left;\n"
            "	padding-left: 44px;\n"
            "}\n"
            "#topMenu .QPushButton:hover {\n"
            "	background-color: rgb(40, 44, 52);\n"
            "}\n"
            "#topMenu .QPushButton:pressed {	\n"
            "	background-color: rgb(18"
            "9, 147, 249);\n"
            "	color: rgb(255, 255, 255);\n"
            "}\n"
            "#bottomMenu .QPushButton {	\n"
            "	background-position: left center;\n"
            "    background-repeat: no-repeat;\n"
            "	border: none;\n"
            "	border-left: 20px solid transparent;\n"
            "	background-color:transparent;\n"
            "	text-align: left;\n"
            "	padding-left: 44px;\n"
            "}\n"
            "#bottomMenu .QPushButton:hover {\n"
            "	background-color: rgb(40, 44, 52);\n"
            "}\n"
            "#bottomMenu .QPushButton:pressed {	\n"
            "	background-color: rgb(189, 147, 249);\n"
            "	color: rgb(255, 255, 255);\n"
            "}\n"
            "#leftMenuFrame{\n"
            "	border-top: 3px solid rgb(44, 49, 58);\n"
            "}\n"
            "\n"
            "/* Toggle Button */\n"
            "#toggleButton {\n"
            "	background-position: left center;\n"
            "    background-repeat: no-repeat;\n"
            "	border: none;\n"
            "	border-left: 20px solid transparent;\n"
            "	background-color: rgb(37, 41, 48);\n"
            "	text-align: left;\n"
            "	padding-left: 44px;\n"
            "	color: rgb(113, 126, 149);\n"
            "}\n"
            "#toggleButton:hover {\n"
            "	background-color: rgb(40, 44, 52);\n"
            "}\n"
            "#toggleButton:pressed {\n"
            "	background-color: rgb("
            "189, 147, 249);\n"
            "}\n"
            "\n"
            "/* Title Menu */\n"
            "#titleRightInfo { padding-left: 10px; }\n"
            "\n"
            "\n"
            "/* /////////////////////////////////////////////////////////////////////////////////////////////////\n"
            "Extra Tab */\n"
            "#extraLeftBox {	\n"
            "	background-color: rgb(44, 49, 58);\n"
            "}\n"
            "#extraTopBg{	\n"
            "	background-color: rgb(189, 147, 249)\n"
            "}\n"
            "\n"
            "/* Icon */\n"
            "#extraIcon {\n"
            "	background-position: center;\n"
            "	background-repeat: no-repeat;\n"
            "	background-image: url(:/icons/images/icons/icon_settings.png);\n"
            "}\n"
            "\n"
            "/* Label */\n"
            "#extraLabel { color: rgb(255, 255, 255); }\n"
            "\n"
            "/* Btn Close */\n"
            "#extraCloseColumnBtn { background-color: rgba(255, 255, 255, 0); border: none;  border-radius: 5px; }\n"
            "#extraCloseColumnBtn:hover { background-color: rgb(196, 161, 249); border-style: solid; border-radius: 4px; }\n"
            "#extraCloseColumnBtn:pressed { background-color: rgb(180, 141, 238); border-style: solid; border-radius: 4px; }\n"
            "\n"
            "/* Extra Content */\n"
            "#extraContent{\n"
            "	border"
            "-top: 3px solid rgb(40, 44, 52);\n"
            "}\n"
            "\n"
            "/* Extra Top Menus */\n"
            "#extraTopMenu .QPushButton {\n"
            "background-position: left center;\n"
            "    background-repeat: no-repeat;\n"
            "	border: none;\n"
            "	border-left: 22px solid transparent;\n"
            "	background-color:transparent;\n"
            "	text-align: left;\n"
            "	padding-left: 44px;\n"
            "}\n"
            "#extraTopMenu .QPushButton:hover {\n"
            "	background-color: rgb(40, 44, 52);\n"
            "}\n"
            "#extraTopMenu .QPushButton:pressed {	\n"
            "	background-color: rgb(189, 147, 249);\n"
            "	color: rgb(255, 255, 255);\n"
            "}\n"
            "\n"
            "/* /////////////////////////////////////////////////////////////////////////////////////////////////\n"
            "Content App */\n"
            "#contentTopBg{	\n"
            "	background-color: rgb(33, 37, 43);\n"
            "}\n"
            "#contentBottom{\n"
            "	border-top: 3px solid rgb(44, 49, 58);\n"
            "}\n"
            "\n"
            "/* Top Buttons */\n"
            "#rightButtons .QPushButton { background-color: rgba(255, 255, 255, 0); border: none;  border-radius: 5px; }\n"
            "#rightButtons .QPushButton:hover { background-color: rgb(44, 49, 57); border-sty"
            "le: solid; border-radius: 4px; }\n"
            "#rightButtons .QPushButton:pressed { background-color: rgb(23, 26, 30); border-style: solid; border-radius: 4px; }\n"
            "\n"
            "/* Theme Settings */\n"
            "#extraRightBox { background-color: rgb(44, 49, 58); }\n"
            "#themeSettingsTopDetail { background-color: rgb(189, 147, 249); }\n"
            "\n"
            "/* Bottom Bar */\n"
            "#bottomBar { background-color: rgb(44, 49, 58); }\n"
            "#bottomBar QLabel { font-size: 11px; color: rgb(113, 126, 149); padding-left: 10px; padding-right: 10px; padding-bottom: 2px; }\n"
            "\n"
            "/* CONTENT SETTINGS */\n"
            "/* MENUS */\n"
            "#contentSettings .QPushButton {	\n"
            "	background-position: left center;\n"
            "    background-repeat: no-repeat;\n"
            "	border: none;\n"
            "	border-left: 22px solid transparent;\n"
            "	background-color:transparent;\n"
            "	text-align: left;\n"
            "	padding-left: 44px;\n"
            "}\n"
            "#contentSettings .QPushButton:hover {\n"
            "	background-color: rgb(40, 44, 52);\n"
            "}\n"
            "#contentSettings .QPushButton:pressed {	\n"
            "	background-color: rgb(189, 147, 249);\n"
            "	color: rgb"
            "(255, 255, 255);\n"
            "}\n"
            "\n"
            "/* /////////////////////////////////////////////////////////////////////////////////////////////////\n"
            "QTableWidget */\n"
            "QTableWidget {	\n"
            "	background-color: transparent;\n"
            "	padding: 10px;\n"
            "	border-radius: 5px;\n"
            "	gridline-color: rgb(44, 49, 58);\n"
            "	border-bottom: 1px solid rgb(44, 49, 60);\n"
            "}\n"
            "QTableWidget::item{\n"
            "	border-color: rgb(44, 49, 60);\n"
            "	padding-left: 5px;\n"
            "	padding-right: 5px;\n"
            "	gridline-color: rgb(44, 49, 60);\n"
            "}\n"
            "QTableWidget::item:selected{\n"
            "	background-color: rgb(189, 147, 249);\n"
            "}\n"
            "QHeaderView::section{\n"
            "	background-color: rgb(33, 37, 43);\n"
            "	max-width: 30px;\n"
            "	border: 1px solid rgb(44, 49, 58);\n"
            "	border-style: none;\n"
            "    border-bottom: 1px solid rgb(44, 49, 60);\n"
            "    border-right: 1px solid rgb(44, 49, 60);\n"
            "}\n"
            "QTableWidget::horizontalHeader {	\n"
            "	background-color: rgb(33, 37, 43);\n"
            "}\n"
            "QHeaderView::section:horizontal\n"
            "{\n"
            "    border: 1px solid rgb(33, 37, 43);\n"
            "	background-co"
            "lor: rgb(33, 37, 43);\n"
            "	padding: 3px;\n"
            "	border-top-left-radius: 7px;\n"
            "    border-top-right-radius: 7px;\n"
            "}\n"
            "QHeaderView::section:vertical\n"
            "{\n"
            "    border: 1px solid rgb(44, 49, 60);\n"
            "}\n"
            "\n"
            "/* /////////////////////////////////////////////////////////////////////////////////////////////////\n"
            "LineEdit */\n"
            "QLineEdit {\n"
            "	background-color: rgb(33, 37, 43);\n"
            "	border-radius: 5px;\n"
            "	border: 2px solid rgb(33, 37, 43);\n"
            "	padding-left: 10px;\n"
            "	selection-color: rgb(255, 255, 255);\n"
            "	selection-background-color: rgb(255, 121, 198);\n"
            "}\n"
            "QLineEdit:hover {\n"
            "	border: 2px solid rgb(64, 71, 88);\n"
            "}\n"
            "QLineEdit:focus {\n"
            "	border: 2px solid rgb(91, 101, 124);\n"
            "}\n"
            "\n"
            "/* /////////////////////////////////////////////////////////////////////////////////////////////////\n"
            "PlainTextEdit */\n"
            "QPlainTextEdit {\n"
            "	background-color: rgb(27, 29, 35);\n"
            "	border-radius: 5px;\n"
            "	padding: 10px;\n"
            "	selection-color: rgb(255, 255, 255);\n"
            "	selection-background-c"
            "olor: rgb(255, 121, 198);\n"
            "}\n"
            "QPlainTextEdit  QScrollBar:vertical {\n"
            "    width: 8px;\n"
            " }\n"
            "QPlainTextEdit  QScrollBar:horizontal {\n"
            "    height: 8px;\n"
            " }\n"
            "QPlainTextEdit:hover {\n"
            "	border: 2px solid rgb(64, 71, 88);\n"
            "}\n"
            "QPlainTextEdit:focus {\n"
            "	border: 2px solid rgb(91, 101, 124);\n"
            "}\n"
            "\n"
            "/* /////////////////////////////////////////////////////////////////////////////////////////////////\n"
            "ScrollBars */\n"
            "QScrollBar:horizontal {\n"
            "    border: none;\n"
            "    background: rgb(52, 59, 72);\n"
            "    height: 8px;\n"
            "    margin: 0px 21px 0 21px;\n"
            "	border-radius: 0px;\n"
            "}\n"
            "QScrollBar::handle:horizontal {\n"
            "    background: rgb(189, 147, 249);\n"
            "    min-width: 25px;\n"
            "	border-radius: 4px\n"
            "}\n"
            "QScrollBar::add-line:horizontal {\n"
            "    border: none;\n"
            "    background: rgb(55, 63, 77);\n"
            "    width: 20px;\n"
            "	border-top-right-radius: 4px;\n"
            "    border-bottom-right-radius: 4px;\n"
            "    subcontrol-position: right;\n"
            "    subcontrol-origin: margin;\n"
            "}\n"
            ""
            "QScrollBar::sub-line:horizontal {\n"
            "    border: none;\n"
            "    background: rgb(55, 63, 77);\n"
            "    width: 20px;\n"
            "	border-top-left-radius: 4px;\n"
            "    border-bottom-left-radius: 4px;\n"
            "    subcontrol-position: left;\n"
            "    subcontrol-origin: margin;\n"
            "}\n"
            "QScrollBar::up-arrow:horizontal, QScrollBar::down-arrow:horizontal\n"
            "{\n"
            "     background: none;\n"
            "}\n"
            "QScrollBar::add-page:horizontal, QScrollBar::sub-page:horizontal\n"
            "{\n"
            "     background: none;\n"
            "}\n"
            " QScrollBar:vertical {\n"
            "	border: none;\n"
            "    background: rgb(52, 59, 72);\n"
            "    width: 8px;\n"
            "    margin: 21px 0 21px 0;\n"
            "	border-radius: 0px;\n"
            " }\n"
            " QScrollBar::handle:vertical {	\n"
            "	background: rgb(189, 147, 249);\n"
            "    min-height: 25px;\n"
            "	border-radius: 4px\n"
            " }\n"
            " QScrollBar::add-line:vertical {\n"
            "     border: none;\n"
            "    background: rgb(55, 63, 77);\n"
            "     height: 20px;\n"
            "	border-bottom-left-radius: 4px;\n"
            "    border-bottom-right-radius: 4px;\n"
            "     subcontrol-position: bottom;\n"
            "     su"
            "bcontrol-origin: margin;\n"
            " }\n"
            " QScrollBar::sub-line:vertical {\n"
            "	border: none;\n"
            "    background: rgb(55, 63, 77);\n"
            "     height: 20px;\n"
            "	border-top-left-radius: 4px;\n"
            "    border-top-right-radius: 4px;\n"
            "     subcontrol-position: top;\n"
            "     subcontrol-origin: margin;\n"
            " }\n"
            " QScrollBar::up-arrow:vertical, QScrollBar::down-arrow:vertical {\n"
            "     background: none;\n"
            " }\n"
            "\n"
            " QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {\n"
            "     background: none;\n"
            " }\n"
            "\n"
            "/* /////////////////////////////////////////////////////////////////////////////////////////////////\n"
            "CheckBox */\n"
            "QCheckBox::indicator {\n"
            "    border: 3px solid rgb(52, 59, 72);\n"
            "	width: 15px;\n"
            "	height: 15px;\n"
            "	border-radius: 10px;\n"
            "    background: rgb(44, 49, 60);\n"
            "}\n"
            "QCheckBox::indicator:hover {\n"
            "    border: 3px solid rgb(58, 66, 81);\n"
            "}\n"
            "QCheckBox::indicator:checked {\n"
            "    background: 3px solid rgb(52, 59, 72);\n"
            "	border: 3px solid rgb(52, 59, 72);	\n"
            "	back"
            "ground-image: url(:/icons/images/icons/cil-check-alt.png);\n"
            "}\n"
            "\n"
            "/* /////////////////////////////////////////////////////////////////////////////////////////////////\n"
            "RadioButton */\n"
            "QRadioButton::indicator {\n"
            "    border: 3px solid rgb(52, 59, 72);\n"
            "	width: 15px;\n"
            "	height: 15px;\n"
            "	border-radius: 10px;\n"
            "    background: rgb(44, 49, 60);\n"
            "}\n"
            "QRadioButton::indicator:hover {\n"
            "    border: 3px solid rgb(58, 66, 81);\n"
            "}\n"
            "QRadioButton::indicator:checked {\n"
            "    background: 3px solid rgb(94, 106, 130);\n"
            "	border: 3px solid rgb(52, 59, 72);	\n"
            "}\n"
            "\n"
            "/* /////////////////////////////////////////////////////////////////////////////////////////////////\n"
            "ComboBox */\n"
            "QComboBox{\n"
            "	background-color: rgb(27, 29, 35);\n"
            "	border-radius: 5px;\n"
            "	border: 2px solid rgb(33, 37, 43);\n"
            "	padding: 5px;\n"
            "	padding-left: 10px;\n"
            "}\n"
            "QComboBox:hover{\n"
            "	border: 2px solid rgb(64, 71, 88);\n"
            "}\n"
            "QComboBox::drop-down {\n"
            "	subcontrol-origin: padding;\n"
            "	subco"
            "ntrol-position: top right;\n"
            "	width: 25px; \n"
            "	border-left-width: 3px;\n"
            "	border-left-color: rgba(39, 44, 54, 150);\n"
            "	border-left-style: solid;\n"
            "	border-top-right-radius: 3px;\n"
            "	border-bottom-right-radius: 3px;	\n"
            "	background-image: url(:/icons/images/icons/cil-arrow-bottom.png);\n"
            "	background-position: center;\n"
            "	background-repeat: no-reperat;\n"
            " }\n"
            "QComboBox QAbstractItemView {\n"
            "	color: rgb(255, 121, 198);	\n"
            "	background-color: rgb(33, 37, 43);\n"
            "	padding: 10px;\n"
            "	selection-background-color: rgb(39, 44, 54);\n"
            "}\n"
            "\n"
            "/* /////////////////////////////////////////////////////////////////////////////////////////////////\n"
            "Sliders */\n"
            "QSlider::groove:horizontal {\n"
            "    border-radius: 5px;\n"
            "    height: 10px;\n"
            "	margin: 0px;\n"
            "	background-color: rgb(52, 59, 72);\n"
            "}\n"
            "QSlider::groove:horizontal:hover {\n"
            "	background-color: rgb(55, 62, 76);\n"
            "}\n"
            "QSlider::handle:horizontal {\n"
            "    background-color: rgb(189, 147, 249);\n"
            "    border: none;\n"
            "    h"
            "eight: 10px;\n"
            "    width: 10px;\n"
            "    margin: 0px;\n"
            "	border-radius: 5px;\n"
            "}\n"
            "QSlider::handle:horizontal:hover {\n"
            "    background-color: rgb(195, 155, 255);\n"
            "}\n"
            "QSlider::handle:horizontal:pressed {\n"
            "    background-color: rgb(255, 121, 198);\n"
            "}\n"
            "\n"
            "QSlider::groove:vertical {\n"
            "    border-radius: 5px;\n"
            "    width: 10px;\n"
            "    margin: 0px;\n"
            "	background-color: rgb(52, 59, 72);\n"
            "}\n"
            "QSlider::groove:vertical:hover {\n"
            "	background-color: rgb(55, 62, 76);\n"
            "}\n"
            "QSlider::handle:vertical {\n"
            "    background-color: rgb(189, 147, 249);\n"
            "	border: none;\n"
            "    height: 10px;\n"
            "    width: 10px;\n"
            "    margin: 0px;\n"
            "	border-radius: 5px;\n"
            "}\n"
            "QSlider::handle:vertical:hover {\n"
            "    background-color: rgb(195, 155, 255);\n"
            "}\n"
            "QSlider::handle:vertical:pressed {\n"
            "    background-color: rgb(255, 121, 198);\n"
            "}\n"
            "\n"
            "/* /////////////////////////////////////////////////////////////////////////////////////////////////\n"
            "CommandLinkButton */\n"
            "QCommandLi"
            "nkButton {	\n"
            "	color: rgb(255, 121, 198);\n"
            "	border-radius: 5px;\n"
            "	padding: 5px;\n"
            "	color: rgb(255, 170, 255);\n"
            "}\n"
            "QCommandLinkButton:hover {	\n"
            "	color: rgb(255, 170, 255);\n"
            "	background-color: rgb(44, 49, 60);\n"
            "}\n"
            "QCommandLinkButton:pressed {	\n"
            "	color: rgb(189, 147, 249);\n"
            "	background-color: rgb(52, 58, 71);\n"
            "}\n"
            "\n"
            "/* /////////////////////////////////////////////////////////////////////////////////////////////////\n"
            "Button */\n"
            "#pagesContainer QPushButton {\n"
            "	border: 2px solid rgb(52, 59, 72);\n"
            "	border-radius: 5px;	\n"
            "	background-color: rgb(52, 59, 72);\n"
            "}\n"
            "#pagesContainer QPushButton:hover {\n"
            "	background-color: rgb(57, 65, 80);\n"
            "	border: 2px solid rgb(61, 70, 86);\n"
            "}\n"
            "#pagesContainer QPushButton:pressed {	\n"
            "	background-color: rgb(35, 40, 49);\n"
            "	border: 2px solid rgb(43, 50, 61);\n"
            "}\n"
            "\n"
            ""
        )
        self.appMargins = QVBoxLayout(self.styleSheet)
        self.appMargins.setSpacing(0)
        self.appMargins.setObjectName("appMargins")
        self.appMargins.setContentsMargins(10, 10, 10, 10)
        self.bgApp = QFrame(self.styleSheet)
        self.bgApp.setObjectName("bgApp")
        self.bgApp.setStyleSheet("")
        self.bgApp.setFrameShape(QFrame.NoFrame)
        self.bgApp.setFrameShadow(QFrame.Raised)
        self.appLayout = QHBoxLayout(self.bgApp)
        self.appLayout.setSpacing(0)
        self.appLayout.setObjectName("appLayout")
        self.appLayout.setContentsMargins(0, 0, 0, 0)
        self.leftMenuBg = QFrame(self.bgApp)
        self.leftMenuBg.setObjectName("leftMenuBg")
        self.leftMenuBg.setMinimumSize(QSize(60, 0))
        self.leftMenuBg.setMaximumSize(QSize(60, 16777215))
        self.leftMenuBg.setFrameShape(QFrame.NoFrame)
        self.leftMenuBg.setFrameShadow(QFrame.Raised)
        self.verticalLayout_3 = QVBoxLayout(self.leftMenuBg)
        self.verticalLayout_3.setSpacing(0)
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.verticalLayout_3.setContentsMargins(0, 0, 0, 0)
        self.topLogoInfo = QFrame(self.leftMenuBg)
        self.topLogoInfo.setObjectName("topLogoInfo")
        self.topLogoInfo.setMinimumSize(QSize(0, 60))
        self.topLogoInfo.setMaximumSize(QSize(16777215, 60))
        self.topLogoInfo.setFrameShape(QFrame.NoFrame)
        self.topLogoInfo.setFrameShadow(QFrame.Raised)
        self.topLogo = QFrame(self.topLogoInfo)
        self.topLogo.setObjectName("topLogo")
        self.topLogo.setGeometry(QRect(5, 5, 50, 50))
        self.topLogo.setMinimumSize(QSize(50, 50))
        self.topLogo.setMaximumSize(QSize(50, 50))
        self.topLogo.setAutoFillBackground(False)
        self.topLogo.setStyleSheet(
            "background-image: url(:/images/images/images/Picture3.png);"
        )
        self.topLogo.setFrameShape(QFrame.NoFrame)
        self.topLogo.setFrameShadow(QFrame.Raised)

        self.verticalLayout_3.addWidget(self.topLogoInfo)

        self.leftMenuFrame = QFrame(self.leftMenuBg)
        self.leftMenuFrame.setObjectName("leftMenuFrame")
        self.leftMenuFrame.setFrameShape(QFrame.NoFrame)
        self.leftMenuFrame.setFrameShadow(QFrame.Raised)
        self.verticalMenuLayout = QVBoxLayout(self.leftMenuFrame)
        self.verticalMenuLayout.setSpacing(0)
        self.verticalMenuLayout.setObjectName("verticalMenuLayout")
        self.verticalMenuLayout.setContentsMargins(0, 0, 0, 0)
        self.topMenu = QFrame(self.leftMenuFrame)
        self.topMenu.setObjectName("topMenu")
        self.topMenu.setFrameShape(QFrame.NoFrame)
        self.topMenu.setFrameShadow(QFrame.Raised)
        self.verticalLayout_8 = QVBoxLayout(self.topMenu)
        self.verticalLayout_8.setSpacing(0)
        self.verticalLayout_8.setObjectName("verticalLayout_8")
        self.verticalLayout_8.setContentsMargins(0, 0, 0, 0)
        self.btn_home = QPushButton(self.topMenu)
        self.btn_home.setObjectName("btn_home")
        sizePolicy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.btn_home.sizePolicy().hasHeightForWidth())
        self.btn_home.setSizePolicy(sizePolicy)
        self.btn_home.setMinimumSize(QSize(0, 45))
        self.btn_home.setFont(font)
        self.btn_home.setCursor(QCursor(Qt.PointingHandCursor))
        self.btn_home.setLayoutDirection(Qt.LeftToRight)
        self.btn_home.setStyleSheet(
            "background-image: url(:/icons/images/icons/cil-home.png);"
        )

        self.verticalLayout_8.addWidget(self.btn_home)

        self.verticalMenuLayout.addWidget(self.topMenu, 0, Qt.AlignTop)

        self.verticalLayout_3.addWidget(self.leftMenuFrame)

        self.appLayout.addWidget(self.leftMenuBg)

        self.contentBox = QFrame(self.bgApp)
        self.contentBox.setObjectName("contentBox")
        self.contentBox.setFrameShape(QFrame.NoFrame)
        self.contentBox.setFrameShadow(QFrame.Raised)
        self.verticalLayout_2 = QVBoxLayout(self.contentBox)
        self.verticalLayout_2.setSpacing(0)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.verticalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.contentTopBg = QFrame(self.contentBox)
        self.contentTopBg.setObjectName("contentTopBg")
        self.contentTopBg.setMinimumSize(QSize(0, 60))
        self.contentTopBg.setMaximumSize(QSize(16777215, 60))
        self.contentTopBg.setFrameShape(QFrame.NoFrame)
        self.contentTopBg.setFrameShadow(QFrame.Raised)
        self.horizontalLayout = QHBoxLayout(self.contentTopBg)
        self.horizontalLayout.setSpacing(0)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.horizontalLayout.setContentsMargins(0, 0, 10, 0)
        self.leftBox = QFrame(self.contentTopBg)
        self.leftBox.setObjectName("leftBox")
        sizePolicy1 = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.leftBox.sizePolicy().hasHeightForWidth())
        self.leftBox.setSizePolicy(sizePolicy1)
        self.leftBox.setFrameShape(QFrame.NoFrame)
        self.leftBox.setFrameShadow(QFrame.Raised)
        self.horizontalLayout_3 = QHBoxLayout(self.leftBox)
        self.horizontalLayout_3.setSpacing(0)
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.horizontalLayout_3.setContentsMargins(0, 0, 0, 0)
        self.titleRightInfo = QLabel(self.leftBox)
        self.titleRightInfo.setObjectName("titleRightInfo")
        sizePolicy2 = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
        sizePolicy2.setHorizontalStretch(0)
        sizePolicy2.setVerticalStretch(0)
        sizePolicy2.setHeightForWidth(
            self.titleRightInfo.sizePolicy().hasHeightForWidth()
        )
        self.titleRightInfo.setSizePolicy(sizePolicy2)
        self.titleRightInfo.setMaximumSize(QSize(16777215, 45))
        font1 = QFont()
        font1.setFamilies(["Segoe UI"])
        font1.setPointSize(18)
        font1.setBold(False)
        font1.setItalic(False)
        self.titleRightInfo.setFont(font1)
        self.titleRightInfo.setStyleSheet("font:18pt;")
        self.titleRightInfo.setAlignment(
            Qt.AlignLeading | Qt.AlignLeft | Qt.AlignVCenter
        )

        self.horizontalLayout_3.addWidget(self.titleRightInfo)

        self.horizontalLayout.addWidget(self.leftBox)

        self.rightButtons = QFrame(self.contentTopBg)
        self.rightButtons.setObjectName("rightButtons")
        self.rightButtons.setMinimumSize(QSize(0, 28))
        self.rightButtons.setFrameShape(QFrame.NoFrame)
        self.rightButtons.setFrameShadow(QFrame.Raised)
        self.horizontalLayout_2 = QHBoxLayout(self.rightButtons)
        self.horizontalLayout_2.setSpacing(5)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.horizontalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.minimizeAppBtn = QPushButton(self.rightButtons)
        self.minimizeAppBtn.setObjectName("minimizeAppBtn")
        self.minimizeAppBtn.setMinimumSize(QSize(28, 28))
        self.minimizeAppBtn.setMaximumSize(QSize(28, 28))
        self.minimizeAppBtn.setCursor(QCursor(Qt.PointingHandCursor))
        icon1 = QIcon()
        icon1.addFile(
            ":/icons/images/icons/icon_minimize.png", QSize(), QIcon.Normal, QIcon.Off
        )
        self.minimizeAppBtn.setIcon(icon1)
        self.minimizeAppBtn.setIconSize(QSize(20, 20))

        self.horizontalLayout_2.addWidget(self.minimizeAppBtn)

        self.maximizeRestoreAppBtn = QPushButton(self.rightButtons)
        self.maximizeRestoreAppBtn.setObjectName("maximizeRestoreAppBtn")
        self.maximizeRestoreAppBtn.setMinimumSize(QSize(28, 28))
        self.maximizeRestoreAppBtn.setMaximumSize(QSize(28, 28))
        font2 = QFont()
        font2.setFamilies(["Segoe UI"])
        font2.setPointSize(10)
        font2.setBold(False)
        font2.setItalic(False)
        font2.setStyleStrategy(QFont.PreferDefault)
        self.maximizeRestoreAppBtn.setFont(font2)
        self.maximizeRestoreAppBtn.setCursor(QCursor(Qt.PointingHandCursor))
        icon2 = QIcon()
        icon2.addFile(
            ":/icons/images/icons/icon_restore.png", QSize(), QIcon.Normal, QIcon.Off
        )
        self.maximizeRestoreAppBtn.setIcon(icon2)
        self.maximizeRestoreAppBtn.setIconSize(QSize(20, 20))

        self.horizontalLayout_2.addWidget(self.maximizeRestoreAppBtn)

        self.closeAppBtn = QPushButton(self.rightButtons)
        self.closeAppBtn.setObjectName("closeAppBtn")
        self.closeAppBtn.setMinimumSize(QSize(28, 28))
        self.closeAppBtn.setMaximumSize(QSize(28, 28))
        self.closeAppBtn.setCursor(QCursor(Qt.PointingHandCursor))
        icon3 = QIcon()
        icon3.addFile(
            ":/icons/images/icons/icon_close.png", QSize(), QIcon.Normal, QIcon.Off
        )
        self.closeAppBtn.setIcon(icon3)
        self.closeAppBtn.setIconSize(QSize(20, 20))

        self.horizontalLayout_2.addWidget(self.closeAppBtn)

        self.horizontalLayout.addWidget(self.rightButtons, 0, Qt.AlignRight)

        self.verticalLayout_2.addWidget(self.contentTopBg)

        self.contentBottom = QFrame(self.contentBox)
        self.contentBottom.setObjectName("contentBottom")
        self.contentBottom.setFrameShape(QFrame.NoFrame)
        self.contentBottom.setFrameShadow(QFrame.Raised)
        self.verticalLayout_6 = QVBoxLayout(self.contentBottom)
        self.verticalLayout_6.setSpacing(0)
        self.verticalLayout_6.setObjectName("verticalLayout_6")
        self.verticalLayout_6.setContentsMargins(0, 0, 0, 0)
        self.content = QFrame(self.contentBottom)
        self.content.setObjectName("content")
        self.content.setFrameShape(QFrame.NoFrame)
        self.content.setFrameShadow(QFrame.Raised)
        self.horizontalLayout_4 = QHBoxLayout(self.content)
        self.horizontalLayout_4.setSpacing(0)
        self.horizontalLayout_4.setObjectName("horizontalLayout_4")
        self.horizontalLayout_4.setContentsMargins(0, 0, 0, 0)
        self.pagesContainer = QFrame(self.content)
        self.pagesContainer.setObjectName("pagesContainer")
        self.pagesContainer.setStyleSheet("")
        self.pagesContainer.setFrameShape(QFrame.NoFrame)
        self.pagesContainer.setFrameShadow(QFrame.Raised)
        self.verticalLayout_15 = QVBoxLayout(self.pagesContainer)
        self.verticalLayout_15.setSpacing(0)
        self.verticalLayout_15.setObjectName("verticalLayout_15")
        self.verticalLayout_15.setContentsMargins(10, 10, 10, 10)
        self.stackedWidget = QStackedWidget(self.pagesContainer)
        self.stackedWidget.setObjectName("stackedWidget")
        self.stackedWidget.setStyleSheet("background: transparent;")
        self.home = QWidget()
        self.home.setObjectName("home")
        self.home.setStyleSheet("")
        self.gridLayout_2 = QGridLayout(self.home)
        self.gridLayout_2.setSpacing(0)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.gridLayout_2.setContentsMargins(0, 0, 0, 0)
        self.gridWidget = QWidget(self.home)
        self.gridWidget.setObjectName("gridWidget")
        self.gridLayout = QGridLayout(self.gridWidget)
        self.gridLayout.setObjectName("gridLayout")
        self.gridLayout.setSizeConstraint(QLayout.SetMaximumSize)
        self.gridLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_4 = QVBoxLayout()
        self.verticalLayout_4.setObjectName("verticalLayout_4")
        self.verticalLayout_4.setContentsMargins(5, -1, 5, -1)
        self.horizontalLayout_6 = QHBoxLayout()
        self.horizontalLayout_6.setSpacing(0)
        self.horizontalLayout_6.setObjectName("horizontalLayout_6")
        self.name_0 = QLabel(self.gridWidget)
        self.name_0.setObjectName("name_0")
        self.name_0.setMaximumSize(QSize(16777215, 50))
        self.name_0.setAlignment(Qt.AlignBottom | Qt.AlignLeading | Qt.AlignLeft)

        self.horizontalLayout_6.addWidget(self.name_0)

        self.device_0 = QLabel(self.gridWidget)
        self.device_0.setObjectName("device_0")
        self.device_0.setMaximumSize(QSize(16777215, 50))
        self.device_0.setAlignment(Qt.AlignBottom | Qt.AlignRight | Qt.AlignTrailing)

        self.horizontalLayout_6.addWidget(self.device_0)

        self.verticalLayout_4.addLayout(self.horizontalLayout_6)

        self.value_0 = QLabel(self.gridWidget)
        self.value_0.setObjectName("value_0")
        self.value_0.setEnabled(True)
        font3 = QFont()
        font3.setFamilies(["Segoe UI"])
        font3.setPointSize(48)
        font3.setBold(False)
        font3.setItalic(False)
        self.value_0.setFont(font3)
        self.value_0.setContextMenuPolicy(Qt.DefaultContextMenu)
        self.value_0.setStyleSheet("font: 48pt;")
        self.value_0.setAlignment(Qt.AlignCenter)

        self.verticalLayout_4.addWidget(self.value_0)

        self.unit_0 = QLabel(self.gridWidget)
        self.unit_0.setObjectName("unit_0")
        self.unit_0.setMaximumSize(QSize(16777215, 50))
        self.unit_0.setAlignment(Qt.AlignHCenter | Qt.AlignTop)

        self.verticalLayout_4.addWidget(self.unit_0)

        self.gridLayout.addLayout(self.verticalLayout_4, 0, 0, 1, 1)

        self.verticalLayout_9 = QVBoxLayout()
        self.verticalLayout_9.setObjectName("verticalLayout_9")
        self.verticalLayout_9.setContentsMargins(5, -1, 5, -1)
        self.horizontalLayout_7 = QHBoxLayout()
        self.horizontalLayout_7.setSpacing(0)
        self.horizontalLayout_7.setObjectName("horizontalLayout_7")
        self.name_1 = QLabel(self.gridWidget)
        self.name_1.setObjectName("name_1")
        self.name_1.setMaximumSize(QSize(16777215, 50))
        self.name_1.setAlignment(Qt.AlignBottom | Qt.AlignLeading | Qt.AlignLeft)

        self.horizontalLayout_7.addWidget(self.name_1)

        self.device_1 = QLabel(self.gridWidget)
        self.device_1.setObjectName("device_1")
        self.device_1.setMaximumSize(QSize(16777215, 50))
        self.device_1.setAlignment(Qt.AlignBottom | Qt.AlignRight | Qt.AlignTrailing)

        self.horizontalLayout_7.addWidget(self.device_1)

        self.verticalLayout_9.addLayout(self.horizontalLayout_7)

        self.value_1 = QLabel(self.gridWidget)
        self.value_1.setObjectName("value_1")
        self.value_1.setStyleSheet("font: 48pt;")
        self.value_1.setAlignment(Qt.AlignCenter)

        self.verticalLayout_9.addWidget(self.value_1)

        self.unit_1 = QLabel(self.gridWidget)
        self.unit_1.setObjectName("unit_1")
        self.unit_1.setMaximumSize(QSize(16777215, 50))
        self.unit_1.setAlignment(Qt.AlignHCenter | Qt.AlignTop)

        self.verticalLayout_9.addWidget(self.unit_1)

        self.gridLayout.addLayout(self.verticalLayout_9, 0, 1, 1, 1)

        self.verticalLayout_17 = QVBoxLayout()
        self.verticalLayout_17.setObjectName("verticalLayout_17")
        self.verticalLayout_17.setContentsMargins(5, -1, 5, -1)
        self.horizontalLayout_11 = QHBoxLayout()
        self.horizontalLayout_11.setSpacing(0)
        self.horizontalLayout_11.setObjectName("horizontalLayout_11")
        self.horizontalLayout_11.setSizeConstraint(QLayout.SetDefaultConstraint)
        self.name_5 = QLabel(self.gridWidget)
        self.name_5.setObjectName("name_5")
        self.name_5.setMaximumSize(QSize(16777215, 50))
        self.name_5.setAlignment(Qt.AlignBottom | Qt.AlignLeading | Qt.AlignLeft)

        self.horizontalLayout_11.addWidget(self.name_5)

        self.deivce_5 = QLabel(self.gridWidget)
        self.deivce_5.setObjectName("deivce_5")
        self.deivce_5.setMaximumSize(QSize(16777215, 50))
        self.deivce_5.setAlignment(Qt.AlignBottom | Qt.AlignRight | Qt.AlignTrailing)

        self.horizontalLayout_11.addWidget(self.deivce_5)

        self.verticalLayout_17.addLayout(self.horizontalLayout_11)

        self.value_5 = QLabel(self.gridWidget)
        self.value_5.setObjectName("value_5")
        self.value_5.setStyleSheet("font: 48pt;")
        self.value_5.setAlignment(Qt.AlignCenter)

        self.verticalLayout_17.addWidget(self.value_5)

        self.unit_5 = QLabel(self.gridWidget)
        self.unit_5.setObjectName("unit_5")
        self.unit_5.setMaximumSize(QSize(16777215, 50))
        self.unit_5.setAlignment(Qt.AlignHCenter | Qt.AlignTop)

        self.verticalLayout_17.addWidget(self.unit_5)

        self.gridLayout.addLayout(self.verticalLayout_17, 1, 0, 1, 1)

        self.verticalLayout_16 = QVBoxLayout()
        self.verticalLayout_16.setObjectName("verticalLayout_16")
        self.verticalLayout_16.setContentsMargins(5, -1, 5, -1)
        self.horizontalLayout_9 = QHBoxLayout()
        self.horizontalLayout_9.setSpacing(0)
        self.horizontalLayout_9.setObjectName("horizontalLayout_9")
        self.name_3 = QLabel(self.gridWidget)
        self.name_3.setObjectName("name_3")
        self.name_3.setMaximumSize(QSize(16777215, 50))
        self.name_3.setAlignment(Qt.AlignBottom | Qt.AlignLeading | Qt.AlignLeft)

        self.horizontalLayout_9.addWidget(self.name_3)

        self.device_3 = QLabel(self.gridWidget)
        self.device_3.setObjectName("device_3")
        self.device_3.setMaximumSize(QSize(16777215, 50))
        self.device_3.setAlignment(Qt.AlignBottom | Qt.AlignRight | Qt.AlignTrailing)

        self.horizontalLayout_9.addWidget(self.device_3)

        self.verticalLayout_16.addLayout(self.horizontalLayout_9)

        self.value_3 = QLabel(self.gridWidget)
        self.value_3.setObjectName("value_3")
        self.value_3.setAlignment(Qt.AlignCenter)

        self.verticalLayout_16.addWidget(self.value_3)

        self.unit_3 = QLabel(self.gridWidget)
        self.unit_3.setObjectName("unit_3")
        self.unit_3.setMaximumSize(QSize(16777215, 50))
        self.unit_3.setAlignment(Qt.AlignHCenter | Qt.AlignTop)

        self.verticalLayout_16.addWidget(self.unit_3)

        self.gridLayout.addLayout(self.verticalLayout_16, 0, 3, 1, 1)

        self.verticalLayout_18 = QVBoxLayout()
        self.verticalLayout_18.setObjectName("verticalLayout_18")
        self.verticalLayout_18.setContentsMargins(5, -1, 5, -1)
        self.horizontalLayout_12 = QHBoxLayout()
        self.horizontalLayout_12.setSpacing(0)
        self.horizontalLayout_12.setObjectName("horizontalLayout_12")
        self.name_6 = QLabel(self.gridWidget)
        self.name_6.setObjectName("name_6")
        self.name_6.setMaximumSize(QSize(16777215, 50))
        self.name_6.setAlignment(Qt.AlignBottom | Qt.AlignLeading | Qt.AlignLeft)

        self.horizontalLayout_12.addWidget(self.name_6)

        self.device_6 = QLabel(self.gridWidget)
        self.device_6.setObjectName("device_6")
        self.device_6.setAlignment(Qt.AlignBottom | Qt.AlignRight | Qt.AlignTrailing)

        self.horizontalLayout_12.addWidget(self.device_6)

        self.verticalLayout_18.addLayout(self.horizontalLayout_12)

        self.value_6 = QLabel(self.gridWidget)
        self.value_6.setObjectName("value_6")
        self.value_6.setStyleSheet("font: 48pt;")
        self.value_6.setAlignment(Qt.AlignCenter)

        self.verticalLayout_18.addWidget(self.value_6)

        self.unit_6 = QLabel(self.gridWidget)
        self.unit_6.setObjectName("unit_6")
        self.unit_6.setMaximumSize(QSize(16777215, 50))
        self.unit_6.setAlignment(Qt.AlignHCenter | Qt.AlignTop)

        self.verticalLayout_18.addWidget(self.unit_6)

        self.gridLayout.addLayout(self.verticalLayout_18, 1, 1, 1, 1)

        self.verticalLayout_19 = QVBoxLayout()
        self.verticalLayout_19.setObjectName("verticalLayout_19")
        self.verticalLayout_19.setContentsMargins(5, -1, 5, -1)
        self.horizontalLayout_14 = QHBoxLayout()
        self.horizontalLayout_14.setSpacing(0)
        self.horizontalLayout_14.setObjectName("horizontalLayout_14")
        self.name_8 = QLabel(self.gridWidget)
        self.name_8.setObjectName("name_8")
        self.name_8.setMaximumSize(QSize(16777215, 50))
        self.name_8.setAlignment(Qt.AlignBottom | Qt.AlignLeading | Qt.AlignLeft)

        self.horizontalLayout_14.addWidget(self.name_8)

        self.device_8 = QLabel(self.gridWidget)
        self.device_8.setObjectName("device_8")
        self.device_8.setMaximumSize(QSize(16777215, 50))
        self.device_8.setAlignment(Qt.AlignBottom | Qt.AlignRight | Qt.AlignTrailing)

        self.horizontalLayout_14.addWidget(self.device_8)

        self.verticalLayout_19.addLayout(self.horizontalLayout_14)

        self.value_8 = QLabel(self.gridWidget)
        self.value_8.setObjectName("value_8")
        self.value_8.setAlignment(Qt.AlignCenter)

        self.verticalLayout_19.addWidget(self.value_8)

        self.unit_8 = QLabel(self.gridWidget)
        self.unit_8.setObjectName("unit_8")
        self.unit_8.setMaximumSize(QSize(16777215, 50))
        self.unit_8.setAlignment(Qt.AlignHCenter | Qt.AlignTop)

        self.verticalLayout_19.addWidget(self.unit_8)

        self.gridLayout.addLayout(self.verticalLayout_19, 1, 3, 1, 1)

        self.verticalLayout_22 = QVBoxLayout()
        self.verticalLayout_22.setObjectName("verticalLayout_22")
        self.verticalLayout_22.setContentsMargins(5, -1, 5, -1)
        self.horizontalLayout_15 = QHBoxLayout()
        self.horizontalLayout_15.setSpacing(0)
        self.horizontalLayout_15.setObjectName("horizontalLayout_15")
        self.name_9 = QLabel(self.gridWidget)
        self.name_9.setObjectName("name_9")
        self.name_9.setMaximumSize(QSize(16777215, 50))
        self.name_9.setAlignment(Qt.AlignBottom | Qt.AlignLeading | Qt.AlignLeft)

        self.horizontalLayout_15.addWidget(self.name_9)

        self.device_9 = QLabel(self.gridWidget)
        self.device_9.setObjectName("device_9")
        self.device_9.setMaximumSize(QSize(16777215, 50))
        self.device_9.setAlignment(Qt.AlignBottom | Qt.AlignRight | Qt.AlignTrailing)

        self.horizontalLayout_15.addWidget(self.device_9)

        self.verticalLayout_22.addLayout(self.horizontalLayout_15)

        self.value_9 = QLabel(self.gridWidget)
        self.value_9.setObjectName("value_9")
        self.value_9.setAlignment(Qt.AlignCenter)

        self.verticalLayout_22.addWidget(self.value_9)

        self.unit_9 = QLabel(self.gridWidget)
        self.unit_9.setObjectName("unit_9")
        self.unit_9.setMaximumSize(QSize(16777215, 50))
        self.unit_9.setAlignment(Qt.AlignHCenter | Qt.AlignTop)

        self.verticalLayout_22.addWidget(self.unit_9)

        self.gridLayout.addLayout(self.verticalLayout_22, 1, 4, 1, 1)

        self.verticalLayout_21 = QVBoxLayout()
        self.verticalLayout_21.setObjectName("verticalLayout_21")
        self.verticalLayout_21.setContentsMargins(5, -1, 5, -1)
        self.horizontalLayout_10 = QHBoxLayout()
        self.horizontalLayout_10.setSpacing(0)
        self.horizontalLayout_10.setObjectName("horizontalLayout_10")
        self.name_4 = QLabel(self.gridWidget)
        self.name_4.setObjectName("name_4")
        self.name_4.setMaximumSize(QSize(16777215, 50))
        self.name_4.setAlignment(Qt.AlignBottom | Qt.AlignLeading | Qt.AlignLeft)

        self.horizontalLayout_10.addWidget(self.name_4)

        self.device_4 = QLabel(self.gridWidget)
        self.device_4.setObjectName("device_4")
        self.device_4.setMaximumSize(QSize(16777215, 50))
        self.device_4.setAlignment(Qt.AlignBottom | Qt.AlignRight | Qt.AlignTrailing)

        self.horizontalLayout_10.addWidget(self.device_4)

        self.verticalLayout_21.addLayout(self.horizontalLayout_10)

        self.value_4 = QLabel(self.gridWidget)
        self.value_4.setObjectName("value_4")
        self.value_4.setStyleSheet("font: 48pt;")
        self.value_4.setAlignment(Qt.AlignCenter)

        self.verticalLayout_21.addWidget(self.value_4)

        self.unit_4 = QLabel(self.gridWidget)
        self.unit_4.setObjectName("unit_4")
        self.unit_4.setMaximumSize(QSize(16777215, 50))
        self.unit_4.setAlignment(Qt.AlignHCenter | Qt.AlignTop)

        self.verticalLayout_21.addWidget(self.unit_4)

        self.gridLayout.addLayout(self.verticalLayout_21, 0, 4, 1, 1)

        self.verticalLayout_12 = QVBoxLayout()
        self.verticalLayout_12.setObjectName("verticalLayout_12")
        self.verticalLayout_12.setContentsMargins(5, -1, 5, -1)
        self.horizontalLayout_8 = QHBoxLayout()
        self.horizontalLayout_8.setSpacing(0)
        self.horizontalLayout_8.setObjectName("horizontalLayout_8")
        self.name_2 = QLabel(self.gridWidget)
        self.name_2.setObjectName("name_2")
        self.name_2.setMaximumSize(QSize(16777215, 50))
        self.name_2.setAlignment(Qt.AlignBottom | Qt.AlignLeading | Qt.AlignLeft)

        self.horizontalLayout_8.addWidget(self.name_2)

        self.deivce_2 = QLabel(self.gridWidget)
        self.deivce_2.setObjectName("deivce_2")
        self.deivce_2.setMaximumSize(QSize(16777215, 50))
        self.deivce_2.setAlignment(Qt.AlignBottom | Qt.AlignRight | Qt.AlignTrailing)

        self.horizontalLayout_8.addWidget(self.deivce_2)

        self.verticalLayout_12.addLayout(self.horizontalLayout_8)

        self.value_2 = QLabel(self.gridWidget)
        self.value_2.setObjectName("value_2")
        self.value_2.setStyleSheet("font: 48pt;")
        self.value_2.setAlignment(Qt.AlignCenter)

        self.verticalLayout_12.addWidget(self.value_2)

        self.unit_2 = QLabel(self.gridWidget)
        self.unit_2.setObjectName("unit_2")
        self.unit_2.setMaximumSize(QSize(16777215, 50))
        self.unit_2.setAlignment(Qt.AlignHCenter | Qt.AlignTop)

        self.verticalLayout_12.addWidget(self.unit_2)

        self.gridLayout.addLayout(self.verticalLayout_12, 0, 2, 1, 1)

        self.verticalLayout_13 = QVBoxLayout()
        self.verticalLayout_13.setObjectName("verticalLayout_13")
        self.verticalLayout_13.setContentsMargins(5, -1, 5, -1)
        self.horizontalLayout_13 = QHBoxLayout()
        self.horizontalLayout_13.setSpacing(0)
        self.horizontalLayout_13.setObjectName("horizontalLayout_13")
        self.name_7 = QLabel(self.gridWidget)
        self.name_7.setObjectName("name_7")
        self.name_7.setMaximumSize(QSize(16777215, 50))
        self.name_7.setAlignment(Qt.AlignBottom | Qt.AlignLeading | Qt.AlignLeft)

        self.horizontalLayout_13.addWidget(self.name_7)

        self.device_7 = QLabel(self.gridWidget)
        self.device_7.setObjectName("device_7")
        self.device_7.setMaximumSize(QSize(16777215, 50))
        self.device_7.setAlignment(Qt.AlignBottom | Qt.AlignRight | Qt.AlignTrailing)

        self.horizontalLayout_13.addWidget(self.device_7)

        self.verticalLayout_13.addLayout(self.horizontalLayout_13)

        self.value_7 = QLabel(self.gridWidget)
        self.value_7.setObjectName("value_7")
        self.value_7.setFont(font)
        self.value_7.setAlignment(Qt.AlignCenter)

        self.verticalLayout_13.addWidget(self.value_7)

        self.unit_7 = QLabel(self.gridWidget)
        self.unit_7.setObjectName("unit_7")
        self.unit_7.setMaximumSize(QSize(16777215, 50))
        self.unit_7.setAlignment(Qt.AlignHCenter | Qt.AlignTop)

        self.verticalLayout_13.addWidget(self.unit_7)

        self.gridLayout.addLayout(self.verticalLayout_13, 1, 2, 1, 1)

        self.gridLayout_2.addWidget(self.gridWidget, 0, 0, 1, 1)

        self.stackedWidget.addWidget(self.home)
        self.widgets = QWidget()
        self.widgets.setObjectName("widgets")
        self.widgets.setStyleSheet("b")
        self.verticalLayout = QVBoxLayout(self.widgets)
        self.verticalLayout.setSpacing(10)
        self.verticalLayout.setObjectName("verticalLayout")
        self.verticalLayout.setContentsMargins(10, 10, 10, 10)
        self.stackedWidget.addWidget(self.widgets)
        self.new_page = QWidget()
        self.new_page.setObjectName("new_page")
        self.verticalLayout_20 = QVBoxLayout(self.new_page)
        self.verticalLayout_20.setObjectName("verticalLayout_20")
        self.stackedWidget.addWidget(self.new_page)

        self.verticalLayout_15.addWidget(self.stackedWidget)

        self.horizontalLayout_4.addWidget(self.pagesContainer)

        self.verticalLayout_6.addWidget(self.content)

        self.bottomBar = QFrame(self.contentBottom)
        self.bottomBar.setObjectName("bottomBar")
        self.bottomBar.setMinimumSize(QSize(0, 35))
        self.bottomBar.setMaximumSize(QSize(16777215, 35))
        self.bottomBar.setFrameShape(QFrame.NoFrame)
        self.bottomBar.setFrameShadow(QFrame.Raised)
        self.horizontalLayout_5 = QHBoxLayout(self.bottomBar)
        self.horizontalLayout_5.setSpacing(0)
        self.horizontalLayout_5.setObjectName("horizontalLayout_5")
        self.horizontalLayout_5.setContentsMargins(0, 0, 0, 0)
        self.creditsLabel = QLabel(self.bottomBar)
        self.creditsLabel.setObjectName("creditsLabel")
        self.creditsLabel.setMaximumSize(QSize(200, 35))
        font4 = QFont()
        font4.setFamilies(["Segoe UI"])
        font4.setPointSize(14)
        font4.setBold(False)
        font4.setItalic(False)
        self.creditsLabel.setFont(font4)
        self.creditsLabel.setStyleSheet("font: 14pt;")
        self.creditsLabel.setAlignment(Qt.AlignLeading | Qt.AlignLeft | Qt.AlignVCenter)

        self.horizontalLayout_5.addWidget(self.creditsLabel)

        self.memory = QLabel(self.bottomBar)
        self.memory.setObjectName("memory")

        self.horizontalLayout_5.addWidget(self.memory)

        self.status = QLabel(self.bottomBar)
        self.status.setObjectName("status")
        self.status.setMaximumSize(QSize(100, 16777215))
        self.status.setAlignment(Qt.AlignRight | Qt.AlignTrailing | Qt.AlignVCenter)

        self.horizontalLayout_5.addWidget(self.status)

        self.icon = QLabel(self.bottomBar)
        self.icon.setObjectName("icon")
        self.icon.setMaximumSize(QSize(25, 16777215))
        self.icon.setLayoutDirection(Qt.LeftToRight)
        self.icon.setAutoFillBackground(False)
        self.icon.setStyleSheet(
            "background-image: url(:/images/images/images/red-dot.png);\n"
            "background-position:center;\n"
            "background-repeat:no-repeat;"
        )
        self.icon.setInputMethodHints(Qt.ImhNone)

        self.horizontalLayout_5.addWidget(self.icon)

        self.status_2 = QLabel(self.bottomBar)
        self.status_2.setObjectName("status_2")
        self.status_2.setMaximumSize(QSize(100, 16777215))
        self.status_2.setLayoutDirection(Qt.LeftToRight)
        self.status_2.setAlignment(Qt.AlignRight | Qt.AlignTrailing | Qt.AlignVCenter)

        self.horizontalLayout_5.addWidget(self.status_2)

        self.icon_2 = QLabel(self.bottomBar)
        self.icon_2.setObjectName("icon_2")
        self.icon_2.setMaximumSize(QSize(25, 16777215))
        self.icon_2.setStyleSheet(
            "background-image: url(:/images/images/images/red-dot.png);\n"
            "background-position:center;\n"
            "background-repeat:no-repeat;"
        )

        self.horizontalLayout_5.addWidget(self.icon_2)

        self.version = QLabel(self.bottomBar)
        self.version.setObjectName("version")
        self.version.setMaximumSize(QSize(100, 16777215))
        font5 = QFont()
        font5.setFamilies(["Segoe UI"])
        font5.setBold(False)
        font5.setItalic(False)
        self.version.setFont(font5)
        self.version.setAlignment(Qt.AlignRight | Qt.AlignTrailing | Qt.AlignVCenter)

        self.horizontalLayout_5.addWidget(self.version)

        self.frame_size_grip = QFrame(self.bottomBar)
        self.frame_size_grip.setObjectName("frame_size_grip")
        self.frame_size_grip.setMinimumSize(QSize(20, 0))
        self.frame_size_grip.setMaximumSize(QSize(20, 16777215))
        self.frame_size_grip.setFrameShape(QFrame.NoFrame)
        self.frame_size_grip.setFrameShadow(QFrame.Raised)

        self.horizontalLayout_5.addWidget(self.frame_size_grip)

        self.verticalLayout_6.addWidget(self.bottomBar)

        self.verticalLayout_2.addWidget(self.contentBottom)

        self.appLayout.addWidget(self.contentBox)

        self.appMargins.addWidget(self.bgApp)

        MainWindow.setCentralWidget(self.styleSheet)

        self.retranslateUi(MainWindow)

        self.stackedWidget.setCurrentIndex(0)

        QMetaObject.connectSlotsByName(MainWindow)

    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(
            QCoreApplication.translate("MainWindow", "MainWindow", None)
        )
        self.btn_home.setText(QCoreApplication.translate("MainWindow", "Home", None))
        self.titleRightInfo.setText(
            QCoreApplication.translate(
                "MainWindow",
                '<html><head/><body><p><span style=" font-size:20pt;">\u5bc6\u9589\u7a7a\u9593\u76e3\u6e2c\u7cfb\u7d71</span></p></body></html>',
                None,
            )
        )
        # if QT_CONFIG(tooltip)
        self.minimizeAppBtn.setToolTip(
            QCoreApplication.translate("MainWindow", "Minimize", None)
        )
        # endif // QT_CONFIG(tooltip)
        self.minimizeAppBtn.setText("")
        # if QT_CONFIG(tooltip)
        self.maximizeRestoreAppBtn.setToolTip(
            QCoreApplication.translate("MainWindow", "Maximize", None)
        )
        # endif // QT_CONFIG(tooltip)
        self.maximizeRestoreAppBtn.setText("")
        # if QT_CONFIG(tooltip)
        self.closeAppBtn.setToolTip(
            QCoreApplication.translate("MainWindow", "Close", None)
        )
        # endif // QT_CONFIG(tooltip)
        self.closeAppBtn.setText("")
        self.name_0.setText(QCoreApplication.translate("MainWindow", "title", None))
        self.device_0.setText(
            QCoreApplication.translate("MainWindow", "TextLabel", None)
        )
        self.value_0.setText(
            QCoreApplication.translate(
                "MainWindow",
                '<html><head/><body><p><span style=" font-size:28pt;">Null</span></p></body></html>',
                None,
            )
        )
        self.unit_0.setText(QCoreApplication.translate("MainWindow", "unit", None))
        self.name_1.setText(QCoreApplication.translate("MainWindow", "Title", None))
        self.device_1.setText(
            QCoreApplication.translate("MainWindow", "TextLabel", None)
        )
        self.value_1.setText(
            QCoreApplication.translate(
                "MainWindow",
                '<html><head/><body><p><span style=" font-size:28pt;">Null</span></p></body></html>',
                None,
            )
        )
        self.unit_1.setText(QCoreApplication.translate("MainWindow", "unit", None))
        self.name_5.setText(QCoreApplication.translate("MainWindow", "Title", None))
        self.deivce_5.setText(
            QCoreApplication.translate("MainWindow", "TextLabel", None)
        )
        self.value_5.setText(
            QCoreApplication.translate(
                "MainWindow",
                '<html><head/><body><p><span style=" font-size:28pt;">Null</span></p></body></html>',
                None,
            )
        )
        self.unit_5.setText(QCoreApplication.translate("MainWindow", "unit", None))
        self.name_3.setText(QCoreApplication.translate("MainWindow", "Title", None))
        self.device_3.setText(
            QCoreApplication.translate("MainWindow", "TextLabel", None)
        )
        self.value_3.setText(QCoreApplication.translate("MainWindow", "Null", None))
        self.unit_3.setText(QCoreApplication.translate("MainWindow", "unit", None))
        self.name_6.setText(QCoreApplication.translate("MainWindow", "Title", None))
        self.device_6.setText(
            QCoreApplication.translate("MainWindow", "TextLabel", None)
        )
        self.value_6.setText(
            QCoreApplication.translate(
                "MainWindow",
                '<html><head/><body><p><span style=" font-size:28pt;">Null</span></p></body></html>',
                None,
            )
        )
        self.unit_6.setText(QCoreApplication.translate("MainWindow", "unit", None))
        self.name_8.setText(QCoreApplication.translate("MainWindow", "Title", None))
        self.device_8.setText(
            QCoreApplication.translate("MainWindow", "TextLabel", None)
        )
        self.value_8.setText(QCoreApplication.translate("MainWindow", "Null", None))
        self.unit_8.setText(QCoreApplication.translate("MainWindow", "unit", None))
        self.name_9.setText(QCoreApplication.translate("MainWindow", "Title", None))
        self.device_9.setText(
            QCoreApplication.translate("MainWindow", "TextLabel", None)
        )
        self.value_9.setText(QCoreApplication.translate("MainWindow", "Null", None))
        self.unit_9.setText(QCoreApplication.translate("MainWindow", "unit", None))
        self.name_4.setText(QCoreApplication.translate("MainWindow", "Title", None))
        self.device_4.setText(
            QCoreApplication.translate("MainWindow", "TextLabel", None)
        )
        self.value_4.setText(
            QCoreApplication.translate(
                "MainWindow",
                '<html><head/><body><p><span style=" font-size:28pt;">Null</span></p></body></html>',
                None,
            )
        )
        self.unit_4.setText(QCoreApplication.translate("MainWindow", "unit", None))
        self.name_2.setText(QCoreApplication.translate("MainWindow", "Title", None))
        self.deivce_2.setText(
            QCoreApplication.translate("MainWindow", "TextLabel", None)
        )
        self.value_2.setText(
            QCoreApplication.translate(
                "MainWindow",
                '<html><head/><body><p><span style=" font-size:28pt;">Null</span></p></body></html>',
                None,
            )
        )
        self.unit_2.setText(QCoreApplication.translate("MainWindow", "unit", None))
        self.name_7.setText(QCoreApplication.translate("MainWindow", "Title", None))
        self.device_7.setText(
            QCoreApplication.translate("MainWindow", "TextLabel", None)
        )
        self.value_7.setText(
            QCoreApplication.translate(
                "MainWindow",
                '<html><head/><body><p><span style=" font-size:8pt;">Null</span></p></body></html>',
                None,
            )
        )
        self.unit_7.setText(QCoreApplication.translate("MainWindow", "unit", None))
        self.creditsLabel.setText(
            QCoreApplication.translate(
                "MainWindow",
                '<html><head/><body><p><span style=" font-size:14pt;">Time:</span></p></body></html>',
                None,
            )
        )
        self.memory.setText("")
        self.status.setText("")
        self.icon.setText("")
        self.status_2.setText("")
        self.icon_2.setText("")
        self.version.setText(
            QCoreApplication.translate(
                "MainWindow",
                '<html><head/><body><p><span style=" font-size:14pt;">Version:</span></p></body></html>',
                None,
            )
        )

    # retranslateUi
