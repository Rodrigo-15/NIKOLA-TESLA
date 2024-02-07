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
python manage.py runserver 192.168.16.184:8000
```

## Rutas
- localhost:8000
- localhost:8000/admin


# Seeders
Para eliminar todos los datos de la base de datos y crear nuevos datos de prueba se debe ejecutar el siguiente comando
```python manage.py flush``` y escribir **yes**, luego ejecutar
```python seeder.py```.