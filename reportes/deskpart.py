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
    # strings que se utilizan como pie de pagina
    addres = "Los Rosales s/n, San Juan Bautista"
    email = "postgrado@unapiquitos.edu.pe"
    phonenumber = "Telefono: (5165) 261101"
    pageDirection = "https://tramites.postgradounap.edu.pe/"

    setF(12, "Arial-Bold")
    tableIncomplete = True
    tableHeight = 0
    porcentaje_sacado = False

    while tableIncomplete:
        if datosTabla[0] != columns:
            datosTabla.insert(
                0, columns
            )  # nos aseguramos que la primera fila en la hoja siempre sea el nombre de las columnas

        if tableHeight == 0:
            tabla = Table(datosTabla[0:], colWidths)
        else:
            tabla = Table(datosTabla[0:tableHeight], colWidths)
        tabla.wrap(maxWidht, 250)

        if (tabla._height) > currenty - lBot - fontzise - 5:
            if not porcentaje_sacado:
                a = currenty - lBot - fontzise - 5  # espacio disponible en la pagina
                b = a / tabla._height  # percentaje de la tabla que cabe en la pagina
                tableHeight = (
                    round(len(datosTabla) * b) + 1
                )  # En la primera iteracion, calculamos la altura e base al porcentaje de la tabla que cabe en la pagina
                (
                    currenty - lBot - fontzise - 5
                )  # esto es para optimizar el tiempo en que se genera la tabla
                porcentaje_sacado = True
                continue
            else:
                tableHeight -= 1  # en iteraciones posteriores vamos quitandole 1 valor por cada iteracion hasta que entre en la pagina
                continue
        else:
            if tableHeight == 0:
                datosRestantes = (
                    []
                )  # en caso de que la tabla no entre en 1 hoja, aqui es donde se guardaran los datos que van a la siguiente pagina
            else:

                datosRestantes = datosTabla[tableHeight:]

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
            tabla.drawOn(c, lLeft, currenty - tabla._height)  # se pone la tabla

            # ------------pie de pagina----------------#
            setF(8)
            c.drawCentredString(A4[0] / 2, lBot - fontzise, str(pageCounter))
            pageCounter += 1

            c.drawString(lLeft, lBot, addres)
            c.drawString(lLeft, lBot + fontzise, phonenumber)

            lengt1 = c.stringWidth(email, "Arial", fontzise)
            lengt2 = c.stringWidth(pageDirection, "Arial", fontzise)

            c.drawString(lRigh - lengt1, lBot, email)
            c.drawString(lRigh - lengt2, lBot + fontzise, pageDirection)
            # -------------pie de pagina-----------------#

            if len(datosRestantes) != 0:
                c.showPage()
                currenty = lTop  # si hay datos para poner en la siguiente pagina, se crea un nueva pagina y llamamos  a la funcion
                tableIncomplete, altura, alturay = tabla_dinamica(
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
                    lRigh,
                    columns,
                    colWidths,
                )

                currenty -= altura

            elif len(datosRestantes) == 0:
                tableIncomplete = (
                    False  # en caso de que ya no falten datos se rompe el bucle
                )
                currenty -= tabla._height
    return tableIncomplete, tabla._height, currenty


def upload_file_to_s3(file_name, folder_name):
    # Subir el archivo al bucket de S3 si debug es False de lo contrario se sube a la carpeta media
    if not settings.DEBUG:
        s3_client = settings.CREATE_STORAGE
        bucket_name = settings.AWS_STORAGE_BUCKET_NAME
        try:
            s3_client.head_object(Bucket=bucket_name, Key=folder_name)
        except:
            s3_client.put_object(Bucket=bucket_name, Key=folder_name)
        s3_client.put_object(
            Bucket=bucket_name,
            Key=folder_name + file_name,
            Body=open(file_name, "rb"),
        )
        os.remove(file_name)
        return settings.MEDIA_URL + folder_name + file_name
    else:

        path_return = os.path.join(settings.MEDIA_LOCAL_URL, folder_name, file_name)
        path_return = path_return.replace("\\", "")
        path_return = path_return.replace("/media/", "media/")
        return settings.URL_LOCAL + path_return


def get_process_tracking_sheet(data) -> str:
    try:
        #
        trackins = []  # aqui guardamos todos los datos que iran en nuestra tabla

        for thing in data["trackins"]:
            thing = dict(thing)
            a = dict(thing)  # se obtienen los datos de los trakins
            trackins.append(a)
        #
        code_number = data["procedure"]["code_number"]
        milisecond = str(int(round(time.time() * 1000)))
        # Nombre del archivo PDF que deseas crear

        folder_name = "pdf/hoja_seguimiento/"
        pdf_file_name = "hoja-seguimiento-{}-{}.pdf".format(code_number, milisecond)
        pdf_file_key = folder_name + pdf_file_name
        # -----generar pdf-----#
        if settings.DEBUG:
            c = canvas.Canvas(
                os.path.join(settings.MEDIA_ROOT, folder_name, f"{pdf_file_name}"), A4
            )
        else:
            c = canvas.Canvas(pdf_file_name, A4)

        pdfmetrics.registerFont(
            TTFont("Arial", f"{settings.MEDIA_URL}config/arial.ttf")
        )
        pdfmetrics.registerFont(
            TTFont("Arial-Bold", f"{settings.MEDIA_URL}config/arialbd.ttf")
        )  # fuentes que se utilizan
        # ---margenes---#
        lTop = A4[1] - cm * 1.5
        lBot = cm
        lLeft = cm * 2.5
        lRight = A4[0] - cm * 1.5
        maxWidht = lRight - lLeft
        maxHeight = lTop - lBot
        # ---margenes---#
        fontzise = 10
        fontname = "Arial"

        style = getSampleStyleSheet()  # estilo para el parrafo
        style = style["Normal"]

        datosTabla = [
            ["Fecha", "Accion", "Oficina"]
        ]  # lista donde se pondran los datos de la tabla

        for thing in trackins:
            datosTabla.append(
                [
                    f'{thing["date"]} {thing["hour"]}',
                    thing["action"],
                    thing["area_name"],
                ]
            )

        logoUnap = f"{settings.MEDIA_URL}config/logo_UNAP.png"
        logoPostgrado = f"{settings.MEDIA_URL}config/postgrado.png"  # imagenes de la unap y la escuela de postgrado

        # ---datos que iran en el pdf------------#
        fechaHora = data["procedure"]["created_at"]
        tipoTramite = data["procedure"]["procedure_type_description"]
        asunto = data["procedure"]["subject"]
        usuario = data["procedure"]["user_name"]
        folios = str(data["procedure"]["number_of_sheets"])
        observacion = data["procedure"]["description"]
        date_state = data["procedure"]["state_date"]
        # ---datos que iran en el pdf------------#

        if date_state == 1:
            date_state = "EN PLAZO"
        elif date_state == 2:
            date_state = "POR VENCER"
        else:
            date_state = "VENCIDO"

        for i in range(len(datosTabla)):
            if i > 0:
                datosTabla[i][0] = Paragraph(
                    datosTabla[i][0], style
                )  # hacemos que los datos sean parrafos para que se centren bien en la tabla
                datosTabla[i][1] = Paragraph(datosTabla[i][1], style)
                datosTabla[i][2] = Paragraph(datosTabla[i][2], style)

        def setF(size, name="Arial"):
            fontzise = size
            fontname = name  # esta funcion nos permite cambiar el tamaño de la letra y su fuente de forma sencilla
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
        ###------------datos varios-----------------###
        c.setFont(psfontname="Arial-Bold", size=fontzise)
        c.drawString(lLeft, currenty, "CREADO POR:")
        currenty -= 30
        c.drawString(lLeft, currenty, "TIPO TRAMITE:")
        currenty -= 30
        c.drawString(lLeft, currenty, "ASUNTO:")
        currenty -= 30
        c.drawString(lLeft, currenty, "FECHA:")
        currenty -= 30
        c.drawString(lLeft, currenty, "ESTADO:")
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

        ###------------datos varios-----------------###

        c.line(lLeft, currenty, lRight, currenty)

        currenty -= 30

        # --------------area tabla-----------------#

        setF(12, "Arial-Bold")
        c.drawCentredString(A4[0] / 2, currenty, "SEGUIMIENTO DEL TRAMITE")

        currenty -= 30

        pageCounter = 1

        lol, altura, currenty = tabla_dinamica(
            datosTabla=datosTabla,
            currenty=currenty,
            pageCounter=pageCounter,
            setF=setF,
            c=c,
            fontzise=fontzise,
            maxWidht=maxWidht,
            lLeft=lLeft,
            lTop=lTop,
            lBot=lBot,
            lRigh=lRight,
            columns=["Fecha", "Accion", "Oficina"],
            colWidths=[0.3 * maxWidht, 0.4 * maxWidht, 0.3 * maxWidht],
        )

        ###---------creacion del qr--------------##

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

        if currenty > 150:
            c.drawImage(img_buffer, (A4[0] / 2) - 35, lBot + fontzise * 2, 70, 70)
        else:
            c.showPage()
            c.drawImage(img_buffer, (A4[0] / 2) - 35, lBot + fontzise * 2, 70, 70)

        c.save()

        path_return = upload_file_to_s3(pdf_file_name, folder_name)
        return path_return
    except Exception as e:
        print("error", e)
        return None


def get_charge_procedure(data) -> str:
    try:

        area = data["area"]["nombre"].replace(" ", "_")
        charge_number = data["charge_number"]
        milisecond = str(int(round(time.time() * 1000)))

        # Nombre del archivo PDF que deseas crear

        folder_name = "pdf/hoja_de_cargo/"

        pdf_file_name = "hoja_de_cargo-{}-{}.pdf".format(charge_number, milisecond)
        pdf_file_key = folder_name + pdf_file_name
        # -----generar pdf-----#
        if settings.DEBUG:
            c = canvas.Canvas(
                os.path.join(settings.MEDIA_ROOT, folder_name, f"{pdf_file_name}"), A4
            )
        else:
            c = canvas.Canvas(pdf_file_name, A4)

        # ----variables autogeneradas---------#

        pdfmetrics.registerFont(
            TTFont("Arial", f"{settings.MEDIA_URL}config/arial.ttf")
        )
        pdfmetrics.registerFont(
            TTFont("Arial-Bold", f"{settings.MEDIA_URL}config/arialbd.ttf")
        )
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
        logoUnap = f"{settings.MEDIA_URL}config/logo_UNAP.png"
        logoPostgrado = f"{settings.MEDIA_URL}config/postgrado.png"

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

        currentY -= 22

        setF(10, "Arial-Bold")

        c.drawString(limiteIzquierda, currentY, "CORREO USUARIO")
        c.drawString(limiteIzquierda + 100, currentY, ":")

        setF(10)

        c.drawString(areaParrafoizquierda, currentY, data["original_user"]["correo"])

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

        c.drawImage(img_buffer, A4[0] / 2 - 35, limiteAbajo + fontzise * 3, 70, 70)

        c.drawString(
            limiteIzquierda,
            limiteAbajo + fontzise * 2,
            f'{data["usuario"]["nombres"]} {data["usuario"]["apellido_paterno"]} {data["usuario"]["apellido_materno"]}',
        )

        c.save()

        path_return = upload_file_to_s3(pdf_file_name, folder_name)
        return path_return
    except Exception as e:
        print(e)
        return None


def get_procedure_data_xlsx(data) -> str:

    # milisecond
    milisecond = str(int(round(time.time() * 1000)))

    area_usuaria = data["area_usuaria"]
    # Nombre del archivo PDF que deseas crear

    folder_name = "excel/deskpart/"
    excel_file_name = f"{data['name']}-{area_usuaria}-{milisecond}.xlsx"

    if settings.DEBUG:
        file = Workbook(
            os.path.join(settings.MEDIA_ROOT, folder_name, f"{excel_file_name}")
        )
    else:
        file = Workbook(excel_file_name)

    procedures = data["procedures"]

    datostabla = [
        [
            "Codigo",
            "Fecha de Creacion",
            "Asunto",
            "Tipo de Tramite",
            "Solicitante",
            "Estado",
            "Estado de Fecha",
            "Fecha Vencimiento",
        ],
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

    ws = file.add_worksheet()
    ws2 = file.add_worksheet()

    formato_cuadro = file.add_format(
        {
            "border": 3,
            "align": "center",
            "valign": "vcenter",
        }
    )
    formato_cuadro.set_bg_color("yellow")
    format_with_font = file.add_format({"font_size": 15})

    # Aplicar el formato al rango de celdas especificado (columnas B a D, filas 2 a 3)
    ws.conditional_format("B2:D3", {"type": "no_blanks", "format": formato_cuadro})

    ws.write_string(1, 1, f"Area Usuaria: {area_usuaria}", format_with_font)
    ws.write_string(1, 2, f"Usuario: {data['usuario']}", format_with_font)
    ws.write_string(1, 3, f"Fecha de creacion: {data['creacion']}", format_with_font)

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
    path_return = upload_file_to_s3(excel_file_name, folder_name)
    return path_return


def generate_constancia_de_registro(data) -> str:
    lLeft = 2 * cm
    lRigth = A4[0] - 2 * cm
    lTop = A4[1] - 2 * cm
    lBot = cm

    # milisecond
    milisecond = str(int(round(time.time() * 1000)))
    folder_name = "pdf/constancia_de_registro/"
    pdf_file_name = f"constancia_de_registro-{data[1]}-{milisecond}.pdf"

    pdf_file_key = folder_name + pdf_file_name

    # -----generar pdf-----#
    if settings.DEBUG:
        c = canvas.Canvas(
            os.path.join(settings.MEDIA_ROOT, folder_name, f"{pdf_file_name}"), A4
        )
    else:
        c = canvas.Canvas(pdf_file_name, A4)

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

    fontzise = 10
    fontname = "Arial"

    style = getSampleStyleSheet()
    style = style["Normal"]

    pdfmetrics.registerFont(TTFont("Arial", "arial.ttf"))
    pdfmetrics.registerFont(TTFont("Arial-Bold", "arialbd.ttf"))

    estudiante = data[0]["person_full_name"]

    tipoTramite = data[0]["procedure_type_description"]

    fecha, hora = data[0]["created_at"].split(" ", 1)

    hora = hora.replace("P", "")
    hora = hora.replace("A", "")
    hora = hora.replace("M", "")

    addres = "Los Rosales s/n, San Juan Bautista"
    email = "postgrado@unapiquitos.edu.pe"
    phonenumber = "Telefono: (5165) 261101"
    pageDirection = "https://admision.postgradounap.edu.pe/"

    c.drawImage(logoUnap, lLeft, lTop - 37.5, 75, 37.5)
    c.drawImage(logoPostgrado, lRigth - 40, lTop - 40, 40, 40)

    c.setFont(psfontname=fontname, size=fontzise)

    c.drawCentredString(
        (lRigth + lLeft) / 2,
        lTop - fontzise - 5,
        "UNIVERSIDAD NACIONAL DE LA AMAZONIA PERUANA",
    )
    c.drawCentredString(
        (lRigth + lLeft) / 2,
        lTop - fontzise * 3,
        "ESCUELA DE POSTGRADO",
    )

    fontname = "Arial-Bold"
    c.setFont(psfontname=fontname, size=fontzise + 3)

    c.drawCentredString(
        (lRigth + lLeft) / 2,
        lTop - 60,
        "CONSTANCIA DE REGISTRO",
    )

    currenty = lTop - 120

    setF(fontzise, "Arial-Bold")

    c.setFont(psfontname="Arial-Bold", size=fontzise)
    c.drawString(lLeft + 20, currenty, "USUARIO")
    c.drawString(lLeft + 20 + 120, currenty, ":")
    currenty -= 30
    c.drawString(lLeft + 20, currenty, "PARA EL AREA")
    c.drawString(lLeft + 20 + 120, currenty, ":")
    currenty -= 30
    c.drawString(lLeft + 20, currenty, "FECHA")
    c.drawString(lLeft + 20 + 120, currenty, ":")
    currenty -= 30
    c.drawString(lLeft + 20, currenty, "HORA")
    c.drawString(lLeft + 20 + 120, currenty, ":")
    currenty -= 30
    c.drawString(lLeft + 20, currenty, "TIPO DE DOCUMENTO")
    c.drawString(lLeft + 20 + 120, currenty, ":")
    currenty -= 20

    currenty = lTop - 120

    setF(fontzise, "Arial")

    c.drawString(lLeft + 160, currenty, data[0]["person_full_name"])
    currenty -= 30
    c.drawString(lLeft + 160, currenty, data[1])
    currenty -= 30
    c.drawString(lLeft + 160, currenty, fecha)
    currenty -= 30
    c.drawString(lLeft + 160, currenty, hora)
    currenty -= 30
    c.drawString(lLeft + 160, currenty, data[0]["procedure_type_description"])
    currenty -= 30

    setF(fontzise, "Arial-Bold")

    finalText = f"MEDIANTE EL PRESENTE SE HACE CONSTAR EL REGISTRO DEL DOCUMENTO CON NUMERO N°{data[0]['code_number']} A NOMBRE DE {estudiante}"

    style.alignment = 1
    finalParagraph = Paragraph(finalText, style)

    finalParagraph.wrapOn(c, maxWidth, 1000)
    finalParagraph.drawOn(c, lLeft, currenty - 50)

    setF(8)

    c.drawString(lLeft, lBot, addres)
    c.drawString(lLeft, lBot + fontzise, phonenumber)

    lengt1 = c.stringWidth(email, "Arial", 8)
    lengt2 = c.stringWidth(pageDirection, "Arial", 8)

    c.drawString(lRigth - lengt1, lBot, email)
    c.drawString(lRigth - lengt2, lBot + fontzise, pageDirection)

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

    c.drawImage(img_buffer, A4[0] / 2 - 35, lBot + fontzise * 3, 70, 70)

    c.save()

    path_return = upload_file_to_s3(pdf_file_name, folder_name)

    return path_return
