#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""What Key Was It: parses the iCUE profiles to find what keys are bound to what.
TODO: other programs"""

import os
import sys
import pprint as pp
import xml.etree.ElementTree as ET
from PyQt5 import QtWidgets, QtCore, uic, QtGui
from PyQt5.QtCore import QAbstractNativeEventFilter, QAbstractEventDispatcher
from PyQt5.QtWidgets import QMainWindow, QPushButton, QSizePolicy
from pyqtkeybind import keybinder
from os import system

import MicrosoftScrape
import RazerScrape

latch = False
system("title " + "PopUp")
profilePathList = list
pageHolder = dict()


class ImportProfile(profilePathList):
    """ Imports a list of predefined profiles """
    def __init__(self):
        super().__init__()

    def scrapeall(self, profileList):
        """Scrapes Corsair iCUE profiles for shortcuts, Bound keys, and modifiers"""

        # Contains the roots of each XML profiles of a given folder/file
        rootContainer = [ET.parse(value).getroot() for value in profileList]

        # Key connections: key shortcut, key bound, modifier [click, long press]
        keyCons = list()
        # Key connection page: each value is a new
        keyConPage = list()

        # Search through xml for KeyStokes and Save into a list of list
        # Top list contains each list of keystrokes
        for root in rootContainer:

            profileName = root.find('.//name')

            # Find the location of keyStroke's ancestor, We use the ancestor to navigate the keybindings.
            for parent in root.findall('.//keyStroke/../../../..'):

                # drop into the child of the parent.
                for child in parent:

                    nameTag = child.find('ptr_wrapper/data/base/name')
                    keyStrokeChild = child.find('ptr_wrapper/data/keyStroke')
                    keyNameChild = child.find('ptr_wrapper/data/keyName')
                    keyBound = child.find('.//second/..')
                    strokeContainer = None

                    if nameTag is not None:
                        if nameTag.text is not None:
                            if strokeContainer is None:
                                strokeContainer = nameTag.text
                            else:
                                strokeContainer = strokeContainer + ', ' + nameTag.text

                    if keyNameChild is not None:
                        if keyNameChild.text is not None:
                            if strokeContainer is None:
                                strokeContainer = keyNameChild.text
                            else:
                                strokeContainer = strokeContainer + ', ' + keyNameChild.text

                    if keyStrokeChild is not None:
                        if keyStrokeChild.text is not None:
                            for value in keyStrokeChild:
                                if strokeContainer is None:
                                    strokeContainer = value.text
                                else:
                                    strokeContainer = strokeContainer + ', ' + value.text

                    if keyBound is not None:
                        if keyBound.find('first') is not None:
                            if strokeContainer is None:
                                strokeContainer = keyBound.find('first').text
                                # print(strokeContainer)
                                strokeContainer = strokeContainer + ', ' + keyBound.find('second').text
                                # print(strokeContainer)
                            else:
                                strokeContainer = strokeContainer + ', ' + keyBound.find('first').text
                                strokeContainer = strokeContainer + ', ' + keyBound.find('second').text

                    keyCons.append(strokeContainer)

            keyCons.append(profileName)
            keyConPage.append(keyCons.copy())
            keyCons.clear()

        return keyConPage


class WinEventFilter(QAbstractNativeEventFilter):
    def __init__(self, keybinder):
        self.keybinder = keybinder
        super().__init__()

    def nativeEventFilter(self, eventType, message):
        ret = self.keybinder.handler(eventType, message)
        return ret, 0


class MainWindow(QMainWindow):
    def __init__(self):
        QMainWindow.__init__(self)

        # self.ui = uic.loadUi("ui\keyboard.ui", self)

        self.setWindowFlags(
            QtCore.Qt.WindowStaysOnTopHint |
            QtCore.Qt.FramelessWindowHint |
            QtCore.Qt.X11BypassWindowManagerHint
        )

        self.setGeometry(
            QtWidgets.QStyle.alignedRect(
                QtCore.Qt.LeftToRight, QtCore.Qt.AlignCenter,
                QtCore.QSize(750, 500),
                QtWidgets.qApp.desktop().availableGeometry()
            ))

        self.setStyleSheet("""QToolTip { 
                                   background-color: black; 
                                   color: white; 
                                   border: black solid 1px
                                   }""")

        pagehold = 0
        buttonList = list()
        global pageHolder
        nameHolder = list()
        maxHeightReached = 0
        maxWidthReached = 0

        # Bring in iCUE settings.
        try:
            profileList = listifyFolderFiles(os.path.expandvars(r'%APPDATA%\Corsair\CUE\profiles'))
            DATA = ImportProfile()

            shortcutsParsed = DATA.scrapeall(profileList)

            for page in shortcutsParsed:
                section = 1
                shortcutCounter = 0
                x = 20
                y = 20
                profileName = page.pop(-1)
                nameHolder.append(profileName.text)
                M4_triggered_once = False
                M5_triggered_once = False
                tcounter = 0

                for part in page:

                    if section == 1:
                        shortcutName, shortcutKeys = part.split(",", 1)
                        section = 2
                    else:
                        boundKey, modifier = part.split(",", 1)
                        section = 1

                    if section == 1:
                        if shortcutCounter == 9:
                            x = x + 155
                            if maxWidthReached < x:
                                maxWidthReached = x
                            y = 20
                            shortcutCounter = 0

                        labelNew = QPushButton(boundKey + ": " + shortcutName, self)
                        labelNew.setToolTip("The Key(s) are: " + shortcutKeys + ". Modifier: " + modifier)
                        labelNew.resize(150, 30)

                        if shortcutCounter == 0:
                            labelNew.move(x, y)
                        else:
                            y = y + 35
                            if maxHeightReached < y:
                                maxHeightReached = y

                            labelNew.move(x, y)

                        # This is ugly but it works, TODO: come back to it, I dont want to do this for every weird thing
                        if labelNew.text()[:6] == "Mouse4" and M4_triggered_once is False:
                            tcounter += 1
                            buttonList.append(labelNew)
                            section = 1
                            M4_triggered_once = True
                            shortcutCounter += 1
                        elif labelNew.text()[:6] == "Mouse5" and M5_triggered_once is False:
                            buttonList.append(labelNew)
                            section = 1
                            M5_triggered_once = True
                            shortcutCounter += 1
                        elif labelNew.text()[:6] != "Mouse4" and labelNew.text()[:6] != "Mouse5":
                            buttonList.append(labelNew)
                            section = 1
                            shortcutCounter += 1
                        else:
                            if shortcutCounter > 0:
                                y = y - 35
                            labelNew.deleteLater()

                pageHolder.update({pagehold: buttonList.copy()})
                pagehold += 1
                buttonList.clear()
        except FileNotFoundError:
            print('Skipping corsair since its not in use')

        try:
            # Bring in Microsoft's Keyboard Manager settings.
            x = 20
            y = 20
            m_section = 0
            m_counter = 0
            microsoft_keybindings = MicrosoftScrape.getListofChanges()
            microsoft_enable_check = microsoft_keybindings.pop()
            microsoft_label = [QPushButton(bind[0], self) for bind in microsoft_keybindings]
            microsoft_tooltip = [bind[1] for bind in microsoft_keybindings]

            for label in microsoft_label:
                if m_section == 9:
                    x = x + 175
                    y = 20
                    if maxWidthReached < x:
                        maxWidthReached = x
                    m_section = 0
                if m_section == 0:
                    label.move(x, y)
                    label.resize(150, 30)
                    label.setToolTip(microsoft_tooltip[m_counter])
                else:
                    y = y + 35
                    if maxHeightReached < y:
                        maxHeightReached = y
                    label.move(x, y)
                    label.resize(150, 30)
                    label.setToolTip(microsoft_tooltip[m_counter])
                m_section += 1
                m_counter += 1

            pageHolder.update({pagehold: microsoft_label})
            pagehold += 1
            nameHolder.append("Microsoft Keyboard. Enabled: " + str(microsoft_enable_check))
        except FileNotFoundError:
            print('Skipping Microsoft Keyboard Manager since it is not in use.')

        # Bring in Razer Synapse settings.
        try:
            x = 20
            y = 20
            m_section = 0

            razer_profiles = RazerScrape.scrape_profiles()
            razer_button_list = []

            for profile in razer_profiles:
                x = 20
                y = 20
                m_section = 0

                name = profile.pop()
                # print(name)
                for bind in profile:
                    # print(bind)
                    key_id, shortcut = bind.split(',')

                    if m_section == 9:
                        x = x + 175
                        y = 20
                        if maxWidthReached < x:
                            maxWidthReached = x
                        m_section = 0

                    if m_section == 0:
                        label = QPushButton(key_id, self)
                        label.move(x, y)
                        label.resize(150, 30)
                        label.setToolTip(shortcut)
                        # label.hide()
                    else:
                        y = y + 35
                        if maxHeightReached < y:
                            maxHeightReached = y
                        label = QPushButton(key_id, self)
                        label.move(x, y)
                        label.resize(150, 30)
                        label.setToolTip(shortcut)
                        # label.hide()

                    m_section += 1
                    razer_button_list.append(label)

                    pageHolder.update({pagehold: razer_button_list.copy()})

                    # razer_button_list.clear()
                # print(len(pageHolder[pagehold]))
                # print(pagehold)
                pagehold += 1
                razer_button_list.clear()
                nameHolder.append(name)

        except FileNotFoundError:
            print('Skipping Microsoft Keyboard Manager since it is not in use.')

        # only show first "page" on start
        try:
            if pageHolder is not None:
                pageSelectBox = QtWidgets.QComboBox(self)
                pageSelectBox.resize(200,25)
                pageSelectBox.move(int(maxWidthReached - (pageSelectBox.width() / 2)), int((maxHeightReached + 100) - 50))
                pageSelectBox.activated.connect(self.changePage)

            for key, page in pageHolder.items():
                pageSelectBox.addItem(nameHolder[key])
                for button in page:
                    if key == 0:
                        button.show()
                    else:
                        button.hide()
        finally:
            pass

        self.setFixedSize(maxWidthReached * 2, maxHeightReached + 100)  # Is this the best way?

    def mousePressEvent(self, a0) -> None:
        """ Click the main window to hide"""
        global latch
        self.hide()
        latch = True

    def changePage(self, wantedPage):
        """Changing the combo box will change which profile's bindings are shown"""
        global pageHolder

        for key, page in pageHolder.items():
            for button in page:
                if key == wantedPage:
                    button.show()
                else:
                    button.hide()


def listifyFolderFiles(folderPath):
    """ Returns a list of profile data in the given directory."""
    unsortedlist = os.listdir(folderPath)
    returnlist = list()

    for path in unsortedlist:
        filename, extenstion = os.path.splitext(path)
        if extenstion == '.cueprofiledata':
            fullpath = folderPath + '\\' + path
            returnlist.append(fullpath)

    return returnlist


def main():
    # sys._excepthook = sys.excepthook
    #
    # def exception_hook(exctype, value, traceback):
    #     print(exctype, value, traceback)
    #     sys._excepthook(exctype, value, traceback)
    #     sys.exit(1)
    #
    # sys.excepthook = exception_hook

    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()

    print("This will show a quick view of your keybindings (corsair only currently).")
    print("Until I can figure out how to hide this window, just minimize it.")
    print("\tPress Ctrl+Shift+F10 any where to trigger a callback.")
    print("\tCtrl+Shift+F unregisters and re-registers previous callback.")
    print("\tCtrl+Shift+E exits the app.")

    # Setup a global keyboard shortcut to print "Hello World" on pressing
    # the shortcut
    keybinder.init()
    unregistered = False

    def on_toggle():

        global latch
        nonlocal window

        if latch:
            window.show()
            latch = False
            print("worked On")
        else:
            window.hide()
            latch = True
            print("worked Off")

    def exit_app():
        window.close()

    def unregister():
        keybinder.unregister_hotkey(window.winId(), "Shift+Ctrl+F10")
        print("unregister and register previous binding")
        keybinder.register_hotkey(window.winId(), "Shift+Ctrl+F10", on_toggle)

    keybinder.register_hotkey(window.winId(), "Shift+Ctrl+F10", on_toggle)
    keybinder.register_hotkey(window.winId(), "Shift+Ctrl+E", exit_app)
    keybinder.register_hotkey(window.winId(), "Shift+Ctrl+F", unregister)

    # Install a native event filter to receive events from the OS
    win_event_filter = WinEventFilter(keybinder)
    event_dispatcher = QAbstractEventDispatcher.instance()
    event_dispatcher.installNativeEventFilter(win_event_filter)

    window.show()
    app.exec_()
    keybinder.unregister_hotkey(window.winId(), "Shift+Ctrl+F10")
    keybinder.unregister_hotkey(window.winId(), "Shift+Ctrl+F")
    keybinder.unregister_hotkey(window.winId(), "Shift+Ctrl+E")


if __name__ == '__main__':
    main()
