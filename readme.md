# Intranet Postgrado UNAP
## Backend Django
### Instalar Python >= 3.7 e instalar Virtualenv con pip de manera global
```
pip install virtualenv
```
### Crear el Virtulenv en la misma carpeta del repositorio
```
virtualenv .venv
```
### activar el virtual env
```
source .venv/Scripts/activate
```
### Instalar los requerimientos del Proyecto
```
pip install -r requirements.txt
```
### Ejecutar las migraciones
```
python manage.py makemigrations
python manage.py migrate
```
### Crear un supuersusuario con permisos de administrador
```
python manage.py createsuperuser
User: 
Email: 
Password:
```
### Correr el Servidor
```
python manage.py runserver
```

## Rutas
- localhost:8000
- localhost:8000/admin
