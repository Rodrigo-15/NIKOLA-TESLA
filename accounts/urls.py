from django.urls import path
from . import views

urlpatterns = [
    path("login/", views.login, name="login"),
    path("get_user_data_by_token/", views.get_user_data_by_token,
         name="get_user_data_by_token"),     
    path("create_users_alumnos/", views.create_users_alumnos, name="create_users_alumnos"),    
]
