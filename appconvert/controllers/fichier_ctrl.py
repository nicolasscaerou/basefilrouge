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
from flask import request, jsonify
from werkzeug.utils import secure_filename
import numpy as np
import pandas as pd
import yaml
from PIL import Image
from PyPDF2 import PdfFileReader
#local applicatoin import
from utils.aws_s3_operations import reconnaitre_image, deposer_fichier,\
                                          recuperer_fichier, supprimer_fichier
from utils.hateoas import recuperer_hateoas
from utils.exif import recuperer_exiftags
from models.modele_fichier import Fichier

def fichier_post(data: str) -> str:
    """Fonction de conversion un fichier posté, en fonction de son type

    -si image: retourne meta_donnees spécifiques(dimensions, EXIF) + donnees en Array RVB
    -si texte simple: retourne aucune meta_donnees spécifique
    -si YAML: transforme les donnees en JSON
    -si CSV, fonctionne pas encore

    :param data: donnees reçues via requête POST
    """
    # pylint: disable=too-many-locals

    #====================
    # informations de base, peu importe le type de fichier
    #====================
    adresseip = request.remote_addr
    contenu = request.files['data'].read() #type(contenu)=bytes
    nomfic = secure_filename(data.filename)
    mimetype = data.mimetype
    taille = request.headers.get('Content-Length')
    extension = nomfic.split(".")[-1]

    #creation objet Fichier
    fichiercourant = Fichier(ip_origine=adresseip, nom_fic=nomfic, mime_type=mimetype,\
                            taille=taille, extension=extension)

    donnees = {}
    meta = {}
    code_retour = 201
    #====================
    # rajouter en plus des donnees dans un format particulier à chaque type
    #  + meta_donnees adaptées à chaque type de fichier
    #  + informations de type HATEOAS (voir fichier hateoas.py)
    #====================
    if extension in ['jpg', 'jpeg', 'bmp', 'png', 'tiff']:
        # convert string of image data to uint8
        img = Image.open(data)
        width, height = img.size
        dimensions = {'height':height, 'width':width}
        if extension == 'png':
            exif = img.info
            exif = {"test":3} #FIXMZ
        else:
            exif = recuperer_exiftags(img)

        #pour transformer la photo en liste de pixels RVB
        #npimg = np.array(img) #type=ndarray
        #donnees = npimg.tolist() #type=list
        donnees = "".join(map(chr,contenu))

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


    elif extension in ['txt', 'md', 'rst']:
        donnees = contenu.decode('utf-8')

    elif extension == 'json':
        contenu = contenu.decode('utf-8')
        donnees = json.loads(contenu)

    elif extension == 'yaml':
        contenu = contenu.decode('utf-8')
        donnees = yaml.load(contenu)

    elif extension == 'csv':
        #permet de décoder le fichier, détecter les libellés de la ligne de titre
        #puis convertir le tableau de données en dictionnaire
        temp = contenu.decode('utf-8')
        temp = StringIO(temp)
        line = next(temp)
        dialect = csv.Sniffer().sniff(next(temp))
        temp.seek(0)
        reader = csv.DictReader(temp, dialect=dialect)
        temp = []
        for row in reader:
            temp.append(dict(row))
        donnees = temp
        #ajouter en meta-données le délimiteur qui a été détecté
        meta = {'delimiter': dialect.delimiter}

    elif extension == 'pdf':
        #créé un objet pdffile, détecte le nombre de pages et le texte de toutes les pages
        temp = BytesIO(contenu)
        input_pdf = PdfFileReader(temp)
        #docInfo = inputPdf.getDocumentInfo() #renvoie des données moisies pour le moment
        nbpages = input_pdf.getNumPages()
        meta.update({"nb_pages":nbpages})
        temp = ""
        for page in range(nbpages):
            temp += input_pdf.getPage(page).extractText() + "\n"
        donnees = {"texte":temp}
    elif extension == 'mp3':
        #temp = eyeD3.load(contenu)
        print("encours")
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
        result = {"code_erreur:": code_retour,"erreur": "format non supporté!"}
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
