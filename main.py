from pathlib import Path
import sys, io, json, tempfile, time, os
from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QFileDialog, QComboBox, QFormLayout, QMessageBox, QScrollArea, QTextEdit,
)
import fitz  # PyMuPDF
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QPixmap, QImage
from overlay import generar_pdf_con_overlay

APP_DIR = Path(__file__).parent
TEMPLATES_DIR = APP_DIR / "templates"
ASSETS_DIR = APP_DIR / "assets"
COORD_TXT = APP_DIR / "cord_txt"

# Asegurar que las carpetas existan
TEMPLATES_DIR.mkdir(exist_ok=True)
ASSETS_DIR.mkdir(exist_ok=True)
COORD_TXT.mkdir(exist_ok=True)

class PreviewWidget(QLabel):
    coordClicked = Signal(float, float)

    def __init__(self):
        super().__init__()
        self.setAlignment(Qt.AlignCenter)
        self.setStyleSheet("background:#f8f8f8; border:1px solid #ccc;")
        self._doc = None
        self._page_index = 0
        self._page_height_pt = None
        self._zoom = 1.2
        self._pixmap = None
        self._calibrate_mode = False

    def set_calibrate_mode(self, enabled: bool):
        self._calibrate_mode = enabled
        self.setCursor(Qt.CrossCursor if enabled else Qt.ArrowCursor)

    def set_pdf_preview(self, pdf_path, page_index=0, zoom=1.2):
        self._zoom = zoom
        self._page_index = page_index
        try:
            if self._doc: self._doc.close()
            self._doc = fitz.open(pdf_path)
            page = self._doc.load_page(page_index)
            mat = fitz.Matrix(zoom, zoom)
            pm = page.get_pixmap(matrix=mat, alpha=False)
            self._page_height_pt = page.rect.height
            img = QImage(pm.samples, pm.width, pm.height, pm.stride, QImage.Format_RGB888)
            self._pixmap = QPixmap.fromImage(img)
            self.setPixmap(self._pixmap)
        except Exception as e:
            self.setText(f"Error al renderizar: {e}")

    def mousePressEvent(self, event):
        if not self._calibrate_mode or self._pixmap is None:
            return super().mousePressEvent(event)
        pos = event.position()
        x_pt = pos.x() / self._zoom
        y_pt_top = pos.y() / self._zoom
        y_pt = self._page_height_pt - y_pt_top
        mm_x = x_pt * 25.4 / 72.0
        mm_y = y_pt * 25.4 / 72.0
        self.coordClicked.emit(mm_x, mm_y)

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Relleno de PDFs - Datos de Unidad y Solicitud")
        self.resize(1200, 850)

        # 1. Cargar Plantillas (JSONs)
        self.unidad_templates , self.solicitud_templates = self.load_templates() 
        
        # 2. Cargar Assets (PDFs reales disponibles)
        self.pdf_assets = {file.stem: str(file) for file in ASSETS_DIR.glob("*.pdf")}
        
        self.pdf_base = None
        self.last_pdf_out = None
        self.current_page = 0
        self.total_pages = 0
        self.field_widgets = {}

        root = QHBoxLayout(self)
        left = QVBoxLayout()

        # SELECTORES
        left.addWidget(QLabel("<b>Documento PDF (Solicitud):</b>"))
        self.cboTemplate = QComboBox()
        self.cboTemplate.addItems(list(self.solicitud_templates.keys()))
        left.addWidget(self.cboTemplate)

        left.addWidget(QLabel("<b>Añadir Campos de Unidad:</b>"))
        self.cbotipo_unidad = QComboBox()
        self.cbotipo_unidad.addItems(["Sin campos extra"] + list(self.unidad_templates.keys()))
        left.addWidget(self.cbotipo_unidad)

        # FORMULARIOS
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        container = QWidget()
        self.main_form_layout = QVBoxLayout(container)
        
        self.layout_base = QFormLayout()
        self.layout_unidad = QFormLayout()
        
        self.main_form_layout.addWidget(QLabel("<br>--- CAMPOS DE UNIDAD ---"))
        self.main_form_layout.addLayout(self.layout_unidad)
        
        self.main_form_layout.addWidget(QLabel("--- SOLICITUD DE RETIRO ---"))
        self.main_form_layout.addLayout(self.layout_base)
        
        self.scroll.setWidget(container)
        left.addWidget(self.scroll)

        # NAVEGACIÓN
        nav = QHBoxLayout()
        self.btnPrev = QPushButton("◀")
        self.btnNext = QPushButton("▶")
        self.lblPageStatus = QLabel("Pág: 0 / 0")
        nav.addWidget(self.btnPrev)
        nav.addWidget(self.lblPageStatus)
        nav.addWidget(self.btnNext)
        left.addLayout(nav)

        # BOTONES ACCIÓN
        self.btnPreview = QPushButton("Previsualizar PDF")
        self.btnCalibrate = QPushButton("Modo Calibrar")
        self.btnCalibrate.setCheckable(True)
        self.btnSave = QPushButton("Guardar Final")
        
        left.addWidget(self.btnPreview)
        left.addWidget(self.btnCalibrate)
        left.addWidget(self.btnSave)

        self.lblCoords = QLabel("Coords: -")
        left.addWidget(self.lblCoords)
        root.addLayout(left, 3)

        self.preview = PreviewWidget()
        scroll_pre = QScrollArea()
        scroll_pre.setWidgetResizable(True)
        scroll_pre.setWidget(self.preview)
        root.addWidget(scroll_pre, 7)

        # CONEXIONES
        self.cboTemplate.currentTextChanged.connect(self.on_base_change)
        self.cbotipo_unidad.currentTextChanged.connect(self.render_unit_fields)
        self.btnPreview.clicked.connect(self.preview_pdf)
        self.btnSave.clicked.connect(self.save_pdf)
        self.btnCalibrate.toggled.connect(self.preview.set_calibrate_mode)
        self.btnPrev.clicked.connect(lambda: self.change_page(-1))
        self.btnNext.clicked.connect(lambda: self.change_page(1))
        self.preview.coordClicked.connect(self.on_coord_clicked)

        # Carga Inicial
        if self.cboTemplate.count() > 0:
            self.on_base_change(self.cboTemplate.currentText())

    def load_templates(self, ):

        json_path = TEMPLATES_DIR / "templates.json"
        if not json_path.exists():
            return {}, {}

        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        print(f"Templates cargados: {data.get("solicitud", {})}")
        return data.get("unidad", {}), data.get("solicitud", {})
    def on_base_change(self, key):
        # Aquí sí buscamos el PDF físico
        self.pdf_base = self.pdf_assets.get(key)
        self.last_pdf_out = None
        if self.pdf_base:
            doc = fitz.open(self.pdf_base)
            self.total_pages = len(doc)
            doc.close()
            self.current_page = 0
            self.update_page_view()
        
        # Renderizar campos del documento base
        self.clear_layout(self.layout_base)
        template = self.solicitud_templates.get(key, {})
        self.render_fields_to_layout(template, self.layout_base)
        # Forzar que los campos de unidad se mantengan si hay algo seleccionado
        self.render_unit_fields(self.cbotipo_unidad.currentText())

    def render_unit_fields(self, key):
        # Aquí NO buscamos PDF, solo renderizamos los QLineEdit
        self.clear_layout(self.layout_unidad)
        if key == "Sin campos extra": return
        template = self.unidad_templates.get(key, {})
        self.render_fields_to_layout(template, self.layout_unidad)

    def render_fields_to_layout(self, template, layout):
        for field in template.get("fields", []):
            name = field["name"]
            label = field.get("label", name)
            widget = QLineEdit()
            if name == "fecha": widget.setText(time.strftime("%d/%m/%Y"))
            self.field_widgets[name] = widget
            layout.addRow(label + ":", widget)

    def clear_layout(self, layout):
        while layout.rowCount() > 0:
            layout.removeRow(0)

    def change_page(self, delta):
        new_page = self.current_page + delta
        if 0 <= new_page < self.total_pages:
            self.current_page = new_page
            self.update_page_view()

    def update_page_view(self):
        path = self.last_pdf_out if self.last_pdf_out else self.pdf_base
        if path:
            self.preview.set_pdf_preview(path, page_index=self.current_page)
            self.lblPageStatus.setText(f"Pág: {self.current_page + 1} / {self.total_pages}")

    def preview_pdf(self):
        if not self.pdf_base: return
        try:
            # UNIFICAR CAMPOS: Sumamos los campos del JSON base + los del JSON unidad
            base_key = self.cboTemplate.currentText()
            unit_key = self.cbotipo_unidad.currentText()
            
            campos_base = self.solicitud_templates.get(base_key, {}).get("fields", [])
            campos_unidad = self.unidad_templates.get(unit_key, {}).get("fields", []) if unit_key != "Sin campos extra" else []
            
            full_template = {"fields": campos_base + campos_unidad}
            data = {n: w.text() for n, w in self.field_widgets.items()}

            tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
            out_path = tmp.name
            tmp.close()

            generar_pdf_con_overlay([self.pdf_base], full_template, data, out_path)
            self.last_pdf_out = out_path
            self.update_page_view()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al generar preview: {e}")

    def save_pdf(self):
        if not self.last_pdf_out: return
        path, _ = QFileDialog.getSaveFileName(self, "Guardar", "final.pdf", "PDF (*.pdf)")
        if path:
            Path(path).write_bytes(Path(self.last_pdf_out).read_bytes())
            QMessageBox.information(self, "Éxito", "PDF guardado.")

    def on_coord_clicked(self, mm_x, mm_y):
        self.get_coord_filetxt(mm_x, mm_y)
        self.lblCoords.setText(f"X:{mm_x:.1f} Y:{mm_y:.1f}")
        # Copiar al portapapeles para facilitar edición de JSONs
        clip = {"name": "nuevo", "x": round(mm_x, 2), "y": round(mm_y, 2), "page": self.current_page}
        QApplication.clipboard().setText(json.dumps(clip, indent=4))

    def get_coord_filetxt(self, mm_x, mm_y):
        with io.open(COORD_TXT / 'coord.txt', 'a', encoding='utf-8') as f:
            f.write(f"P{self.current_page} -> x: {round(mm_x,2)}, y: {round(mm_y,2)}\n")

#def getnames_from_template_route():
#    with io.open(TEMPLATES_DIR / 'rutas.txt', 'a', encoding='utf-8') as f:
#        for filename in os.listdir(ASSETS_DIR):
#            f.write(f"{filename}\n")
#getnames_from_template_route()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())