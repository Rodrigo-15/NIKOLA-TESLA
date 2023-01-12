from django.conf import settings
from django.core.mail import EmailMultiAlternatives


def send_mail(receive_email_addr, file_path):              
    text_content = 'Este es un correo electrónico de informe importante'
    html_content = '<p> Este es un <strong> correo electrónico de informe importante </ strong>. </ p>'
    from_email = settings.DEFAULT_FROM_EMAIL
    msg = EmailMultiAlternatives(
        "UNAP-POSTGRADO 2022", text_content, from_email, [receive_email_addr])
    msg.attach_alternative(html_content, "text/html")     
    msg.attach_file(file_path) 
    if msg.send():
        print('****************** enviado con éxito *********************')
    else:
        print('****************** Error de envío ************************')
    print ('******************** Envío completado ********************')