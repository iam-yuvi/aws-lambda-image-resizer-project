# AWS Lambda Image Resizer Project -- Complete Documentation

## Overview

This project demonstrates how to automatically resize images uploaded to
an S3 bucket using **AWS Lambda** with the **Pillow** Python library.\
When a new image is uploaded to the `uploads/` folder in the S3 bucket,
the Lambda function triggers, resizes the image, and saves the resized
version into the `resized/` folder --- all within the same bucket.

------------------------------------------------------------------------

## Services Used

1.  **Amazon S3** -- To store the uploaded and resized images.\
2.  **AWS Lambda** -- To run the serverless function that resizes images
    automatically.\
3.  **IAM (Identity and Access Management)** -- To create roles and
    permissions for Lambda.\
4.  **Amazon CloudWatch** -- To monitor logs of Lambda function
    execution.

------------------------------------------------------------------------

## Project Flow

1.  User uploads an image to the **uploads/** folder in S3.\
2.  S3 triggers the **Lambda function**.\
3.  Lambda downloads the image temporarily, resizes it using **Pillow**,
    and uploads the new image to the **resized/** folder in the same
    bucket.\
4.  Resized image can be viewed or downloaded from the **resized/**
    folder.

------------------------------------------------------------------------

## Detailed Step-by-Step Setup

### Step 1: Create an S3 Bucket

1.  Go to the **S3 Console**.\
2.  Click **Create Bucket** → Give a unique bucket name (e.g.,
    `image-resizer-bucket`).\
3.  Keep default settings (Block Public Access enabled).\
4.  Inside the bucket, create two folders:
    -   `uploads/` → for original images\
    -   `resized/` → for resized images

------------------------------------------------------------------------

### Step 2: Create an IAM Role for Lambda

1.  Go to the **IAM Console** → **Roles** → **Create Role**.\

2.  Choose **AWS Service** → Select **Lambda** → Click **Next**.\

3.  Attach the policy:

    -   `AWSLambdaBasicExecutionRole` → allows CloudWatch logging.\

4.  Continue and name the role (e.g., `LambdaImageResizerRole`).\

5.  After role creation, open it → go to **Permissions** tab → click
    **Add inline policy**.\

6.  Add this **inline policy** to give full S3 access:

    ``` json
    {
      "Version": "2012-10-17",
      "Statement": [
        {
          "Effect": "Allow",
          "Action": "s3:*",
          "Resource": "*"
        }
      ]
    }
    ```

7.  Save it as `S3FullAccessInline`.

✅ *This role lets Lambda log to CloudWatch and read/write images in
S3.*

------------------------------------------------------------------------

### Step 3: Create and Upload Pillow Layer

AWS Lambda doesn't include the **Pillow** library by default, so we must
add it as a **Layer**.

#### A. Create a Pillow Layer Compatible with Python 3.9

Execute the following commands on an **EC2 instance** or **Linux
terminal**:

``` bash
mkdir -p ~/lambda-pillow-layer
cd ~/lambda-pillow-layer
rm -rf python pillow-layer.zip
mkdir -p python
sudo apt update
sudo apt install python3.9 python3.9-venv python3.9-distutils -y
curl -sS https://bootstrap.pypa.io/get-pip.py | sudo python3.9
python3.9 -m pip install Pillow -t python/
sudo apt install zip -y
zip -r pillow-layer.zip python
```

#### B. Upload the Layer to AWS Lambda

1.  Go to **AWS Console → Lambda → Layers → Create layer**.\
2.  Name it (e.g., `pillow-layer`).\
3.  Upload the file `pillow-layer.zip`.\
4.  Choose **Compatible runtimes** → `Python 3.9`.\
5.  Leave **Compatible architectures** empty (optional).\
6.  Click **Create**.

✅ *This layer allows Lambda to use Pillow for image processing.*

------------------------------------------------------------------------

### Step 4: Create the Lambda Function

1.  Go to **Lambda Console** → **Create Function**.\
2.  Choose **Author from scratch**.\
3.  Enter:
    -   Function name: `image-resizer`
    -   Runtime: **Python 3.9**
    -   Permissions: Use existing role → select `LambdaImageResizerRole`
4.  Click **Create Function**.

------------------------------------------------------------------------

### Step 5: Attach the Pillow Layer

1.  In your Lambda function → **Layers** section → click **Add a
    layer**.\
2.  Choose **Custom layers** → select the previously created
    `pillow-layer`.\
3.  Choose version → click **Add**.

------------------------------------------------------------------------

### Step 6: Add the Lambda Code

Replace the default code with the following:

``` python
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
```

------------------------------------------------------------------------

### Step 7: Add S3 Trigger

1.  Open the Lambda function.\
2.  Under **Function overview**, click **+ Add trigger**.\
3.  Choose **S3**.\
4.  Select your bucket → choose **All object create events**.\
5.  Add a **prefix filter** as `uploads/` (optional but recommended).\
6.  Check "Recursive invocation" is unchecked.\
7.  Click **Add**.

✅ *Now, whenever an image is uploaded to the `uploads/` folder, the
Lambda function will automatically trigger.*

------------------------------------------------------------------------

### Step 8: Test the Setup

1.  Go to the S3 bucket → `uploads/` folder.\
2.  Upload an image (e.g., `sample.jpg`).\
3.  Wait a few seconds.\
4.  Open the `resized/` folder --- a resized version of your image
    should appear.\
5.  You can check **CloudWatch Logs** to see function execution logs.

------------------------------------------------------------------------

## Result

🎯 Successfully created an **automated image resizing system** using AWS
Lambda and Pillow, where images uploaded to `uploads/` are resized and
stored in `resized/` --- all within the same S3 bucket.
