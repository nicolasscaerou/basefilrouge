import logging
import boto3
from botocore.exceptions import ClientError


def upload_file(file_name, bucket, object_name=None):
    """Upload a file to an S3 bucket

    :param file_name: File to upload
    :param bucket: Bucket to upload to
    :param object_name: S3 object name. If not specified then file_name is used
    :return: True if file was uploaded, else False
    """

    # If S3 object_name was not specified, use file_name
    if object_name is None:
        object_name = file_name

    # Upload the file
    s3_client = boto3.client('s3')
    try:
        response = s3_client.upload_file(file_name, bucket, object_name)
    except ClientError as e:
        logging.error(e)
        return False
    return True

def detect_labels(bucket, key, max_labels=10, min_confidence=90, region="eu-west-1"):
    rekognition = boto3.client("rekognition", region)
    response = rekognition.detect_labels(
		Image={
			"S3Object": {
				"Bucket": bucket,
				"Name": key,
			}
		},
		MaxLabels=max_labels,
		MinConfidence=min_confidence,
	)
    return response['Labels']

def detect_celebrities(bucket, image, region="eu-west-1"):
    rekognition = boto3.client("rekognition", region)
    response = rekognition.recognize_celebrities(
                 Image={
                        "S3Object": {
                                  "Bucket": bucket,
                                  "Name": key,
                        },
        )
    return response['CelebrityFaces'] 


s3 = boto3.client('s3')
response = s3.list_buckets()
# Output the bucket names
#for bucket in response['Buckets']:
#    print(f'  {bucket["Name"]}')
BUCKET = response['Buckets'][0]['Name']
KEY = "rom1.jpeg"

print("========= CONNEXION SUR ========")
print(response['Buckets'][0]['Name'])
with open(KEY, "rb") as f:
    s3.upload_fileobj(f, BUCKET, KEY)
    print("========= UPLOAD OK ========")

#AWS REKO LABELS
dico_label
for label in detect_labels(BUCKET, KEY):
    print("{Name} - {Confidence}%".format(**label))
    
#AWS REKO CELEBRITIES
for celebrities in detect_celebrities(BUCKET, KEY):
    print("{Name}")

