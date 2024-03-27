from reportlab.lib import colors
from reportlab.lib.pagesizes import landscape, A4
from reportlab.lib import utils
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.lib.colors import HexColor
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.utils import ImageReader
from reportlab.platypus import Paragraph, Table, TableStyle, Frame
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import cm
from rest_framework.response import Response
from django.conf import settings
from PIL import Image
from io import BytesIO
import qrcode
import datetime
import time
import os
from xlsxwriter import Workbook


def diploma_egresado(data):
    try:
        # Guardar el PDF en la carpeta media
        media_root = settings.MEDIA_ROOT
        pdf_folder = os.path.join(media_root)
        if not os.path.exists(pdf_folder):
            os.makedirs(pdf_folder)

        # milisecond
        milisecond = str(int(round(time.time() * 1000)))
        # Crear un objeto PDF con orientación horizontal y tamaño de página A4

        persona = data["persona"]
        num_doc = data["num_doc"]
        programa: str = data["programa"]
        programa_id = data["programa_id"]
        facultad_id = data["facultad_id"]
        archivoPdf = canvas.Canvas(
            os.path.join(
                settings.MEDIA_ROOT,
                "diplomas",
                f"diploma_egregasado-{persona}-{num_doc}-{programa}-{milisecond}.pdf",
            ),
            landscape(A4),
        )

        background = os.path.join(settings.MEDIA_ROOT, "config", f"diploma.png")

        lLeft = 48
        lRight = A4[1] - 82
        maxWidth = lRight - lLeft

        style = getSampleStyleSheet()
        style = style["Normal"]

        parrafo1 = "El Director de la Escuela de Postgrado de la Universidad Nacional de la Amazonia Peruana otorga el presente a:"
        parrafo2 = f"Como testimonio de haber culminado satisfactoriamente sus estudios en el Programa de {programa.title()}."

        import json

        ruta_archivo = f"media/config/autoridades.json"
        with open(ruta_archivo, "r") as archivo:
            autoridades = json.load(archivo)

        # cargar la firma verificando si es director y esta activo
        director = ["", ""]
        secretario = ["", ""]
        unidad = ["", ""]

        for item in autoridades["director"]:
            if item["is_active"]:
                director = [item["nombre"], item["cargo"]]
            break

        for item in autoridades["secretario"]:
            if item["is_active"]:
                secretario = [item["nombre"], item["cargo"]]
            break

        for item in autoridades["unidad"]:
            if item["is_active"] and item["facultad"] == facultad_id:
                unidad = [item["nombre"], item["cargo"]]
                break

        # cerrar el archivo
        archivo.close()

        print(unidad)

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
        font_path2 = os.path.join(settings.MEDIA_ROOT, "config", "Chalisa Octavia.ttf")
        # Ajusta la ruta
        pdfmetrics.registerFont(TTFont("times", font_path))
        pdfmetrics.registerFont(TTFont("timesbd", font_path1))
        pdfmetrics.registerFont(TTFont("chalsiaoctavia", font_path2))

        # Crear un objeto PDF con orientación horizontal y tamaño de página A4
        archivoPdf.drawImage(background, 0, 0, A4[1], A4[0])

        archivoPdf.setFillColor(HexColor("#02273E"))
        archivoPdf.setFont("timesbd", 38)

        style.fontSize = 70
        style.alignment = 1
        style.leading = 60
        style.fontName = "chalsiaoctavia"
        style.textColor = HexColor("#02273E")

        titulo = Paragraph("Diploma de Egresado", style)
        titulo.wrapOn(archivoPdf, maxWidth, 1000)
        titulo.drawOn(archivoPdf, lLeft, 430 - titulo.height + style.fontSize)

        style.fontSize = 21
        style.alignment = 0
        style.leading = 25.2
        style.fontName = "times"
        style.textColor = "#000000"
        style.alignment = 4  # Justificar

        para01 = Paragraph(parrafo1, style)
        para01.wrapOn(archivoPdf, maxWidth, 1000)
        para01.drawOn(archivoPdf, lLeft, 340)

        style.fontSize = 32
        style.fontName = "timesbd"
        style.alignment = 1
        style.leading = 38.4
        style.textColor = HexColor("#02273E")

        namePara = Paragraph(persona, style)
        namePara.wrap(maxWidth, 1000)
        namePara.wrapOn(archivoPdf, maxWidth, 1000)
        namePara.drawOn(archivoPdf, lLeft, 290 - namePara.height + style.fontSize)

        currenty = 290 - namePara.height

        style.fontSize = 21
        style.alignment = 0
        style.leading = 25.2
        style.fontName = "times"
        style.textColor = "#000000"
        style.alignment = 4  # Justificar

        para02 = Paragraph(parrafo2, style)
        para02.wrapOn(archivoPdf, maxWidth, 1000)
        para02.drawOn(archivoPdf, lLeft, currenty - para02.height + style.fontSize)

        currenty -= para02.height

        archivoPdf.setFillColor(HexColor("#000000"))
        archivoPdf.setFont("times", 21)
        archivoPdf.drawString(500, 150, f"{fecha}.".capitalize())

        style.fontName = "times"
        style.fontSize = 9
        style.alignment = 1
        style.leading = 10.8

        firma1Nombre = Paragraph(director[0], style)
        firma1Nombre.wrapOn(archivoPdf, 195, 1000)
        firma1Nombre.drawOn(
            archivoPdf, lLeft + 11, 83 - firma1Nombre.height + style.fontSize
        )
        currenty = 83 - firma1Nombre.height

        firma1Cargo = Paragraph(director[1], style)
        firma1Cargo.wrapOn(archivoPdf, 195, 1000)
        firma1Cargo.drawOn(
            archivoPdf, lLeft + 11, currenty - firma1Cargo.height + style.fontSize
        )

        firma2Nombre = Paragraph(unidad[0], style)
        firma2Nombre.wrapOn(archivoPdf, 195, 1000)
        firma2Nombre.drawOn(
            archivoPdf, lLeft + 226, 83 - firma2Nombre.height + style.fontSize
        )
        currenty = 83 - firma2Nombre.height

        firma2Cargo = Paragraph(unidad[1], style)
        firma2Cargo.wrapOn(archivoPdf, 195, 1000)
        firma2Cargo.drawOn(
            archivoPdf, lLeft + 226, currenty - firma2Cargo.height + style.fontSize
        )

        firma3Nombre = Paragraph(secretario[0], style)
        firma3Nombre.wrapOn(archivoPdf, 195, 1000)
        firma3Nombre.drawOn(
            archivoPdf, lLeft + 449, 83 - firma3Nombre.height + style.fontSize
        )
        currenty = 83 - firma3Nombre.height

        firma3Cargo = Paragraph(secretario[1], style)
        firma3Cargo.wrapOn(archivoPdf, 195, 1000)
        firma3Cargo.drawOn(
            archivoPdf, lLeft + 449, currenty - firma3Cargo.height + style.fontSize
        )

        archivoPdf.save()

        # retornar la ruta del archivo PDF
        path_return = os.path.join(
            settings.MEDIA_URL,
            "diplomas",
            f"diploma_egregasado-{persona}-{num_doc}-{programa}-{milisecond}.pdf",
        )
        path_return = path_return.replace("\\", "/")
        return path_return
    except Exception as e:
        print(e)
        return None


def diploma_diplomado(data):
    try:
        # Guardar el PDF en la carpeta media
        media_root = settings.MEDIA_ROOT
        pdf_folder = os.path.join(media_root)
        if not os.path.exists(pdf_folder):
            os.makedirs(pdf_folder)

        # milisecond
        milisecond = str(int(round(time.time() * 1000)))
        # Crear un objeto PDF con orientación horizontal y tamaño de página A4

        persona = data["persona"]
        num_doc = data["num_doc"]
        programa: str = data["programa"]
        programa_id = data["programa_id"]
        c = canvas.Canvas(
            os.path.join(
                settings.MEDIA_ROOT,
                "diplomas",
                f"diploma_egregasado-{persona}-{num_doc}-{programa}-{milisecond}.pdf",
            ),
            landscape(A4),
        )

        def setF(size, name="Arial"):
            fontzise = size
            fontname = (
                name  # simplemente nos ayuda a cambiar las fuentes de todo mas rapido
            )
            c.setFont(psfontname=fontname, size=fontzise)
            style.fontSize = fontzise
            style.fontName = fontname
            style.leading = size

        pdfmetrics.registerFont(TTFont("Arial", "arial.ttf"))
        pdfmetrics.registerFont(TTFont("Arial-Bold", "arialbd.ttf"))
        lTop = A4[0] - cm * 2
        lBot = cm * 2
        lLeft = cm * 2
        lRight = A4[1] - cm * 2
        maxWidht = lRight - lLeft
        maxHeight = lTop - lBot
        fontzise = 10
        fontname = "Arial"

        style = getSampleStyleSheet()
        style = style["Normal"]

        # ------variables que se utilizan dentro del documento------#
        logoUnap = "media\config\logo_UNAP.png"
        logoPostgrado = "media\config\postgrado.png"

        # Generate QR code
        codigo = "CY3ILIXD"
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(codigo)
        qr.make(fit=True)

        # Create an image from the QR code instance
        QRImage = qr.make_image(fill_color="black", back_color="white")

        img_buffer = BytesIO()
        QRImage.save(img_buffer)
        img_buffer.seek(0)

        img_buffer = ImageReader(img_buffer)

        egresado = data["persona"]
        docentes = data["docentes"]

        diplomado = data["programa"]
        duracion = 260
        fechaInicio = data["fecha_inicio"]
        fechaFinal = data["fecha_final"]

        año1, mes1, dia1 = str(fechaInicio).split("-")
        año2, mes2, dia2 = str(fechaFinal).split("-")

        mes_array = {
            "01": "Enero",
            "02": "Febrero",
            "03": "Marzo",
            "04": "Abril",
            "05": "Mayo",
            "06": "Junio",
            "07": "Julio",
            "08": "Agosto",
            "09": "Septiembre",
            "10": "Octubre",
            "11": "Noviembre",
            "12": "Diciembre",
        }

        mes1 = mes_array[mes1]
        mes2 = mes_array[mes2]

        dia1 = fechaInicio.day
        dia2 = fechaFinal.day

        fechaInicio = f"{dia1} de {mes1} del {año1}"
        fechaFinal = f"{dia2} de {mes2} del {año2}"

        fechaEmisionDelDiploma = datetime.date.today()

        texto1 = "La Universidad Nacional de la Amazonia Peruana y La escuela de Postgrado tienen el honor de entregar el presente:"
        texto2 = "Por haber culminado satisfactoriamente el:"
        texto3 = f"Con fecha de inicio el {fechaInicio} y finalizado el {fechaFinal}, con una duracion de {duracion} horas academicas."

        datosFirma = [
            ["Mauricio Lovera Torres", "Director", ""],
            ["Ernesto Chavez Tuaname", "Secretario Academico", ""],
        ]

        modulos = data["cursos"]
        creditosTotales = 0
        sumaDeNotas = 0

        for curso in modulos:
            creditosTotales += curso[2]
            sumaDeNotas += curso[1] * curso[2]
        nota = sumaDeNotas / creditosTotales

        # ------------------pagina 1--------------------#

        c.drawImage(logoUnap, lLeft, lTop - 70, 140, 70)
        c.drawImage(logoPostgrado, lRight - 70, lTop - 70, 70, 70)

        currenty = lTop - 80

        setF(18, "Arial-Bold")

        style.alignment = 1

        parrafo1 = Paragraph(texto1, style)
        parrafo1.wrap(maxWidht - 100, 1000)
        parrafo1.wrapOn(c, maxWidht - 100, 1000)
        parrafo1.drawOn(c, lLeft + 50, currenty - parrafo1.height)

        setF(40, "Arial-Bold")

        currenty -= parrafo1.height + fontzise + 18 + 30

        c.drawCentredString(A4[1] / 2, currenty, "DIPLOMA")

        currenty -= fontzise + 40

        setF(20)

        c.drawString(150, currenty, "a:")
        c.line(170, currenty, 700, currenty)

        c.drawCentredString(A4[1] / 2, currenty + 5, egresado)

        setF(17)

        currenty -= fontzise + 10

        parrafo1 = Paragraph(texto2, style)
        parrafo1.wrap(maxWidht - 100, 1000)
        parrafo1.wrapOn(c, maxWidht - 100, 1000)
        parrafo1.drawOn(c, lLeft + 50, currenty - parrafo1.height + fontzise)

        currenty -= parrafo1.height

        setF(25, "Arial-Bold")

        parrafo1 = Paragraph(diplomado, style)
        parrafo1.wrap(maxWidht - 100, 1000)
        parrafo1.wrapOn(c, maxWidht - 100, 1000)
        parrafo1.drawOn(c, lLeft + 50, currenty - parrafo1.height + fontzise)

        currenty -= parrafo1.height + 10

        setF(18)

        parrafo1 = Paragraph(texto3, style)
        parrafo1.wrap(maxWidht - 100, 1000)
        parrafo1.wrapOn(c, maxWidht - 100, 1000)
        parrafo1.drawOn(c, lLeft + 50, currenty - parrafo1.height + fontzise)

        xd = lBot

        lBot += 30

        c.line(lLeft, lBot + 20, lLeft + 250, lBot + 20)
        setF(16)
        c.drawCentredString(lLeft + 125, lBot + 2, datosFirma[0][0])
        setF(10)
        c.drawCentredString(lLeft + 125, lBot - 16, datosFirma[0][1])
        c.drawCentredString(lLeft + 125, lBot - 34, datosFirma[0][2])

        c.line(lRight - 250, lBot + 20, lRight, lBot + 20)
        setF(16)
        c.drawCentredString(lRight - 125, lBot + 2, datosFirma[1][0])
        setF(10)
        c.drawCentredString(lRight - 125, lBot - 16, datosFirma[1][1])
        c.drawCentredString(lRight - 125, lBot - 34, datosFirma[1][2])

        lBot = xd

        c.drawImage(img_buffer, 385, lBot + fontzise + 10, 75, 75)
        c.drawCentredString(A4[1] / 2, lBot, f"Codigo: {codigo}")

        c.showPage()

        # -------------------pagina 2-------------------------#

        tablaModulosLista1 = [["", "MODULO", "NOTA MODULO"]]
        tablaModulosLista = []

        setF(12)

        for value in tablaModulosLista1:
            for i in range(len(value)):
                value[i] = Paragraph(value[i], style)
            tablaModulosLista.append([value[0], value[1], value[2]])

        for i in range(len(modulos)):
            parrafo1 = Paragraph(modulos[i][0], style)
            parrafo2 = Paragraph(str(modulos[i][1]), style)

            tablaModulosLista.append([f"{i+1}", parrafo1, parrafo2])

        tablaModulos = Table(
            tablaModulosLista, [0.05 * maxWidht, 0.75 * maxWidht, 0.2 * maxWidht]
        )

        currenty = lTop

        setF(20, "Arial-Bold")

        c.drawCentredString(A4[1] / 2, currenty - fontzise, "CONTENIDO TEMATICO")

        currenty -= fontzise + 20

        setF(20)

        light_red = colors.HexColor("#A90000")
        tableStyle = TableStyle(
            [
                ("GRID", (0, 0), (-1, -1), 1, light_red),  # Light red grid
                ("ALIGN", (0, 0), (-1, 0), "CENTER"),  # Center-align the first row
                ("ALIGN", (-1, 0), (-1, -1), "CENTER"),  # Center-align the last column
                (
                    "ALIGN",
                    (1, 1),
                    (1, -1),
                    "LEFT",
                ),  # Left-align the second column from the second to the last row
                ("FONTSIZE", (0, 0), (-1, -1), fontzise),
            ]
        )

        tablaModulos = Table(
            tablaModulosLista, [0.05 * maxWidht, 0.75 * maxWidht, 0.2 * maxWidht]
        )
        tablaModulos.setStyle(tableStyle)

        tablaModulos.wrapOn(c, maxWidht, 1000)
        tablaModulos.drawOn(c, lLeft, currenty - tablaModulos._height)

        currenty -= tablaModulos._height + 30

        setF(20)

        c.drawString(lLeft, currenty - fontzise, "Docentes: ")
        a = currenty
        currenty -= 2 * fontzise + 20

        setF(13)

        for docente in docentes:
            c.drawString(lLeft, currenty, f"- {docente}")
            currenty -= fontzise * 2

        currenty = a

        setF(13, "Arial-Bold")

        frame = Frame(lRight - 100, currenty - fontzise - 10, 70, 30, showBoundary=1)

        frame.addFromList([], c)

        c.drawString(lRight - 150, currenty - fontzise, "Nota:")
        c.drawString(lRight - 75, currenty - fontzise, f"{nota}")

        c.drawImage(logoUnap, lLeft, lBot + fontzise + 10, 140, 70)
        c.drawImage(logoPostgrado, lRight - 70, lBot + fontzise + 10, 70, 80)
        c.drawImage(img_buffer, 385, lBot + fontzise + 10, 75, 75)
        c.drawCentredString(A4[1] / 2, lBot, f"Codigo: {codigo}")

        c.save()

        # retornar la ruta del archivo PDF
        path_return = os.path.join(
            settings.MEDIA_URL,
            "diplomas",
            f"diploma_egregasado-{persona}-{num_doc}-{programa}-{milisecond}.pdf",
        )
        path_return = path_return.replace("\\", "/")
        return path_return
    except Exception as e:
        print(e)
        return


def reporte_matricula(data):
    lLeft = cm * 2
    lRight = A4[0] - cm * 2
    lTop = A4[1] - cm
    lBottom = cm
    maxWidth = lRight - lLeft

    fontzise = 10
    fontname = "Arial"

    def setF(size, name="Arial"):
        fontzise = size
        fontname = (
            name  # simplemente nos ayuda a cambiar las fuentes de todo mas rapido
        )
        c.setFont(psfontname=fontname, size=fontzise)
        style.fontSize = fontzise
        style.fontName = fontname
        style.leading = size * 1.2

    style = getSampleStyleSheet()
    style1 = style["Normal"]
    style = style["Normal"]

    style1.alignment = 0

    # -----generar qr-------#
    codigo = "https://apisunat.com/65baf74a815b810015b21374/documents/new"
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(codigo)
    qr.make(fit=True)

    QRImage = qr.make_image(fill_color="black", back_color="white")

    img_buffer = BytesIO()
    QRImage.save(img_buffer)
    img_buffer.seek(0)

    img_buffer = ImageReader(img_buffer)
    # --------------------------#

    pdfmetrics.registerFont(TTFont("Arial", "arial.ttf"))
    pdfmetrics.registerFont(TTFont("Arial-Bold", "arialbd.ttf"))

    facultad = "FACULTAD DE EDUCACION"
    programa = "DIPLOMADO EN DOCENCIA UNIVERSITARIA"
    nombreAlumno = "ALEGRIA REODRIGUEZ JHONATAN WALDEMA FABRICIO"
    numExp = "4903"
    planEstudios = "xd"
    correo = "None"
    dniAlumno = "71232701"
    periodo = "2023-II"
    promocion = "2023-II"

    cursos = [
        ["N°", "CICLO", "CÓDIGO", "ASIGNATURA", "INTENTO", "SECCION", "CREDITOS"],
        [
            "1",
            "1",
            "DPC-01",
            "INTRODUCCION A LAS COMPETENCIAS DOCENTES",
            "01",
            "A",
            "4.00",
        ],
        [
            "2",
            "1",
            "DPC-02",
            "INNOVACION, DIVERSISDAD Y EQUIDAD EN LA EDUCACION",
            "01",
            "A",
            "4.00",
        ],
        [
            "3",
            "1",
            "DPC-03",
            "COMPETENCIAS DIGITALES EN DOCENCIA UNIVERSITARIA",
            "01",
            "A",
            "4.00",
        ],
        [
            "4",
            "1",
            "DPC-04",
            "METODOLOGIAS ACTIVAS Y TECNICAS DIDACTICAS",
            "01",
            "A",
            "4.00",
        ],
        [
            "5",
            "1",
            "DPC-05",
            "HERRAMIENTAS Y RECURSOS DOCENTES PARA LA ENSEÑANZA Y EL APRENDIZAJE",
            "01",
            "A",
            "4.00",
        ],
        [
            "6",
            "1",
            "DPC-06",
            "METODOLOGIA DE LA INVESTIGACION EDUCATIVA",
            "01",
            "A",
            "4.00",
        ],
    ]

    logoUnap = "media\config\logo_UNAP.jpg"
    logoPostgrado = "media\config\postgrado.png"

    # --------------------PAGINA 1-------------------------#

    c = canvas.Canvas("reporte_matricula.pdf")

    c.drawImage(logoUnap, lLeft, lTop - 37.5, 75, 37.5)
    c.drawImage(logoPostgrado, lRight - 40, lTop - 40, 40, 40)

    setF(10, "Arial-Bold")

    c.drawCentredString(
        A4[0] / 2, lTop - fontzise - 40, "UNIVERSISDAD NACIONAL DE LA AMAZONIA PERUANA"
    )
    c.drawCentredString(A4[0] / 2, lTop - 2 * fontzise - 45, "ESCUELA DE POSTGRADO")
    c.drawCentredString(
        A4[0] / 2, lTop - 3 * fontzise - 50, "OFICINA DE ASUNTOS ACADEMICOS"
    )

    currenty = lTop - 3 * fontzise - 50

    setF(15, "Arial-Bold")

    c.drawCentredString(A4[0] / 2, currenty - 40, "BOLETA DE MATRICULA")

    currenty -= 41
    setF(7, "Arial-Bold")
    leftRightColumn = lLeft + 260

    c.drawString(lLeft, currenty - 30, "FACULTAD:")
    c.drawString(leftRightColumn, currenty - 30, "PROGRAMA:")
    c.drawString(lLeft, currenty - 50, "APELLIDOS Y NOMBRES:")
    c.drawString(lLeft, currenty - 70, "PLAN DE ESTUDIOS:")
    c.drawString(lLeft, currenty - 90, "PERIODO:")

    setF(7)

    c.drawString(lLeft + 45, currenty - 30, facultad)
    programPara = Paragraph(programa, style)
    programPara.wrapOn(c, lRight - (leftRightColumn + 45), 1000)
    programPara.drawOn(
        c, leftRightColumn + 45, currenty - 32.5 - programPara.height + fontzise
    )
    nombrePara = Paragraph(nombreAlumno, style)
    nombrePara.wrapOn(c, leftRightColumn - (lLeft + 90), 1000)
    nombrePara.drawOn(c, lLeft + 90, currenty - 52.5 - nombrePara.height + fontzise)
    c.drawString(lLeft + 75, currenty - 70, planEstudios)
    c.drawString(lLeft + 37, currenty - 90, periodo)

    leftRightColumn = lLeft + 260

    setF(7, "Arial-Bold")

    c.drawString(leftRightColumn, currenty - 50, "NUM. EXP.:")
    c.drawString(leftRightColumn, currenty - 70, "DOCUENTO DE IDENTIDAD: ")

    setF(7)

    c.drawString(leftRightColumn + 40, currenty - 50, numExp)
    c.drawString(leftRightColumn + 100, currenty - 70, dniAlumno)

    currenty -= 120

    # -----------------------tabla-------------------------#

    style.alignment = 0

    for value in cursos:
        for i in range(len(value)):
            if i == 3 and "ASIGNATURA" not in value:
                value[i] = Paragraph(value[i], style)

    tablaCursos = Table(
        cursos,
        [
            maxWidth * 0.05,
            maxWidth * 0.1,
            maxWidth * 0.1,
            maxWidth * 0.45,
            maxWidth * 0.1,
            maxWidth * 0.1,
            maxWidth * 0.1,
        ],
    )

    tableStyle = TableStyle(
        [
            ("GRID", (0, 0), (-1, 0), 1, (0, 0, 0)),
            ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ("FONTSIZE", (0, 0), (-1, -1), fontzise),
            ("BOX", (0, 0), (-1, -1), 1, colors.black),
            ("FONTSIZE", (0, 0), (-1, -1), 7),
            ("FONTNAME", (0, 0), (-1, -1), fontname),
        ]
    )

    tablaCursos.setStyle(tableStyle)

    tablaCursos.wrapOn(c, maxWidth, 1000)
    tablaCursos.drawOn(c, lLeft, currenty - tablaCursos._height)

    # ----------area abajo de la tabla------------#

    currenty -= tablaCursos._height

    c.line(lLeft, currenty, lLeft, currenty - tablaCursos._height)
    c.line(lRight, currenty, lRight, currenty - tablaCursos._height)
    c.line(
        lLeft, currenty - tablaCursos._height, lRight, currenty - tablaCursos._height
    )

    c.line(lLeft, currenty - 20, lRight, currenty - 20)
    c.line(
        lLeft,
        currenty - tablaCursos._height + 20,
        lRight,
        currenty - tablaCursos._height + 20,
    )
    c.line(A4[0] / 2, currenty - 20, A4[0] / 2, currenty - tablaCursos._height)

    setF(7, "Arial-Bold")

    c.drawString(lLeft + 5, currenty - 13.5, "OBSERVACIONES: ")
    c.drawString(lLeft + 300, currenty - 13.5, "TOTAL DE CREDITOS MATRICULADOS")
    c.line(lLeft + 435, currenty, lLeft + 435, currenty - 20)
    c.drawString(lLeft + 450, currenty - 13.5, "24.00")

    c.drawString(
        lLeft + 5,
        currenty - tablaCursos._height + 7.5,
        "Fecha-Hora de Matricula: 09/10/2023 - 08:34",
    )
    c.drawString(
        (A4[0] / 2) + 5,
        currenty - tablaCursos._height + 7.5,
        "Fecha-Hora de Impresión: 09/10/2023 - 08:34",
    )

    c.line(
        lLeft + 70,
        currenty - tablaCursos._height + 45,
        lLeft + 170,
        currenty - tablaCursos._height + 45,
    )
    c.drawString(
        lLeft + 79, currenty - tablaCursos._height + 37, "FIRMA DEL ESTUDIANTE"
    )

    currenty -= tablaCursos._height

    c.drawImage(img_buffer, (A4[0] / 2) - 50, currenty - 110, 100, 100)

    c.save()


def reporte_excel_programas_by_promocion_xlsx(data) -> str:
    media_root = settings.MEDIA_ROOT
    pdf_folder = os.path.join(media_root, "excel", "academicos")
    if not os.path.exists(pdf_folder):
        os.makedirs(pdf_folder)

    # milisecond
    milisecond = str(int(round(time.time() * 1000)))

    programa = data["programa"]
    promocion = data["promocion"]

    path_file = os.path.join(
        settings.MEDIA_ROOT,
        "excel",
        "academicos",
        f"reporte-{programa}-{promocion}-{milisecond}.xlsx",
    )

    if os.path.exists(path_file):
        os.remove(path_file)
    cursos = data["cursos"]
    datostabla = []

    # for procedure in procedures:
    #     datostabla.append(
    #         [
    #             procedure["code_number"],
    #             procedure["subject"],
    #             procedure["procedure_type_description"],
    #             procedure["person_full_name"],
    #         ]
    #     )

    file = Workbook(path_file)
    ws = file.add_worksheet()

    ws.write_string(1, 1, f"PROGRAMA: {programa}-{promocion}")

    # ---------------tabla------------------#
    headers = datostabla[0:1][0]
    rows = datostabla[1:]

    print(headers)

    ws.add_table(
        f"A4:D{len(rows) + 4}",
        {
            "data": rows,
            "columns": [
                {"header": headers[0]},
                {"header": headers[1]},
                {"header": headers[2]},
                {"header": headers[3]},
            ],
        },
    )

    border_format = file.add_format(
        {"border": 1}
    )  # 1 is for a thin border. You can use other values for different border styles.

    rowCounter = 3
    largestAsunto = 0
    for row in datostabla:
        for i in range(len(row)):
            if i == 2:
                if len(row[i]) > largestAsunto:
                    largestAsunto = len(row[i])
        rowCounter += 1

    ws.set_column("A:A", 12.5)
    ws.set_column("B:B", largestAsunto * 2.4)

    ws.set_column("C:D", 50)

    path_return = os.path.join(
        settings.MEDIA_URL,
        "excel",
        "academicos",
        f"reporte-{programa}-{promocion}-{milisecond}.xlsx",
    )

    path_return = path_return.replace("\\", "/")
    return path_return
