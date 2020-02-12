# coding: utf-8
"""
   APP filrouge - controller.convert_ctrl
   Selon modèle d'architecture MVC (model/vue/controller)

   controller -> convertisseur de fichiers vers Json

"""

#standard import
import json
import csv
#3-party import
from flask import request, jsonify
from werkzeug.utils import secure_filename
import numpy as np
import yaml
from PIL import Image
#from PyPDF2 import PdfFileReader
#local applicatoin import
from controllers.aws_s3_operations import reconnaissance_image
from controllers.hateoas import recup_hateoas
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
        exif = img.getexif()

        npimg = np.array(img)
        donnees = npimg.flatten().tolist()

        #mettre a True si le service fonctionne avec RosettaHUB
        activation_aws_rekognition = False
        if activation_aws_rekognition:
            reko = reconnaissance_image(contenu)
        else:
            reko = {'aws-rekognition':'desactive'}
        meta = {'dimensions':dimensions, 'exif':exif, 'reconnaissance':reko}

        #enregistrement metadonnees particulières
        fichiercourant.meta_donnees = meta

    elif extension in ['txt', 'md', 'rst']:
        donnees = contenu.decode('utf-8')

    elif extension == 'json':
        contenu = contenu.decode('utf-8')
        donnees = json.loads(contenu)

    elif extension == 'yaml':
        contenu = contenu.decode('utf-8')
        donnees = yaml.load(contenu)

    elif extension == 'csv':
        contenu = contenu.decode('utf-8')
        print("decodeUtf8:", contenu)
        reader = csv.DictReader(contenu, dialect="excel")
        titres = []
        for row in contenu:
            print(row)
        #for row in reader:
        #    print("row:", row)
        #    contenu.append(row)
        #print("append", contenu)
        #print("dump:", json.dumps(contenu))
#        message = jsonify(ip=adresseip,
#                          mimetype=mimetype,
#                          filename=nomfic,
#                         data=contenu
#                         )

#    elif extension == 'pdf':
#        inputPdf = PdfFileReader(contenu)
#        docInfo = inputPdf.getDocumentInfo()
#        donnees = json.dumps(docInfo)

    #enregistrement donnees
    fichiercourant.donnees = donnees
    print(fichiercourant.donnees)
    #enregistrement hateoas
    fichiercourant.hateoas = recup_hateoas(request.url,\
                                                 fichiercourant.id_fichier)
    return jsonify(fichiercourant.serialise())

def fichier_get(id_fichier: str) -> str:
    """ fonction de récupération d'un fichier précédemment récupéré

    :param id_fichier: id fichier (se trouve dans le json d'upload de la requete POST 200 initiale
    :return: récupération du fichier au format json
    :rtype: json
 """
    with open(id_fichier, 'r') as fichier:
        donnees = fichier.read()
        return donnees
