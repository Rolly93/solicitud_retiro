import fitz
from pathlib import Path
from core.data_manager import DataManager
class PDFService:
    MM_TO_PTS = 2.83465

    def __init__(self):
        self.doc = None
        self.current_path = None
        
    
    def is_empty_page(self):
        return None
        
    def calcular_coordenadas_click(self,x_pix,y_pix ,img_h,img_w,n_pagina=0):
        if not self.doc: return self.is_empty_page()
            
        page = self.doc.load_page(n_pagina)
        
        pdf_w_pts = page.rect.width
        pdf_h_pts = page.rect.height
                
        x_pt = (x_pix / img_w) * pdf_w_pts
        y_pt = (y_pix / img_h) * pdf_h_pts
        
        x_mm = x_pt / self.MM_TO_PTS
        y_mm = y_pt / self.MM_TO_PTS
        
        return x_mm, y_mm

    def cargar_documento(self, ruta_pdf: str):
        """Carga un PDF y cierra el anterior si existe."""
        try:
            if hasattr(self,'doc') and self.doc: self.doc.close()
        except Exception:
            pass
        
        
        path = Path(ruta_pdf).resolve()
        
        if not path.exists():
            raise FileNotFoundError(f"No se encontró el PDF en: {ruta_pdf}")
        
        self.doc = fitz.open(str(path))
        
        return self.doc.page_count

    def obtener_pixmap(self, n_pagina: int, zoom: float = 2.0):
        """Genera una imagen de la página para la UI."""
        if not self.doc: return self.is_empty_page()
        
        page = self.doc.load_page(n_pagina)
        mat = fitz.Matrix(zoom, zoom)
        return page.get_pixmap(matrix=mat, alpha=False)

    def escribir_campos(self, campos: dict, func_coords,nombre_pdf_activo):
        """
        Inserta texto en el PDF basado en un diccionario de valores
        y una función que provea las coordenadas.
        """
        if not self.doc: return self.is_empty_page()
        
        page = self.doc.load_page(0)
        tipo_solicitud = [s for  s in campos["tipo_solicitud"] ]
        for nombre, valor in campos.items():
            if nombre == "tipo_solicitud" or not valor:
                continue
            coords = func_coords(nombre_pdf_activo.lower().replace(" ", "-"), nombre)
            
            if coords and coords[0] is None: continue
            x_mm , y_mm = coords    
            x_pts = x_mm * self.MM_TO_PTS
            y_pts = (y_mm * self.MM_TO_PTS) - 2
            page.insert_text(
                    (x_pts, y_pts), 
                    str(valor),
                    fontsize=11,
                    fontname="helv",
                    color=(0, 0, 0)
                )


    def guardar_como(self, ruta_destino: str) ->str:
        
        base =Path( "./documents")
        ruta_destino =base  / ruta_destino
        
        ruta_destino.parent.mkdir(parents=True, exist_ok=True)
        
        if self.doc:
            self.doc.save(str(ruta_destino), garbage=4, deflate=True)
        
        return str(ruta_destino)
        

    def cerrar(self):
        if self.doc: self.doc.close()
