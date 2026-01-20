from ui.adress_form_ui import Ui_Dialog as Ui_AdressForm
from ui.transfer_form_ui import Ui_Dialog as Ui_TransferForm   
from PySide6.QtWidgets import QDialog

class BasePopout(QDialog):
    def __init__(self,Ui_class:object , parent=None):
        super().__init__(parent)

        self.ui= Ui_class()
        self.ui.setupUi(self)
    def guardar_datos(self):
        print("ceerado formulario")
        self.accept()

class AdressForm(BasePopout):
    def __init__(self , parent =None):
        super().__init__(Ui_AdressForm,parent)


        self.ui.btn_add_nAddress.clicked.connect(self.guadar_datos)


        
class TransferForm(BasePopout):
    
    def __init__(self,parent =None):
        super().__init__(Ui_TransferForm,parent)


        self.ui.btn_add_nTransfer.clicked.connect(self.guardar_datos)
