# coding: utf-8
""" outils de récupération d'informations sur des images - service AWS rekognition """

import logging
from datetime import datetime
import boto3
from botocore.exceptions import ClientError

TAUX_MIN_CONFIANCE = 85


#def upload_file(file_name, bucket, object_name=None):
#    """Upload a file to an S3 bucket
#
##    :param file_name: File to upload
#    :param bucket: Bucket to upload to
#    :param object_name: S3 object name. If not specified then file_name is used
#    :return: True if file was uploaded, else False
#    """
#
#    # If S3 object_name was not specified, use file_name
#    if object_name is None:
#        object_name = file_name
#
#    # Upload the file
#    s3_client = boto3.client('s3')
#    try:
#        response = s3_client.upload_file(file_name, bucket, object_name)
#    except ClientError as erreur:
#        logging.error(erreur)
#        return False
#    return True

def detect_labels(bucket, key, max_labels=10, min_confidence=TAUX_MIN_CONFIANCE,\
                                              region="eu-west-1"):
    """Détecte des labels sur une image

    :param bucket: Bucket sur lequel lire l'image précédemment déposée avec upload_file
    :param image: Image dont on veut récupérer des informations (base64 ou objet AWS-S3)
    :param max_labels: nombre maximum de labels à récupérer
    :param min_confidence: % minimum de confiance dans les labels récupérés
    :param region: region AWS pour l'execution de leur API rekognition
    :return: retourne les labels d'éléments reconnus dans l'image transmise
    """
    rekognition = boto3.client("rekognition", region)
    response = rekognition.detect_labels(
                Image={
                    "S3Object": {
                            "Bucket": bucket,
                            "Name": key,
                     }
                },
                MaxLabels=max_labels,
                MinConfidence=min_confidence
        )
    return response['Labels']

def detect_celebrities(bucket, key, region="eu-west-1"):
    """Détecte des célébrités sur une image

    :param bucket: Bucket sur lequel lire l'image précédemment déposée avec upload_file
    :param image: Image dont on veut récupérer des informations
    :param region: region AWS pour l'execution de leur API rekognition
    :return: retourne les labels d'éléments reconnus dans l'image transmise
    """
    rekognition = boto3.client("rekognition", region)
    response = rekognition.recognize_celebrities(
                 Image={
                        "S3Object": {
                                  "Bucket": bucket,
                                  "Name": key,
                        }
                 },
        )
    return response['CelebrityFaces']


def reconnaissance_image(donnees) -> dict:
    """Détecte des features sur des images

    :param donnees: Image dont on veut récupérer des informations
    :return: retourne les labels d'éléments et éventuels célébrités reconnues dans l'image
    """
    result = {}
    #with open(image, "rb") as donnees: #a utiliser si nom fichier en entree et non des bytes

    #creation client aws-s3
    s3_client = boto3.client('s3')
    #recuperation d'un bucket
    response = s3_client.list_buckets()
    bucket = response['Buckets'][0]['Name']
    #definition d'un nom d'objet temporaore
    key = "temp" + str(datetime.now().strftime("%H%M%S%f"))
    logging.info("S3- connexion sur : {}", bucket)
    #depot du fichier en objet sur s3
    s3_client.upload_fileobj(donnees, bucket, key)
    logging.info("S3: upload OK")
    try:
        labels = {"TauxMinDeConfiancePrediction":TAUX_MIN_CONFIANCE}
        #AWS REKO LABELS
        liste = []
        for label in detect_labels(bucket, key):
            liste.append("{Name}".format(**label))
        labels.update({"Noms_labels":liste})

        #AWS REKO CELEBRITIES
        celebrites = []
        for celebrite in detect_celebrities(bucket, key):
            element = {}
            element.update({"Nom:": "{Name}".format(**celebrite)})
            element.update({"Urls:": "{Urls}".format(**celebrite)})
            element.update({"TauxDeConfiancePrediction":\
                             format(float("{MatchConfidence}".format(**celebrite))/100, '.3f')})
            celebrites.append(element)
    
        result.update({"Labels":labels})
        if len(celebrites) > 0:
            result.update({"Celebrites":celebrites})
    #except ClientError as erreur:
    except:
        result = {"aws_rekognition":"indisponible"}
    #finally:
        #suppression de l'objet temporaire
        #s3_client.delete_object(bucket, key)   #ne fonctionne pas pour le moment

    return result

#monimage = "friends.jpg"
#with open(monimage, "rb") as donnees:
#    print(reconnaissance_image(donnees))
