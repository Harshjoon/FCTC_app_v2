import sys
import os
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtWidgets import QApplication, QLabel
from PyQt6.QtWidgets import (
    QCheckBox,
    QPushButton,
    QMainWindow,
    QMessageBox,
    QComboBox,
    QPlainTextEdit
)
import datetime as dt
import threading
import sqlite3
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
import pymongo
import sys
from PIL import Image
import io
import os
import json
import ast
import time
from passlib.context import CryptContext
import threading


class Main_window(QMainWindow):
    def __init__(self,client=None, user_details=""):
        super().__init__()

        self.client         = client
        self.user_details   = user_details
        
        #self.admin_user         = admin_user
        #self.approver_user      = approver_user
        self.window_height      = 750
        self.window_width       = 800

        #print(login_details['username'])
        #self.login_details      = login_details
        self.meta_data          = {}

        self.init_UI()

    def init_UI(self):

        self.setFixedSize(QSize(self.window_width, self.window_height))

        heading = "SELECT TASK"
        self.heading_label = self.make_label(heading,190,10,16)

        self.app_1_button                   = self.make_button("Friction compensation checklist",100,100)
        self.app_2_button                   = self.make_button("IPC Checklist",100,150)
        self.app_3_button                   = self.make_button("HDVR checklist",100,200)

        self.connect_signals_and_slots()

        return None
    
    def connect_signals_and_slots(self):
        self.app_1_button.clicked.connect(self.on_app_1_clicked)
        self.app_2_button.clicked.connect(self.on_app_2_clicked)
        self.app_3_button.clicked.connect(self.on_app_3_clicked)
        return None

    def on_app_1_clicked(self):
        from FCTC_app.FCTC_app import Main_window
        self.app_1_window = Main_window(client=self.client, user_detail=self.user_details)
        self.app_1_window.show()
        self.close()
        return None
    
    def on_app_2_clicked(self):
        self.show_message("Not implemented yet.")
        return None
    
    def on_app_3_clicked(self):
        self.show_message("Not implemented yet.")
        return None

    def make_label(
            self,
            text        = "",
            x           = 0,
            y           = 0,
            font_size   = 12,
            bold        = False
    ):
        label = QLabel(text,self)
        label.setStyleSheet("QLabel{{font-size: {0}pt}}".format(font_size))
        label.move(x,y)
        label.adjustSize()
        return label

    def make_lineedit(
            self,
            text        = "",
            x           = 0,
            y           = 0,
            w           = None,
            h           = None,
    ):
        #lineedit = QLineEdit(self)
        lineedit = QPlainTextEdit(self)
        lineedit.setPlaceholderText(text)
        lineedit.move(x,y)
        #lineedit.adjustSize()

        if (w != None) and (h != None):
            lineedit.setFixedSize(QSize(w,h))

        return lineedit

    def make_check_box(
            self,
            text        = "",
            x           = 0,
            y           = 0,
            font_size   = 12,
    ):
        check_box = QCheckBox(text,self)
        check_box.setStyleSheet("QCheckBox{{font-size: {0}pt}}".format(font_size))
        check_box.move(x,y)
        check_box.adjustSize()

        return check_box
    
    def make_combobox(
            self,
            texts   = [],
            x       = 0,
            y       = 0,
    ):
        combobox = QComboBox(self)
        for text in texts:
            combobox.addItem(text)
        combobox.move(x,y)
        combobox.adjustSize()
        return combobox
    
    def make_button(
            self,
            text    ="",
            x       =0,
            y       =0,
    ):
        button = QPushButton(text,self)
        button.move(x,y)
        button.adjustSize()
        return button

    def show_message(
            self,
            text = "message"
            ):
        choice = QMessageBox.information(
            None,
            "Warning",
            text,
            QMessageBox.StandardButton.Ok,
            #QMessageBox.StandardButton.No,
        )
        if choice == QMessageBox.StandardButton.Ok:
            return None
        return None
    
    def show_warning(
            self,
            text = "warning"
            ):
        choice = QMessageBox.critical(
            None,
            "Warning",
            text,
            QMessageBox.StandardButton.Ok
        )
        if choice == QMessageBox.StandardButton.Ok:
            return None
        return None


def main():
    app     = QApplication(sys.argv)
    
    window  = Main_window(
        admin_user=False,
        login_details={"username":"user"},
        approver_user=False
    )
    window.show()
    app.exec()

if __name__ == '__main__':
    main()