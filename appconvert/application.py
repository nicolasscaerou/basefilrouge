#!/usr/bin/env python3
"""
   APPLICATION WEB contenant
    * API de transformation fichier -> Json

   - utilisation de connexion OVER Flask qui gère mieux l'OPENAPI3 (demande du prof SOA)
   - https avec SSL codés mais pas activé pour le moment
   - codé entièrement avec VI :)

"""
from __future__ import absolute_import
import logging
from datetime import datetime
#utilisation de connexion qui agit par-dessus Flask et gère mieux l'OPENAPI3 (demande du prof SOA)
import connexion
from flask import request, render_template
#from OpenSSL import SSL

#architecture MVC:
import controllers

#attention, pour l'instant incompatible avec connexion(zalando)
UPLOAD_FOLDER = '/path/to/the/uploads'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}
MAX_CONTENT_LENGTH = 10 * 1024 * 1024

#APP = connexion.FlaskApp(__name__, port=10000, specification_dir='openapi/')
APP = connexion.FlaskApp(__name__, specification_dir='openapi/')
APP.add_api('swagger.yaml', arguments={'title': 'SIO API'})
#attention, pour l'instant incompatible avec connexion(zalando)
#APP.config['MAX_CONTENT_LENGTH'] = MAX_CONTENT_LENGTH
#APP.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

#HTTPS SSL certificat
#context = SSL.Context(SSL.SSLv23_METHOD)
#context.use_privatekey_file('ssl/appfilrouge.key')
#context.use_certificate_file('ssl/appfilrouge.crt')

#########################
# PAGE D'INDEX (ACCUEIL)
#########################
@APP.route('/')
def index():
    """
    route permettant d'avoir la page d'accueil
    """

    return render_template('index.html', title="index")

#########################
# SWAGGER UI
#########################
@APP.route('/ui')
def redirection_ui():
    """
    route de redirection vers l'interface swagger
    """
    headers = {'Location': 'api/ui'}
    return '', 302, headers

#########################
# FORMULAIRE
#########################
@APP.route('/formulaire/', methods=['POST', 'GET'])
def formulaire(data=None):
    """
    formulaire de conversion de fichier
    """
    message = ""
    if request.method == 'GET':
        message = render_template('upload.html', title="upload")
    elif request.method == 'POST':
        print("cacadoudinnnnnnnnn")
        #message = controllers.convert_ctrl.convert_post(request)
        message = controllers.convert_ctrl.convert_post(data)

    return message

#########################
# PAGE DE PRESENTATION
#########################
@APP.route('/apropos/')
def apropos():
    """
    route permettant d'avoir infos sur moi
    """
    return render_template('apropos.html', title="apropos", heure_actuelle=datetime.now())



if __name__ == '__main__':

    #a changer lorsque le certificat ssl sera obtenu
    #APP.run(port=56020, debug=False, ssl_context=context))
    APP.run(port=56020, debug=True)
