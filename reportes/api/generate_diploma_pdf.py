from rest_framework.response import Response
from rest_framework import status
from backend import settings
from academicos.models import Matricula, CursoGrupo
from admision.models import Expediente
from reportes.functions import funtion_upload_file_to_s3
from reportlab.lib.pagesizes import landscape, A4
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.lib.colors import HexColor
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Paragraph, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import cm
import qrcode
import datetime
import time
import os
import json


def api_generate_diploma_pdf(request):
    try:
        expediente_id = request.GET.get("expediente_id")
        if expediente_id == None:
            return Response(
                {"error": "No se encontro el expediente"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        expediente = Expediente.objects.filter(id=expediente_id).first()

        if expediente == None:
            return Response(
                {"error": "No se encontro el expediente"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        num_doc = expediente.persona.numero_documento
        persona = (
            expediente.persona.nombres
            + " "
            + expediente.persona.apellido_paterno
            + " "
            + expediente.persona.apellido_materno
        )
        nombres = expediente.persona.nombres
        apellidos = (
            expediente.persona.apellido_paterno
            + " "
            + expediente.persona.apellido_materno
        )
        programa = expediente.programa.nombre
        programa_id = expediente.programa
        facultad_id = expediente.programa.facultad.id

        data_matricula = Matricula.objects.filter(expediente=expediente_id)

        curso_grupo_ids = list(data_matricula.values_list("curso_grupo", flat=True))

        data_curso = CursoGrupo.objects.filter(id__in=curso_grupo_ids)

        docentes = list(set([curso.docente.full_name() for curso in data_curso]))
        cursos = [grupocurso.curso.nombre for grupocurso in data_curso]
        creditos = [grupocurso.curso.creditos for grupocurso in data_curso]
        notas = [matricula.promedio_final for matricula in data_matricula]

        curso_nota = []

        for i in range(len(cursos)):
            curso_nota.append([cursos[i], notas[i], creditos[i]])

        if expediente.programa.tipo.id == 3:
            data = {
                "num_doc": num_doc,
                "persona": persona,
                "nombres": nombres,
                "apellidos": apellidos,
                "programa": programa,
                "programa_id": programa_id,
                "fecha_inicio": expediente.periodo.fecha_inicio,
                "fecha_final": expediente.periodo.fecha_fin,
                "docentes": docentes,
                "cursos": curso_nota,
                "codigo_diploma": expediente.codigo_diploma,
                "fecha_diploma": expediente.fecha_diploma,
                "horas_academicas": expediente.programa.horas_academicas,
                "resolucion": expediente.res_diploma,
                "resolucion_directoral": expediente.res_dirc_ingreso,
                "fecha_inicio": expediente.fecha_inicio,
                "fecha_fin": expediente.fecha_fin,
            }
            path_return = diploma_diplomado(data)
        else:
            data = {
                "num_doc": num_doc,
                "persona": persona,
                "nombres": nombres,
                "apellidos": apellidos,
                "programa": programa,
                "programa_id": programa_id,
                "facultad_id": facultad_id,
            }
            path_return = diploma_egresado(data)
        return Response({"path": path_return})

    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


def diploma_egresado(data):
    try:
        # milisecond
        #
        # Crear un objeto PDF con orientación horizontal y tamaño de página A4
        milisecond = str(int(round(time.time() * 1000)))
        persona = data["persona"]
        num_doc = data["num_doc"]
        programa: str = data["programa"]
        programa_id = data["programa_id"]
        facultad_id = data["facultad_id"]

        folder_name = "pdf/diplomas/"

        pdf_file_name = f"diploma_egregasado-{persona}-{num_doc}-{programa}-{milisecond}.pdf"
        # -----generar pdf-----#
        if settings.DEBUG:
            pdf_folder = os.path.join(settings.MEDIA_ROOT, folder_name)
            if not os.path.exists(pdf_folder):
                os.makedirs(pdf_folder)
            archivoPdf = canvas.Canvas(
                os.path.join(pdf_folder, f"{pdf_file_name}"), landscape(A4),
            )
        else:
            archivoPdf = canvas.Canvas(pdf_file_name, landscape(A4))
        
        background = settings.MEDIA_URL + "config/diploma.png"

        lLeft = 48
        lRight = A4[1] - 82
        maxWidth = lRight - lLeft

        style = getSampleStyleSheet()
        style = style["Normal"]

        parrafo1 = "El Director de la Escuela de Postgrado de la Universidad Nacional de la Amazonia Peruana otorga el presente a:"
        parrafo2 = f"Como testimonio de haber culminado satisfactoriamente sus estudios en el Programa de {programa.title()}."


        s3 = settings.CREATE_STORAGE
        bucket_name = settings.AWS_STORAGE_BUCKET_NAME

        response = s3.get_object(Bucket=bucket_name, Key="config/autoridades.json")
        autoridades = json.loads(response["Body"].read().decode("utf-8"))
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

        font_path = settings.MEDIA_URL + "config/times.ttf"
        font_path1 = settings.MEDIA_URL + "config/timesbd.ttf"
        font_path2 = settings.MEDIA_URL + f"config/Chalisa%20Octavia.ttf"
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

        path_return = funtion_upload_file_to_s3(pdf_file_name, folder_name)
        return path_return
    except Exception as e:
        path_return = str(e)
        return path_return


def diploma_diplomado(data):
    try:
       
        # milisecond
        milisecond = str(int(round(time.time() * 1000)))
        # Crear un objeto PDF con orientación horizontal y tamaño de página A4
        num_doc = data["num_doc"]
        programa: str = data["programa"]
        horas_academicas = data["horas_academicas"]
        resolucion = data["resolucion"]
        resolucion_directoral = data["resolucion_directoral"]
        diplomado = programa
        fondo1 = settings.MEDIA_URL + "config/diplomado01.png"
        fondo2 = settings.MEDIA_URL + "config/diplomado02.png"
        #fondo1 =os.path.join(settings.MEDIA_ROOT, f"config/diplomado01.png")
        #fondo2 = os.path.join(settings.MEDIA_ROOT, f"config/diplomado02.png")
        fecha_diploma = data["fecha_diploma"]
        fecha_inicio = data["fecha_inicio"]
        fecha_fin = data["fecha_fin"]
        day = fecha_diploma.day
        month = fecha_diploma.month
        year = fecha_diploma.year
        # feha de inicio
        day_inicio = fecha_inicio.day
        month_inicio = fecha_inicio.month
        year_inicio = fecha_inicio.year
        # fecha de fin
        day_fin = fecha_fin.day
        month_fin = fecha_fin.month
        year_fin = fecha_fin.year
        arrayMeses = [
            "Enero",
            "Febrero",
            "Marzo",
            "Abril",
            "Mayo",
            "Junio",
            "Julio",
            "Agosto",
            "Septiembre",
            "Octubre",
            "Noviembre",
            "Diciembre",
        ]
        month = arrayMeses[month - 1]
        month_inicio = arrayMeses[month_inicio - 1]
        month_fin = arrayMeses[month_fin - 1]
        
        folder_name = "pdf/diplomas/"

        pdf_file_name =  f"diplomado-{num_doc}-{milisecond}.pdf"
        # -----generar pdf-----#
        if settings.DEBUG:
            pdf_folder = os.path.join(settings.MEDIA_ROOT, folder_name)
            if not os.path.exists(pdf_folder):
                os.makedirs(pdf_folder)
            c = canvas.Canvas(
                os.path.join(pdf_folder, f"{pdf_file_name}"), landscape(A4),
            )
        else:
            c = canvas.Canvas(pdf_file_name, landscape(A4))


        def setF(size, name="Arial"):
            fontzise = size
            fontname = (
                name  # simplemente nos ayuda a cambiar las fuentes de todo mas rapido
            )
            c.setFont(psfontname=fontname, size=fontzise)
            style.fontSize = fontzise
            style.fontName = fontname
            style.leading = size

        font_path = settings.MEDIA_URL + "config/arial.ttf"
        font_path1 = settings.MEDIA_URL + "config/arialbd.ttf"
        font_path2 = settings.MEDIA_URL + f"config/Chalisa%20Octavia.ttf"
        # Ajusta la ruta
        pdfmetrics.registerFont(TTFont("Arial", font_path))
        pdfmetrics.registerFont(TTFont("Arial-Bold", font_path1))
        pdfmetrics.registerFont(TTFont("Chalisa", font_path2))
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

        egresado = data["persona"]

        roman_numbers = {
            "1": "I",
            "2": "II",
            "3": "III",
            "4": "IV",
            "5": "V",
            "6": "VI",
            "7": "VII",
            "8": "VIII",
        }
        codigo = data["codigo_diploma"]
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(codigo)
        qr.make(fit=True)

        # Create the QR code image
        qr_image = qr.make_image(fill_color="black", back_color="white")

        # Specify the path to save the QR code image
        qr_path = f"media/qrcodes/codigo-{num_doc}.png"

        # Create the directory if it doesn't exist
        directory = os.path.dirname(qr_path)
        if not os.path.exists(directory):
            os.makedirs(directory)

        # Save the QR code image to the specified path
        qr_image.save(qr_path)

        texto1 = "El Director de la Escuela de Postgrado de la Universidad Nacional de la Amazonia Peruana tiene el honor de otorgar el presente a:"
        texto2 = "Por haber culminado satisfactoriamente el Diplomado especializado en:"
        texto3 = f"Evento realizado del {day_inicio} de {month_inicio} al {day_fin} de {month_fin} de {year_inicio}, con una duración de {horas_academicas} horas académicas, el diplomado se impartió de manera presencial y contó con la aprobación oficial según la Resolución Directoral N° {resolucion_directoral}."
        texto4 = f"Resolución Directoral de Diploma N° {resolucion}."
        texto5 = f"Iquitos, {day} de {month} de {year}."


        s3 = settings.CREATE_STORAGE
        bucket_name = settings.AWS_STORAGE_BUCKET_NAME

        response = s3.get_object(Bucket=bucket_name, Key="config/autoridades.json")
        autoridades = json.loads(response["Body"].read().decode("utf-8"))
        # cargar la firma verificando si es director y esta activo
        director = ["", ""]
        secretario = ["", ""]

        
        for item in autoridades["director"]:
            if item["is_active"]:
                director = [item["nombre"], item["cargo"]]
            break

        for item in autoridades["secretario"]:
            if item["is_active"]:
                secretario = [item["nombre"], item["cargo"]]
            break

      

        modulos = data["cursos"]

        creditosTotales = 0
        sumaDeNotas = 0

        for curso in modulos:
            creditosTotales += curso[2]
            sumaDeNotas += curso[1] * curso[2]
        nota = sumaDeNotas / creditosTotales

        nota = round(nota, 2)

        # ------------------pagina 1--------------------#
        c.drawImage(fondo1, 0, 0, A4[1], A4[0])

        currenty = lTop - 180

        setF(18, "Arial-Bold")

        style.alignment = 0

        parrafo1 = Paragraph(texto1, style)
        parrafo1.wrap(maxWidht - 100, 1000)
        parrafo1.wrapOn(c, maxWidht - 100, 1000)
        parrafo1.drawOn(c, lLeft + 50, currenty - parrafo1.height)

        setF(30, "Arial")

        currenty -= parrafo1.height + fontzise + 18 + 30

        setF(60, "Chalisa")

        c.drawCentredString(A4[1] / 2, currenty + 5, egresado.title())

        setF(16)

        currenty -= fontzise + 20
        style.alignment = 1
        parrafo1 = Paragraph(texto2, style)
        parrafo1.wrap(maxWidht - 100, 1000)
        parrafo1.wrapOn(c, maxWidht - 100, 1000)
        parrafo1.drawOn(c, lLeft + 50, currenty - parrafo1.height + fontzise)

        currenty -= parrafo1.height + 5

        setF(22, "Arial-Bold")

        parrafo1 = Paragraph(diplomado, style)
        parrafo1.wrap(maxWidht - 100, 1000)
        parrafo1.wrapOn(c, maxWidht - 100, 1000)
        parrafo1.drawOn(c, lLeft + 50, currenty - parrafo1.height + fontzise)

        currenty -= parrafo1.height + 10

        setF(16)
        style.alignment = 1
        parrafo1 = Paragraph(texto3, style)
        parrafo1.wrap(maxWidht - 100, 1000)
        parrafo1.wrapOn(c, maxWidht - 100, 1000)
        parrafo1.drawOn(c, lLeft + 50, currenty - parrafo1.height + fontzise)
        currenty -= parrafo1.height + 5

        setF(12)
        style.alignment = 2
        parrafo1 = Paragraph(texto5, style)
        parrafo1.wrap(maxWidht - 100, 1000)
        parrafo1.wrapOn(c, maxWidht - 100, 1000)
        parrafo1.drawOn(c, lLeft + 50, currenty - parrafo1.height + fontzise)
        currenty -= parrafo1.height + 10

        xd = lBot

        lBot -= 15
        setF(10)
        c.drawCentredString(lLeft + 135, lBot + 2, director[0])
        setF(9)
        c.drawCentredString(lLeft + 135, lBot - 10, director[1])

        setF(10)
        c.drawCentredString(lRight - 140, lBot + 2, secretario[0])
        setF(9)
        c.drawCentredString(lRight - 140, lBot - 10, secretario[1])

        lBot = xd

        c.showPage()

        # -------------------pagina 2-------------------------#
        c.drawImage(fondo2, 0, 0, A4[1], A4[0])

        setF(12)
        currenty = lTop - 120
        style.alignment = 0

        avHeigh = 170
        totalHeight = 0

        style.alignment = 0
        l = 1

        for value in modulos:
            value: list
            value.insert(0, str(l))
            l += 1

        modulos.insert(0, ["N°", "MODULO", "NOTA", "CREDITOS"])
        modulos.insert(0, ["MODULOS CURSADOS"])
        for value in modulos:
            for i in range(len(value)):
                if i == 1:
                    style.fontName = "Arial-Bold"
                    value[i] = Paragraph(str(value[i]), style)

        maxWidth = 600
        tablaCursos = Table(
            modulos,
            [
                maxWidth * 0.05,
                maxWidth * 0.67,
                maxWidth * 0.08,
                maxWidth * 0.125,
            ],
        )

        tableStyle = TableStyle(
            [
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                ("FONTSIZE", (0, 0), (-1, -1), 12),
                ("FONTNAME", (0, 0), (-1, -1), "Arial-Bold"),
                ("SPAN", (0, 0), (-1, 0)),
            ]
        )

        tablaCursos.setStyle(tableStyle)

        tablaCursos.wrapOn(c, maxWidth, 1000)
        tablaCursos.drawOn(c, 143, currenty - tablaCursos._height)

        currenty -= tablaCursos._height + 20

        setF(12, "Arial-Bold")

        c.drawString(510, currenty - 15, f"Total: {horas_academicas} horas académicas")

        setF(20, "Arial-Bold")

        c.drawString(lRight - 575, lTop - 357, "PROMEDIO GENERAL")

        c.drawString(lRight - 245, lTop - 357, f"{nota}")

        setF(12, "Arial")
        style.alignment = 1
        parrafo1 = Paragraph(texto4, style)
        parrafo1.wrap(maxWidht - 100, 1000)
        parrafo1.wrapOn(c, maxWidht - 100, 1000)
        parrafo1.drawOn(c, lLeft + 50, lTop - 430 + fontzise)

        setF(9, "Arial-Bold")

        c.drawImage(qr_path, (A4[1] / 2) - 20, lBot + 5, 40, 40)
        c.drawCentredString(A4[1] / 2, lBot, f"CODIGO: {codigo}")

        c.save()

        path_return = funtion_upload_file_to_s3(pdf_file_name, folder_name)
        return path_return
    except Exception as e:
        path_return = str(e)
        return path_return
