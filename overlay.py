import io
import time
from reportlab.pdfgen import canvas
from PyPDF2 import PdfReader, PdfWriter
def pt(val_mm):
    return val_mm * 72.0 / 25.4

def crear_capa(dimensiones, fields, datos):
    packet = io.BytesIO()
    c = canvas.Canvas(packet, pagesize=dimensiones)
    # Ya no necesitamos alto_puntos para invertir, porque el JSON ya viene en formato PDF
    
    for f in fields:
        if not f: continue
        name = f["name"]
        
        # Lógica de fecha automática
        import time
        txt = time.strftime("%d/%m/%Y") if (name == "fecha" and datos.get('fecha') == "") else datos.get(name, "")
        if not txt: continue
        
        # COORDENADAS: Usamos el valor directo del JSON
        # Como on_coord_clicked ya hizo la resta (alto - y), aquí solo convertimos a puntos
        x = pt(f.get("x", 0))
        y_final = pt(f.get("y", 0)) # Quitamos la resta de 'alto_puntos'
        
        font = f.get("font", "Helvetica")
        size = f.get("size", 10)
        c.setFont(font, size)
        
        # Ajuste de línea base (opcional según qué tan exacto quieras el click)
        # y_final -= size 
        
        if f.get("multiline"):
            ls = f.get("line_spacing", size * 1.2)
            # Para multilínea, el PDF escribe hacia abajo, restamos el espaciado
            for i, line in enumerate(str(txt).splitlines()):
                c.drawString(x, y_final - (i * ls), line)
        else:
            c.drawString(x, y_final, str(txt))
            
    c.save()
    packet.seek(0)
    return PdfReader(packet)

def generar_pdf_con_overlay(lista_pdf_caminos, plantilla, datos, out_path):
    writer = PdfWriter()
    pagina_global_idx = 0

    # lista_pdf_caminos es ['ruta/archivo.pdf']
    for pdf_path in lista_pdf_caminos:
        # AQUÍ ESTABA EL ERROR: Asegúrate de pasar pdf_path (el string), no la lista completa
        reader = PdfReader(pdf_path) 
        
        for page in reader.pages:
            if page.get("/Rotate", 0) != 0:
                page.transfer_rotation_to_content()
                page.rotation = 0

            w = float(page.mediabox.width)
            h = float(page.mediabox.height)
            
            p_fields = [f for f in plantilla.get("fields", []) 
                        if int(f.get("page", 0)) == pagina_global_idx]
            
            if p_fields:
                capa_pdf = crear_capa((w, h), p_fields, datos)
                page.merge_page(capa_pdf.pages[0])
            
            writer.add_page(page)
            pagina_global_idx += 1
        
    with open(out_path, "wb") as f:
        writer.write(f)