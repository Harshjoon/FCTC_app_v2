import sys

from PyQt6.QtWidgets import QApplication, QWidget, QLabel
from PyQt6.QtWidgets import (
    QPushButton,
    QLineEdit,
    QGridLayout,
    QMessageBox,
    QSizePolicy
)

from passlib.context import CryptContext
import sqlite3
import pymongo
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
#from sqlite3 import Error

class ChangePasswordPage(QWidget):
    def __init__(self, client, old_username):
        super().__init__()

        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        self.old_username = old_username
        self.client = client

        self.users          = [
            'users',
            'approvers',
            'admins'
        ]

        #self.username       = username
        #self.user_type      = user_type

        self.setWindowTitle('Change password page')
        # set window icon
        # self.setWindowIcon(QIcon(''))
        self.database_filepath = "../../databases/main.db"

        self.window_width, self.window_height = 600,200
        self.setFixedSize( self.window_width, self.window_height )

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

        # upload_sig_button = QPushButton('&Upload signature')#, clicked=self.checkCredential)
        # layout.addWidget(upload_sig_button,                          3,0,1,1)

        add_users_button = QPushButton('&Change username and password', clicked=self.change_username_and_password)
        layout.addWidget(add_users_button,                              3,3,1,1)

        self.status = QLabel('')
        self.status.setStyleSheet('font-size: 25px; color: red;')
        layout.addWidget(self.status,                                   4,0,1,3)


    def initUI(self):
        return None

    def verify_password(self, plain_password, hashed_password):
        return self.pwd_context.verify(plain_password, hashed_password)
    
    def get_password_hash(self, password):
        return self.pwd_context.hash(password)

    def change_username_and_password(self):
        
        new_username        = self.lineEdits['New Username'].text()
        password            = self.lineEdits['Password'].text()
        confirm_password    = self.lineEdits['Confirm Password'].text()
        if new_username == "":
            self.show_warning("username cannot be empty")
            return None
        if password != confirm_password:
            self.show_warning("Confirm password does not match.")
            return None

        self.db = self.client.myDatabase
        users_db    = self.db['users']

        if new_username != self.old_username:
            cursor      = users_db.find({"username": new_username})
            cursor      = list(cursor)

            if len(cursor) > 0:
                self.show_warning(text="Username already present user differect username.")
                return None        
        
        cursor      = users_db.find({"username": self.old_username})
        cursor      = list(cursor)
        if len(cursor) == 0:
            self.show_warning(text="Error occured, please go back to login page.")
            return None
        user_data    = cursor[0]
        new_user_data = user_data
        new_user_data['username']       = new_username
        new_user_data['hashedpassword'] = self.get_password_hash(password=confirm_password)
        try:
            result      = users_db.replace_one(
                {"username": self.old_username},
                new_user_data
            )
            self.close()
            return None
        except pymongo.errors.OperationFailure:
            print("An authentication error was received. Are you sure your database user is authorized to perform write operations?")
            self.show_warning("Error Occured, pls go back to login page.")
            return False
        else:
            print("Inserted 1 document.")
            print("\n") 
            return None
        self.close()
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

def main():
    print("This is the main function.")
    app = QApplication(sys.argv)
    # set app stylesheet
    # app.setStyleSheet()
    #client = None
    loginWindow = ChangePasswordPage(client=client, old_username="admin")
    loginWindow.show()

    try:
        sys.exit(app.exec())
    except SystemExit:
        print('Closing Window ...')

if __name__ == '__main__':
    main()