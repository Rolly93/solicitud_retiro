# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'main.ui'
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
from PySide6.QtWidgets import (QAbstractScrollArea, QApplication, QComboBox, QFrame,
    QGraphicsView, QGridLayout, QHBoxLayout, QLabel,
    QLineEdit, QMainWindow, QMenuBar, QPushButton,
    QSizePolicy, QStatusBar, QToolButton, QVBoxLayout,
    QWidget)

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(1017, 767)
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.gridLayout = QGridLayout(self.centralwidget)
        self.gridLayout.setObjectName(u"gridLayout")
        self.frame = QFrame(self.centralwidget)
        self.frame.setObjectName(u"frame")
        self.frame.setFrameShape(QFrame.Shape.StyledPanel)
        self.frame.setFrameShadow(QFrame.Shadow.Raised)
        self.horizontalLayout_4 = QHBoxLayout(self.frame)
        self.horizontalLayout_4.setObjectName(u"horizontalLayout_4")
        self.frame_3 = QFrame(self.frame)
        self.frame_3.setObjectName(u"frame_3")
        self.frame_3.setFrameShape(QFrame.Shape.Box)
        self.frame_3.setFrameShadow(QFrame.Shadow.Plain)
        self.verticalLayout_6 = QVBoxLayout(self.frame_3)
        self.verticalLayout_6.setObjectName(u"verticalLayout_6")
        self.frame_4 = QFrame(self.frame_3)
        self.frame_4.setObjectName(u"frame_4")
        self.frame_4.setFrameShape(QFrame.Shape.StyledPanel)
        self.frame_4.setFrameShadow(QFrame.Shadow.Raised)
        self.verticalLayout_2 = QVBoxLayout(self.frame_4)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.lbl_aduana = QLabel(self.frame_4)
        self.lbl_aduana.setObjectName(u"lbl_aduana")

        self.verticalLayout_2.addWidget(self.lbl_aduana)

        self.cobox_aduana = QComboBox(self.frame_4)
        self.cobox_aduana.setObjectName(u"cobox_aduana")
        self.cobox_aduana.setDuplicatesEnabled(False)

        self.verticalLayout_2.addWidget(self.cobox_aduana)

        self.lbl_format = QLabel(self.frame_4)
        self.lbl_format.setObjectName(u"lbl_format")

        self.verticalLayout_2.addWidget(self.lbl_format)

        self.cmbox_formato = QComboBox(self.frame_4)
        self.cmbox_formato.setObjectName(u"cmbox_formato")

        self.verticalLayout_2.addWidget(self.cmbox_formato)

        self.lbl_tipo_unidad = QLabel(self.frame_4)
        self.lbl_tipo_unidad.setObjectName(u"lbl_tipo_unidad")

        self.verticalLayout_2.addWidget(self.lbl_tipo_unidad)

        self.cmbox_tipo_unidad = QComboBox(self.frame_4)
        self.cmbox_tipo_unidad.setObjectName(u"cmbox_tipo_unidad")

        self.verticalLayout_2.addWidget(self.cmbox_tipo_unidad)


        self.verticalLayout_6.addWidget(self.frame_4)

        self.frame_5 = QFrame(self.frame_3)
        self.frame_5.setObjectName(u"frame_5")
        self.frame_5.setFrameShape(QFrame.Shape.StyledPanel)
        self.frame_5.setFrameShadow(QFrame.Shadow.Raised)
        self.verticalLayout_7 = QVBoxLayout(self.frame_5)
        self.verticalLayout_7.setObjectName(u"verticalLayout_7")
        self.lbl_datos_embarque = QLabel(self.frame_5)
        self.lbl_datos_embarque.setObjectName(u"lbl_datos_embarque")
        self.lbl_datos_embarque.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.verticalLayout_7.addWidget(self.lbl_datos_embarque)

        self.lbl_origen = QLabel(self.frame_5)
        self.lbl_origen.setObjectName(u"lbl_origen")

        self.verticalLayout_7.addWidget(self.lbl_origen)

        self.cmbox_origen = QComboBox(self.frame_5)
        self.cmbox_origen.setObjectName(u"cmbox_origen")

        self.verticalLayout_7.addWidget(self.cmbox_origen)

        self.lbl_destino = QLabel(self.frame_5)
        self.lbl_destino.setObjectName(u"lbl_destino")

        self.verticalLayout_7.addWidget(self.lbl_destino)

        self.cmbox_destino = QComboBox(self.frame_5)
        self.cmbox_destino.setObjectName(u"cmbox_destino")

        self.verticalLayout_7.addWidget(self.cmbox_destino)

        self.lbl_referencia = QLabel(self.frame_5)
        self.lbl_referencia.setObjectName(u"lbl_referencia")

        self.verticalLayout_7.addWidget(self.lbl_referencia)

        self.input_Referencia = QLineEdit(self.frame_5)
        self.input_Referencia.setObjectName(u"input_Referencia")

        self.verticalLayout_7.addWidget(self.input_Referencia)


        self.verticalLayout_6.addWidget(self.frame_5)

        self.frame_8 = QFrame(self.frame_3)
        self.frame_8.setObjectName(u"frame_8")
        self.frame_8.setFrameShape(QFrame.Shape.Box)
        self.frame_8.setFrameShadow(QFrame.Shadow.Raised)
        self.verticalLayout_4 = QVBoxLayout(self.frame_8)
        self.verticalLayout_4.setObjectName(u"verticalLayout_4")
        self.horizontalLayout_3 = QHBoxLayout()
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.btn_previews = QPushButton(self.frame_8)
        self.btn_previews.setObjectName(u"btn_previews")

        self.horizontalLayout_3.addWidget(self.btn_previews)

        self.lbl_page_counter = QLabel(self.frame_8)
        self.lbl_page_counter.setObjectName(u"lbl_page_counter")
        self.lbl_page_counter.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.horizontalLayout_3.addWidget(self.lbl_page_counter)

        self.btn_next = QPushButton(self.frame_8)
        self.btn_next.setObjectName(u"btn_next")

        self.horizontalLayout_3.addWidget(self.btn_next)


        self.verticalLayout_4.addLayout(self.horizontalLayout_3)

        self.btn_previsuzalizar = QPushButton(self.frame_8)
        self.btn_previsuzalizar.setObjectName(u"btn_previsuzalizar")

        self.verticalLayout_4.addWidget(self.btn_previsuzalizar)

        self.btn_generar_pdf = QPushButton(self.frame_8)
        self.btn_generar_pdf.setObjectName(u"btn_generar_pdf")

        self.verticalLayout_4.addWidget(self.btn_generar_pdf)


        self.verticalLayout_6.addWidget(self.frame_8)


        self.horizontalLayout_4.addWidget(self.frame_3)

        self.display_pdf = QGraphicsView(self.frame)
        self.display_pdf.setObjectName(u"display_pdf")
        self.display_pdf.setSizeAdjustPolicy(QAbstractScrollArea.SizeAdjustPolicy.AdjustToContents)
        self.display_pdf.setTransformationAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)

        self.horizontalLayout_4.addWidget(self.display_pdf)


        self.gridLayout.addWidget(self.frame, 1, 0, 1, 1)

        self.frame_2 = QFrame(self.centralwidget)
        self.frame_2.setObjectName(u"frame_2")
        self.frame_2.setFrameShape(QFrame.Shape.StyledPanel)
        self.frame_2.setFrameShadow(QFrame.Shadow.Raised)
        self.horizontalLayout_5 = QHBoxLayout(self.frame_2)
        self.horizontalLayout_5.setObjectName(u"horizontalLayout_5")
        self.horizontalLayout_5.setContentsMargins(0, -1, -1, -1)
        self.tbox_agregar_linea_transfer = QToolButton(self.frame_2)
        self.tbox_agregar_linea_transfer.setObjectName(u"tbox_agregar_linea_transfer")

        self.horizontalLayout_5.addWidget(self.tbox_agregar_linea_transfer)

        self.tbox_agregar_direccion = QToolButton(self.frame_2)
        self.tbox_agregar_direccion.setObjectName(u"tbox_agregar_direccion")

        self.horizontalLayout_5.addWidget(self.tbox_agregar_direccion)


        self.gridLayout.addWidget(self.frame_2, 0, 0, 1, 1)

        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QMenuBar(MainWindow)
        self.menubar.setObjectName(u"menubar")
        self.menubar.setGeometry(QRect(0, 0, 1017, 25))
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QStatusBar(MainWindow)
        self.statusbar.setObjectName(u"statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)

        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi


    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"MainWindow", None))
        self.lbl_aduana.setText(QCoreApplication.translate("MainWindow", u"Aduana", None))
        self.cobox_aduana.setPlaceholderText("")
        self.lbl_format.setText(QCoreApplication.translate("MainWindow", u"Formato Solicitud", None))
        self.lbl_tipo_unidad.setText(QCoreApplication.translate("MainWindow", u"Tipo De Unidad", None))
        self.lbl_datos_embarque.setText(QCoreApplication.translate("MainWindow", u"--- Datos de embarque ---", None))
        self.lbl_origen.setText(QCoreApplication.translate("MainWindow", u"Origen", None))
        self.cmbox_origen.setCurrentText("")
        self.lbl_destino.setText(QCoreApplication.translate("MainWindow", u"Destino", None))
        self.lbl_referencia.setText(QCoreApplication.translate("MainWindow", u"Referencia", None))
        self.btn_previews.setText(QCoreApplication.translate("MainWindow", u"Pagina Anterior", None))
        self.lbl_page_counter.setText(QCoreApplication.translate("MainWindow", u"Page p / x", None))
        self.lbl_page_counter.setProperty(u"page_count", "")
        self.btn_next.setText(QCoreApplication.translate("MainWindow", u"Siguiente pagina", None))
        self.btn_previsuzalizar.setText(QCoreApplication.translate("MainWindow", u"Pre-visualizar", None))
        self.btn_generar_pdf.setText(QCoreApplication.translate("MainWindow", u"Generar PDF", None))
        self.tbox_agregar_linea_transfer.setText(QCoreApplication.translate("MainWindow", u"Agregar Linea Trasfer", None))
        self.tbox_agregar_direccion.setText(QCoreApplication.translate("MainWindow", u"Agregar Direccion", None))
    # retranslateUi

