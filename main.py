import sys
import os
from pathlib import Path

from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QGraphicsScene,
    QMessageBox,
    QGraphicsView,
    QSizePolicy
)
from PySide6.QtGui import QPixmap, QImage, QPainter
from PySide6.QtCore import Qt, QTimer

from ui.main_ui import Ui_MainWindow
from data import cargar_todo, cargar_patios


class MiApp(QMainWindow):
    def __init__(self):
        super().__init__()

        # ----------------------------
        # Estado interno
        # ----------------------------
        self._aduana = ""
        self._tipo_solicitud = ""
        self._tipo_unidad = ""
        self._origen = ""
        self._destino = ""
        self._referencia = ""
        # ----------------------------
        # Cargar rutas de PDF
        # ----------------------------
        rutas_brutas = self.dic_file_route()

        self.lista_solicitudes = sorted([
            item["name"].replace("-", " ").title()
            for item in rutas_brutas
        ])

        self.format_data = {
            item["name"].replace("-", " ").title(): item["route_file"]
            for item in rutas_brutas
        }

        # ----------------------------
        # UI
        # ----------------------------
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)







        # ----------------------------
        # Configuración del visor PDF
        # ----------------------------
        self.escena_pdf = QGraphicsScene(self)
        self.ui.display_pdf.setScene(self.escena_pdf)

        self.ui.display_pdf.setAlignment(Qt.AlignCenter)
        self.ui.display_pdf.setRenderHint(QPainter.Antialiasing)
        self.ui.display_pdf.setRenderHint(QPainter.SmoothPixmapTransform)
        self.ui.display_pdf.setDragMode(QGraphicsView.ScrollHandDrag)
        self.ui.display_pdf.setTransformationAnchor(
            QGraphicsView.ViewportAnchor.AnchorUnderMouse
        )

        # IMPORTANTE: evitar AdjustToContents
        self.ui.display_pdf.setSizeAdjustPolicy(
            QGraphicsView.SizeAdjustPolicy.AdjustIgnored
        )

        # ----------------------------
        # Combos
        # ----------------------------
        self.ui.cmbox_formato.addItems(self.lista_solicitudes)
        self.ui.cmbox_tipo_unidad.addItems(["Trailer", "Placa"])
        self.ui.cobox_aduana.addItems(["240", "800"])

        patios = self.cargar_patios()
        self.ui.cmbox_origen.addItems(patios)
        self.ui.cmbox_destino.addItems(patios)

        # ----------------------------
        # Señales
        # ----------------------------
        self.ui.cmbox_formato.currentTextChanged.connect(self.cambio_plantilla)
        self.ui.btn_previsuzalizar.clicked.connect(self.previsualizar_pdf)
        self.ui.tbox_agregar_direccion.clicked.connect(self.popout_addres_form)
        self.ui.tbox_agregar_linea_transfer.clicked.connect(self.popout_tranferForm)

        # ----------------------------
        # Cargar primer PDF
        # ----------------------------
        if self.lista_solicitudes:
            self.cambio_plantilla(self.ui.cmbox_formato.currentText())

    # =====================================================
    # Datos
    # =====================================================

    def dic_file_route(self):
        ASSETS_DIR = Path(__file__).parent / "assets"
        return [
            {
                "name": nombre,
                "route_file": str(ASSETS_DIR / ruta.get("filename", ""))
            }
            for nombre, ruta in cargar_todo().get("solicitud", {}).items()
        ]

    def cargar_patios(self):
        return [patio.get("name") for patio in cargar_patios()]

    # =====================================================
    # PDF
    # =====================================================

    def cambio_plantilla(self, format_name: str):
        ruta_pdf = self.format_data.get(format_name)
        if ruta_pdf:
            self.mostrar_pdf(ruta_pdf)

    def mostrar_pdf(self, ruta_pdf):
        pass
    # =====================================================
    # Acciones
    # =====================================================

    def previsualizar_pdf(self):
        referencia = self.ui.input_Referencia.text()
        if not self._isvalid_reference(referencia):
            return

        self._aduana = self.ui.cobox_aduana.currentText()
        self._tipo_solicitud = self.ui.cmbox_formato.currentText()
        self._tipo_unidad = self.ui.cmbox_tipo_unidad.currentText()
        self._origen = self.ui.cmbox_origen.currentText()
        self._destino = self.ui.cmbox_destino.currentText()
        self._referencia = referencia

        print("Datos listos para procesar:", self._referencia)

    def _isvalid_reference(self, referencia):
        if len(referencia) == 10 and (
            referencia.startswith("92B") or referencia.startswith("82B")
        ):
            return True

        msg = QMessageBox(self)
        msg.setIcon(QMessageBox.Critical)
        msg.setWindowTitle("Error de Referencia")
        msg.setText("La referencia ingresada es inválida.")
        msg.setInformativeText(
            "Debe tener 10 caracteres y comenzar con '92B' o '82B'."
        )
        msg.exec()
        return False

    # =====================================================
    # Popouts
    # =====================================================

    def popout_tranferForm(self):
        from popout import TransferForm
        dialog = TransferForm(self)
        if dialog.exec():
            self._scac = dialog.ui.scac_transfer.text()
            self._name_transfer = dialog.ui.name_linea_transfer.text()

    def popout_addres_form(self):
        from popout import AdressForm
        dialog = AdressForm(self)
        if dialog.exec():
            self._nombre_patio = dialog.ui.name_yard.text()
            self._direccion_patio = dialog.ui.address_yard.text()

    # =====================================================
    # Resize
    # =====================================================

    def resizeEvent(self, event):
        if not self.escena_pdf.items():
            return

        self.ui.display_pdf.fitInView(
            self.escena_pdf.sceneRect(),
            Qt.KeepAspectRatio
        )
        super().resizeEvent(event)


# =========================================================
# Main
# =========================================================

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MiApp()
    window.show()
    sys.exit(app.exec())
