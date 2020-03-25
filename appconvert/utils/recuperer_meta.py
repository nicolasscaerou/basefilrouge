# coding: utf-8
"""
   APP filrouge - utils.recuperer_meta

"""

#standard import
import csv
from io import BytesIO, StringIO
import zipfile
#3-party import
#import numpy as np
#import pandas as pd
import yaml
import xmltodict
from PIL import Image
from PyPDF2 import PdfFileReader
#local applicatoin import
from utils.aws_s3_operations import reconnaitre_image, deposer_fichier, supprimer_fichier
from utils.exif import recuperer_exiftags

def meta_csv(donnees):
    """ fonction de recuperation de metadonnees sur les csv """

    temp = donnees.decode('utf-8')
    temp = StringIO(temp)
    next(temp)
    dialect = csv.Sniffer().sniff(next(temp))
    temp.seek(0)
    reader = csv.DictReader(temp, dialect=dialect)
    traduction = []
    for row in reader:
        traduction.append(dict(row))

    meta = {'delimiter': dialect.delimiter}
    meta.update({"traduction_json":traduction})

    return meta


def meta_images(databytes, donnees, extension):
    """ fonction de recuperation de metadonnees sur les images """

    img = Image.open(databytes)
    width, height = img.size
    dimensions = {'height':height, 'width':width}
    if extension != 'png':
        exif = recuperer_exiftags(img)
    else:
        exif = ""

    #mettre a True si le service fonctionne avec RosettaHUB
    activation_aws_rekognition = True
    if activation_aws_rekognition:
        temp = BytesIO(donnees)#1types=BytesIO
        deposer_fichier(temp, "temporaire") #depot format bytes pour reko
        reko = reconnaitre_image("temporaire")
        supprimer_fichier("temporaire") #supprimer objet pour reko
    else:
        reko = {'aws-rekognition':'desactive'}
    meta = {'dimensions':dimensions, 'exif':exif, 'reconnaissance':reko}

    #pour transformer la photo en liste de pixels RVB
    #npimg = np.array(img) #type=ndarray
    #temp = npimg.tolist() #type=list
    #meta.update({"tableau-RVB": temp})
    #prend BEAUCOUP trop de place

    return meta


def meta_pdf(donnees):
    """ fonction de recuperation de metadonnees sur les pdf """

    meta = {}
    input_pdf = PdfFileReader(donnees)
    pdf_info = input_pdf.getDocumentInfo()
    if pdf_info.author is not None:
        meta.update({"auteur":pdf_info.author})
    if pdf_info.title is not None:
        meta.update({"titre":pdf_info.title})
    if pdf_info.subject is not None:
        meta.update({"sujet":pdf_info.subject})

    nbpages = input_pdf.getNumPages()
    meta.update({"nb_pages":nbpages})
    temp = ""
    for page in range(nbpages):
        temp += input_pdf.getPage(page).extractText() + "\n"
    meta.update({"texte_extrait":temp})

    return meta


def meta_xml(donnees):
    """
        fonction de recuperation de metadonnees sur les xml
        fournit la traduction du xml en json
    """

    temp = donnees.decode('utf-8')
    meta = {"traduction_json": xmltodict.parse(temp)}

    return meta


def meta_yaml(donnees):
    """
        fonction de recuperation de metadonnees sur les yaml
        fournit la traduction du yaml en json
    """

    meta = {"traduction_json": yaml.load(donnees, Loader=yaml.FullLoader)}

    return meta

def meta_zip(donnees):
    """
        fonction de recuperation de metadonnees sur les zip
        fournit la liste des fichiers présents dans l'archive
    """

    try:
        tempzip = zipfile.ZipFile(BytesIO(donnees))
        meta = {"archive_liste_fichiers": tempzip.namelist()}
    except zipfile.BadZipFile:
        meta = {"erreur:": "Fichier zip erroné"}

    return meta
