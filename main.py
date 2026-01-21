import sys
from PySide6.QtWidgets import QApplication, QMainWindow ,QGraphicsScene ,QGraphicsPixmapItem
from PySide6.QtGui import QPixmap ,QImage 
import fitz
from PySide6.QtGui import QPainter 
from PySide6.QtCore import Qt
from ui.main_ui import Ui_MainWindow 
from data import cargar_todo
from data import cargar_patios
from PySide6.QtWidgets import QMessageBox
from PySide6 import  QtCore
import os
from pathlib import Path
class MiApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self._aduana = ""
        self._tipo_solicitud = ""
        self._tipo_unidad = ""
        self._origen = ""
        self._destino = ""
        self._referencia = ""
        self._nombre_patio = ""
        self._direccion_patio = ""
        self._scac = ""
        self._name_transfer = ""
        self._doc = None
        self.page_actual = 0
        self.total_paginas = 0
        self.lista_solicitudes = list(sorted([format_solicitu for format_solicitu in self.dic_file_route()]))
        self.dic_solicitudes = self.dic_file_route()
        
        #que era esto??
        #self.datos = load_data()

        
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.scene = QGraphicsScene(self)
        self.ui.display_pdf.setScene(self.scene)

        self.pdf_item = QGraphicsPixmapItem()
        self.scene.addItem(self.pdf_item)

        #Ajuste Visual para visor
        self.ui.display_pdf.setRenderHint(QPainter.Antialiasing)
        #self.ui.display_pdf.dragMoveEvent(QtWidgets.QGraphicsView.ScrollHandDrag)
        self.ui.display_pdf.setStyleSheet("background-color: #202020;")

        #funcionamento del los toolbox
        self.ui.tbox_agregar_direccion.clicked.connect(self.popout_addres_form)
        self.ui.tbox_agregar_linea_transfer.clicked.connect(self.popout_tranferForm)

        #asignacion de comboBoc
        self.ui.cmbox_formato.addItems(self.lista_solicitudes)
        self.ui.cmbox_formato.currentTextChanged.connect(self.cambio_plantilla)
        self.ui.cmbox_tipo_unidad.addItems(["Trailer","Placa"])
        
        self.ui.cmbox_origen.addItems(self.cargar_patios())
        self.ui.cmbox_destino.addItems(self.cargar_patios())

        
        self.ui.btn_previsuzalizar.clicked.connect(self.previsualizar_pdf)
        self.ui.display_pdf
        #extraccion del dato del combox
        self.ui.display_pdf

        self.ui.cobox_aduana.addItem("240")
        self.ui.cobox_aduana.addItem("800")

        if self.dic_solicitudes:
            QtCore.QTimer.singleShot(0, self.cambio_plantilla)

    

    def get_file_route(self):
        ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
        ASSTES_DIR = os.path.join(ROOT_DIR, "assets")

        file_names = [route_plantilla.get("filename","") for route_plantilla in cargar_todo().get("solicitud", {}).values()]
        route_filename = [os.path.join(ASSTES_DIR, filename) for filename in file_names]
        print(route_filename)


    def previsualizar_pdf(self):
        print("previsualizar")

        referencia = self.ui.input_Referencia.text()
        if not self._isvalid_reference(referencia):
            return
       
        self._aduana = self.ui.cobox_aduana.currentText()
        self._tipo_solicitud = self.ui.cmbox_formato.currentText()
        self._tipo_unidad = self.ui.cmbox_tipo_unidad.currentText()
        self._origen = self.ui.cmbox_origen.currentText()
        self._destino = self.ui.cmbox_destino.currentText()
        self._referencia = self.ui.input_Referencia.text()
        print("revision de datos", self._aduana, self._tipo_solicitud, self._tipo_unidad, self._origen, self._destino, self._referencia)


    def _isvalid_reference(self,referencia):
        count_characteres = len(referencia)
        if not count_characteres == 10 and not (referencia.startswith("92B") or referencia.startswith("82B")) :
            msg = QMessageBox(self)
            msg.setIcon(QMessageBox.Critical) 
            msg.setWindowTitle("Error de Referencia")
            msg.setText("La referencia ingresada es inválida.")
            msg.setInformativeText("Asegúrese de que tenga 10 caracteres y comience con '92B' o '82B'.")
            msg.exec()
            return False
        return True
            
            


    def popout_tranferForm(self):
        from popout import TransferForm
        
        dialog_transfer = TransferForm(self)

        if dialog_transfer.exec():
            scac = dialog_transfer.ui.scac_transfer.text()
            name_transfer = dialog_transfer.ui.name_linea_transfer.text()
        

    def popout_addres_form(self):
        from popout import AdressForm
        dialog_adress = AdressForm(self)

        if dialog_adress.exec():
            nombre_patio = dialog_adress.ui.name_yard.text()
            adress_patio = dialog_adress.ui.address_yard.text()
        
    def dic_file_route(self):
        from pathlib import Path
        ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
        ASSTES_DIR = Path(__file__).parent / "assets"

        dic_format = {
        nombre:  str(ASSTES_DIR / ruta.get("filename", ""))
        
          for nombre, ruta in cargar_todo().get("solicitud", {}).items() 
    }
        return dic_format

    def cargar_patios(self):
        patios = [patio.get("name") for patio in cargar_patios() ]
        
        return patios
    
        

    def cambio_plantilla(self ):
        
        nombre_solicitud = self.ui.cmbox_formato.currentText()
        nombre_solicitud = nombre_solicitud.replace(" ","-").lower()
        
        if nombre_solicitud in self.dic_solicitudes:
            pdf_route = Path(__file__).parent /self.dic_solicitudes[nombre_solicitud]

        if pdf_route.exists():
            try:
                if self._doc:
                    self._doc.close()
                
                self._doc = fitz.open(str(pdf_route))   
                self.tota_pages = self._doc.page_count
                self.page_actual = 0
                self.mostrar_pagina()
                
            except Exception as e:
                print(f"Error al abrir PDF: {e}")
        else:
            print(f"Archivo no encontrado en: {pdf_route}")

    def mostrar_pagina(self):
        if not self._doc:
            return

        try:
            page = self._doc.load_page(self.page_actual)
            
            # Renderizado de alta calidad (Zoom 2.0)
            mat = fitz.Matrix(2.0, 2.0)
            pix = page.get_pixmap(matrix=mat, alpha=False)
            
            # Conversión a formato Qt
            img = QImage(pix.samples, pix.width, pix.height, pix.stride, QImage.Format_RGB888)
            self.pdf_item.setPixmap(QPixmap.fromImage(img))
            self.ui.lbl_page_counter.setText(f"Pagina {self.page_actual + 1} / {self.total_paginas}")

            self.ui.display_pdf.fitInView(self.pdf_item, Qt.KeepAspectRatio)
            
        except Exception as e:
            print(f"Error al renderizar página: {e}")


    def mostrar_pdf(self,ruta_pdf):
        import fitz
        doc = fitz.open(ruta_pdf)
        page = doc.load_page(0)

        pix = page.get_pixmap(matrix=fitz.Matrix(2.0,2.0))

        fmt = QImage.Format_RGBA888
        img = QImage(pix.samples, pix.width, pix.height, pix.stride, fmt)
        pixmap = QPixmap.fromImage(img)
        
        self.escena = QGraphicsScene()
        self.escena.addPixmap(pixmap)




if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MiApp()
    window.show()
    sys.exit(app.exec())