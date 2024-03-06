import os
from backend import settings
from django.template.loader import render_to_string
from weasyprint import HTML
import time
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.lib.pagesizes import A4
from reportlab.platypus import Paragraph, Table, TableStyle
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib import colors

def tabla_dinamica(datosTabla: list, currenty, pageCounter, setF, c, fontzise, maxWidht, lLeft, lTop, lBot,columns, colWidths):
    setF(12, "Arial-Bold")
    lol = True
    thing = 0
    while lol:
        if datosTabla[0] == columns:
            pass
        else:
            datosTabla.insert(0, columns)
        if thing == 0:
            tabla = Table(datosTabla[0:], colWidths)
        else:
            tabla = Table(datosTabla[0:thing], colWidths)
        tabla.wrap(maxWidht, 1000)

        if tabla._height > currenty - lBot - fontzise - 5:
            thing -= 1
            continue
        else:
            if thing == 0:
                datosRestantes = []
            else:

                datosRestantes = datosTabla[thing:]

            tabla.setStyle(
                TableStyle([
                        ("BACKGROUND", (0, 0), (-1, 0), colors.gray),
                        ("GRID", (0, 0), (-1, -1), 1, colors.black),
                        ("VALIGN", (0, 0),(-1, -1),"MIDDLE",),  # Align all cells' content to the top
                        ("LINEABOVE",(0, 0),(-1, 0),1,(0, 0, 0)),  # Add a line above the header row
                        ("LINEBELOW",(0, 0),(-1, 0),1,(0, 0, 0),),  # Add a line below the header row}
                        ("WORDWRAP",(0, 0),(-1, -1),),  # Enable word wrap for all cells
                        ]))

            tabla.wrapOn(c, maxWidht, 1000)
            tabla.drawOn(c, lLeft, currenty - tabla._height)
            currenty = lTop

            setF(8)
            c.drawCentredString(A4[0] / 2, lBot, str(pageCounter))
            pageCounter += 1
            c.showPage()

            if len(datosRestantes) != 0:
                lol = tabla_dinamica(datosRestantes, currenty, pageCounter, setF, c, fontzise, maxWidht, lLeft, lTop, lBot,columns, colWidths)
            elif len(datosRestantes) == 0:
                lol = False
    return lol


def get_process_tracking_sheet(data) -> str:
    try:
        #
        trackins = []

        for thing in data["trackins"]:
            thing = dict(thing)
            a = dict(thing)
            trackins.append(a)

        media_root = settings.MEDIA_ROOT
        pdf_folder = os.path.join(media_root, "pdf")
        if not os.path.exists(pdf_folder):
            os.makedirs(pdf_folder)
        code_number = data["procedure"]["code_number"]
        #
        # html_string = render_to_string("reports/hoja_seguimiento.html", data)
        milisecond = str(int(round(time.time() * 1000)))
        # html = HTML(string=html_string)
        pdf_file_name = os.path.join(
            pdf_folder, "hoja-seguimiento-{}-{}.pdf".format(code_number, milisecond)
        )
        if os.path.exists(pdf_file_name):
            os.remove(pdf_file_name)
        # html.write_pdf(pdf_file_name)
        #
        path_return = os.path.join(
            settings.MEDIA_URL,
            "pdf",
            f"hoja-seguimiento-{code_number}-{milisecond}.pdf",
        )

        pdfmetrics.registerFont(TTFont("Arial", "arial.ttf"))
        pdfmetrics.registerFont(TTFont("Arial-Bold", "arialbd.ttf"))
        lTop = A4[1] - cm * 1.5
        lBot = cm
        lLeft = cm * 2.5
        lRight = A4[0] - cm * 1.5
        maxWidht = lRight - lLeft
        maxHeight = lTop - lBot
        fontzise = 10
        fontname = "Arial"

        style = getSampleStyleSheet()
        style = style["Normal"]

        datosTabla = [["Fecha", "Accion", "Oficina"]]

        for thing in trackins:
            a = thing
            datosTabla.append([f'{a["date"]} {a["hour"]}', a["action"], a["area_name"]])

        c = canvas.Canvas(pdf_file_name)

        logoUnap = "media\config\logo_UNAP.png"
        logoPostgrado = "media\config\postgrado.png"

        fechaHora = data["procedure"]["created_at"]
        tipoTramite = data["procedure"]["procedure_type_description"]
        asunto = data["procedure"]["subject"]

        observacion = data["procedure"]["description"]

        for i in range(len(datosTabla)):
            if i > 0:
                datosTabla[i][0] = Paragraph(datosTabla[i][0], style)
                datosTabla[i][1] = Paragraph(datosTabla[i][1], style)
                datosTabla[i][2] = Paragraph(datosTabla[i][2], style)

        def setF(size, name="Arial"):
            fontzise = size
            fontname = name
            c.setFont(psfontname=fontname, size=fontzise)
            style.fontzise = fontzise

        # -----encabezado-----#
        c.drawImage(logoUnap, lLeft, lTop - 37.5, 75, 37.5)
        c.drawImage(logoPostgrado, lRight - 37.5, lTop - 37.5, 42, 45)

        fontname = "Arial-Bold"
        c.setFont(psfontname=fontname, size=fontzise - 1)
        c.drawCentredString(
            A4[0] / 2 + cm,
            lTop - fontzise - 5,
            "UNIVERSIDAD NACIONAL DE LA AMAZONIA PERUANA",
        )
        c.drawCentredString(A4[0] / 2 + cm, lTop - fontzise * 3, "ESCUELA DE POSTGRADO")

        # ----------inicio-------------#
        fontname = "Arial-Bold"
        c.setFont(psfontname=fontname, size=fontzise + 3)
        c.drawCentredString(
            A4[0] / 2,
            lTop - 60,
            f"TRAMITE N° {data['procedure']['code_number']}-EPG-UNAP",
        )

        currenty = lTop - 100

        fontname = "Arial"
        c.setFont(psfontname=fontname, size=fontzise)

        c.drawString(lLeft, currenty, "TIPO TRAMITE:")
        currenty -= 30
        c.drawString(lLeft, currenty, "ASUNTO:")
        currenty -= 30
        c.drawString(lLeft, currenty, "FECHA:")
        currenty -= 30
        c.drawString(lLeft, currenty, "OBSERVACION:")
        currenty = lTop - 100

        c.drawString(lLeft + 100, currenty, tipoTramite)
        currenty -= 30
        c.drawString(lLeft + 100, currenty, asunto)
        currenty -= 30
        c.drawString(lLeft + 100, currenty, fechaHora)
        currenty -= 30

        observacionPara = Paragraph(observacion, style)
        observacionPara.wrapOn(c, maxWidht - 100, 1000)
        observacionPara.drawOn(
            c, lLeft + 100, currenty - observacionPara.height + fontzise
        )
        c.drawString(lLeft, currenty, "OBSERVACION:")
        currenty -= 30

        c.line(lLeft, currenty, lRight, currenty)

        currenty -= 30

        # --------------area tabla-----------------#

        setF(12, "Arial-Bold")
        c.drawCentredString(A4[0] / 2, currenty, "SEGUIMIENTO DEL TRAMITE")

        currenty -= 30

        pageCounter = 1

        def tabla_dinamica(datosTabla: list, currenty, pageCounter):
            setF(12, "Arial-Bold")
            lol = True
            thing = 0
            while lol:
                if datosTabla[0] == ["Fecha", "Accion", "Oficina"]:
                    pass
                else:
                    datosTabla.insert(0, ["Fecha", "Accion", "Oficina"])
                if thing == 0:
                    tabla = Table(datosTabla[0:], colWidths=[80, 300, 80])
                else:
                    tabla = Table(datosTabla[0:thing], colWidths=[80, 300, 80])
                tabla.wrap(maxWidht, 1000)

                if tabla._height > currenty - lBot - fontzise - 5:
                    thing -= 1
                    continue
                else:
                    if thing == 0:
                        datosRestantes = []
                    else:

                        datosRestantes = datosTabla[thing:]

                    tabla.setStyle(
                        TableStyle([
                                ("BACKGROUND", (0, 0), (-1, 0), colors.gray),
                                ("GRID", (0, 0), (-1, -1), 1, colors.black),
                                ("VALIGN", (0, 0),(-1, -1),"MIDDLE",),  # Align all cells' content to the top
                                ("LINEABOVE",(0, 0),(-1, 0),1,(0, 0, 0)),  # Add a line above the header row
                                ("LINEBELOW",(0, 0),(-1, 0),1,(0, 0, 0),),  # Add a line below the header row}
                                ("WORDWRAP",(0, 0),(-1, -1),),  # Enable word wrap for all cells
                                ]))

                    tabla.wrapOn(c, maxWidht, 1000)
                    tabla.drawOn(c, lLeft, currenty - tabla._height)
                    currenty = lTop

                    setF(8)
                    c.drawCentredString(A4[0] / 2, lBot, str(pageCounter))
                    pageCounter += 1
                    c.showPage()

                    if len(datosRestantes) != 0:
                        lol = tabla_dinamica(datosRestantes, currenty, pageCounter)
                    elif len(datosRestantes) == 0:
                        lol = False
            return lol

        tabla_dinamica(datosTabla, currenty, pageCounter)

        c.save()

        path_return = path_return.replace("\\", "/")
        return path_return
    except Exception as e:
        print(e)
        return None


def get_charge_procedure(data) -> str:
    try:
        #
        media_root = settings.MEDIA_ROOT
        pdf_folder = os.path.join(media_root, "pdf")
        if not os.path.exists(pdf_folder):
            os.makedirs(pdf_folder)
        area = data["area"]["nombre"].replace(" ", "_")
        milisecond = str(int(round(time.time() * 1000)))
        pdf_file_name = os.path.join(
            pdf_folder,
            "hoja_de_cargo-{}-{}.pdf".format(area, milisecond),
        )
        if os.path.exists(pdf_file_name):
            os.remove(pdf_file_name)

        # -----generar pdf-----#
        c = canvas.Canvas(pdf_file_name, A4)
        # ----variables autogeneradas---------#

        pdfmetrics.registerFont(TTFont("Arial", "arial.ttf"))
        pdfmetrics.registerFont(TTFont("Arial-Bold", "arialbd.ttf"))
        limiteArriba = A4[1] - cm * 1.5
        limiteAbajo = cm
        limiteIzquierda = cm * 2.5
        limiteDerecha = A4[0] - cm * 1.5
        maxWidht = limiteDerecha - limiteIzquierda
        maxHeight = limiteArriba - limiteAbajo
        fontzise = 10
        fontname = "Arial"

        style = getSampleStyleSheet()
        style = style["Normal"]

        tablestyle = tablestyle([('GRID', (0, 0), (-1, -1), 1, colors.black)])

        columnasTabla = ["Expediente N°", "Asunto", "Area", "Fecha"]

        # ----funciones---------#
        def setF(size, name="Arial"):
            fontzise = size
            fontname = name  # simplemente nos ayuda a cambiar las fuentes de todo de forma mas rapido
            c.setFont(psfontname=fontname, size=fontzise)
            style.fontzise = fontzise

        # ---------variables o datos adquiridos----------#
        logoUnap = "media\config\logo_UNAP.jpg"
        logoPostgrado = "media\config\postgrado.png"

        areaUsuaria = data["area"]["nombre"].upper()
        usuario = f"{data['usuario']['nombres']}  {data['usuario']['apellido_paterno']}  {data['usuario']['apellido_materno']}".upper()
        fecha = data["fecha"]
        hora = data["hora"]
        consolidado = data["procedure_count"]

        tramites = []
        i = 0
        for value in data["procedure"]:
            fechaaa, horaaa = value["created_at"].split(" ", 1)
            tramites.insert(
                i,
                [
                    value["code_number"],
                    value["subject"].upper(),
                    value["to_area"]["nombre"].upper(),
                    fechaaa,
                ],
            )

        # ------------------------------construccion del documento------------------------------#
        # -----cabezal-----#
        c.drawImage(logoUnap, limiteIzquierda, limiteArriba - 37.5, 75, 37.5)
        c.drawImage(logoPostgrado, limiteDerecha - 40, limiteArriba - 40, 40, 40)
        # c.line(limiteDerecha, limiteArriba, limiteDerecha, limiteAbajo)

        c.setFont(psfontname=fontname, size=fontzise)

        c.drawCentredString(
            (limiteDerecha + limiteIzquierda) / 2,
            limiteArriba - fontzise - 5,
            "UNIVERSIDAD NACIONAL DE LA AMAZONIA PERUANA",
        )
        c.drawCentredString(
            (limiteDerecha + limiteIzquierda) / 2,
            limiteArriba - fontzise * 3,
            "ESCUELA DE POSTGRADO",
        )

        fontname = "Arial-Bold"
        c.setFont(psfontname=fontname, size=fontzise + 3)

        c.drawCentredString(
            (limiteDerecha + limiteIzquierda) / 2,
            limiteArriba - 60,
            "HOJA DE CARGO N°      -MP-EPG-UNAP",
        )

        fontname = "Arial"
        c.setFont(psfontname=fontname, size=fontzise)
        # ----------datos de Usuario-----------#
        setF(10, "Arial-Bold")

        currentY = limiteArriba - 120

        areaParrafoizquierda = limiteIzquierda + 120
        areaParrafoDerecha = limiteDerecha - 140
        paragraphwidth = areaParrafoDerecha - areaParrafoizquierda

        c.drawString(limiteIzquierda, currentY, "AREA USUARIA")
        c.drawString(limiteIzquierda + 100, currentY, ":")

        areaUsuariaParagraph = Paragraph(areaUsuaria, style)
        parWidth, parHeight = areaUsuariaParagraph.wrap(paragraphwidth, 1000)
        areaUsuariaParagraph.wrapOn(c, paragraphwidth, 1000)
        areaUsuariaParagraph.drawOn(
            c, areaParrafoizquierda, currentY - parHeight + fontzise
        )

        c.drawString(limiteDerecha - 120, currentY, "FECHA")
        c.drawString(limiteDerecha - 70, currentY, ":")

        setF(10)

        dateWidht = c.stringWidth(fecha, fontname, fontzise)
        c.drawString(limiteDerecha - dateWidht * 1.3, currentY, fecha)

        currentY -= parHeight + fontzise

        setF(10, "Arial-Bold")

        c.drawString(limiteIzquierda, currentY, "USUARIO")
        c.drawString(limiteIzquierda + 100, currentY, ":")

        usuarioParagraph = Paragraph(usuario, style)
        parWidth, parHeight = usuarioParagraph.wrap(paragraphwidth, 1000)
        usuarioParagraph.wrapOn(c, paragraphwidth, 1000)
        usuarioParagraph.drawOn(
            c, areaParrafoizquierda, currentY - parHeight + fontzise
        )
        setF(10, "Arial-Bold")

        c.drawString(limiteDerecha - 120, currentY, "HORA")
        c.drawString(limiteDerecha - 70, currentY, ":")
        setF(10)

        c.drawString(limiteDerecha - dateWidht * 1.3, currentY, hora)

        currentY -= parHeight + fontzise
        setF(10, "Arial-Bold")

        c.drawString(limiteIzquierda, currentY, "CONSOLIDADO")
        c.drawString(limiteIzquierda + 100, currentY, ":")

        setF(10)

        c.drawString(areaParrafoizquierda, currentY, str(consolidado))

        currentY -= 20

        c.line(limiteIzquierda, currentY, limiteDerecha, currentY)

        # -------------tabla-----------------#
        currentY -= 20
        setF(14)

        c.drawCentredString(A4[0] / 2, currentY, "TRAMITES")

        currentY -= 20

        def tabla_dinamica(datosTabla: list, currenty, pageCounter):
            setF(12, "Arial-Bold")
            lol = True
            thing = 0
            while lol:
                if datosTabla[0] == ["Expediente N°", "Asunto", "Area", "Fecha"]:
                    pass
                else:
                    datosTabla.insert(0, ["Expediente N°", "Asunto", "Area", "Fecha"])
                if thing == 0:
                    tabla = Table(datosTabla[0:], [maxWidht * 0.25,maxWidht * 0.25,maxWidht * 0.25,maxWidht * 0.25])
                else:
                    tabla = Table(datosTabla[0:thing], [maxWidht * 0.25,maxWidht * 0.25,maxWidht * 0.25,maxWidht * 0.25])
                tabla.wrap(maxWidht, 1000)

                if tabla._height > currenty - limiteAbajo - fontzise - 5:
                    thing -= 1
                    continue
                else:
                    if thing == 0:
                        datosRestantes = []
                    else:

                        datosRestantes = datosTabla[thing:]

                    tabla.wrapOn(c, maxWidht, 1000)
                    tabla.drawOn(c, limiteIzquierda, currenty - tabla._height)
                    currenty = limiteArriba

                    setF(8)
                    c.drawCentredString(A4[0] / 2, limiteAbajo, str(pageCounter))
                    pageCounter += 1
                    c.showPage()

                    if len(datosRestantes) != 0:
                        lol = tabla_dinamica(datosRestantes, currenty, pageCounter)
                    elif len(datosRestantes) == 0:
                        lol = False
            return lol

        for value in tramites:
            for i in range(len(value)):
                value[i] = Paragraph(value[i], style)   

        tabla_dinamica(tramites, currentY, 1)

        if currentY < 170:
            c.showPage()
            currentY = 250
        else:
            c.setFont(psfontname="Arial-Bold", size=fontzise + 3)
            c.drawCentredString(A4[0] / 2, currentY, "RECIBIDO CONFORME:")

        # ---------guardar archivo-------------#
        c.setTitle("hoja_de_cargo-{}-{}".format(area, milisecond))
        c.save()
        #
        path_return = os.path.join(
            settings.MEDIA_URL,
            "pdf",
            "hoja_de_cargo-{}-{}.pdf".format(area, milisecond),
        )
        path_return = path_return.replace("\\", "/")
        return path_return
    except Exception as e:
        print(e)
        return None


def get_unfinished_procedures(data) -> str:

    def setF(size, name = "Arial"):
        fontzise = size
        fontname = name             #simplemente nos ayuda a cambiar las fuentes de todo mas rapido
        c.setFont(psfontname=fontname, size= fontzise)
        style.fontSize = fontzise
        style.fontName = fontname
        style.leading = size*1.2

        # Guardar el PDF en la carpeta media
    media_root = settings.MEDIA_ROOT
    pdf_folder = os.path.join(media_root, "pdf", "reportes")
    if not os.path.exists(pdf_folder):
        os.makedirs(pdf_folder)

    # milisecond
    milisecond = str(int(round(time.time() * 1000)))

    path_file =     os.path.join(
        settings.MEDIA_ROOT,
        "pdf",
        "reportes",
        f"tramites-no-finalizados-{data['area_usuaria']}-{milisecond}.pdf",
    )
    if os.path.exists(path_file):
            os.remove(path_file)

    c = canvas.Canvas(path_file, A4)

    pdfmetrics.registerFont(TTFont('Arial', 'arial.ttf'))
    pdfmetrics.registerFont(TTFont('Arial-Bold', 'arialbd.ttf'))

    lLeft = cm
    lRight = A4[0] - cm
    lTop = A4[1] - cm
    lBottom = cm

    fontzise = 10
    fontname = "Arial"
    
    maxWidth = lRight - lLeft
    area_usuaria = data["area_usuaria"]

    procedures = data["procedures"]

    datostabla = [["Codigo", "Asunto", "Tipo", "Solicitante"],]

    for procedure in procedures:
        datostabla.append([procedure["code_number"], procedure["subject"], procedure["procedure_type_description"], procedure["person_full_name"]])

    style = getSampleStyleSheet()
    style = style["Normal"]

    logoUnap = "media\config\logo_UNAP.jpg"
    logoPostgrado = "media\config\postgrado.png"

    c.drawImage(logoUnap, lLeft, lTop - 32.5,75 , 32.5)
    c.drawImage(logoPostgrado, lRight - 40, lTop - 40, 40, 40)

    setF(10)

    c.drawCentredString(A4[0]/2, lTop - fontzise, "UNIVERSIDAD NACIONAL DE LA AMAZONIA PERUANA")
    c.drawCentredString(A4[0]/2, lTop - 2*fontzise - 10, "ESCUELA DE POSTGRADO")


    setF(13, "Arial-Bold")

    c.drawCentredString(A4[0]/2, lTop - 70, "TRAMITES SIN FINALIZAR")

    c.drawString(lLeft, lTop - 150, f"AREA USUARIA: {area_usuaria}")

    setF(8)

    for values in datostabla:
        for i in range(len(values)):
            values[i] = Paragraph(values[i], style)


    tablaTramites = Table(datostabla, colWidths=[maxWidth*0.15, maxWidth * 0.4, maxWidth *0.20, maxWidth * 0.25])


    style_table = TableStyle([
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ])

    tabla_dinamica(datostabla, lTop -200, 1, setF, c, fontzise, maxWidth, lLeft, lTop, lBottom, ["Codigo", "Asunto", "Tipo", "Solicitante"], [maxWidth*0.12, maxWidth * 0.48, maxWidth*0.2, maxWidth*0.2])

    path_return = os.path.join(
            settings.MEDIA_URL,
            "pdf",
            "reportes",
            f"tramites-no-finalizados-{data['area_usuaria']}-{milisecond}.pdf",
        )


    c.save()
    path_return = path_return.replace("\\", "/")
    return path_return