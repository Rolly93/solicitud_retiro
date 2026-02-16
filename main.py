
import sys
from PySide6 import  QtCore
from PySide6.QtCore import Qt  
from ui.main_ui import Ui_MainWindow 
from core.pdf_service import PDFService
from ui.form_manager import FormManager 
from  core.data_manager import DataManager
from PySide6.QtGui import QPainter ,QPixmap ,QImage 
from PySide6.QtWidgets import( QMessageBox ,
                              QComboBox,
                              QLineEdit ,
                              QApplication,
                              QMainWindow ,
                              QGraphicsScene ,
                              QGraphicsPixmapItem,
)
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
        self.pdf_service = PDFService()
        self.data_managet = DataManager()
        
        
        self._doc = self.pdf_service.doc
        
        self.total_paginas = 0
        self.page_actual = 0

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
        self.lista_solicitudes = self.data_managet.list_solicitud

        self.dic_solicitudes = self.data_managet._dict_solicitudes()
        self.inputs_extra = {}
        self.i_values_extra={}
        

        self.ui = Ui_MainWindow()
        
        
        self.ui.setupUi(self)
        self.scene = QGraphicsScene(self)
        self.ui.display_pdf.setScene(self.scene)

        layout = self.ui.horizontalLayout_4
        layout.setStretch(0, 0)
        layout.setStretch(1, 1)
        self.combos_box = [self.ui.cmbox_destino, self.ui.cmbox_origen, self.ui.cmbox_formato, self.ui.cmbox_tipo_unidad , self.ui.cobox_aduana]
        
        self.form_manager =FormManager(self, self.ui.frame_5, self.data_managet)
        
        
        
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

        self.ui.cmbox_origen.addItems(self.data_managet.list_yard)
        self.ui.cmbox_destino.addItems(self.data_managet.list_yard)
       
        self.ui.btn_previsuzalizar.clicked.connect(self.previsualizar_pdf)
        self.ui.display_pdf

        self.ui.cobox_aduana.addItem("240")
        self.ui.cobox_aduana.addItem("800")

        self.ui.input_Referencia.returnPressed.connect(self.focusNextChild)
        self._tipo_unidad = self.ui.cmbox_tipo_unidad.currentText()

        if self.ui.cmbox_tipo_unidad or self.dic_solicitudes:
            QtCore.QTimer.singleShot(0, self.preparar_campos_por_unidad)
            QtCore.QTimer.singleShot(0, self.cambio_plantilla)

        
    def handle_error(func):
        def wrapper(self,*args,**kwargs):
            try:
                return func(self,*args, **kwargs)
            except ValueError as e:
                self.show_message("Dato Invalido", "hubo un un problema con los datos",e,"warning" )
            except Exception as e:
                self.show_message("Erro del Sistema","Ocurrio un error inesperado",e,"error")
        return wrapper
        
        
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



    
    def return_values_dynamic(self ,dynamic_values ):
        data_input = {}
        
        for nombre_campo , wdget in dynamic_values:
            if not isinstance(wdget , QComboBox):
                data_input[nombre_campo]= wdget.text()
            else:
                data_input[nombre_campo] =wdget.currentText()
        return data_input

    def recolectar_formularios(self):
        self._destino = self.ui.cmbox_destino.currentText() 
        d_estado , d_calle  = self.data_managet.obtener_direccion(self._destino)
        self._tipo_unidad = self.ui.cmbox_tipo_unidad.currentText()
        self._origen = self.ui.cmbox_origen.currentText()
        self._aduana = self.ui.cobox_aduana.currentText() 
        o_estado , o_calle  = self.data_managet.obtener_direccion(self._origen)
        

        datos = {
        "referencia" :self._referencia,
        "aduana" :self._aduana,
        "tipo_solicitud" :self._tipo_solicitud,
        "tipo_unidad" :self._tipo_unidad,
        "origen" :self._origen,
        "destino" :self._destino,
        "direccion" : f"{d_estado} \n {d_calle}",
        "direccion_o":f"{o_estado} \n {o_calle}"
        }
        datos.update(self.return_values_dynamic(self.inputs_extra.items()))
        return datos
    
    
    @handle_error
    def previsualizar_pdf(self):
        self._referencia =self.ui.input_Referencia.text()

        
        if not self.data_managet.validar_Referencia(self._referencia):
            return

        
        datos =self.recolectar_formularios()

        self.pdf_service.escribir_campos(datos , self.data_managet.get_coord)
        self.mostrar_pagina()        

        


    @handle_error
    def popout_tranferForm(self):
        from popout import TransferForm
        
        dialog_transfer = TransferForm(self)
            
        if dialog_transfer.exec():
            scac = dialog_transfer.ui.scac_transfer.text()
            name_transfer = dialog_transfer.ui.name_linea_transfer.text()

            self.data_managet.insert_new_transfer(name_transfer,scac)
                
        self.show_message("Exito","Transfer Guardado",f"El Patio {name_transfer} se registro correctamente","info")

    @handle_error
    def popout_addres_form(self):
        from popout import AdressForm
        dialog_adress = AdressForm(self)

        if dialog_adress.exec():
            nombre_patio = dialog_adress.ui.name_yard.text()
            calle = dialog_adress.ui.input_calle.text()
            estado = dialog_adress.ui.input_municipio.text()
             
            
            self.data_managet.insert_new_address(nombre_patio,calle,estado)
        self.show_message("Exito","Patio Guardado",f"El Patio {nombre_patio} se registro correctamente","info")

    def cambio_plantilla(self ):
        
        
        
                        
        self._tipo_solicitud  = self.ui.cmbox_formato.currentText()
        
        wdget = dict(self.inputs_extra.items())
        if "caja_dueno" in wdget :
            if not self._tipo_solicitud.lower() == "gtr solicitud retiro":
                wdget["caja_dueno"].setEnabled(False)
            else:
                wdget["caja_dueno"].setEnabled(True)            
            
        
        try:
            pdf_route = self.data_managet.obtener_ruta_solicitud(self._tipo_solicitud)
            self.total_paginas = self.pdf_service.cargar_documento(pdf_route)
            self.page_actual = 0
            self.mostrar_pagina()
            
        except Exception as e:
            print(f"Error al cambiar de plantilla: \t {e}")

        
    def mostrar_pagina(self):
        

        pix = self.pdf_service.obtener_pixmap(self.page_actual)
        
        if pix:
            img = QImage(pix.samples,pix.width , pix.height,pix.stride , QImage.Format_RGB888)
            
            self.pdf_item.setPixmap(QPixmap.fromImage(img))
            self.ui.lbl_page_counter.setText(f"Pagina {self.page_actual +1} / {self.total_paginas} ")
            self.ui.display_pdf.fitInView(self.pdf_item , Qt.KeepAspectRatio)



            
    def restablecer_order_tab(self):
        self._tipo_solicitud = self.ui.cmbox_formato.currentText()
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
            self._tipo_unidad = self.ui.cmbox_tipo_unidad.currentText()
            if self._tipo_unidad :
                config_unidad = self.data_managet.request_input_type_unit(tipo_unidad=self._tipo_unidad)

                self.inputs_extra = self.form_manager.generar_formulario(config_unidad)
                self.ui.verticalLayout_7 = self.ui.frame_5.layout()
                self.restablecer_order_tab()
                

                
                
    def guardar(self):

        self.pdf_service.guardar_como(self._referencia)


    def on_pdf_click(self, x_pix, y_pix):
        if not self.pdf_service.doc : return


        pixmap_rect = self.pdf_item.pixmap().rect()
        img_w = pixmap_rect.width()
        img_h = pixmap_rect.height()
        
        coords = self.pdf_service.calcular_coordenadas_click(
            x_pix,
            y_pix,
            img_h,
            img_w,
            self.page_actual
        )
        if coords:
            x_mm , y_mm = coords

        print(f"--- NUEVA CALIBRACIÓN ---")
        print(f"X: {x_mm:.2f} mm, Y: {y_mm:.2f} mm")


        QApplication.clipboard().setText(f'"x": {x_mm:.2f}, "y": {y_mm:.2f}')
        self.ui.statusbar.showMessage(f"Copiado: X={x_mm:.2f}, Y={y_mm:.2f}")
        
    def show_message(self,title,header,txt,type="error"):
        """fabrica de mensajes centralizado"""
        
        msg = QMessageBox(self)
        
        config = {
            "error":(QMessageBox.Critical,"Error"),
            "warning":(QMessageBox.Warning,"Advertencia"),
            "info":(QMessageBox.Information,"Informacion")
                       
        }
        
        icon,default_title = config.get(type,config["info"])
        
        msg.setIcon(icon)
        msg.setWindowTitle(title or default_title)
        msg.setText(header)
        msg.setInformativeText(str(txt))
        msg.exec()
        

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MiApp()
    window.show()
    sys.exit(app.exec())
