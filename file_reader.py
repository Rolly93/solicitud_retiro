import io
import time
from reportlab.pdfgen import canvas
from PyPDF2 import PdfReader, PdfWriter

def generar_pdf_overlay(file_path,file_name):
    from pathlib import Path
    writer = PdfWriter()
    pagina_global_idx = 0
    reader = PdfReader(file_path)
    for page in reader.pages:
        w = float(page.mediabox.width)
        h = float(page.mediabox.height)
    packet = io.BytesIO()
    can = canvas.Canvas(packet, pagesize=(w, h))
    can.setFont("Helvetica", 12)

    can.drawString(100 ,h-100 , "REferencia: 92b1234567")
    can.save()
    packet.seek(0)
    new_pdf = PdfReader(packet)
    page = new_pdf.pages[0]
    page.merge_page(reader.pages[0])
    writer.add_page(page)

    outh_path = f"Final_{file_name}.pdf"
    with open(outh_path, "wb") as f:
        writer.write(f)
    return outh_path


