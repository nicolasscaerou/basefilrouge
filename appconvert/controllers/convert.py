# coding: utf-8
"""
   APP filrouge - controller.convert_ctrl
   Selon modèle d'architecture MVC (model/vue/controller)

   controller -> convertisseur de fichiers vers Json

"""

#standard import
import json
import csv
from io import BytesIO, StringIO
#3-party import
#import numpy as np
#import pandas as pd
import yaml
import xmltodict
import zipfile
from PIL import Image
from PyPDF2 import PdfFileReader
#local applicatoin import
from utils.aws_s3_operations import reconnaitre_image, deposer_fichier,\
                                          recuperer_fichier, supprimer_fichier
from utils.hateoas import recuperer_hateoas
from utils.exif import recuperer_exiftags
from models.modele_fichier import Fichier

def convert_image(donnees):
        # convert string of image data to uint8
        img = Image.open(data)
        width, height = img.size
        dimensions = {'height':height, 'width':width}
        if extension != 'png':
            exif = recuperer_exiftags(img)
        else:
            exif = ""

        #pour transformer la photo en liste de pixels RVB
        #npimg = np.array(img) #type=ndarray
        #donnees = npimg.tolist() #type=list
        donnees = "".join(map(chr, contenu))

        #mettre a True si le service fonctionne avec RosettaHUB
        activation_aws_rekognition = True
        if activation_aws_rekognition:
            temp = BytesIO(contenu)#1types=BytesIO
            deposer_fichier(temp, fichiercourant.id_fichier) #depot format bytes pour reko
            reko = reconnaitre_image(fichiercourant.id_fichier)
            supprimer_fichier(fichiercourant.id_fichier) #supprimer objet pour reko
        else:
            reko = {'aws-rekognition':'desactive'}
        meta = {'dimensions':dimensions, 'exif':exif, 'reconnaissance':reko}
    return 

    elif extension in ['txt', 'md', 'rst', 'css'] or\
          mimetype in ['text/plain']:
        donnees = contenu.decode('utf-8')

    elif extension == 'json' or \
          mimetype == 'application/json':
        contenu = contenu.decode('utf-8')
        donnees = json.loads(contenu)

    elif extension == 'yaml':
        contenu = contenu.decode('utf-8')
        donnees = yaml.load(contenu, Loader=yaml.FullLoader)

    elif extension == 'csv' or \
          mimetype == 'text/csv':
        #permet de décoder le fichier, détecter les libellés de la ligne de titre
        #puis convertir le tableau de données en dictionnaire
        temp = contenu.decode('utf-8')
        temp = StringIO(temp)
        next(temp)
        dialect = csv.Sniffer().sniff(next(temp))
        temp.seek(0)
        reader = csv.DictReader(temp, dialect=dialect)
        temp = []
        for row in reader:
            temp.append(dict(row))
        donnees = temp
        #ajouter en meta-données le délimiteur qui a été détecté
        meta = {'delimiter': dialect.delimiter}

    elif extension == 'pdf' or \
          mimetype == 'application/pdf':
        #créé un objet pdffile, détecte le nombre de pages et le texte de toutes les pages
        temp = BytesIO(contenu)
        input_pdf = PdfFileReader(temp)
        
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
        donnees = {"texte":temp}

    elif extension in ['xml', 'svg'] or \
          mimetype in ['application/xml', 'image/svg+xml']:
        contenu = contenu.decode('utf-8')
        donnees = xmltodict.parse(contenu)

    elif extension == 'zip' or \
          mimetype == 'application/zip':
        try:
            tempzip = zipfile.ZipFile(BytesIO(contenu))
            donnees = "".join(map(chr,contenu))
            meta = {"archive_liste_fichiers": tempzip.namelist()}
        except zipfile.BadZipFile:
            meta = {"erreur:": "Fichier zip erroné"}

    else:
        code_retour = 415
        message = "Unsupported Media Type"

    #enregistrement donnees
    fichiercourant.donnees = donnees
    #enregistrement metadonnees particulières
    fichiercourant.meta_donnees = meta
    #enregistrement hateoas
    fichiercourant.hateoas = recuperer_hateoas(request.url,\
                                                 fichiercourant.id_fichier)

    #REUPLOAD FICHIER
    #result = fichiercourant.serialise()
    #temp = json.dumps(result)
    #temp = jsonify(result)

    if code_retour >= 400:
        result = {"code_erreur:": code_retour, "erreur": message}
    else:
        result = fichiercourant.serialise()
        pour_aws = BytesIO(json.dumps(result).encode('utf-8'))
        deposer_fichier(pour_aws, fichiercourant.id_fichier)
    return jsonify(result), code_retour
    #return jsonify(result), 201

def fichier_get(idFichier: str):
    """ fonction de récupération d'un fichier précédemment récupéré

    :param id_fichier: id fichier (se trouve dans le json d'upload de la requete POST 200 initiale)
    :return: récupération du fichier au format json
    :rtype: json
    """
    temp = recuperer_fichier(idFichier)
    if temp == 404:
        result = "Ressource introuvable", temp
    elif temp == 400:
        result = "Mauvaise requête", temp
    else:
        temp = json.loads(temp.decode('utf-8'))
        result = jsonify(temp), 200

    return result

def fichier_delete(idFichier: str):
    """ fonction de récupération puis suppression d'un fichier précédemment récupéré

    :param id_fichier: id fichier (se trouve dans le json d'upload de la requete POST 200 initiale)
    :return: récupération du fichier au format json
    :rtype: json
    """
    temp = recuperer_fichier(idFichier)
    if temp == 404:
        result = "Ressource introuvable", temp
    elif temp == 400:
        result = "Mauvaise requête", temp
    else:
        temp = json.loads(temp.decode('utf-8'))
        result = jsonify(temp), 200
        supprimer_fichier(idFichier)

    return result
