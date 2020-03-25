# coding: utf-8
"""
   APP filrouge - controller.convert_ctrl
   Selon modèle d'architecture MVC (model/vue/controller)

   controller -> convertisseur de fichiers vers Json

"""

#standard import
import json
from io import BytesIO
#3-party import
from flask import request, jsonify
from werkzeug.utils import secure_filename
#local application import
from utils.aws_s3_operations import deposer_fichier, recuperer_fichier, supprimer_fichier
from utils.hateoas import recuperer_hateoas
from utils import recuperer_meta
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

    #================""
    # informations de base, peu importe le type de fichier
    #====================
    adresseip = request.remote_addr
    contenu = request.files['data'].read() #type(contenu)=bytes
    mimetype = data.mimetype
    taille = request.headers.get('Content-Length')
    nomfic = secure_filename(data.filename)
    extension = nomfic.split(".")[-1].lower()

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
    if extension in ['jpg', 'jpeg', 'gif', 'bmp', 'png', 'tiff', 'ico'] or\
        mimetype in ['image/jpeg', 'image/gif', 'image/x-icon', 'image/png', 'image/tiff']:

        donnees = "".join(map(chr, contenu))
        meta = recuperer_meta.meta_images(data, contenu, extension)

    elif extension == 'csv' or \
          mimetype == 'text/csv':
        donnees = contenu.decode('utf-8')
        meta = recuperer_meta.meta_csv(contenu)

    elif extension == 'json' or \
          mimetype == 'application/json':
        contenu = contenu.decode('utf-8')
        donnees = json.loads(contenu)

    elif extension == 'pdf' or \
          mimetype == 'application/pdf':
        donnees = "".join(map(chr, contenu))
        meta = recuperer_meta.meta_pdf(BytesIO(contenu))

    elif extension in ['txt', 'md', 'rst', 'css'] or\
          mimetype in ['text/plain']:
        donnees = contenu.decode('utf-8')

    elif extension in ['xml', 'svg'] or \
          mimetype in ['application/xml', 'image/svg+xml']:
        donnees = contenu.decode('utf-8')
        meta = recuperer_meta.meta_xml(contenu)

    elif extension == 'yaml':
        donnees = contenu.decode('utf-8')
        meta = recuperer_meta.meta_yaml(contenu)

    elif extension == 'zip' or \
          mimetype == 'application/zip':
        donnees = "".join(map(chr, contenu))
        meta = recuperer_meta.meta_zip(contenu)

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
