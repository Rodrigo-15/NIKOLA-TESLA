from django.urls import path
from . import views

urlpatterns = [
    path("login/", views.login, name="login"),
    path(
        "get_user_data_by_token/",
        views.get_user_data_by_token,
        name="get_user_data_by_token",
    ),
    path(
        "create_users_alumnos/", views.create_users_alumnos, name="create_users_alumnos"
    ),
    path("rename_files/", views.rename_files, name="rename_files"),
    path("importar_persona_expediente_xlsx", views.importar_persona_expediente_xlsx),
    path("resend_email", views.resend_email, name="resend_email"),
    
]
