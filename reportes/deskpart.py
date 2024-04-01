import os
from backend import settings
import time
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.lib.pagesizes import A4
from reportlab.platypus import Paragraph, Table, TableStyle
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.utils import ImageReader
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.lib import colors
from xlsxwriter import Workbook
from PIL import Image
from io import BytesIO
import qrcode


def tabla_dinamica(
    datosTabla: list,
    currenty,
    pageCounter,
    setF,
    c: canvas.Canvas,
    fontzise,
    maxWidht,
    lLeft,
    lTop,
    lBot,
    lRigh,
    columns,
    colWidths,
):
    addres = "Los Rosales s/n, San Juan Bautista"
    email = "postgrado@unapiquitos.edu.pe"
    phonenumber = "Telefono: (5165) 261101"
    pageDirection = "https://admision.postgradounap.edu.pe/"
    setF(12, "Arial-Bold")
    lol = True
    thing = 0
    porcentaje_sacado = False
    while lol:
        if datosTabla[0] != columns and pageCounter != 1:
            pass
        if thing == 0:
            datosTabla.insert(0, columns)
            tabla = Table(datosTabla[0:], colWidths)
        else:
            tabla = Table(datosTabla[0:thing], colWidths)
        tabla.wrap(maxWidht, 250)

        if tabla._height > currenty - lBot - fontzise - 5:
            if not porcentaje_sacado:
                a = currenty - lBot - fontzise - 5
                b = a / tabla._height
                thing = round(len(datosTabla) * b) + 1
                currenty - lBot - fontzise - 5
                porcentaje_sacado = True
                continue
            else:
                thing -= 1
                continue
        else:
            if thing == 0:
                datosRestantes = []
            else:

                datosRestantes = datosTabla[thing:]

            tabla.setStyle(
                TableStyle(
                    [
                        ("BACKGROUND", (0, 0), (-1, 0), colors.gray),
                        ("GRID", (0, 0), (-1, -1), 1, colors.black),
                        (
                            "VALIGN",
                            (0, 0),
                            (-1, -1),
                            "MIDDLE",
                        ),  # Align all cells' content to the top
                        (
                            "LINEABOVE",
                            (0, 0),
                            (-1, 0),
                            1,
                            (0, 0, 0),
                        ),  # Add a line above the header row
                        (
                            "LINEBELOW",
                            (0, 0),
                            (-1, 0),
                            1,
                            (0, 0, 0),
                        ),  # Add a line below the header row}
                        (
                            "WORDWRAP",
                            (0, 0),
                            (-1, -1),
                        ),  # Enable word wrap for all cells
                    ]
                )
            )

            tabla.wrapOn(c, maxWidht, 250)
            tabla.drawOn(c, lLeft, currenty - tabla._height)

            setF(8)
            c.drawCentredString(A4[0] / 2, lBot- fontzise, str(pageCounter))
            pageCounter += 1

            c.drawString(lLeft, lBot, addres)
            c.drawString(lLeft, lBot + fontzise, phonenumber)

            lengt1 = c.stringWidth(email, "Arial", fontzise)
            lengt2 = c.stringWidth(pageDirection, "Arial", fontzise)

            c.drawString(lRigh - lengt1, lBot, email)
            c.drawString(lRigh - lengt2, lBot + fontzise, pageDirection)



            if len(datosRestantes) != 0:
                c.showPage()
                currenty = lTop
                lol, altura, alturay = tabla_dinamica(
                    datosRestantes,
                    currenty,
                    pageCounter,
                    setF,
                    c,
                    fontzise,
                    maxWidht,
                    lLeft,
                    lTop,
                    lBot,
                    columns,
                    colWidths,
                )

                currenty -= altura

            elif len(datosRestantes) == 0:
                lol = False
                currenty -= tabla._height
    return lol, tabla._height, currenty


def get_process_tracking_sheet(data) -> str:
    try:
        #
        trackins = []

        for thing in data["trackins"]:
            thing = dict(thing)
            a = dict(thing)
            trackins.append(a)
        #
        s3_client = settings.CREATE_STORAGE
        bucket_name = settings.AWS_STORAGE_BUCKET_NAME
        folder_name = "pdf/hoja_seguimiento/"

        # Crea la carpeta en el bucket si no existe
        try:
            s3_client.head_object(Bucket=bucket_name, Key=folder_name)
        except:
            s3_client.put_object(Bucket=bucket_name, Key=folder_name)
        code_number = data["procedure"]["code_number"]
        milisecond = str(int(round(time.time() * 1000)))
        # Nombre del archivo PDF que deseas crear
        pdf_file_name = "hoja-seguimiento-{}-{}.pdf".format(code_number, milisecond)

        # Ruta completa del archivo PDF en el bucket
        pdf_file_key = folder_name + pdf_file_name

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
        usuario = data["procedure"]["user_name"]
        folios = str(data["procedure"]["number_of_sheets"])
        observacion = data["procedure"]["description"]
        date_state = data["procedure"]["state_date"]

        if date_state == 1:
            date_state = "EN PLAZO"
        elif date_state == 2:
            date_state == "POR VENCER"
        else:
            date_state == "VENCIDO"

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

        setF(fontzise, "Arial-Bold")

        c.setFont(psfontname="Arial-Bold", size=fontzise)
        c.drawString(lLeft, currenty, "CREADO POR:")
        currenty -= 30
        c.drawString(lLeft, currenty, "TIPO TRAMITE:")
        currenty -= 30
        c.drawString(lLeft, currenty, "ASUNTO:")
        currenty -= 30
        c.drawString(lLeft, currenty, "FECHA:")
        currenty -= 30
        c.drawString(lLeft, currenty, "ESTADO FECHA:")
        currenty -= 30
        c.drawString(lLeft, currenty, "N° DE FOLIOS:")
        currenty -= 30
        c.drawString(lLeft, currenty, "OBSERVACION:")
        currenty = lTop - 100

        setF(fontzise, "Arial")

        c.drawString(lLeft + 100, currenty, usuario)
        currenty -= 30
        c.drawString(lLeft + 100, currenty, tipoTramite)
        currenty -= 30
        c.drawString(lLeft + 100, currenty, asunto)
        currenty -= 30
        c.drawString(lLeft + 100, currenty, fechaHora)
        currenty -= 30
        c.drawString(lLeft + 100, currenty, date_state)
        currenty -= 30
        c.drawString(lLeft + 100, currenty, folios)
        currenty -= 30

        observacionPara = Paragraph(observacion, style)
        observacionPara.wrapOn(c, maxWidht - 100, 1000)
        observacionPara.drawOn(
            c, lLeft + 100, currenty - observacionPara.height + fontzise
        )
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
                        TableStyle(
                            [
                                ("BACKGROUND", (0, 0), (-1, 0), colors.gray),
                                ("GRID", (0, 0), (-1, -1), 1, colors.black),
                                (
                                    "VALIGN",
                                    (0, 0),
                                    (-1, -1),
                                    "MIDDLE",
                                ),  # Align all cells' content to the top
                                (
                                    "LINEABOVE",
                                    (0, 0),
                                    (-1, 0),
                                    1,
                                    (0, 0, 0),
                                ),  # Add a line above the header row
                                (
                                    "LINEBELOW",
                                    (0, 0),
                                    (-1, 0),
                                    1,
                                    (0, 0, 0),
                                ),  # Add a line below the header row}
                                (
                                    "WORDWRAP",
                                    (0, 0),
                                    (-1, -1),
                                ),  # Enable word wrap for all cells
                            ]
                        )
                    )

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
        s3_client.put_object(
            Bucket=bucket_name,
            Key=folder_name + pdf_file_name,
            Body=open(pdf_file_name, "rb"),
        )

        path_return = settings.MEDIA_URL + pdf_file_key

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


        return path_return
    except Exception as e:
        print(e)
        return None


def get_charge_procedure(data) -> str:
    try:
        #
        s3_client = settings.CREATE_STORAGE
        bucket_name = settings.AWS_STORAGE_BUCKET_NAME
        folder_name = "pdf/hoja_de_cargo/"

        # Crea la carpeta en el bucket si no existe
        try:
            s3_client.head_object(Bucket=bucket_name, Key=folder_name)
        except:
            s3_client.put_object(Bucket=bucket_name, Key=folder_name)

        area = data["area"]["nombre"].replace(" ", "_")
        charge_number = data["charge_number"]
        milisecond = str(int(round(time.time() * 1000)))

        # Nombre del archivo PDF que deseas crear
        pdf_file_name = "hoja_de_cargo-{}-{}.pdf".format(charge_number, milisecond)

        # Ruta completa del archivo PDF en el bucket
        pdf_file_key = folder_name + pdf_file_name

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

        columnasTabla = ["Expediente N°", "Asunto", "Accion", "Area", "Folios", "Fecha"]

        # ----funciones---------#
        def setF(size, name="Arial"):
            fontzise = size
            fontname = name  # simplemente nos ayuda a cambiar las fuentes de todo de forma mas rapido
            c.setFont(psfontname=fontname, size=fontzise)
            style.fontzise = fontzise

        # ---------variables o datos adquiridos----------#
        logoUnap = "media/config/logo_UNAP.png"
        logoPostgrado = "media/config/postgrado.png"

        areaUsuaria = data["area"]["nombre"].upper()
        usuario = f"{data['original_user']['nombres']}  {data['original_user']['apellido_paterno']}  {data['original_user']['apellido_materno']}".upper()
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
                    value["action"].upper(),
                    value["to_area"]["nombre"].upper(),
                    value["number_of_sheets"],
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
            f"CARGO UNICO N° {charge_number}",
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
        for value in tramites:
            for i in range(len(value)):
                if i != 4:
                    value[i] = Paragraph(value[i], style)

        lol, altura, currentY = tabla_dinamica(
            tramites,
            currentY,
            1,
            setF,
            c,
            fontzise,
            maxWidht,
            limiteIzquierda,
            limiteArriba,
            limiteAbajo,
            limiteDerecha,
            columnasTabla,
            [
                maxWidht * 0.15,
                maxWidht * 0.20,
                maxWidht * 0.24,
                maxWidht * 0.18,
                maxWidht * 0.1,
                maxWidht * 0.13,
            ],
        )

        c.setFont(psfontname="Arial-Bold", size=fontzise + 3)
        c.drawCentredString(A4[0] / 2, currentY - 50, "RECIBIDO CONFORME")

        setF(8)
        # ---------guardar archivo-------------#
        c.setTitle("hoja_de_cargo-{}-{}".format(area, milisecond))
        #

        path_return = settings.MEDIA_URL + pdf_file_key

        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(path_return)
        qr.make(fit=True)

        # Create an image from the QR code instance
        QRImage = qr.make_image(fill_color="black", back_color="white")

        img_buffer = BytesIO()
        QRImage.save(img_buffer)
        img_buffer.seek(0)

        img_buffer = ImageReader(img_buffer)

        c.drawImage(img_buffer, A4[0]/2 -35, limiteAbajo + fontzise * 3, 70,70)
        c.save()

        # Subir el archivo PDF al bucket de S3
        s3_client.put_object(
            Bucket=bucket_name,
            Key=folder_name + pdf_file_name,
            Body=open(pdf_file_name, "rb"),
        )

        path_return = settings.MEDIA_URL + pdf_file_key
        return path_return
    except Exception as e:
        print(e)
        return None


def get_procedure_data_xlsx(data) -> str:
    s3_client = settings.CREATE_STORAGE
    bucket_name = settings.AWS_STORAGE_BUCKET_NAME
    folder_name = "excel/deskpart/"

    # Crea la carpeta en el bucket si no existe
    try:
        s3_client.head_object(Bucket=bucket_name, Key=folder_name)
    except:
        s3_client.put_object(Bucket=bucket_name, Key=folder_name)
    # milisecond
    milisecond = str(int(round(time.time() * 1000)))

    area_usuaria = data["area_usuaria"]

    # Nombre del archivo PDF que deseas crear
    excel_file_name = (
        f"{data['name']}-{area_usuaria.replace(' ', '_')}-{milisecond}.xlsx"
    )

    # Ruta completa del archivo PDF en el bucket
    pdf_file_key = folder_name + excel_file_name

    procedures = data["procedures"]

    datostabla = [
        ["Codigo", "Fecha de Creacion","Asunto", "Tipo de Tramite", "Solicitante", "Estado", "Estado de Fecha", "Fecha Vencimiento"],
    ]

    for procedure in procedures:
        datostabla.append(
            [
                procedure["code_number"],
                procedure["created_at"],
                procedure["subject"],
                procedure["procedure_type_description"],
                procedure["person_full_name"],
                procedure["state"],
                procedure["state_date"],
                procedure["due_date"],
            ]
        )

    file = Workbook(excel_file_name)
    ws = file.add_worksheet()
    ws2 = file.add_worksheet()

    formato_cuadro = file.add_format({
    'border': 3,
    'align': 'center',
    'valign': 'vcenter',
})
    formato_cuadro.set_bg_color("yellow")
    format_with_font = file.add_format({'font_size': 15})

# Aplicar el formato al rango de celdas especificado (columnas B a D, filas 2 a 3)
    ws.conditional_format('B2:D3', {'type': 'no_blanks', 'format': formato_cuadro})

    ws.write_string(1, 1, f"Area Usuaria: {area_usuaria}", format_with_font)
    ws.write_string(1,2, f"Usuario: {data['usuario']}", format_with_font)
    ws.write_string(1,3, f"Fecha de creacion: {data['creacion']}", format_with_font)

    # ---------------tabla------------------#
    headers = datostabla[0:1][0]
    rows = datostabla[1:]

    rowCounter = 3
    largestName = 0

    for row in datostabla:
        for i in range(len(row)):
            if i == 4:
                if len(row[i]) > largestName:
                    largestName = len(row[i])
            if i == 6:
                if row[6] == 3:
                    row[6] = "En Plazo"
                elif row[6] == 2:
                    row[6] = "Por Vencer"
                elif row[6] == 1:
                    row[6] = "Vencido"
        rowCounter += 1

    ws.add_table(
        f"A6:H{len(rows) + 6}",
        {
            "data": rows,
            "columns": [
                {"header": headers[0]},
                {"header": headers[1]},
                {"header": headers[2]},
                {"header": headers[3]},
                {"header": headers[4]},
                {"header": headers[5]},
                {"header": headers[6]},
                {"header": headers[7]},
            ],
        },
    )

    border_format = file.add_format(
        {"border": 1}
    )  # 1 is for a thin border. You can use other values for different border styles.

    ws.set_column("A:A", 12.5)
    ws.set_column("B:B", 22)

    ws.set_column("C:D", 50)

    ws.set_column("E:E", largestName)

    ws.set_column("F:F", 10)

    ws.set_column("G:H", 20)

    # ----------grafico-------------------#
    chart = file.add_chart({"type": "pie"})

    listaDeTipos = []

    listaSumaDeTipos = []

    for procedure in procedures:
        listaDeTipos.append(procedure["state_date"])

    for value in listaDeTipos:
        new = True
        for par in listaSumaDeTipos:
            if value in par:
                par[0] += 1
                new = False
        if new:
            listaSumaDeTipos.append([1, value])

    for i in range(len(listaSumaDeTipos)):
        listaSumaDeTipos[i] = listaSumaDeTipos[i][::-1]

    for value in listaSumaDeTipos:
        if value[0] == 1:
            value[0] = "Vencido"
        elif value[0] == 2:
            value[0] = "Por Vencer"
        elif value[0] == 3:
            value[0] = "En Plazo"

    ws2.add_table(
        f"B2:C{len(listaSumaDeTipos) + 1}",
        {
            "data": listaSumaDeTipos,
            "columns": [
                {"header": "Estado de Fecha"},
                {"header": "Cantidad"},
            ],
        },
    )

    listaNumeros = [number[0] for number in listaSumaDeTipos]
    listaCategorias = [par[1] for par in listaSumaDeTipos]
    chart.add_series(
        {
            "name": f"Tramites Pendientes {area_usuaria}",
            "categories": ["Sheet2", 2, 1, len(listaCategorias) + 1, 1],
            "values": ["Sheet2", 2, 2, len(listaNumeros) + 1, 2],
            "data_labels": {
                "category": True,
                "position": "outside_end",
                "percentage": True,
            },
        }
    )

    chart.set_size({"width": 1000, "height": 1000})
    chart.set_legend({"none": True})
    ws2.insert_chart("E3", chart)

    file.close()
    s3_client.put_object(
        Bucket=bucket_name,
        Key=folder_name + excel_file_name,
        Body=open(excel_file_name, "rb"),
    )

    path_return = settings.MEDIA_URL + pdf_file_key
    return path_return


def generate_constancia_de_registro(data) -> str:
    lLeft = 2 * cm
    lRigth = A4[1] - 2 * cm
    lTop = A4[0] - 2 * cm
    lBot = cm

    s3_client = settings.CREATE_STORAGE
    bucket_name = settings.AWS_STORAGE_BUCKET_NAME
    folder_name = "media/pdf/constanciaRegistro"

    try:
        s3_client.head_object(Bucket=bucket_name, Key=folder_name)
    except:
        s3_client.put_object(Bucket=bucket_name, Key=folder_name)
    # milisecond
    milisecond = str(int(round(time.time() * 1000)))

    pdf_file_name = (
        f"{folder_name}-{data[1]}-{milisecond}.pdf"
    )

    pdf_file_key = pdf_file_name

    if os.path.exists(pdf_file_name):
        os.remove(pdf_file_name)

    maxWidth = lRigth - lLeft

    def setF(size, name="Arial"):
        fontzise = size
        fontname = (
            name  # simplemente nos ayuda a cambiar las fuentes de todo mas rapido
        )
        c.setFont(psfontname=fontname, size=fontzise)
        style.fontSize = fontzise
        style.fontName = fontname
        style.leading = size

    logoUnap = "media/config/logo_UNAP.png"
    logoPostgrado = "media/config/postgrado.png"
    fondo = "media/config/constanciabg.jpg"

    fontzise = 10
    fontname = "Arial"

    style = getSampleStyleSheet()
    style = style["Normal"]

    pdfmetrics.registerFont(TTFont("Arial", "arial.ttf"))
    pdfmetrics.registerFont(TTFont("Arial-Bold", "arialbd.ttf"))

    estudiante = [data[0], data[1]]

    tipoTramite = data[2]

    c = canvas.Canvas(pdf_file_name, A4[::-1])

    c.drawImage(fondo, 0, 0, A4[1], A4[0])

    c.drawImage(logoUnap, lLeft + 100, lTop - 75, 150, 75)
    c.drawImage(logoPostgrado, lRigth - 200, lTop - 75, 75, 75)

    setF(18, "Arial-Bold")

    style.alignment = 1

    c.drawCentredString(A4[1] / 2, lTop - 135, "CONSTANCIA DE REGISTRO")

    setF(18)

    parrafo01 = Paragraph(
        "La escuela de Postgrado, hace constar mediante el presente que:", style
    )
    parrafo01.wrapOn(canv=c, aW=maxWidth, aH=1000)
    parrafo01.drawOn(c, lLeft, lTop - 175)

    setF(16)

    c.drawString(lLeft + 180, lTop - 210, "Nombres y Apellidos: ")
    c.drawString(lLeft + 180, lTop - 240, "DNI: ")

    setF(16, "Arial-Bold")

    c.drawString(lLeft + 340, lTop - 210, estudiante[0])
    c.drawString(lLeft + 340, lTop - 240, estudiante[1])

    parrafo02 = Paragraph(f"Ha registrado con fecha {data[3]} su {tipoTramite}.", style)
    parrafo02.wrapOn(c, maxWidth, 1000)
    parrafo02.drawOn(c, lLeft, lTop - 300)


    c.save()

    path_return = settings.MEDIA_URL +pdf_file_key
    return path_return
