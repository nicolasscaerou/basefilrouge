# coding: utf-8
""" Ajout de la fonctionnalité HATEOAS pour être niveau 3 sur l'échelle de maturité Richardson

    - https://martinfowler.com/articles/richardsonMaturityModel.html
    - https://putaindecode.io/articles/hateoas-le-graal-des-developpeurs-d-api/
    - https://fr.wikipedia.org/wiki/Uniform_Resource_Identifier

"""

def recuperer_hateoas(adresse: str, id_fichier: str) -> dict:
    """
        fonction qui renvoie un dictionnaire à partir d'éléments d'une URI
    """

    hateoas = {"methods": ["get","delete"]}
    hateoas.update({"url": adresse})
    hateoas.update({"urn": id_fichier})
    return hateoas

def test_recuperer_hateoas():
    """ utiliser PYTEST pour tester """

    resultat = recuperer_hateoas('a', 'b')
    devraitetre = {'methods': ['get','delete'], 'url': 'a', 'urn': 'b'}
    assert resultat == devraitetre
