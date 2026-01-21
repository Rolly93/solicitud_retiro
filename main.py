import sys
from PySide6.QtWidgets import QApplication, QMainWindow ,QGraphicsScene ,QGraphicsPixmapItem
from PySide6.QtGui import QPixmap ,QImage 
import fitz
from PySide6.QtGui import QPainter 
from PySide6.QtCore import Qt
from ui.main_ui import Ui_MainWindow 
from data import cargar_todo
from data import cargar_patios
from PySide6.QtWidgets import QMessageBox ,QLineEdit ,QLabel
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
        #self.inputs_extra = {}
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

        self.layout_dinamico = self.ui.verticalLayout_7
        
        #funcionamento del los toolbox
        self.ui.tbox_agregar_direccion.clicked.connect(self.popout_addres_form)
        self.ui.tbox_agregar_linea_transfer.clicked.connect(self.popout_tranferForm)

        #asignacion de comboBoc
        self.ui.cmbox_formato.addItems(self.lista_solicitudes)
        self.ui.cmbox_formato.currentTextChanged.connect(self.cambio_plantilla)

        self.ui.cmbox_tipo_unidad.addItems(["Trailer","Placa"])
        self.ui.cmbox_tipo_unidad.currentTextChanged.connect(self.preparar_campos_por_unidad)

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
        self.cambio_plantilla()

        

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


    def actualizar_inputs_dinamicos(self, config_unidad):
            """
            config_unidad: es el diccionario de 'fields' para Placa o Trailer
            """
            # Limpieza (como hicimos antes)
            for i in reversed(range(self.layout_dinamico.count())):
                widget = self.layout_dinamico.itemAt(i).widget()
                if widget and widget.objectName() not in ["lbl_datos_embarque", "lbl_origen", "cmbox_origen", 
                                                         "lbl_destino", "cmbox_destino", "lbl_referencia", "input_Referencia"]:
                    widget.deleteLater()

            self.inputs_extra = {}
            self.config_actual = config_unidad # Guardamos la config para el PDF

            # Crear inputs basados en el JSON
            for field in config_unidad["fields"]:
                # Saltamos los campos que ya son fijos en tu UI (opcional)
                if field["name"] in ["referencia", "origen", "destino"]:
                    continue

                label = QLabel(field["label"])
                line_edit = QLineEdit()
                line_edit.setObjectName(f"input_{field['name']}")

                self.layout_dinamico.addWidget(label)
                self.layout_dinamico.addWidget(line_edit)

                # Guardamos por 'name' para mapear con el JSON después
                self.inputs_extra[field["name"]] = line_edit

    def escribir_en_pdf(self):
            if not self._doc or not self.config_actual:
                return
    
            page = self._doc.load_page(0) # O usar field["page"]
            
            for field in self.config_actual["fields"]:
                valor = ""
                
                # 1. Buscar si es un campo fijo de la UI
                if field["name"] == "referencia": valor = self.ui.input_Referencia.text()
                elif field["name"] == "origen": valor = self.ui.cmbox_origen.currentText()
                elif field["name"] == "destino": valor = self.ui.cmbox_destino.currentText()
                # 2. Si no, buscar en los inputs dinámicos
                elif field["name"] in self.inputs_extra:
                    valor = self.inputs_extra[field["name"]].text()
    
                if valor:
                    # Convertir coordenadas de mm a puntos fitz
                    # Nota: fitz usa el origen arriba a la izquierda. 
                    # Si tus mm son desde abajo, hay que restar de la altura total.
                    rect_height = page.rect.height
                    x_pts = mm_to_pts(field["x"])
                    # Si el PDF mide 297mm (A4), ajustamos el eje Y si es necesario
                    y_pts = mm_to_pts(field["y"]) 
    
                    page.insert_text((x_pts, y_pts), valor, 
                                     fontsize=field["size"], 
                                     fontname="helv") # 'helv' es Helvetica en fitz
    

    def preparar_campos_por_unidad(self):
            tipo = self.ui.cmbox_tipo_unidad.currentText() # "Trailer" o "Placa"

            # Aquí cargarías tu JSON (o usarías la variable donde lo tengas)
            # Por ahora simulamos que 'data_config' es tu JSON:
            data_config = cargar_todo().get("unidad", {}) 

            if tipo in data_config:
                config_unidad = data_config[tipo]
                self.actualizar_inputs_dinamicos(config_unidad)

def mm_to_pts(mm):
    """Convierte milímetros a puntos tipográficos de PDF (1mm = 2.83465 pts)."""
    return mm * 2.83465
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MiApp()
    window.show()
    sys.exit(app.exec())