import fitz

class PDFEditor:
    @staticmethod

    def llenar_plantilla (doc , data , coords):
        """
        doc: objeto fitz.Document
        data: diccionario con valores {'referencia': '92B...', ...}
        coords: diccionario con coordenadas {'referencia': [x, y], ...}
        """

        if not doc : return
        page = doc[0]

        for campo , texto in data.items():
            if campo in coords:
                punto = coords[campo]
                page.insert_text(punto , str(texto) , fontsize=12 , color=(0,0,0))
        return doc