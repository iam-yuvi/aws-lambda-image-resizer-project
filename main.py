import boto3
import os
from PIL import Image
import tempfile

s3 = boto3.client('s3')

def lambda_handler(event, context):
    bucket_name = event['Records'][0]['s3']['bucket']['name']
    key = event['Records'][0]['s3']['object']['key']

    # Process only images from 'uploads/' folder
    if not key.startswith('uploads/'):
        return

    download_path = os.path.join(tempfile.gettempdir(), os.path.basename(key))
    upload_key = key.replace('uploads/', 'resized/')
    upload_path = os.path.join(tempfile.gettempdir(), os.path.basename(upload_key))

    s3.download_file(bucket_name, key, download_path)

    with Image.open(download_path) as img:
        img.thumbnail((300, 300))
        img.save(upload_path)

    s3.upload_file(upload_path, bucket_name, upload_key)
    print(f"Resized image uploaded to {upload_key}")
