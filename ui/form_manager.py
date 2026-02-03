from PySide6.QtCore import Qt
from PySide6.QtWidgets import QLineEdit, QComboBox, QLabel, QGridLayout, QWidget

class FormManager:
    def __init__(self, parent_window, container_frame, data_manager):
        self.window = parent_window  # Para focusNextChild y setTabOrder
        self.container = container_frame
        self.data_manager = data_manager
        self.inputs_extra = {}

    def limpiar_layout(self, layout):
        """Elimina widgets dinámicos, conservando los fijos."""
        widgets_fijos = [
            "lbl_datos_embarque", "lbl_origen", "cmbox_origen", 
            "lbl_destino", "cmbox_destino", "lbl_referencia", "input_Referencia"
        ]
        for i in reversed(range(layout.count())):
            item = layout.itemAt(i)
            if item and item.widget():
                widget = item.widget()
                if widget.objectName() not in widgets_fijos:
                    widget.deleteLater()

    def generar_formulario(self, config_unidad):
        self.inputs_extra.clear()
        layout = self.container.layout()

        # 1. Asegurar que tenemos un QGridLayout
        if not isinstance(layout, QGridLayout):
            layout = self._convertir_a_grid(layout)

        self.limpiar_layout(layout)

        # 2. Construcción de campos dinámicos
        fila_inicio = 7
        columna = 0
        offset_fila = 0

        for field in config_unidad["fields"]:
            if field["name"] in ["referencia", "origen", "destino"]:
                continue

            # Crear widget según tipo
            if field["name"] == "linea_transporte":
                widget = QComboBox()
                widget.addItems(self.data_manager.get_data_transfer)
            else:
                widget = QLineEdit()
                widget.returnPressed.connect(self.window.focusNextChild)

            widget.setObjectName(f"input_{field['name']}")
            label = QLabel(field["label"])

            # Posicionamiento
            r = fila_inicio + offset_fila
            c_label = 0 if columna == 0 else 2
            c_input = 1 if columna == 0 else 3

            layout.addWidget(label, r, c_label)
            layout.addWidget(widget, r, c_input)

            self.inputs_extra[field["name"]] = widget

            # Alternar columnas
            if columna == 0:
                columna = 1
            else:
                columna = 0
                offset_fila += 1
        
        return self.inputs_extra

    def _convertir_a_grid(self, old_layout):
        """Convierte el layout vertical original a Grid la primera vez."""
        fijos = [
            self.window.ui.lbl_datos_embarque, self.window.ui.lbl_origen, 
            self.window.ui.cmbox_origen, self.window.ui.lbl_destino, 
            self.window.ui.cmbox_destino, self.window.ui.lbl_referencia, 
            self.window.ui.input_Referencia
        ]
        
        nuevo_layout = QGridLayout()
        nuevo_layout.setSpacing(10)

        for fila, widget in enumerate(fijos):
            nuevo_layout.addWidget(widget, fila, 0, 1, 2)

        # Reemplazo oficial en la UI
        if old_layout:
            # Truco para liberar el layout viejo
            QWidget().setLayout(old_layout) 
        
        self.container.setLayout(nuevo_layout)
        return nuevo_layout
