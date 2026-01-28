import fitz
import os
from pathlib import Path

class PDFHandler:
    def __init__(self):
        self.doc = None
        self.current_page = 0

    def open_pdf(self, path):
        if self.doc:
            self.doc.close()
        self.doc = fitz.open(str(path))
        return self.doc.page_count
        
    def open(self,path):
        close = None
        doc = None
        try:
            doc = fitz.open(str(path))

            doc.page_count
        except(NameError):
            raise("Erro: Arcvhio no encotrado", NameError)


    def get_page_pixmap(self, page_num, zoom=2.0):
        if not self.doc: return None
        page = self.doc.load_page(page_num)
        mat = fitz.Matrix(zoom, zoom)
        return page.get_pixmap(matrix=mat, alpha=False)

    def write_text(self, data, get_coord_func, mm_to_pts_func):
        if not self.doc: return
        page = self.doc.load_page(0)
        tipo = data.get("tipo_solicitud")
        
        for name, value in data.items():
            if name == "tipo_solicitud" or not value: continue
            
            x, y = get_coord_func(tipo, name)
            if x:
                pos = (mm_to_pts_func(x), mm_to_pts_func(y))
                page.insert_text(pos, str(value), fontsize=20, fontname="helv")