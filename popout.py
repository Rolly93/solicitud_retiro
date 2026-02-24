from PySide6.QtWidgets import QDialog
from ui.adress_form_ui import Ui_Dialog as Ui_AdressForm
from ui.transfer_form_ui import Ui_Dialog as Ui_TransferForm   

class BasePopout(QDialog):
    def __init__(self,Ui_class:object , parent=None):
        super().__init__(parent)

        self.ui= Ui_class()
        self.ui.setupUi(self)
    def guardar_datos(self):
        print("cerrando formulario")
        self.accept()

class AdressForm(BasePopout):
    def __init__(self , parent =None):
        super().__init__(Ui_AdressForm,parent)
        

        self.setWindowTitle("Datos del Patio")
        self.ui.btn_add_nAddress.clicked.connect(self.guardar_datos)
        self.ui.name_yard.textChanged.connect(self.direccion)
        self.ui.input_calle.textChanged.connect(self.direccion)
        self.ui.btn_add_nAddress.setEnabled(False)

    def direccion (self):
        self.name = self.ui.name_yard.text()
        self.street = self.ui.input_calle.text()
        if self.name.strip() != "" and self.street.strip() !="":
            self.ui.name_yard.setStyleSheet("border: 1px solid #27ae60;")
            self.ui.input_calle.setStyleSheet("border: 1px solid #27ae60;")
            self.ui.btn_add_nAddress.setEnabled(True)
        else:
            self.ui.name_yard.setStyleSheet("border: 1px solid #c0392b;")
            self.ui.input_calle.setStyleSheet("border: 1px solid #c0392b;")
            self.ui.btn_add_nAddress.setEnabled(False)
        

class TransferForm(BasePopout):
    
    def __init__(self,parent =None):
        super().__init__(Ui_TransferForm,parent)
        
        self.setWindowTitle("Datos del Trasnfer")
        self.ui.scac_transfer.setInputMask(">AAAA;_")
        self.ui.scac_transfer.setMaxLength(4)

        self.ui.scac_transfer.textChanged.connect(self.validar_scac)
        self.ui.btn_add_nTransfer.setEnabled(False)
        self.ui.btn_add_nTransfer.clicked.connect(self.guardar_datos)
        
        
    def validar_scac (self):
        if self.ui.scac_transfer.hasAcceptableInput():
            self.ui.scac_transfer.setStyleSheet("border: 1px solid #27ae60;")
            self.ui.btn_add_nTransfer.setEnabled(True)
        else:
            self.ui.scac_transfer.setStyleSheet("border: 1px solid #c0392b;")
            self.ui.btn_add_nTransfer.setEnabled(False)
