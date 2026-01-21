import io
import time
from reportlab.pdfgen import canvas
from PyPDF2 import PdfReader, PdfWriter
def pt(val_mm):
    return val_mm * 72.0 / 25.4

def crear_capa(dimensiones, fields, datos):

    packet = io.BytesIO()
    c = canvas.Canvas(packet, pagesize=dimensiones)    
    print("datos recibidos en crear_capa:", datos)
    for f in fields:
        if not f: continue
        name = f["name"]
        import time
        txt = time.strftime("%d/%m/%Y") if (name == "fecha" and datos.get('fecha') == "") else datos.get(name, "")
        if not txt: continue
        
        x = pt(f.get("x", 0))
        y_final = pt(f.get("y", 0)) # Quitamos la resta de 'alto_puntos'
        
        font = f.get("font", "Helvetica")
        size = f.get("size", 10)
        c.setFont(font, size)
        c.drawString(x, y_final, str(txt))
            
    c.save()
    packet.seek(0)
    return PdfReader(packet)

def solicitudes_cordendas(plantilla_name):
    # Esta función debería devolver las coordenadas basadas en el nombre de la plantilla
    # Aquí se proporciona una implementación de ejemplo
    
    
    pass
#    return coordenadas.get(plantilla_name, {})
def generar_pdf_con_overlay(lista_pdf_caminos, plantilla, datos, out_path):
    from pathlib import Path
    writer = PdfWriter()
    pagina_global_idx = 0
    
    # DEBUG: Para verificar qué estructura está recibiendo
    print(f"DEBUG: Estructura de plantilla recibida: {plantilla.keys() if isinstance(plantilla, dict) else 'No es dict'}")

    for pdf_path in lista_pdf_caminos:
        reader = PdfReader(pdf_path) 
        
        for page in reader.pages:
            w = float(page.mediabox.width)
            h = float(page.mediabox.height)
            
            # Buscamos los campos dentro de la llave 'fields'
            fields_list = plantilla.get("fields", [])
            
            p_fields = [f for f in fields_list if int(f.get("page", 0)) == pagina_global_idx]
            
            print(f"Página {pagina_global_idx}: Encontrados {len(p_fields)} campos para procesar.")



            if p_fields:
                capa_pdf = crear_capa((w, h), p_fields, datos)
                page.merge_page(capa_pdf.pages[0])
            
            writer.add_page(page)
            pagina_global_idx += 1
        
    with open(out_path, "wb") as f:
        writer.write(f)

def get_coord_solicitud(plantilla_name, solicitud_tipo):
    coordenadas = solicitudes_cordendas(plantilla_name)
    return coordenadas.get(solicitud_tipo, {})