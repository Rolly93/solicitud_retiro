# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'adress_form.ui'
##
## Created by: Qt User Interface Compiler version 6.10.2
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
        Dialog.resize(389, 300)
        self.verticalLayout = QVBoxLayout(Dialog)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.frame_5 = QFrame(Dialog)
        self.frame_5.setObjectName(u"frame_5")
        self.frame_5.setFrameShape(QFrame.Shape.StyledPanel)
        self.frame_5.setFrameShadow(QFrame.Shadow.Raised)
        self.verticalLayout_5 = QVBoxLayout(self.frame_5)
        self.verticalLayout_5.setObjectName(u"verticalLayout_5")
        self.lbl_name_yard = QLabel(self.frame_5)
        self.lbl_name_yard.setObjectName(u"lbl_name_yard")

        self.verticalLayout_5.addWidget(self.lbl_name_yard)

        self.name_yard = QLineEdit(self.frame_5)
        self.name_yard.setObjectName(u"name_yard")
        self.name_yard.setMaxLength(32767)

        self.verticalLayout_5.addWidget(self.name_yard)

        self.lbl_calle = QLabel(self.frame_5)
        self.lbl_calle.setObjectName(u"lbl_calle")

        self.verticalLayout_5.addWidget(self.lbl_calle)

        self.input_calle = QLineEdit(self.frame_5)
        self.input_calle.setObjectName(u"input_calle")

        self.verticalLayout_5.addWidget(self.input_calle)

        self.lbl_municipio = QLabel(self.frame_5)
        self.lbl_municipio.setObjectName(u"lbl_municipio")

        self.verticalLayout_5.addWidget(self.lbl_municipio)

        self.input_municipio = QLineEdit(self.frame_5)
        self.input_municipio.setObjectName(u"input_municipio")

        self.verticalLayout_5.addWidget(self.input_municipio)

        self.btn_add_nAddress = QPushButton(self.frame_5)
        self.btn_add_nAddress.setObjectName(u"btn_add_nAddress")

        self.verticalLayout_5.addWidget(self.btn_add_nAddress)


        self.verticalLayout.addWidget(self.frame_5)


        self.retranslateUi(Dialog)

        QMetaObject.connectSlotsByName(Dialog)
    # setupUi

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(QCoreApplication.translate("Dialog", u"Dialog", None))
        self.lbl_name_yard.setText(QCoreApplication.translate("Dialog", u"Nombre del Patio", None))
        self.lbl_calle.setText(QCoreApplication.translate("Dialog", u"Calle", None))
        self.lbl_municipio.setText(QCoreApplication.translate("Dialog", u"Estado / Municipio", None))
        self.btn_add_nAddress.setText(QCoreApplication.translate("Dialog", u"Guardar Nueva Direccion", None))
    # retranslateUi

