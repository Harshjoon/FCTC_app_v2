#!user/bin/python

'''
TODO
- make code more efficient for exe              : Pending

- add login window                              : Done
- encryption algorithm for users                : Pending
- Fixed irregular spaces in document            : Done

- write algorithm for document number           : Done
- password protect sqlite database              : Pending
- save data in json and connect it
  to a database                                 : Pending 

- replace all path to absolute path             : Pending
- loading signature image from save data        : Done

- write a check for valid actuator number       : Pending

- save word document in a seperate folder       : Done
- add check for if document is already open     : Pending
'''

import sys
import os
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtWidgets import QApplication, QLabel, QWidget
from PIL import Image
from PIL.ImageQt import ImageQt

from PyQt6.QtWidgets import (
    QCheckBox,
    QPushButton,
    QMainWindow,
    QTabWidget,
    QVBoxLayout,
    QMessageBox,
    QComboBox,
    QPlainTextEdit
)

import datetime as dt
import threading
import io

from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi

from FCTC_app.make_document  import make_document
from FCTC_app.make_meta_data import make_meta_data
from FCTC_app.save_json      import save_json, file_exists, read_json
from FCTC_app.fill_data      import fill_data
from FCTC_app.send_email     import send_email

class Main_window(QMainWindow):
    #def __init__(self,admin_user, login_details, approver_user):
    def __init__(self, client, user_detail):
        super().__init__()
        #self.admin_user         = admin_user
        #self.approver_user      = approver_user
        self.window_height      = 750
        self.window_width       = 800
        self.client             = client
        #print(login_details['username'])
        #self.login_details      = login_details
        self.meta_data          = {}
        
        self.user_detail        = user_detail
        self.user_type          = self.user_detail["user_type"]
        self.username           = self.user_detail["username"]

        self.init_UI()

    def init_UI(self):
        tab = QTabWidget(self)
        #layout = QVBoxLayout()
        self.cl_page = QWidget()
        #self.da_page = QWidget()

        self.signature_image = self.get_signatures_from_db(usernmae=self.username)

        tab.addTab( self.cl_page, "Checklist page" )
        #tab.addTab( self.da_page, "Data analysis page" )
        # with open("../../user_data/{0}.txt".format(self.login_details['username']), "r") as file:
        #     self.email = file.readline()

        #self.setFixedSize(QSize(self.window_width, self.window_height))
        tab.setFixedSize(QSize( self.window_width, self.window_height + 20))
        self.setFixedSize(QSize( self.window_width, self.window_height + 20))

        heading = "FRICTION COMPENSATION TESTING CHECKLIST"
        self.heading_label = self.make_label(heading,190,10,16,parent=self.cl_page)

        text    = "Actuator Serial Number"
        self.actuator_sno_label      = self.make_label(text,50,60,10,parent=self.cl_page)
        self.actuator_sno_lineedit   = self.make_lineedit("",200,60-5,120,30,parent=self.cl_page) 
        self.actuator_find_button = self.make_button("Find",200,100,parent=self.cl_page)


        text    = "Document number :"
        self.document_no_label       = self.make_label(text,400,60,10,parent=self.cl_page)
        text    = "Revision number    : 1.0"
        self.revision_no_label       = self.make_label(text,400,80,10,parent=self.cl_page)

        self.checklist_content = {
            "Check the test setup assembly" : None,
            "Check the connection"          : None,
            "Check the active current value\
 just after enabling the \
drive"                                        : None,
            "Check if actuator is warmed up": None,
            "Test the actuator for velocity\
 control mode."                             : None,
            "Record Actual velocity"        : None,
            "Record Active current"         : None,
            "Recording time"                : None
        }

        self.yes_no_content = {
            "Any abnormal noise"            : None,
            "Abnormal peak current"         : None
        }

        self.remarks_label          = self.make_label("Remarks",500,120,10,parent=self.cl_page)

        self.checklist_checkboxes = []
        self.checklist_lineedits  = []

        x_start,y_start = 40,150
        y = y_start
        for key,value in self.checklist_content.items():
            self.checklist_checkboxes.append(
                self.make_check_box(key,x_start,y,10,parent=self.cl_page)
            )
            y += 32

        x_start,y_start = 500,150
        y = y_start
        for key,value in self.checklist_content.items():
            self.checklist_lineedits.append(
                self.make_lineedit("",x_start,y-5,250,30,parent=self.cl_page)
            )
            y += 32
        
        self.yes_no_labels              = []
        self.yes_no_linedits            = []
        self.yes_no_combobox            = []

        x_start,y_start = 40,420
        y = y_start
        for key,value in self.yes_no_content.items():
            self.yes_no_labels.append(
                self.make_label(key,x_start,y,10,parent=self.cl_page)
            )
            y += 32

        x_start,y_start = 500,420
        y = y_start
        for key,value in self.yes_no_content.items():
            self.yes_no_linedits.append(
                self.make_lineedit("Inspector name",x_start,y-10,250,30,parent=self.cl_page)
            )
            y += 32

        x_start,y_start = 200,420
        y = y_start
        for key,value in self.yes_no_content.items():
            self.yes_no_combobox.append(
                self.make_combobox(["yes", "no"],x_start,y - 2,parent=self.cl_page)
            )
            y += 32

        self.end_remark_label    = self.make_label("Remarks",40,600,10,parent=self.cl_page)
        self.end_remark_lineedit = self.make_lineedit("",40,620,700,60,parent=self.cl_page)

        a = 20
        text = "Assembled by: "
        self.assembled_by_name_label          = self.make_label(text,40 + a,500,10,parent=self.cl_page)
        text = "Date: "
        self.assembled_by_date_label          = self.make_label(text,300 ,500,10,parent=self.cl_page)
        text = "Signature: "
        self.assembled_by_signature_label     = self.make_label(text,500 ,500,10,parent=self.cl_page)
        #text = self.login_details['username']#"No name found"
        text = "No name found"
        self.assembled_by_name                = self.make_label(text,140 + a,500,10,parent=self.cl_page)
        text = "No date found"
        self.assembled_by_date                = self.make_label(text,350 ,500,10,parent=self.cl_page)
        text = ""#"No signature found"
        self.assembled_by_signature           = self.make_label(text,580 ,500,10,parent=self.cl_page)
        self.assembled_checkbox               = self.make_check_box("",30,502,parent=self.cl_page)
        #self.assembled_checkbox.setChecked(True)
        self.assembler_pixmap                 = QPixmap("../../images/1.png")
        w,h = 150,40
        #self.assembled_by_signature.setPixmap(self.assembler_pixmap.scaled(
        #    w,h,Qt.AspectRatioMode.KeepAspectRatio
        #))
        #self.assembled_by_signature.adjustSize()

        text = "Tested by: "
        self.tested_by_name_label             = self.make_label(text,40 + a,530,10,parent=self.cl_page)
        text = "Date: "
        self.tested_by_date_label             = self.make_label(text,300,530,10,parent=self.cl_page)
        text = "Signature: "
        self.tested_by_signature_label        = self.make_label(text,500,530,10,parent=self.cl_page)
        text = "No name found"
        self.tested_by_name                   = self.make_label(text,140 + a,530,10,parent=self.cl_page)
        text = "No date found"
        self.tested_by_date                   = self.make_label(text,350,530,10,parent=self.cl_page)
        text = ""#"No signature found"
        self.tested_by_signature              = self.make_label(text,580,530,10,parent=self.cl_page)
        self.tested_checkbox                  = self.make_check_box("",30,532,parent=self.cl_page)

        text = "Approved by"
        self.approved_by_name_label           = self.make_label(text,40 + a,560,10,parent=self.cl_page)
        text = "Date: "
        self.approved_by_date_label           = self.make_label(text,300,560,10,parent=self.cl_page)
        text = "Signature: "
        self.approved_by_signature_label      = self.make_label(text,500,560,10,parent=self.cl_page)
        text = "No name found"
        self.approved_by_name                 = self.make_label(text,140 + a,560,10,parent=self.cl_page)
        text = "No date found"
        self.approved_by_date                 = self.make_label(text,350,560,10,parent=self.cl_page)
        text = ""#"No signature found"
        self.approved_by_signature            = self.make_label(text,580,560,10,parent=self.cl_page)
        self.approved_checkbox                = self.make_check_box("",30,562,parent=self.cl_page)

        self.save_data_button                 = self.make_button("Save data",40,700,parent=self.cl_page)
        self.show_document_button             = self.make_button("Show document",180,700,parent=self.cl_page)
        self.make_document_button             = self.make_button("Make document",350,700,parent=self.cl_page)
        #self.request_approval_button          = self.make_button("Request approval",500,700,parent=self.cl_page)
        #self.send_email_button                = self.make_button("Send email",660,700,parent=self.cl_page)

        self.show_signature_image(object=self.assembled_by_signature,no_sig=True)
        self.show_signature_image(object=self.tested_by_signature,no_sig=True)
        self.show_signature_image(object=self.approved_by_signature,no_sig=True)
        self.connect_signals_and_slots()
        return None
    
    def connect_signals_and_slots(
            self
    ):
        #self.actuator_find_button
        self.save_data_button.clicked.connect(self.on_save_clicked)
        self.make_document_button.clicked.connect(self.on_make_document_clicked)
        #self.request_approval_button .clicked.connect(self.on_request_approval_clicked)
        self.show_document_button.clicked.connect(lambda:  self.show_document(document_path = "../documents/checklist_report.docx"))
        #self.send_email_button.clicked.connect(self.on_send_email_clicked)
        self.actuator_find_button.clicked.connect(self.on_find_clicked)
        self.assembled_checkbox.stateChanged.connect(self.on_assemble_state_change)
        self.tested_checkbox.stateChanged.connect(self.on_tested_state_change)
        self.approved_checkbox.stateChanged.connect(self.on_approved_state_change)
        self.actuator_sno_lineedit.textChanged.connect(self.make_document_number)
        return None
    
    def on_assemble_state_change(self):
        
        if self.assembled_checkbox.isChecked():
            #if self.admin_user or self.approver_user:
            if self.user_type == "admin" or self.user_type == "approver":
                # show message
                choice = QMessageBox.information(
                    None,
                    "Warning",
                    "Are you sure that you want to make this change.",
                    QMessageBox.StandardButton.Yes,
                    QMessageBox.StandardButton.No,
                )
                if choice == QMessageBox.StandardButton.No:
                    self.assembled_checkbox.setChecked(False)
                    return None
                elif choice == QMessageBox.StandardButton.Yes:
                    pass

            date_format = "%d-%m-%Y" 
            self.assembled_by_name.setText(self.user_detail['username'])
            self.assembled_by_date.setText(dt.datetime.now().strftime(format=date_format))
            self.show_signature_image(object=self.assembled_by_signature)
            #self.assembled_by_signature

        elif not self.assembled_checkbox.isChecked():
            self.assembled_by_name.setText("No name found")
            self.assembled_by_date.setText("No date found")
            self.assembled_by_name.adjustSize()
            self.assembled_by_date.adjustSize()
            self.show_signature_image(object=self.assembled_by_signature,no_sig=True)

        return None
    
    def on_tested_state_change(self):
        
        if self.tested_checkbox.isChecked():

            #if self.admin_user or self.approver_user:
            if self.user_type == "admin" or self.user_type == "approver":
                # show message
                choice = QMessageBox.information(
                    None,
                    "Warning",
                    "Are you sure that you want to make this change.",
                    QMessageBox.StandardButton.Yes,
                    QMessageBox.StandardButton.No,
                )
                if choice == QMessageBox.StandardButton.No:
                    self.tested_checkbox.setChecked(False)
                    return None
                elif choice == QMessageBox.StandardButton.Yes:
                    pass

            date_format = "%d-%m-%Y"
            self.tested_by_name.setText(self.user_detail['username'])
            self.tested_by_date.setText(dt.datetime.now().strftime(format=date_format))
            #self.tested_by_signature

            self.show_signature_image(object=self.tested_by_signature)

        elif not self.tested_checkbox.isChecked():
            self.tested_by_name.setText("No name found")
            self.tested_by_date.setText("No date found")
            self.tested_by_name.adjustSize()
            self.tested_by_date.adjustSize()
            self.show_signature_image(object=self.tested_by_signature,no_sig=True)

        return None
    
    def on_approved_state_change(self):
        #if not (self.admin_user or self.approver_user):
        if not (self.user_type == "admin" or self.user_type == "approver"):
            choice = QMessageBox.critical(
                None,
                "Warning",
                "Only admin user or approver user can approve checlist.",
                QMessageBox.StandardButton.Ok
            )
            self.approved_checkbox.setChecked(False)
            if choice == QMessageBox.StandardButton.Ok:
                self.approved_checkbox.setChecked(False)
                return None

        else:
            if self.approved_checkbox.isChecked():
                date_format = "%d-%m-%Y"
                self.approved_by_name.setText(self.user_detail['username'])
                self.approved_by_date.setText(dt.datetime.now().strftime(format=date_format))
                #self.approved_by_signature

                self.show_signature_image(object=self.approved_by_signature)
            elif not self.approved_checkbox.isChecked():
                self.show_signature_image(object=self.approved_by_signature,no_sig=True)

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
    
    def make_lineedit(
            self,
            text        = "",
            x           = 0,
            y           = 0,
            w           = None,
            h           = None,
            parent      = None
    ):
        if parent == None:
            parent = self
        #lineedit = QLineEdit(self)
        lineedit = QPlainTextEdit(parent)
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
            parent      = None
    ):
        check_box = QCheckBox(text,parent)
        check_box.setStyleSheet("QCheckBox{{font-size: {0}pt}}".format(font_size))
        check_box.move(x,y)
        check_box.adjustSize()

        return check_box
    
    def make_combobox(
            self,
            texts   = [],
            x       = 0,
            y       = 0,
            parent  = None
    ):
        combobox = QComboBox(parent)
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
            parent  = None
    ):
        button = QPushButton(text,parent)
        button.move(x,y)
        button.adjustSize()
        return button

    def on_save_clicked(self):
        """
            Description : Save data in a database
                          Save data in json

            TODO        : Save data in a database - Pending
                          Save data in json       - Pending
        """
        actuator_number         = self.actuator_sno_lineedit.toPlainText()
        # validate actuator number
        if not self.valid_actuator_number(actuator_number):
            self.show_warning("Actuator number not valid.")
            return None
        print("on_save_clicked function called.")
        # show warning for dave data
        choice = QMessageBox.critical(
            None,
            "Warning",
            "Are you sure you want to save this data?",
            QMessageBox.StandardButton.Yes,
            QMessageBox.StandardButton.No,
        )
        if choice == QMessageBox.StandardButton.Yes:
            pass
        elif choice == QMessageBox.StandardButton.No:
            return None
        else:
            return None
        
        if actuator_number == "":
            self.show_warning("Cannot have empty actuator number.")
            return None
        
        from FCTC_app.save_doc_data import upload_data_to_db, download_data_from_db
        doc_data = download_data_from_db( actuator_no=actuator_number, client=self.client )
        if len(doc_data) > 0:
            choice = QMessageBox.critical(
                None,
                "Warning",
                "Data exists, Do you want to override it ?",
                QMessageBox.StandardButton.Yes,
                QMessageBox.StandardButton.No,
            )
            if choice == QMessageBox.StandardButton.Yes:
                upload_data_to_db(make_meta_data(self), client=self.client)
                make_document(
                    meta_data=make_meta_data(self),
                    output_path="../local_data/documents/{}.docx".format(actuator_number),
                    client=self.client
                )    
                #save_json(make_meta_data(self))
                self.show_message("Data saved.")
            elif choice == QMessageBox.StandardButton.No:
                return None
            else:
                return None
        elif len(doc_data) == 0:
            upload_data_to_db(make_meta_data(self), client=self.client)
            make_document(
                meta_data=make_meta_data(self),
                output_path="../local_data/documents/{}.docx".format(actuator_number),
                client=self.client
            )
            #save_json(make_meta_data(self))
            self.show_message("Data saved.")
        return None
    
    def on_make_document_clicked(self):
        """
            Description : make word document and pdf.
        """
        meta_data = make_meta_data(self,default=False)
        # make_document_thread = threading.Thread(
        #     target=lambda: make_document(
        #         meta_data=meta_data,
        #         save_pdf=True,
        #         client=self.client
        #     )
        # )
        # make_document_thread.start()

        make_document(
                meta_data=meta_data,
                save_pdf=True,
                client=self.client
            )

        self.show_message("Document made.")
        print(meta_data)

        return None

    def show_document(
            self,
            document_path = "../documents/checklist_report.docx"
            ):
        os.system('start {}'.format(document_path))
        return None

    def make_document_number(
            self
    ):
        actuator_number = self.actuator_sno_lineedit.toPlainText()
        if len(actuator_number) > 0:
            i = len(actuator_number)
            if i > 5:
                i = 5
            act_last_digits = actuator_number[-i:]
        else:
            act_last_digits = ""

        time_format     = "%d%m%Y"
        time_digits     = dt.datetime.now().strftime(format=time_format)

        document_number = "FCTC_" + act_last_digits + "_" + time_digits

        self.document_no_label.setText("Document number : " + document_number)
        self.document_no_label.adjustSize()

        return None

    def set_signature_image(
            self,
            label
    ):
        self.signature_image_path = "../images/1.png"

        w,h = 150,40
        label.setPixmap(self.assembler_pixmap.scaled(
            w,h,Qt.AspectRatioMode.KeepAspectRatio
        ))
        label.adjustSize()
        return None

    def on_find_clicked(self):
                
        actuator_number         = self.actuator_sno_lineedit.toPlainText()

        from FCTC_app.save_doc_data import download_data_from_db

        doc_data = download_data_from_db(actuator_no=actuator_number, client=self.client)

        if len(doc_data) > 0:
            choice = QMessageBox.critical(
                None,
                "Warning",
                "Do you want to populate the data in gui",
                QMessageBox.StandardButton.Yes,
                QMessageBox.StandardButton.No,
            )
            if choice == QMessageBox.StandardButton.Yes:
                fill_data(
                    gui_object=self,
                    meta_data=doc_data[0]
                )
                self.update_signature_image()
                self.assembled_by_signature.adjustSize()
                self.tested_by_signature.adjustSize()
                self.approved_by_signature.adjustSize()
                self.show_message("Done.")
            elif choice == QMessageBox.StandardButton.No:
                return None
        elif len(doc_data) == 0:
            self.show_warning("Data does not exists.")
            return None
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

    def show_signature_image(
            self,
            object=None,
            no_sig=False,
            username=""
    ):
        # if not no_sig:
        #     object_pixmap           = QPixmap("../images/signatures/{0}.png".format(self.user_detail['username']))
        # elif no_sig:
        #     object_pixmap           = QPixmap("../images/signatures/no_signature_found.png")

        if no_sig:
            object_pixmap           = QPixmap("../images/signatures/no_signature_found.png")
        else :
            image                   = ImageQt(self.get_signatures_from_db(usernmae=self.username))
            object_pixmap           = QPixmap.fromImage(image)

        w,h = 120,30
        object.setPixmap(object_pixmap.scaled(
           w,h,Qt.AspectRatioMode.KeepAspectRatio
        ))
        object.adjustSize()
        return None

    def update_signature_image(
            self
    ):
        assembler_name      = self.assembled_by_name.text()
        tester_name         = self.tested_by_name.text()
        approver_name       = self.approved_by_name.text()

        print("-----------------------------------------------------")
        print(assembler_name, tester_name, approver_name)
        
        #object_pixmap           = QPixmap("../images/signatures/{0}.png".format(assembler_name))
        if assembler_name == "No name found":
            object_pixmap           = QPixmap("../images/signatures/no_signature_found.png")
        else:
            image               = self.get_signatures_from_db(usernmae=assembler_name)
            image               = ImageQt(image)
            object_pixmap       = QPixmap.fromImage(image)
        w,h = 120,30
        self.assembled_by_signature.setPixmap(object_pixmap.scaled(
           w,h,Qt.AspectRatioMode.KeepAspectRatio
        ))
        self.assembled_by_signature.adjustSize()

        #object_pixmap           = QPixmap("../images/signatures/{0}.png".format(tester_name))
        if tester_name == "No name found":
            object_pixmap           = QPixmap("../images/signatures/no_signature_found.png")
        else:
            image               = self.get_signatures_from_db(usernmae=tester_name)
            image               = ImageQt(image)
            object_pixmap       = QPixmap.fromImage(image)
        w,h = 120,30
        self.tested_by_signature.setPixmap(object_pixmap.scaled(
           w,h,Qt.AspectRatioMode.KeepAspectRatio
        ))
        self.tested_by_signature.adjustSize()

        #object_pixmap           = QPixmap("../images/signatures/{0}.png".format(approver_name))
        if approver_name == "No name found":
            object_pixmap           = QPixmap("../images/signatures/no_signature_found.png")
        else:
            image               = self.get_signatures_from_db(usernmae=approver_name)
            image               = ImageQt(image)
            object_pixmap       = QPixmap.fromImage(image)
        w,h = 120,30
        self.approved_by_signature.setPixmap(object_pixmap.scaled(
           w,h,Qt.AspectRatioMode.KeepAspectRatio
        ))
        self.approved_by_signature.adjustSize()

        return None

    def on_request_approval_clicked(
            self
    ):
        
        self.show_message("Not implemented yet.")

        return None

    def on_send_email_clicked(
            self
    ):
        self.show_message("Not implemented yet.")

        """
        TODO
        - set the reciver email and cc email addresses.
        - algorithm to email not found.
        - send email but first give a warning message.
        """
        # with open("../../user_data/emails/admin.txt", "r") as file:
        #     admin_email = file.readline()

        # cc = []
        # with open("../../user_data/emails/cc.txt", "r") as file:
        #     cc = file.readlines()[0].split(',')

        # send_email(
        #     to=admin_email,
        #     cc=cc,
        #     actuator_no=self.actuator_sno_lineedit.toPlainText()
        # )

        return None

    def valid_actuator_number(
            self,
            actuator_number = ""
    ):
        bool = True

        '''
        Example actuator no: 1040101B350
        '''
        # length check
        #if len(actuator_number) == 11:
        #    bool = True
        # astype check
        return bool

    def save_data_on_common_shared(self):
        return None

    def get_signatures_from_db(self, usernmae=""):
        
        signatures      = self.client.myDatabase['signatures']
        cursor          = signatures.find({"username": usernmae})
        cursor          = list(cursor)
        if len(cursor) == 0:
            self.show_warning("Signature cannot be found, please contact administration.")
            return None
        elif len(cursor) > 0:
            return Image.open(io.BytesIO(cursor[0]['data']))
        return None

def main():
    app     = QApplication(sys.argv)

    user_detail = {
        "username": "admin",
        "user_type": "admin"
    }

    window  = Main_window(
        client=client,
        user_detail=user_detail
    )
    window.show()
    app.exec()

if __name__ == '__main__':
    main()