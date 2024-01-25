import os
from backend import settings
from django.template.loader import render_to_string
from weasyprint import HTML
import time


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
        charge_number = data["charge_number"]
        #
        html_string = render_to_string("reports/hoja_de_cargo.html", data)
        milisecond = str(int(round(time.time() * 1000)))
        html = HTML(string=html_string)
        pdf_file_name = os.path.join(
            pdf_folder, "hoja_de_cargo-{}-{}.pdf".format(charge_number, milisecond)
        )
        if os.path.exists(pdf_file_name):
            os.remove(pdf_file_name)
        html.write_pdf(pdf_file_name)
        #
        path_return = os.path.join(
            settings.MEDIA_URL,
            "pdf",
            "hoja_de_cargo-{}-{}.pdf".format(charge_number, milisecond),
        )
        path_return = path_return.replace("\\", "/")
        return path_return
    except Exception as e:
        print(e)
        return None
