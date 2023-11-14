import sys

from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtWidgets import QApplication, QWidget, QLabel
from PyQt6.QtWidgets import (
    QCheckBox,
    QPushButton,
    QLineEdit,
    QGridLayout,
    QMessageBox,
    QSizePolicy,
    QFileDialog
)

from passlib.context import CryptContext
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
from PIL.ImageQt import ImageQt

class NewUserPage(QWidget):
    def __init__(self, client):
        super().__init__()

        self.client = client
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

        self.initUI()

    def initUI(self):

        print("new user page initialized")
        self.setWindowTitle('Login')
        # set window icon
        # self.setWindowIcon(QIcon(''))
        self.database_filepath = "../../databases/main.db"

        self.window_width, self.window_height = 600,200
        self.setFixedSize( self.window_width, self.window_height )

        self.signature_image_data = None
        self.signature_added      = False

        layout = QGridLayout()
        self.setLayout(layout)

        self.labels = {}
        self.lineEdits = {}

        self.labels['New Username'] = QLabel('New Username')
        self.labels['Password'] = QLabel('Password')
        self.labels['Confirm Password'] = QLabel('Confirm Password')
        self.labels['New Username'].setSizePolicy(QSizePolicy.Policy.Fixed,QSizePolicy.Policy.Fixed)
        self.labels['Password'].setSizePolicy(QSizePolicy.Policy.Fixed,QSizePolicy.Policy.Fixed)
        self.labels['Confirm Password'].setSizePolicy(QSizePolicy.Policy.Fixed,QSizePolicy.Policy.Fixed)

        self.lineEdits['New Username']     = QLineEdit()
        self.lineEdits['Password']     = QLineEdit()
        self.lineEdits['Password'].setEchoMode(QLineEdit.EchoMode.Password)
        self.lineEdits['Confirm Password']     = QLineEdit()
        self.lineEdits['Confirm Password'].setEchoMode(QLineEdit.EchoMode.Password)

        layout.addWidget(self.labels['New Username'],                   0,0,1,1)
        layout.addWidget(self.lineEdits['New Username'],                0,1,1,3)
        layout.addWidget(self.labels['Password'],                       1,0,1,1)
        layout.addWidget(self.lineEdits['Password'],                    1,1,1,3)
        layout.addWidget(self.labels['Confirm Password'],               2,0,1,1)
        layout.addWidget(self.lineEdits['Confirm Password'],            2,1,1,3)


        text  = ""
        self.approved_by_signature            = self.make_label(text,100,100,10,parent=self)
        layout.addWidget(self.approved_by_signature,            4,1,1,3)


        self.approver_user_checkbox            = QCheckBox("Approver User", self)
        self.approver_user_checkbox.move(30,90)

        self.signature_uploaded = False
        login_button = QPushButton('&Upload signature', clicked=self.select_signature_image)
        layout.addWidget(login_button,                          3,2,1,1)

        add_users_button = QPushButton('&Add Users', clicked=self.add_user)
        layout.addWidget(add_users_button,                      3,3,1,1)

        self.status = QLabel('')
        self.status.setStyleSheet('font-size: 25px; color: red;')
        layout.addWidget(self.status,                           4,0,1,3)
        return None
    
    def add_user(self):

        new_username        = self.lineEdits['New Username'].text()
        password            = self.lineEdits['Password'].text()
        confirm_password    = self.lineEdits['Confirm Password'].text()

        if new_username     == "":
            self.show_warning("Username cannot be empty.")
            return None
        
        if password         == "":
            self.show_warning("Password cannot be empty.")
            return None
        
        if len(password)    < 5:
            self.show_warning("lenght of password must be greater than 5.")
            return None

        if password != confirm_password:
            self.show_warning("Confirm password did not match.")
            return None
        
        if not self.signature_added:
            self.show_warning("Please add signatures")
            return None
        
        users_db    = self.client.myDatabase['users']
        cursor      = users_db.find({"username": new_username})
        cursor      = list(cursor)

        print(cursor)

        if len(cursor) > 0:
            self.show_warning("User already exists")
            return None
        
        user_type = "user"
        if self.approver_user_checkbox.isChecked():
            user_type = "approver"

        users_data = {
                "usertype"       : user_type,
                "username"       : new_username,
                "hashedpassword" : self.get_password_hash(password),
            }

        try:
            result = users_db.insert_one(users_data)

            self.add_signature_to_db(self.client, new_username)

        except pymongo.errors.OperationFailure:
            print("An authentication error was received. Are you sure your database user is authorized to perform write operations?")
            self.show_warning("An authentication error was received. Are you sure your database user is authorized to perform write operations?")
            return None
        else:
            print("I inserted 1 documents.")
            print("\n") 
            self.show_message("Username added")
            self.close()
        
        self.close()
        return None
    
    def add_signature_to_db(self, client, username):
        db = client.myDatabase['signatures']
        signature_data = {
            "username" : username,
            "data"     : self.signature_image_data
        }

        try:
            result = db.insert_one(signature_data)
        except pymongo.errors.OperationFailure:
            print("An authentication error was received. Are you sure your database user is authorized to perform write operations?")
            self.show_warning("An authentication error was received. Are you sure your database user is authorized to perform write operations?")
            return None
        else:
            print("I inserted 1 signature.")
            print("\n") 

        return None

    def get_password_hash(self, password):
        return self.pwd_context.hash(password)

    def select_signature_image(self):

        file = QFileDialog.getOpenFileName(self, "Select Folder")
        print("--------------------------------------------", file)

        if len(file[0]) == 0:
            return None
        
        if file[0][-4:] != ".png":
            self.show_warning("Only png images accepted.")
            return None

        im          = Image.open(file[0])
        img_data        = ImageQt(im)#img_data)
        object_pixmap   = QPixmap.fromImage(img_data)
        w,h = 210,30
        self.approved_by_signature.setPixmap(object_pixmap.scaled(
           w,h,Qt.AspectRatioMode.KeepAspectRatio
        ))

        im_bytes  = io.BytesIO()
        im.save(im_bytes, format='PNG')
        self.signature_image_data = im_bytes.getvalue()
        self.signature_added = True
        return None
    
    def upload_signature(self):    
        file = QFileDialog.getOpenFileName(self, "Select Folder")
        print("--------------------------------------------", file)

        return None

    def remove_user(self):
        return None

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

    def make_label(
            self,
            text        = "",
            x           = 0,
            y           = 0,
            font_size   = 12,
            bold        = False,
            parent      = None
    ):
        if parent == None:
            parent = self
        label = QLabel(text,parent)
        label.setStyleSheet("QLabel{{font-size: {0}pt}}".format(font_size))
        label.move(x,y)
        label.adjustSize()
        return label
    

def main():
    print("This is the main function.")
    app = QApplication(sys.argv)
    # set app stylesheet
    # app.setStyleSheet()   

    loginWindow = NewUserPage(client)
    loginWindow.show()

    try:
        sys.exit(app.exec())
    except SystemExit:
        print('Closing Window ...')

if __name__ == '__main__':
    main()