#!/usr/bin/env python3
"""
   APP filrouge - controller.convert_ctrl
   Selon modèle d'architecture MVC (model/vue/controller)

   controller -> convertisseur de fichiers vers Json

"""
from __future__ import absolute_import

from hashlib import md5
from datetime import datetime
from flask import request, jsonify
from werkzeug.utils import secure_filename
import numpy as np
import cv2, json, yaml, csv 

def fichier_post(data: str) -> str:
    """
    fonction de conversion
    """
    message = ""
    adresseip = request.remote_addr
    contenu = request.files['data'].read()
    dateconversion = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    nomfic = secure_filename(data.filename)
    mimetype = data.mimetype
    taille = request.headers.get('Content-Length')
    print("tailleheader: ", taille)

    #creation d'un id unique
    #temp = nomfic + taille + dateconversion
    #idFic = md5(temp.encode()).hexdigest()

    extension = nomfic.split(".")[-1]
    print("================ EXTENSION : ", extension, " ====================")

    if extension in ['jpg', 'jpeg', 'bmp', 'png', 'tiff', ]:
        # convert string of image data to uint8
        
        #METHODE n°2
        #contenu = np.fromstring(contenu, np.uint8)
        #img = cv2.imdecode(contenu, cv2.IMREAD_COLOR)
        #dimensions = {'height':img.shape[1], 'width':img.shape[0]}
        #imgplate = img.flatten().tolist()
 
        from PIL import Image
        from PIL.ExifTags import TAGS
        img = Image.open(data)
        width, height = img.size
        dimensions = {'height':height, 'width':width}
        exif = img._getexif()

        npimg = np.array(img)
        imgplate = npimg.flatten().tolist()

        message = jsonify(ip=adresseip,
                          mimetype=mimetype,
                          dimensions=dimensions,
                          data=imgplate,
                          filename=nomfic
                          )
                          #exif=exif
    elif extension in ['txt', 'md', 'rst']:
        contenu = contenu.decode('utf-8')
        message = jsonify(ip=adresseip,
                          mimetype=mimetype,
                          filename=nomfic,
                          data=contenu
                          )
    elif extension == 'json':
        contenu = contenu.decode('utf-8')
        contenu = json.loads(contenu)
        message = jsonify(ip=adresseip,
                          mimetype=mimetype,
                          filename=nomfic,
                          data=contenu
                          )
    elif extension == 'yaml':
        contenu = contenu.decode('utf-8')
        contenu = yaml.load(contenu)
        message = jsonify(ip=adresseip,
                          mimetype=mimetype,
                          filename=nomfic,
                          data=contenu
                          )
    elif extension == 'csv':
        contenu = contenu.decode('utf-8')
        print("decodeUtf8:", contenu)
        reader = csv.DictReader(contenu,dialect="excel")
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

    return message

def fichier_post(data: str) -> str:
