from backend import settings
import os


def funtion_upload_file_to_s3(file_name, folder_name):
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
