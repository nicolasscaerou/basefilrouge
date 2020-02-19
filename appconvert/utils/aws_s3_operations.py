# coding: utf-8
""" outils de récupération d'informations sur des images - service AWS rekognition """

import logging
import boto3
from botocore.exceptions import ClientError

TAUX_MIN_CONFIANCE = 85
BUCKET = "cataire"


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
                Image={"S3Object": {"Bucket": bucket, "Name": key}},
                MaxLabels=max_labels,
                MinConfidence=min_confidence)
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
                Image={"S3Object": {"Bucket": bucket, "Name": key}})
    return response['CelebrityFaces']


def reconnaitre_image(key) -> dict:
    """Détecte des features sur des images

    :param key: identifiant de l'objet s3
    :return: retourne les labels d'éléments et éventuels célébrités reconnues dans l'image
    """
    result = {}

    try:
        labels = {"TauxMinDeConfiancePrediction":TAUX_MIN_CONFIANCE / 100}
        #AWS REKO LABELS
        liste = []
        for label in detect_labels(BUCKET, key):
            liste.append("{Name}".format(**label))
        labels.update({"Noms_labels":liste})

        #AWS REKO CELEBRITIES
        celebrites = []
        for celebrite in detect_celebrities(BUCKET, key):
            element = {}
            element.update({"Nom:": "{Name}".format(**celebrite)})
            element.update({"Urls:": "{Urls}".format(**celebrite)})
            element.update({"TauxDeConfiancePrediction":\
                             format(float("{MatchConfidence}".format(**celebrite))/100, '.3f')})
            celebrites.append(element)

        result.update({"Labels":labels})
        if len(celebrites) > 0:
            result.update({"Celebrites":celebrites})
    except ClientError:
        result = {"aws_rekognition":"indisponible"}

    return result

def deposer_fichier(donnees, key):
    """ envoi un fichier sur bucket S3

    :param donnees: format bytes
    :param key: objet S3
    :return: True if file was uploaded, else False
    """

    result = False

    #creation client aws-s3
    s3_client = boto3.client('s3')
    try:
        s3_client.upload_fileobj(donnees, BUCKET, key)
        logging.info("S3: upload OK")
        result = True
    except ClientError as erreur:
        logging.error(erreur)
    return result

def recuperer_fichier(key):
    """recuperation d'un objet par sa key sur aws-s3

    :param: AWS-S3 key-object
    :return: contenu objet
    :rtype: string
    """

    s3_ress = boto3.resource('s3')
    try:
        objet = s3_ress.Object(BUCKET, key)
        result = objet.get()['Body'].read()
    except ClientError as erreur:
        logging.error(erreur)
        result = "Ressource absente", 404
    return result

def supprimer_fichier(key):
    """ supprime un objet aws-s3

    :param key: objet S3
    :return: True if file was uploaded, else False
    """

    result = False

    #creation client aws-s3
    s3_client = boto3.client('s3')
    try:
        s3_client.delete_object(Bucket=BUCKET, Key=key) #retour type response[]
        #response['HTTPStatusCode'] doit être égal à 204
        logging.info("S3: delete OK")
        result = True
    except ClientError as erreur:
        logging.error(erreur)
        result = "Ressource absente", 404
    return result

def compter_objets():
    """ compte le nombre d'objets presents sur le bucket

    :rtype: integer
    """
    cpt = 0
    s3_ress = boto3.resource('s3')
    for _ in s3_ress.Bucket(BUCKET).objects.all():
        #print(file.key)
        cpt += 1
    return cpt
