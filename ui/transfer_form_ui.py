# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'transfer_form.ui'
##
## Created by: Qt User Interface Compiler version 6.10.1
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QApplication, QDialog, QFrame, QLabel,
    QLineEdit, QPushButton, QSizePolicy, QVBoxLayout,
    QWidget)

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        if not Dialog.objectName():
            Dialog.setObjectName(u"Dialog")
        Dialog.resize(400, 300)
        self.verticalLayout = QVBoxLayout(Dialog)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.frame_2 = QFrame(Dialog)
        self.frame_2.setObjectName(u"frame_2")
        self.frame_2.setFrameShape(QFrame.Shape.StyledPanel)
        self.frame_2.setFrameShadow(QFrame.Shadow.Raised)
        self.verticalLayout_3 = QVBoxLayout(self.frame_2)
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.lbl_scac = QLabel(self.frame_2)
        self.lbl_scac.setObjectName(u"lbl_scac")

        self.verticalLayout_3.addWidget(self.lbl_scac)

        self.scac_transfer = QLineEdit(self.frame_2)
        self.scac_transfer.setObjectName(u"scac_transfer")

        self.verticalLayout_3.addWidget(self.scac_transfer)

        self.lbl_trasfer_name = QLabel(self.frame_2)
        self.lbl_trasfer_name.setObjectName(u"lbl_trasfer_name")

        self.verticalLayout_3.addWidget(self.lbl_trasfer_name)

        self.name_linea_transfer = QLineEdit(self.frame_2)
        self.name_linea_transfer.setObjectName(u"name_linea_transfer")

        self.verticalLayout_3.addWidget(self.name_linea_transfer)

        self.btn_add_nTransfer = QPushButton(self.frame_2)
        self.btn_add_nTransfer.setObjectName(u"btn_add_nTransfer")

        self.verticalLayout_3.addWidget(self.btn_add_nTransfer)


        self.verticalLayout.addWidget(self.frame_2)


        self.retranslateUi(Dialog)

        QMetaObject.connectSlotsByName(Dialog)
    # setupUi

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(QCoreApplication.translate("Dialog", u"Dialog", None))
        self.lbl_scac.setText(QCoreApplication.translate("Dialog", u"SCAC", None))
        self.lbl_trasfer_name.setText(QCoreApplication.translate("Dialog", u"Linea transfer", None))
        self.btn_add_nTransfer.setText(QCoreApplication.translate("Dialog", u"Guardar Transfer", None))
    # retranslateUi

