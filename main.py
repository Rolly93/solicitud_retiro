import os
import sys
import fitz
from pathlib import Path
from PySide6 import  QtCore
from data import cargar_todo
from PySide6.QtCore import Qt
from data import cargar_patios
from PySide6.QtGui import QPainter 
from ui.main_ui import Ui_MainWindow 
from PySide6.QtGui import QPixmap ,QImage 
from PySide6.QtWidgets import QMessageBox ,QLineEdit ,QLabel , QComboBox
from PySide6.QtWidgets import QApplication, QMainWindow ,QGraphicsScene ,QGraphicsPixmapItem, QGridLayout, QLabel, QLineEdit , QWidget



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
        self.inputs_extra = {}
        

        
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.scene = QGraphicsScene(self)
        self.ui.display_pdf.setScene(self.scene)

        self.combos_box = [self.ui.cmbox_destino, self.ui.cmbox_origen, self.ui.cmbox_formato, self.ui.cmbox_tipo_unidad , self.ui.cobox_aduana]
        
        
        
        
        self.pdf_item = QGraphicsPixmapItem()
        self.scene.addItem(self.pdf_item)

        #Ajuste Visual para visor
        self.ui.display_pdf.setRenderHint(QPainter.Antialiasing)
        #self.ui.display_pdf.dragMoveEvent(QtWidgets.QGraphicsView.ScrollHandDrag)
        self.ui.display_pdf.setStyleSheet("background-color: #202020;")

        self.layout_dinamico = self.ui.verticalLayout_7
        
        #funcionamento del los toolbox
        self.ui.tbox_agregar_direccion.clicked.connect(self.popout_addres_form)
        self.ui.tbox_agregar_direccion.setFocusPolicy(Qt.TabFocus)
        self.ui.tbox_agregar_direccion.installEventFilter(self)
        
        self.ui.tbox_agregar_linea_transfer.clicked.connect(self.popout_tranferForm)
        self.ui.tbox_agregar_linea_transfer.setFocusPolicy(Qt.TabFocus)
        self.ui.tbox_agregar_linea_transfer.installEventFilter(self)
        
        self.ui.input_Referencia.setFocusPolicy(Qt.TabFocus)

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

        self.ui.input_Referencia.returnPressed.connect(self.focusNextChild)
        
        for combo in self.combos_box:
            combo.installEventFilter(self)
        
        if self.dic_solicitudes:
            QtCore.QTimer.singleShot(0, self.cambio_plantilla)

        if self.ui.cmbox_tipo_unidad:
            QtCore.QTimer.singleShot(0, self.preparar_campos_por_unidad)
            
        
    def eventFilter(self, obj, event):
        if event.type() == QtCore.QEvent.KeyPress:
            if event.key() in (Qt.Key_Return, Qt.Key_Enter):
                if isinstance(obj , QComboBox):
                    self.focusNextChild()
                    return True
        
        if obj in [self.ui.tbox_agregar_direccion]:
            obj.animateClick()
            return True
        return super().eventFilter(obj, event)


    def get_file_route(self):
        ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
        ASSTES_DIR = os.path.join(ROOT_DIR, "assets")

        file_names = [route_plantilla.get("filename","") for route_plantilla in cargar_todo().get("solicitud", {}).values()]
        route_filename = [os.path.join(ASSTES_DIR, filename) for filename in file_names]
        print(route_filename)

    def 
    def previsualizar_pdf(self):
        
        for nombre_campo , wdget in self.inputs_extra.items():
            print(nombre_campo )
            if not isinstance(wdget , QComboBox):
                print(nombre_campo , wdget.text())
            else:
                print(nombre_campo , wdget.currentText())
                
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
        # 1. Referenciamos el layout que viene del UI (verticalLayout_7)
        # Si aún es un QVBoxLayout, lo vamos a manejar.
        layout = self.ui.verticalLayout_7 

        # 2. Limpieza de widgets antiguos
        for i in reversed(range(layout.count())):
            item = layout.itemAt(i)
            if item.widget():
                widget = item.widget()
                # No borrar los elementos base
                if widget.objectName() not in ["lbl_datos_embarque", "lbl_origen", "cmbox_origen", 
                                             "lbl_destino", "cmbox_destino", "lbl_referencia", "input_Referencia"]:
                    widget.deleteLater()


        # Verificamos si ya hemos hecho el cambio, si no, lo cambiamos.
        if not isinstance(layout, QGridLayout):
            # Guardamos los widgets fijos que queremos conservar
            fijos = [self.ui.lbl_datos_embarque, self.ui.lbl_origen, self.ui.cmbox_origen, 
                     self.ui.lbl_destino, self.ui.cmbox_destino, self.ui.lbl_referencia, self.ui.input_Referencia]

            # Creamos el nuevo layout de rejilla
            nuevo_layout = QGridLayout()
            nuevo_layout.setSpacing(10)

            # Re-insertamos los fijos al principio del nuevo layout (ocupando 2 columnas)
            for fila, widget in enumerate(fijos):
                nuevo_layout.addWidget(widget, fila, 0, 1, 2) # span de 2 columnas

            # Reemplazamos el layout del frame_5
            from PySide6.QtWidgets import QLayout
            old_layout = self.ui.frame_5.layout()
            if old_layout:

                QWidget().setLayout(old_layout) 

            self.ui.frame_5.setLayout(nuevo_layout)
            self.ui.verticalLayout_7 = nuevo_layout # Actualizamos la referencia
            layout = nuevo_layout


        self.config_actual = config_unidad

        # 4. Iniciar inserción en dos columnas DESPUÉS de los campos fijos
        # Como insertamos 7 widgets fijos, empezamos en la fila 7
        fila_inicio_dinamica = 7
        columna = 0
        offset_fila = 0

        for field in config_unidad["fields"]:
            if field["name"] in ["referencia", "origen", "destino"]:
                continue
            
            if field["name"] in ["linea_transporte"]:
                line_edit = QComboBox()
                line_edit.addItems(["TFSQ" , "MOGA"])
                
                
            else:
                line_edit = QLineEdit()
                line_edit.returnPressed.connect(self.focusNextChild)

            label = QLabel(field["label"])
            line_edit.setObjectName(f"input_{field['name']}")

            # Calculamos posición
            # Columna 0 usa c0 y c1 | Columna 1 usa c2 y c3
            r = fila_inicio_dinamica + offset_fila
            c_label = 0 if columna == 0 else 2
            c_input = 1 if columna == 0 else 3

            layout.addWidget(label, r, c_label)
            layout.addWidget(line_edit, r, c_input)

            self.inputs_extra[field["name"]] = line_edit
            
            self.restablecer_order_tab()

            # Lógica de alternancia
            if columna == 0:
                columna = 1
            else:
                columna = 0
                offset_fila += 1

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
    
    def restablecer_order_tab(self):
        order_widgets = [
            self.ui.cobox_aduana,
            self.ui.cmbox_formato,
            self.ui.cmbox_tipo_unidad,
            self.ui.cmbox_origen,
            self.ui.cmbox_destino,
            self.ui.input_Referencia
        ]
        

        
        def obtener_posicion(w):
            idx = self.ui.verticalLayout_7.indexOf(w)
            return self.ui.verticalLayout_7.getItemPosition(idx)

        
        dynamic = sorted(self.inputs_extra.values() , key=lambda w: obtener_posicion(w))
        
        btn_widgets = [
            self.ui.btn_previsuzalizar,
            self.ui.btn_generar_pdf,
            self.ui.tbox_agregar_linea_transfer,
            self.ui.tbox_agregar_direccion
        ]
        reorder_widgets = order_widgets + dynamic + btn_widgets
        
        for i in range(len(reorder_widgets) - 1):
            widget_actual = reorder_widgets[i]
            widget_next = reorder_widgets[i+1]
            
            self.setTabOrder(widget_actual, widget_next)
            

    def eventFilter(self, obj, event):
        # Verificamos si el evento es una tecla presionada
        if event.type() == QtCore.QEvent.KeyPress:
            # Si la tecla es Enter o Return
            if event.key() in (Qt.Key_Return, Qt.Key_Enter):
                # Si el objeto que tiene el foco es uno de tus ToolButtons
                if obj in [self.ui.tbox_agregar_direccion, self.ui.tbox_agregar_linea_transfer]:
                    obj.animateClick() # Simula el click visualmente
                    return True # Indica que ya manejamos el evento

        # Si es cualquier otro evento, dejar que Qt lo maneje normalmente
        return super().eventFilter(obj, event)

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