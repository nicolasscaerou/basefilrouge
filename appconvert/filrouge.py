#!/usr/bin/env python3
"""
   APPLICATION WEB contenant
    * API de transformation fichier -> Json
"""
from __future__ import absolute_import
import logging
from datetime import datetime
import connexion
from flask import Flask, jsonify, request, render_template, url_for

#architecture MVC:
import controllers

APP = connexion.FlaskApp(__name__, port=10000, specification_dir='openapi/')
APP.add_api('swagger.yaml', arguments={'title': 'SIO API'})

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
        message = controllers.convert_ctrl.convert_post(request)

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
    APP.run(debug=True)
