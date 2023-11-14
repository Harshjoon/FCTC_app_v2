import sys
from PyQt6.QtWidgets import QApplication, QWidget, QLabel
from PyQt6.QtWidgets import (
    QPushButton,
    QLineEdit,
    QGridLayout,
    QMessageBox,
    QSizePolicy
)

import sqlite3
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
import pymongo
from PIL import Image
import io
import os
import json
import ast
import time
from passlib.context import CryptContext
import passlib.handlers.bcrypt
import passlib
import threading
#from sqlite3 import Error

#from new_user_page          import NewUserPage
import FCTC_app

class LoginPage(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Login')
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        self.initUI()

    def initUI(self):

        self.window_width, self.window_height = 600,200
        self.setFixedSize( self.window_width, self.window_height )
        self.layout = QGridLayout()
        self.setLayout(self.layout)
        self.connecting_to_db_label = QLabel('Connecting to server')
        self.layout.addWidget(self.connecting_to_db_label,                    3,0,1,2)

        self.labels = {}
        self.lineEdits = {}

        self.labels['Username'] = QLabel('Username')
        self.labels['Password'] = QLabel('Password')
        self.labels['Confirm Password'] = QLabel('Confirm Password')
        self.labels['Username'].setSizePolicy(QSizePolicy.Policy.Fixed,QSizePolicy.Policy.Fixed)
        self.labels['Password'].setSizePolicy(QSizePolicy.Policy.Fixed,QSizePolicy.Policy.Fixed)
        self.labels['Confirm Password'].setSizePolicy(QSizePolicy.Policy.Fixed,QSizePolicy.Policy.Fixed)

        self.lineEdits['Username']     = QLineEdit()
        self.lineEdits['Password']     = QLineEdit()
        self.lineEdits['Password'].setEchoMode(QLineEdit.EchoMode.Password)
        self.lineEdits['Confirm Password']     = QLineEdit()
        self.lineEdits['Confirm Password'].setEchoMode(QLineEdit.EchoMode.Password)

        self.layout.addWidget(self.labels['Username'],                    0,0,1,1)
        self.layout.addWidget(self.lineEdits['Username'],                 0,1,1,3)
        self.layout.addWidget(self.labels['Password'],                    1,0,1,1)
        self.layout.addWidget(self.lineEdits['Password'],                 1,1,1,3)
        self.layout.addWidget(self.labels['Confirm Password'],            2,0,1,1)
        self.layout.addWidget(self.lineEdits['Confirm Password'],         2,1,1,3)

        self.login_button = QPushButton('&Log In', clicked= lambda:  self.check_credentials())
        self.layout.addWidget(self.login_button,                               3,3,1,1)

        # self.add_users_button = QPushButton('&Add Users', clicked=self.on_add_user_clicked)
        # self.layout.addWidget(self.add_users_button,                           3,2,1,1)

        self.change_password_button = QPushButton('&Change Password', clicked=self.on_change_password)# add slots
        self.layout.addWidget(self.change_password_button,                     3,1,1,1)

        self.hide_elements()

        self.status = QLabel('')
        self.status.setStyleSheet('font-size: 25px; color: red;')
        self.layout.addWidget(self.status,                                     4,0,1,3)

        return None
    
    def check_credentials(self):
        username = self.lineEdits['Username'].text()
        password = self.lineEdits['Password'].text()
        if username == "":
            self.show_warning("username cannot be empty")
            return None
        self.db = self.client.myDatabase
        users_db    = self.db['users']
        cursor      = users_db.find({"username": username})
        cursor      = list(cursor)
        if len(cursor) == 0:
            self.show_warning("Username not found.")
            return None
        if not self.verify_password( password, cursor[0]['hashedpassword'] ):
            self.show_warning("Incorrect password.")
            return None
        #self.show_message("password correct")
        user_details = {
            "username" : username,
            "user_type": cursor[0]["usertype"]
        }
        from main_page import Main_window
        self.main_window_page = Main_window(client=self.client, user_details=user_details)
        self.main_window_page.show()
        self.close()
        return None
        return None

    def on_change_password(self):
        username = self.lineEdits['Username'].text()
        password = self.lineEdits['Password'].text()
        if username == "":
            self.show_warning("username cannot be empty")
            return None
        self.db = self.client.myDatabase
        users_db    = self.db['users']
        cursor      = users_db.find({"username": username})
        cursor      = list(cursor)
        if len(cursor) == 0:
            self.show_warning("Username not found.")
            return None
        if not self.verify_password( password, cursor[0]['hashedpassword'] ):
            self.show_warning("Incorrect password.")
            return None
        print("Password verified")
        from change_password import ChangePasswordPage
        self.change_pass_page = ChangePasswordPage(client=self.client, old_username=username)
        self.change_pass_page.show()
        return None

    def on_add_user_clicked(self):
        username = self.lineEdits['Username'].text()
        password = self.lineEdits['Password'].text()
        if username == "":
            self.show_warning("username cannot be empty")
            return None
        self.db = self.client.myDatabase
        users_db    = self.db['users']
        cursor      = users_db.find({"username": username})
        cursor      = list(cursor)
        if len(cursor) == 0:
            self.show_warning("Username not found.")
            return None
        if not self.verify_password( password, cursor[0]['hashedpassword'] ):
            self.show_warning("Incorrect password.")
            return None
        if cursor[0]['usertype'] != 'admin':
            self.show_warning("only admins can add users")

        # self.new_user_window = NewUserPage(self.client)
        # self.new_user_window.show()

        return None

    def verify_password(self, plain_password, hashed_password):
        return self.pwd_context.verify(plain_password, hashed_password)
    
    def get_password_hash(self, password):
        return self.pwd_context.hash(password)

    def hide_elements(self):
        self.labels['Username'].setHidden(True)
        self.lineEdits['Username'].setHidden(True)
        self.labels['Password'].setHidden(True)
        self.lineEdits['Password'].setHidden(True)
        self.labels['Confirm Password'].setHidden(True)
        self.lineEdits['Confirm Password'].setHidden(True)
        self.login_button.setHidden(True)
        #self.add_users_button.setHidden(True)
        self.change_password_button.setHidden(True)

    def show_elements(self):
        self.labels['Username'].setHidden(False)
        self.lineEdits['Username'].setHidden(False)
        self.labels['Password'].setHidden(False)
        self.lineEdits['Password'].setHidden(False)
        self.login_button.setHidden(False)
        #self.add_users_button.setHidden(False)
        self.change_password_button.setHidden(False)

    def connect_to_db(self):

        connected = False

        try:
            self.client.admin.command('ping')
            print("Pinged your deployment. You successfully connected to MongoDB!")
            connected = True

            self.show_elements()
            self.connecting_to_db_label.setText("")
            #self.layout.removeWidget(self.connecting_to_db_label)
            return True

        except Exception as e:
            print(e)
            self.connecting_to_db_label.setText("Connecting to db failed, check internet connections.")
            connected = False
        return connected
    
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
    app = QApplication(sys.argv)
    loginWindow = LoginPage()
    loginWindow.show()

    connect_to_db_thread = threading.Thread(
                target=lambda: loginWindow.connect_to_db()
            )
    
    connect_to_db_thread.start()
    #loginWindow.connect_to_db()

    try:
        sys.exit(app.exec())
    except SystemExit:
        print('Closing Window ...')

if __name__ == '__main__':
    main()