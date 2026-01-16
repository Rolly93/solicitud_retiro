from pathlib import Path
import sys, io, json, tempfile
from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QFileDialog, QComboBox, QFormLayout, QMessageBox, QScrollArea, QTextEdit,
)

import time
import fitz  # PyMuPDF
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QPixmap, QImage
from overlay import generar_pdf_con_overlay

APP_DIR = Path(__file__).parent
TEMPLATES_DIR = APP_DIR / "templates"
ASSETS_DIR = APP_DIR / "assets"

# Asegurar que las carpetas existan
TEMPLATES_DIR.mkdir(exist_ok=True)
ASSETS_DIR.mkdir(exist_ok=True)

class PreviewWidget(QLabel):
    coordClicked = Signal(float, float)

    def __init__(self):
        super().__init__()
        self.setAlignment(Qt.AlignCenter)
        self.setStyleSheet("background:#f8f8f8; border:1px solid #ccc;")
        self._doc = None
        self._page_index = 0
        self._page_height_pt = None
        self._page_width_pt = None
        self._zoom = 1.2
        self._pixmap = None
        self._calibrate_mode = False
        self._current_rotation = 0

    def set_calibrate_mode(self, enabled: bool):
        self._calibrate_mode = enabled
        self.setCursor(Qt.CrossCursor if enabled else Qt.ArrowCursor)

    def set_pdf_preview(self, pdf_path, page_index=0, zoom=1.2):
        self._zoom = zoom
        self._page_index = page_index
        try:
            if self._doc:
                self._doc.close()
            
            self._doc = fitz.open(pdf_path)
            page = self._doc.load_page(page_index)
            self._current_rotation = page.rotation
            
            mat = fitz.Matrix(zoom, zoom)
            if self._current_rotation != 0:
                mat = mat.prerotate(-self._current_rotation)
                
            pm = page.get_pixmap(matrix=mat, alpha=False)
            
            if self._current_rotation in (90, 270):
                self._page_height_pt = page.rect.width
                self._page_width_pt = page.rect.height
            else:
                self._page_height_pt = page.rect.height
                self._page_width_pt = page.rect.width

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
        self.setWindowTitle("Relleno de PDFs - Sistema Unificado")
        self.resize(1200, 800)

        self.templates = self.load_templates()
        self.pdf_assets = {file.stem: str(file) for file in ASSETS_DIR.glob("*.pdf")}
        
        self.pdf_base = None
        self.last_pdf_out = None
        self.current_page = 0
        self.total_pages = 0
        self.field_widgets = {}

        root = QHBoxLayout(self)
        left = QVBoxLayout()

        self.cboTemplate = QComboBox()
        self.cboTemplate.addItems(list(self.templates.keys()))
        self.cboTemplate.currentTextChanged.connect(self.on_template_change)
        left.addWidget(QLabel("Seleccionar Plantilla:"))
        left.addWidget(self.cboTemplate)

        # Contenedor para campos dinámicos
        self.formScroll = QScrollArea()
        self.formContainer = QWidget()
        self.formLayout = QFormLayout(self.formContainer)
        self.formScroll.setWidget(self.formContainer)
        self.formScroll.setWidgetResizable(True)
        left.addWidget(self.formScroll)

        nav_layout = QHBoxLayout()
        self.btnPrev = QPushButton("◀ Anterior")
        self.btnNext = QPushButton("Siguiente ▶")
        self.lblPageStatus = QLabel("Página: 0 / 0")
        self.btnPrev.clicked.connect(lambda: self.change_page(-1))
        self.btnNext.clicked.connect(lambda: self.change_page(1))
        nav_layout.addWidget(self.btnPrev)
        nav_layout.addWidget(self.lblPageStatus)
        nav_layout.addWidget(self.btnNext)
        left.addLayout(nav_layout)

        btns = QVBoxLayout()
        self.btnPreview = QPushButton("Previsualizar / Actualizar")
        self.btnCalibrate = QPushButton("Modo Calibrar (Click para Coords)")
        self.btnCalibrate.setCheckable(True)
        self.btnSave = QPushButton("Guardar PDF Final")
        
        btns.addWidget(self.btnPreview)
        btns.addWidget(self.btnCalibrate)
        btns.addWidget(self.btnSave)
        left.addLayout(btns)

        self.lblCoords = QLabel("Coords: -")
        self.lblCoords.setStyleSheet("color: red; font-weight: bold;")
        left.addWidget(self.lblCoords)
        root.addLayout(left, 3)

        self.preview = PreviewWidget()
        scroll_preview = QScrollArea()
        scroll_preview.setWidgetResizable(True)
        scroll_preview.setWidget(self.preview)
        root.addWidget(scroll_preview, 7)

        # Conexiones
        self.btnPreview.clicked.connect(self.preview_pdf)
        self.btnSave.clicked.connect(self.save_pdf)
        self.btnCalibrate.toggled.connect(self.toggle_calibrate)
        self.preview.coordClicked.connect(self.on_coord_clicked)

        if self.cboTemplate.count() > 0:
            self.on_template_change(self.cboTemplate.currentText())

    def load_templates(self):
        tpl = {}
        if not TEMPLATES_DIR.exists(): TEMPLATES_DIR.mkdir()
        for jf in TEMPLATES_DIR.glob("*.json"):
            try:
                with open(jf, "r", encoding="utf-8") as f:
                    tpl[jf.stem] = json.load(f)
            except: pass
        return tpl

    def on_template_change(self, key):
        self.pdf_base = self.pdf_assets.get(key)
        self.last_pdf_out = None
        self.current_page = 0
        if self.pdf_base:
            doc = fitz.open(self.pdf_base)
            self.total_pages = len(doc)
            doc.close()
            self.update_page_view()
        self.render_fields(key)

    def render_fields(self, key):
        # Limpiar formulario
        while self.formLayout.rowCount() > 0:
            self.formLayout.removeRow(0)
        self.field_widgets = {}

        template = self.templates.get(key, {})
        for field in template.get("fields", []):
            name = field["name"]
            label = field.get("label", name)
            
            if field.get("name") == "fecha":
                widget = QLineEdit()
                widget.setText(time.strftime("%d/%m/%Y"))
                
            else:
                widget = QLineEdit()
                
            self.field_widgets[name] = widget
            self.formLayout.addRow(label + ":", widget)

    def change_page(self, delta):
        new_page = self.current_page + delta
        if 0 <= new_page < self.total_pages:
            self.current_page = new_page
            self.update_page_view()

    def update_page_view(self):
        path = self.last_pdf_out if self.last_pdf_out else self.pdf_base
        if path:
            self.preview.set_pdf_preview(path, page_index=self.current_page)
            self.lblPageStatus.setText(f"Página: {self.current_page + 1} / {self.total_pages}")

    def toggle_calibrate(self, enabled):
        self.preview.set_calibrate_mode(enabled)

    def collect_data(self):
        data = {}
        for name, widget in self.field_widgets.items():
            if isinstance(widget, QTextEdit):
                data[name] = widget.toPlainText()
            else:
                data[name] = widget.text()
        return data

    def preview_pdf(self):
            if not self.pdf_base: 
                QMessageBox.warning(self, "Error", "No hay un PDF base seleccionado.")
                return

            try:
                template = self.templates.get(self.cboTemplate.currentText())
                data = self.collect_data()

                # Crear ruta temporal
                tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
                out_path = tmp.name
                tmp.close()

                # DEBUG: Verifica que esto sea una lista de strings
                print(f"Procesando: {[self.pdf_base]}") 

                # Llamada a la lógica de overlay
                generar_pdf_con_overlay([self.pdf_base], template, data, out_path)

                self.last_pdf_out = out_path
                self.update_page_view()

            except Exception as e:
                # Imprime el error completo en consola para ver la línea exacta
                import traceback
                traceback.print_exc()
                QMessageBox.critical(self, "Error", f"No se pudo generar la previa: {e}")

    def save_pdf(self):
        if not self.last_pdf_out:
            QMessageBox.warning(self, "Aviso", "Primero genera una previsualización.")
            return
        
        path, _ = QFileDialog.getSaveFileName(self, "Guardar PDF", "documento_final.pdf", "PDF (*.pdf)")
        if path:
            Path(path).write_bytes(Path(self.last_pdf_out).read_bytes())
            QMessageBox.information(self, "Éxito", "PDF guardado correctamente.")

    def on_coord_clicked(self, mm_x, mm_y):
        nuevo_campo = {
            "name": "nuevo_campo",
            "label": "Etiqueta",
            "page": self.current_page,
            "x": round(mm_x, 2),
            "y": round(mm_y, 2),
            "font": "Helvetica",
            "size": 10
        }
        QApplication.clipboard().setText(json.dumps(nuevo_campo, indent=4))
        self.lblCoords.setText(f"Copiado: Pág {self.current_page+1} | X:{mm_x:.1f} Y:{mm_y:.1f}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())