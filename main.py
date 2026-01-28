import os
import sys
import fitz
from pathlib import Path
from PySide6 import  QtCore
from data import cargar_todo , get_coord
from PySide6.QtCore import Qt
from data import cargar_patios , get_data_transfer
from PySide6.QtGui import QPainter 
from ui.main_ui import Ui_MainWindow 
from PySide6.QtGui import QPixmap ,QImage 
from PySide6.QtWidgets import QMessageBox ,QLineEdit ,QLabel , QComboBox
from PySide6.QtWidgets import QApplication, QMainWindow ,QGraphicsScene ,QGraphicsPixmapItem, QGridLayout, QLabel, QLineEdit , QWidget

class PDFGraphicsItem(QGraphicsPixmapItem):
    # Definimos una señal personalizada (necesita heredar de QObject para señales, 
    # pero para simplicidad usaremos un callback)
    def __init__(self, callback):
        super().__init__()
        self.callback = callback

    def mousePressEvent(self, event):
        # Obtener posición local al item (la imagen)
        pos = event.pos()
        self.callback(pos.x(), pos.y())
        super().mousePressEvent(event)


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
        self.i_values_extra={}
        

        
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.scene = QGraphicsScene(self)
        self.ui.display_pdf.setScene(self.scene)

        self.combos_box = [self.ui.cmbox_destino, self.ui.cmbox_origen, self.ui.cmbox_formato, self.ui.cmbox_tipo_unidad , self.ui.cobox_aduana]
        
        
        
        
        #self.pdf_item = QGraphicsPixmapItem()
        self.pdf_item = PDFGraphicsItem(self.on_pdf_click)
        self.scene.addItem(self.pdf_item)

        #Ajuste Visual para visor
        self.ui.display_pdf.setRenderHint(QPainter.Antialiasing)
        #self.ui.display_pdf.dragMoveEvent(QtWidgets.QGraphicsView.ScrollHandDrag)
        self.ui.display_pdf.setStyleSheet("background-color: #202020;")

        self.layout_dinamico = self.ui.verticalLayout_7

        #btn de guardar
        self.ui.btn_generar_pdf.clicked.connect(self.guardar)
        
        #funcionamento del los toolbox
        self.ui.tbox_agregar_direccion.clicked.connect(self.popout_addres_form)
        self.ui.tbox_agregar_direccion.setFocusPolicy(Qt.TabFocus)
       # self.ui.tbox_agregar_direccion.installEventFilter(self)
        
        self.ui.tbox_agregar_linea_transfer.clicked.connect(self.popout_tranferForm)
        self.ui.tbox_agregar_linea_transfer.setFocusPolicy(Qt.TabFocus)
        #self.ui.tbox_agregar_linea_transfer.installEventFilter(self)
        

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
        
        #for combo in self.combos_box:
        #    combo.installEventFilter(self)
        
        if self.dic_solicitudes:
            QtCore.QTimer.singleShot(0, self.cambio_plantilla)

        if self.ui.cmbox_tipo_unidad:
            QtCore.QTimer.singleShot(0, self.preparar_campos_por_unidad)
            
        

    def eventFilter(self, obj, event):
        if event.type() == QtCore.QEvent.KeyPress:
            if event.key() in (Qt.key_Return , Qt.Key_Enter):

                if isinstance(obj , (QComboBox , QLineEdit)):
                    self.focusNextChild()
                    return True
                
                if obj in [self.ui.tbox_agregar_direccion , self.ui.tbox_agregar_linea_transfer]:
                    obj.animateClick()
                    return True

        # Si es cualquier otro evento, dejar que Qt lo maneje normalmente
        return super().eventFilter(obj, event)


    def get_file_route(self):
        ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
        ASSTES_DIR = os.path.join(ROOT_DIR, "assets")

        file_names = [route_plantilla.get("filename","") for route_plantilla in cargar_todo().get("solicitud", {}).values()]
        route_filename = [os.path.join(ASSTES_DIR, filename) for filename in file_names]

    
    def return_values_dynamic(self ,dynamic_values ):
        data_input = {}
        for nombre_campo , wdget in dynamic_values:

            if not isinstance(wdget , QComboBox):
                data_input[nombre_campo]= wdget.text()
            else:
                data_input[nombre_campo] =wdget.currentText()
        return data_input


    def previsualizar_pdf(self):
        
        data = {}
        self.i_values_extra = self.return_values_dynamic(self.inputs_extra.items())
                
        referencia = self.ui.input_Referencia.text()
        if not self._isvalid_reference(referencia):
            return
       
        self._aduana = self.ui.cobox_aduana.currentText()
        self._tipo_solicitud = self.ui.cmbox_formato.currentText()
        self._tipo_unidad = self.ui.cmbox_tipo_unidad.currentText()
        self._origen = self.ui.cmbox_origen.currentText()
        self._destino = self.ui.cmbox_destino.currentText()
        self._referencia = self.ui.input_Referencia.text()
        
        data["referencia"] = self._referencia
        data["aduana"] = self._aduana
        data["tipo_solicitud"] = self._tipo_solicitud
        data["tipo_unidad"] = self._tipo_unidad
        data["origen"] = self._origen
        data["destino"] = self._destino

        self.i_values_extra.update(data)

        self.escribir_en_pdf(self.i_values_extra)


        

        

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

        self.inputs_extra.clear()
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

        fila_inicio_dinamica = 7
        columna = 0
        offset_fila = 0

        for field in config_unidad["fields"]:
            if field["name"] in ["referencia", "origen", "destino"]:
                continue
            
            if field["name"] in ["linea_transporte"]:
                line_edit = QComboBox()
                line_edit.addItems(get_data_transfer().keys())
                
                
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

    def escribir_en_pdf(self, input_values):
        if not self._doc or not input_values: return
        page = self._doc.load_page(0) 

        # Constante universal: 72 pts/pulgada / 25.4 mm/pulgada
        MM_TO_PTS = 2.83465

        tipo_solicitud = input_values.get("tipo_solicitud")
        values = {k: v for k, v in input_values.items() if k != "tipo_solicitud"}

        for name, value in values.items():
            coords = get_coord(tipo_solicitud, name)
            if not coords or coords[0] is None: continue

            x_mm, y_mm = coords

            # Conversión directa y limpia
            x_pts = x_mm * MM_TO_PTS
            y_pts = y_mm * MM_TO_PTS

            if value:
                # Ajustamos un poco y_pts (-2) para que el texto no "pise" la línea
                page.insert_text((x_pts, y_pts - 2), str(value), 
                                 fontsize=15, # Tamaño más estándar para formularios
                                 fontname="helv",
                                 color=(0, 0, 0))

        self.mostrar_pagina()
            
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
            

    def preparar_campos_por_unidad(self):
            tipo = self.ui.cmbox_tipo_unidad.currentText() # "Trailer" o "Placa"

            # Aquí cargarías tu JSON (o usarías la variable donde lo tengas)
            # Por ahora simulamos que 'data_config' es tu JSON:
            data_config = cargar_todo().get("unidad", {}) 

            if tipo in data_config:
                config_unidad = data_config[tipo]
                self.actualizar_inputs_dinamicos(config_unidad)
    def guardar(self):
        guardar = "./test.pdf"

        self._doc.save(guardar,garbage=4 , deflate=True)


    def on_pdf_click(self, x_pix, y_pix):
        if not self._doc: return

        # 1. Obtener dimensiones reales del PDF en puntos (pts)
        rect = self._doc.load_page(0).rect
        pdf_w_pts = rect.width
        pdf_h_pts = rect.height

        # 2. Obtener el tamaño de la imagen renderizada (Pixmap)
        # Esto es vital para manejar el zoom de 2.0 correctamente
        pixmap_rect = self.pdf_item.pixmap().rect()
        img_w = pixmap_rect.width()
        img_h = pixmap_rect.height()

        # 3. Mapear Píxel -> Punto PDF (Regla de 3)
        x_pt = (x_pix / img_w) * pdf_w_pts
        y_pt = (y_pix / img_h) * pdf_h_pts

        # 4. Convertir Punto PDF -> Milímetros (1mm = 2.83465 pts)
        x_mm = x_pt / 2.83465
        y_mm = y_pt / 2.83465

        print(f"--- NUEVA CALIBRACIÓN ---")
        print(f"X: {x_mm:.2f} mm, Y: {y_mm:.2f} mm")

        # Copiar al portapapeles en formato listo para data.py
        QApplication.clipboard().setText(f'"x": {x_mm:.2f}, "y": {y_mm:.2f}')
        self.ui.statusbar.showMessage(f"Copiado: X={x_mm:.2f}, Y={y_mm:.2f}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MiApp()
    window.show()
    sys.exit(app.exec())