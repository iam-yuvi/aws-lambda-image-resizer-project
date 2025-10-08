import boto3
from PIL import Image
import io

s3 = boto3.client('s3')

def lambda_handler(event, context):
    # Extract bucket and object info
    bucket = event['Records'][0]['s3']['bucket']['name']
    source_key = event['Records'][0]['s3']['object']['key']

    # Skip already resized images
    if source_key.startswith('resized/'):
        print("Skipping resized image.")
        return

    # Define destination key (uploads → resized)
    resized_key = source_key.replace('uploads/', 'resized/')

    # Download image from S3
    image_obj = s3.get_object(Bucket=bucket, Key=source_key)
    image_data = image_obj['Body'].read()

    # Open and resize image
    image = Image.open(io.BytesIO(image_data))
    image = image.resize((300, 300))

    # Save resized image to buffer
    buffer = io.BytesIO()
    image.save(buffer, format=image.format)
    buffer.seek(0)

    # Upload resized image to 'resized/' folder
    s3.put_object(Bucket=bucket, Key=resized_key, Body=buffer)

    print(f"✅ Resized image saved as {resized_key}")
    return {
        'statusCode': 200,
        'body': f"Image resized and saved as {resized_key}"
    }
