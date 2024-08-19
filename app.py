from flask import Flask, render_template, request, redirect, url_for
import boto3
import os
from datetime import datetime

app = Flask(__name__)

# Configure AWS S3 and DynamoDB
S3_BUCKET = "cloud-internship-project3-s3"
DYNAMO_TABLE = "S3MetadataTable"

s3_client = boto3.client('s3',region_name='ap-northeast-1')
dynamodb = boto3.resource('dynamodb',region_name='ap-northeast-1')
table = dynamodb.Table(DYNAMO_TABLE)


@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        if 'file' not in request.files:
            return "No file part"
        
        file = request.files['file']
        if file.filename == '':
            return "No selected file"
        
        if file and file.filename.endswith('.txt'):
            filename = file.filename
            s3_key = f"uploads/{filename}"
            
            # Upload file to S3
            s3_client.upload_fileobj(file, S3_BUCKET, s3_key)
            s3_uri = f"s3://{S3_BUCKET}/{s3_key}"
            upload_time = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
            
            # Save metadata to DynamoDB
            table.put_item(
                Item={
                    'key': s3_key,
                    'filename': filename,
                    'S3Uri': s3_uri,
                    'uploadTime': upload_time
                }
            )
            return redirect(url_for('upload_file'))
        else:
            return "Only .txt files are allowed"

    # List all files in the S3 bucket
    objects = s3_client.list_objects_v2(Bucket=S3_BUCKET)
    file_list = []
    if 'Contents' in objects:
        for obj in objects['Contents']:
            file_list.append(obj['Key'])

    return render_template('upload.html', files=file_list)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True)
