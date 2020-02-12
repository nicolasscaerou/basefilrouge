# coding: utf-8

"""class de base pour chaque type de fichier uploadé"""

#from __future__ import absolute_import
from hashlib import md5
import pprint
from datetime import datetime
import json

class Fichier():
    """class de base pour chaque type de fichier uploadé

        modèle défini comme components dans le swagger.yaml

    """
    # pylint: disable=too-many-instance-attributes
    # pylint: disable=too-many-arguments

    def __init__(self, ip_origine, nom_fic, mime_type, taille, extension):
        """Constructeur d'instanciation d'un fichier uploadé)


        :param ip_origine: Ip de la demande
        :param nom_fic: nom du fichier uploadé
        :param mime-type: mime-type du fichier uploadé
        :param taille: taille du fichier uploadé
        :param extension: détecte la partie du nom après le dernier point
        :param date_conversion: date de lupload/conversion
        :param meta_donnees: meta qui dependent du type de fichier uploadé
        :param donnees: donnees brutes du fichier qui sont plus ou moins retraitees
        :param hateoas: pour retourner les uri des actions possibles sur ressources uploadees
        """

        self._ip_origine = ip_origine
        self._nom_fic = nom_fic
        self._mime_type = mime_type
        self._taille = taille
        self._extension = extension
        self._date_conversion = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self._meta_donnees = {}
        self._donnees = {}
        self._hateoas = {}

        #creation d'un id unique
        temp = self._nom_fic + str(self._taille) + str(self._date_conversion)
        self._id_fichier = md5(temp.encode()).hexdigest()

    def __repr__(self):
        """retourne la représentation du modèle en string"""
        return pprint.pformat(self.to_dict())

    #@property permet d'éviter le get_donnees
    @property
    def id_fichier(self):
        """methode pour récupérer fichier._ip_fichier """
        return self._id_fichier

    @property
    def ip_origine(self):
        """methode pour récupérer fichier._ip_origine """
        return self._ip_origine

    @property
    def nom_fic(self):
        """methode pour récupérer fichier._nom_fic """
        return self._nom_fic

    @property
    def mime_type(self):
        """methode pour récupérer fichier._mime_type """
        return self._mime_type

    @property
    def taille(self):
        """methode pour récupérer fichier._taille """
        return self._taille

    @property
    def extension(self):
        """methode pour récupérer fichier._extension """
        return self._extension

    @property
    def date_conversion(self):
        """methode pour récupérer fichier._date_conversion """
        return self._date_conversion

    @property
    def donnees(self):
        """methode pour récupérer fichier._donnees """
        return self._donnees

    @donnees.setter
    def donnees(self, donnees):
        """enregistre les donnees dans l'objet Fichier

        :param donnees: les donnees du fichier
        :type donnees: dict
        """
        self._donnees = donnees

    @property
    def meta_donnees(self):
        """methode pour récupérer fichier._meta_donnees() """
        return self._meta_donnees

    @meta_donnees.setter
    def meta_donnees(self, meta):
        """enregistre les metadonnees dans l'objet Fichier

        :param meta_donnees: les metadonnees du fichier
        :type meta_donnees: dict
        """
        self._meta_donnees = meta

    @property
    def hateoas(self):
        """methode pour récupérer fichier._hateoas() """
        return self._hateoas

    @hateoas.setter
    def hateoas(self, hateoas):
        """enregistre les hateoas dans l'objet Fichier

        :param hateoas: les metadonnees du fichier
        :type hateoas: dict
        """
        self._hateoas = hateoas

    def to_dict(self):
        """retourne les attributs du modèle en dictionnaire

        :rtype: dict
        """
        return vars(self)

    def serialise(self):
        """retourne

        :rtype: json
        """
        result = {'ip_origine': self.ip_origine,
                  'nom_fic': self.nom_fic,
                  'mime_type': self.mime_type,
                  'taille': self.taille,
                  'extension': self.extension,
                  'date_conversion': self.date_conversion,
                  'meta_donnees': self.meta_donnees,
                  'donnees': self.donnees,
                  'hateoas': self.hateoas,
                 }
        return result

    def to_disk(self):
        """enregistre le fichier sur le disque

        :rtype: code retour
        """
        result = 1
        with open(self._id_fichier, 'w') as fichiersortie:
            json.dump(self, fichiersortie)
            result = 0

        # A TRANSFORMER POUR ENREGISTRER SUR AWSS3 avec module boto3

        return result

    def from_disk(self):
        """ouvre un fichier stocké

        :rtype: code retour
        """
        result = 1
        with open(self._id_fichier, 'r') as fichierlu:
            json.load(fichierlu)
            result = 0

        # A TRANSFORMER POUR ENREGISTRER SUR AWSS3 avec module boto3
        return result
