import os
from backend import settings
from django.template.loader import render_to_string
from weasyprint import HTML
import time
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.lib.pagesizes import A4
from reportlab.platypus import Paragraph
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm


def get_process_tracking_sheet(data) -> str:
    try:
        #
        media_root = settings.MEDIA_ROOT
        pdf_folder = os.path.join(media_root, "pdf")
        if not os.path.exists(pdf_folder):
            os.makedirs(pdf_folder)
        code_number = data["procedure"]["code_number"]
        #
        html_string = render_to_string("reports/hoja_seguimiento.html", data)
        milisecond = str(int(round(time.time() * 1000)))
        html = HTML(string=html_string)
        pdf_file_name = os.path.join(
            pdf_folder, "hoja-seguimiento-{}-{}.pdf".format(code_number, milisecond)
        )
        if os.path.exists(pdf_file_name):
            os.remove(pdf_file_name)
        html.write_pdf(pdf_file_name)
        #
        path_return = os.path.join(
            settings.MEDIA_URL,
            "pdf",
            "hoja-seguimiento-{}-{}.pdf".format(code_number, milisecond),
        )
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
            pdf_folder, "hoja_de_cargo-{}-{}.pdf".format(area, milisecond),
        )
        if os.path.exists(pdf_file_name):
            os.remove(pdf_file_name)

        #-----generar pdf-----#
        c = canvas.Canvas(pdf_file_name, A4)
        #----variables autogeneradas---------#

        pdfmetrics.registerFont(TTFont('Arial', 'arial.ttf'))
        pdfmetrics.registerFont(TTFont('Arial-Bold', 'arialbd.ttf'))
        limiteArriba = A4[1] - cm *1.5
        limiteAbajo = cm
        limiteIzquierda = cm*2.5
        limiteDerecha = A4[0] - cm*1.5
        maxWidht = limiteDerecha- limiteIzquierda
        maxHeight = limiteArriba - limiteAbajo
        fontzise = 10
        fontname = "Arial"

        style = getSampleStyleSheet()
        style = style["Normal"]

        columnasTabla = ["Expediente N°","Asunto", "Area", "Fecha"]
        #----funciones---------#
        def setF(size, name = "Arial"):
            fontzise = size
            fontname = name             #simplemente nos ayuda a cambiar las fuentes de todo de forma mas rapido
            c.setFont(psfontname=fontname, size= fontzise)
            style.fontzise = fontzise

        def creacion_tabla_dinamica(modulos, currentY):
            c.line(limiteIzquierda, currentY, limiteDerecha, currentY)
            initialY = currentY + 0
            lleno = True                #currentY es la varible que nos permitira guardar a que altura de la hoja estamos

            setF(11, "Arial-Bold")
            currentY -= fontzise +5
            c.drawString(limiteIzquierda + 4, currentY-2, columnasTabla[0])
            c.drawString(limiteIzquierda + 130, currentY-2, columnasTabla[1])
            c.drawString(limiteIzquierda + 305, currentY-2, columnasTabla[2]) #se ponen los nombres de las columnas
            c.drawString(limiteIzquierda + 425, currentY-2, columnasTabla[3])

            currentY -= fontzise +2
            c.line(limiteIzquierda, currentY, limiteDerecha, currentY)
            currentY -= 6

            limitParLeft = 160
            limitParRight = 310
            tableParWidht = limitParRight - limitParLeft

            setF(10)
            style = ParagraphStyle('custom_style', fontName = fontname, fontSize = fontzise, leading = 15)
            remainingModules = modulos[0:]
            for j in range(len(modulos)):         
                
                lleno = False
                moduleDescription = Paragraph(modulos[j][1], style=style)
                moduleDescription.wrapOn(c, tableParWidht, 10000)

                moduleDescription.drawOn(c, limitParLeft - 5, currentY - moduleDescription.height)
                
                areaParaWidth = 475-315
                areaPara = Paragraph(modulos[j][2], style=style)
                areaX, areaY = areaPara.wrap(areaParaWidth, 1000)
                areaPara.wrapOn(c, areaParaWidth, 1000)
                areaPara.drawOn(c, 315, currentY - areaY)


                c.drawCentredString(512, (moduleDescription.height/2) + currentY - moduleDescription.height, modulos[j][3])
            
                
                if moduleDescription.height > areaY:
                    a = moduleDescription.height
                else:
                    a = areaY
                if modulos[j] != modulos[-1]:
                    c.line(limiteIzquierda, currentY - a * 1.15, limiteDerecha, currentY - a * 1.15)
                setF(10, "Arial-Bold")
                c.drawCentredString(((limiteIzquierda+ limitParLeft)/2)-7, (a/2) + currentY - moduleDescription.height, modulos[j][0])
                setF(10)
                currentY -= a * 1.3

                try:
                    siguienteModulo = Paragraph(modulos[j + 1][1], style=style)
                except IndexError:
                    siguienteModulo = Paragraph(modulos[j][1], style=style)   
                siguienteModulo.wrapOn(c, tableParWidht, 10000)

                for i in range(len(remainingModules)):
                    if remainingModules[i] == modulos[j]:
                        remainingModules.pop(i)
                        break

                if currentY < limiteAbajo + siguienteModulo.height:
                    valor = (currentY + a * 1.3) - a*1.15
                    c.line(limiteIzquierda, initialY, limiteIzquierda, valor )
                    c.line(limiteDerecha, initialY, limiteDerecha,valor )
                    c.line(140, initialY, 140, valor )
                    c.line(310, initialY, 310, valor )
                    c.line(475, initialY, 475, valor )
                    c.showPage()
                    currentY = limiteArriba
                    i = 0
                    lleno = True
                    creacion_tabla_dinamica(remainingModules[0:], currentY)

                    break
            jump = 0
            if not lleno:
                if currentY > limiteAbajo + 90:
                    c.line(limiteIzquierda, currentY, limiteDerecha, currentY)
                    c.line(limiteIzquierda, initialY, limiteIzquierda, currentY)
                    c.line(limiteDerecha, initialY, limiteDerecha, currentY)
                    c.line(limitParLeft-7, initialY, limitParLeft-7, currentY)
                    c.line(310, initialY, 310, currentY)
                    c.line(475, initialY, 475, currentY)
                    currentY -= 50
                    c.setFont(psfontname= "Arial-Bold", size= fontzise+3)
                    c.drawString(limiteIzquierda, currentY, "RECIBIDO CONFORME:")

                else:
                    c.line(limiteIzquierda, limiteAbajo, limiteDerecha, limiteAbajo)
                    c.line(limiteIzquierda, initialY, limiteIzquierda, limiteAbajo)
                    c.line(limiteDerecha, initialY, limiteDerecha, limiteAbajo)
                    c.line(140, initialY, 140, limiteAbajo)
                    c.line(310, initialY, 310, limiteAbajo)
                    c.line(475, initialY, 475, limiteAbajo)
                    jump = 1

            if currentY < 170:
                c.showPage()
            if jump == 1:
                currentY = 250
                c.setFont(psfontname= "Arial-Bold", size= fontzise+3)
                c.drawCentredString(A4[0]/2, currentY, "RECIBIDO CONFORME:")
        #---------variables o datos adquiridos----------#
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
            tramites.insert(i, [value["code_number"], value["subject"].upper(), value["to_area"]["nombre"].upper(), fechaaa])

        #------------------------------construccion del documento------------------------------#
        #-----cabezal-----#
        c.drawImage(logoUnap, limiteIzquierda, limiteArriba - 37.5, 75, 37.5)
        c.drawImage(logoPostgrado, limiteDerecha- 40, limiteArriba- 40, 40, 40)
        #c.line(limiteDerecha, limiteArriba, limiteDerecha, limiteAbajo)

        c.setFont(psfontname=fontname, size= fontzise)

        c.drawCentredString((limiteDerecha + limiteIzquierda)/2, limiteArriba - fontzise - 5, "UNIVERSIDAD NACIONAL DE LA AMAZONIA PERUANA")
        c.drawCentredString((limiteDerecha + limiteIzquierda)/2, limiteArriba - fontzise * 3, "ESCUELA DE POSTGRADO")

        fontname = "Arial-Bold"
        c.setFont(psfontname= fontname, size= fontzise+3)

        c.drawCentredString((limiteDerecha + limiteIzquierda)/2, limiteArriba - 60, "HOJA DE CARGO N°      -MP-EPG-UNAP")

        fontname = "Arial"
        c.setFont(psfontname= fontname, size= fontzise)
        #----------datos de Usuario-----------#
        setF(10, "Arial-Bold")

        currentY = limiteArriba -120

        areaParrafoizquierda = limiteIzquierda + 120
        areaParrafoDerecha = limiteDerecha -140
        paragraphwidth = areaParrafoDerecha - areaParrafoizquierda

        c.drawString(limiteIzquierda, currentY, "AREA USUARIA")
        c.drawString(limiteIzquierda + 100, currentY, ":")

        areaUsuariaParagraph = Paragraph(areaUsuaria, style)
        parWidth, parHeight = areaUsuariaParagraph.wrap(paragraphwidth, 1000)
        areaUsuariaParagraph.wrapOn(c, paragraphwidth, 1000)
        areaUsuariaParagraph.drawOn(c, areaParrafoizquierda, currentY - parHeight + fontzise)

        c.drawString(limiteDerecha- 120, currentY, "FECHA")
        c.drawString(limiteDerecha- 70, currentY, ":")

        setF(10)

        dateWidht = c.stringWidth(fecha, fontname, fontzise)
        c.drawString(limiteDerecha -dateWidht *1.3, currentY, fecha)

        currentY -= parHeight + fontzise

        setF(10, "Arial-Bold")

        c.drawString(limiteIzquierda, currentY, "USUARIO")
        c.drawString(limiteIzquierda + 100, currentY, ":")

        usuarioParagraph = Paragraph(usuario, style)
        parWidth, parHeight = usuarioParagraph.wrap(paragraphwidth, 1000)
        usuarioParagraph.wrapOn(c, paragraphwidth, 1000)
        usuarioParagraph.drawOn(c, areaParrafoizquierda, currentY - parHeight + fontzise)
        setF(10, "Arial-Bold")

        c.drawString(limiteDerecha- 120, currentY, "HORA")
        c.drawString(limiteDerecha- 70, currentY, ":")
        setF(10)

        c.drawString(limiteDerecha -dateWidht *1.3, currentY, hora)

        currentY -= parHeight + fontzise
        setF(10, "Arial-Bold")

        c.drawString(limiteIzquierda, currentY, "CONSOLIDADO")
        c.drawString(limiteIzquierda + 100, currentY, ":")

        setF(10)

        c.drawString(areaParrafoizquierda, currentY, str(consolidado))

        currentY -= 20

        c.line(limiteIzquierda, currentY, limiteDerecha, currentY)

        #-------------tabla-----------------#
        currentY -= 20
        setF(14)

        c.drawCentredString(A4[0]/2, currentY, "TRAMITES")

        currentY -= 20

        creacion_tabla_dinamica(tramites, currentY)


        #---------guardar archivo-------------#
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
    