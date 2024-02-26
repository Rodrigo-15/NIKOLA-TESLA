from reportlab.lib import colors
from reportlab.lib.pagesizes import landscape, A4
from reportlab.lib import utils
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.lib.colors import HexColor
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Paragraph
from reportlab.lib.styles import getSampleStyleSheet
from rest_framework.response import Response
from django.conf import settings
from PIL import Image
import qrcode
import datetime
import time
import os


def diploma_egresado(data):    

    # Guardar el PDF en la carpeta media
    media_root = settings.MEDIA_ROOT
    pdf_folder = os.path.join(media_root)
    if not os.path.exists(pdf_folder):
        os.makedirs(pdf_folder)

    # milisecond
    milisecond = str(int(round(time.time() * 1000)))
    # Crear un objeto PDF con orientación horizontal y tamaño de página A4

    persona = data['persona']
    num_doc = data['num_doc']
    programa: str = data['programa']
    programa_id = data['programa_id']
    archivoPdf = canvas.Canvas(
        os.path.join(
            settings.MEDIA_ROOT,
            "diplomas",
            f"diploma_egregasado-{persona}-{num_doc}-{programa}-{milisecond}.pdf",
        ),
        landscape(A4),
    )

    background = os.path.join(
        settings.MEDIA_ROOT, "config", f"diploma{programa_id}.jpg"
    )

    lLeft = 48
    lRight = A4[1] - 82
    maxWidth = lRight- lLeft

    style = getSampleStyleSheet()
    style = style["Normal"]

    parrafo1 = 'El Director de la Escuela de Postgrado de la Universidad Nacional de la Amazonia Peruana otorga el presente a:'
    parrafo2 = f'Como testimonio de haber culminado satisfactoriamente sus estudios en el Programa de {programa.capitalize()}'

    firma01 = ['Dr. CARLOS HERNAN ZUMAETA VASQUEZ', 'Director de la EPG UNAP']
    firma02 = ['Dr. VICTOR ARTURO JESUS CASTILLO CANANI', 'Director de la Unidad de Postgrado de la Facultad de Ciencias Economicas y de Negocio']
    firma03 = ['Dr. JOSE RICARDO BALBUENA HERNANDEZ', 'Secretario Academico']

    fecha = datetime.datetime.now().strftime("%d/%m/%Y")
    dia = datetime.datetime.now().day
    mes_id = datetime.datetime.now().strftime("%m")
    anio = datetime.datetime.now().year
    mes_array = [
        {"nombre": "Enero"},
        {"nombre": "Febrero"},
        {"nombre": "Marzo"},
        {"nombre": "Abril"},
        {"nombre": "Mayo"},
        {"nombre": "Junio"},
        {"nombre": "Julio"},
        {"nombre": "Agosto"},
        {"nombre": "Septiembre"},
        {"nombre": "Octubre"},
        {"nombre": "Noviembre"},
        {"nombre": "Diciembre"},
    ]

    mes_name = mes_array[int(mes_id) - 1].get("nombre")

    fecha = f"Iquitos, {dia} de {mes_name} de {anio}"

    font_path = os.path.join(settings.MEDIA_ROOT, "config", "times.ttf")
    font_path1 = os.path.join(settings.MEDIA_ROOT, "config", "timesbd.ttf")
    font_path2 = os.path.join(settings.MEDIA_ROOT, "config", 'Chalisa Octavia.ttf')
    # Ajusta la ruta
    pdfmetrics.registerFont(TTFont("times", font_path))
    pdfmetrics.registerFont(TTFont("timesbd", font_path1))
    pdfmetrics.registerFont(TTFont('chalsiaoctavia', font_path2))

    # Crear un objeto PDF con orientación horizontal y tamaño de página A4
    archivoPdf.drawImage(background, 0, 0, A4[1], A4[0])

    archivoPdf.setFillColor(HexColor("#02273E"))
    archivoPdf.setFont("timesbd", 32)

    style.fontSize = 70
    style.alignment = 1
    style.leading = 60
    style.fontName = 'chalsiaoctavia'
    style.textColor = HexColor("#02273E")

    titulo = Paragraph('Diploma de Egresado', style)
    titulo.wrapOn(archivoPdf, maxWidth, 1000)
    titulo.drawOn(archivoPdf, lLeft, 430 - titulo.height + style.fontSize)

    style.fontSize = 21
    style.alignment = 0
    style.leading = 25.2
    style.fontName = 'times'
    style.textColor = "#000000"

    para01 = Paragraph(parrafo1, style)
    para01.wrapOn(archivoPdf, maxWidth, 1000)
    para01.drawOn(archivoPdf, lLeft, 340)

    style.fontSize = 32
    style.fontName = 'timesbd'
    style.alignment = 1
    style.leading = 38.4
    style.textColor = HexColor("#02273E")


    namePara = Paragraph(persona, style)
    namePara.wrap(maxWidth, 1000)
    namePara.wrapOn(archivoPdf, maxWidth, 1000)
    namePara.drawOn(archivoPdf, lLeft, 290-namePara.height + style.fontSize)

    currenty = 290-namePara.height

    style.fontSize = 21
    style.alignment = 0
    style.leading = 25.2
    style.fontName = 'times'
    style.textColor = "#000000"

    para02 = Paragraph(parrafo2, style) 
    para02.wrapOn(archivoPdf, maxWidth, 1000)
    para02.drawOn(archivoPdf, lLeft, currenty - para02.height + style.fontSize)

    currenty -= para02.height 


    archivoPdf.setFillColor(HexColor("#000000"))
    archivoPdf.setFont("times", 21)
    archivoPdf.drawString(500, currenty, f"{fecha}.".capitalize())

    style.fontName = 'times'
    style.fontSize = 9
    style.alignment = 1
    style.leading = 10.8

    firma1Nombre = Paragraph(firma01[0], style)
    firma1Nombre.wrapOn(archivoPdf, 195, 1000)
    firma1Nombre.drawOn(archivoPdf, lLeft + 11, 83 - firma1Nombre.height + style.fontSize)
    currenty = 83 - firma1Nombre.height

    firma1Cargo = Paragraph(firma01[1], style)
    firma1Cargo.wrapOn(archivoPdf, 195, 1000)
    firma1Cargo.drawOn(archivoPdf, lLeft + 11, currenty - firma1Cargo.height + style.fontSize)

    firma2Nombre = Paragraph(firma02[0], style)
    firma2Nombre.wrapOn(archivoPdf, 195, 1000)
    firma2Nombre.drawOn(archivoPdf, lLeft + 226, 83 - firma2Nombre.height + style.fontSize)
    currenty = 83 - firma2Nombre.height

    firma2Cargo = Paragraph(firma02[1], style)
    firma2Cargo.wrapOn(archivoPdf, 195, 1000)
    firma2Cargo.drawOn(archivoPdf, lLeft + 226, currenty - firma2Cargo.height + style.fontSize)

    firma3Nombre = Paragraph(firma03[0], style)
    firma3Nombre.wrapOn(archivoPdf, 195, 1000)
    firma3Nombre.drawOn(archivoPdf, lLeft + 449, 83 - firma3Nombre.height + style.fontSize)
    currenty = 83 - firma3Nombre.height

    firma3Cargo = Paragraph(firma03[1], style)
    firma3Cargo.wrapOn(archivoPdf, 195, 1000)
    firma3Cargo.drawOn(archivoPdf, lLeft + 449, currenty - firma3Cargo.height + style.fontSize)

    archivoPdf.save()

    
    
    # retornar la ruta del archivo PDF
    path_return = os.path.join(
        settings.MEDIA_URL,
        "diplomas",
        f"diploma_egregasado-{persona}-{num_doc}-{programa}-{milisecond}.pdf",
    )
    path_return = path_return.replace("\\", "/")
    return path_return
