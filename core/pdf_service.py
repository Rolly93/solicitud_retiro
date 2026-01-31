import fitz
from pathlib import Path

class PDFService:
    MM_TO_PTS = 2.83465

    def __init__(self):
        self.doc = None
        self.current_path = None

    def cargar_documento(self, ruta_pdf: str):
        """Carga un PDF y cierra el anterior si existe."""
        if self.doc:
            self.doc.close()
        path = Path(ruta_pdf).resolve()
        
        if not path.exists():
            raise FileNotFoundError(f"No se encontró el PDF en: {ruta_pdf}")
        
        self.doc = fitz.open(str(path))
        return self.doc.page_count

    def obtener_pixmap(self, n_pagina: int, zoom: float = 2.0):
        """Genera una imagen de la página para la UI."""
        if not self.doc: return None
        
        page = self.doc.load_page(n_pagina)
        mat = fitz.Matrix(zoom, zoom)
        return page.get_pixmap(matrix=mat, alpha=False)

    def escribir_campos(self, campos: dict, func_coords):
        """
        Inserta texto en el PDF basado en un diccionario de valores
        y una función que provea las coordenadas.
        """
        if not self.doc: return
        
        page = self.doc.load_page(0)
        tipo_solicitud = campos.get("tipo_solicitud", "").lower().replace(" ", "-")

        for nombre, valor in campos.items():
            if nombre == "tipo_solicitud" or not valor:
                continue
            coords = func_coords(tipo_solicitud, nombre)
            
            if coords and coords[0] is None: continue
            
            x_mm , y_mm = coords    
            x_pts = x_mm * self.MM_TO_PTS
            y_pts = (y_mm * self.MM_TO_PTS) - 2
            print("valor " , valor)
            
            
            page.insert_text(
                    (x_pts, y_pts), 
                    str(valor),
                    fontsize=15,
                    fontname="helv",
                    color=(0, 0, 0)
                )

    def guardar_como(self, ruta_destino: str):
        if self.doc:
            self.doc.save(ruta_destino, garbage=4, deflate=True)

    def cerrar(self):
        if self.doc:
            self.doc.close()