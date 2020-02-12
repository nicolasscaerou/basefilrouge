# coding: utf-8
""" Ajout de la fonctionnalité HATEOAS pour être niveau 3 sur l'échelle de maturité Richardson

    - https://martinfowler.com/articles/richardsonMaturityModel.html
    - https://putaindecode.io/articles/hateoas-le-graal-des-developpeurs-d-api/
    - https://fr.wikipedia.org/wiki/Uniform_Resource_Identifier

"""

def recup_hateoas(adresse: str, id_fichier: str) -> dict:
    """
        fonction qui renvoie un dictionnaire à partir d'éléments d'une UFI
    """

    hateoas = {"method": "get"}
    hateoas.update({"url": adresse})
    hateoas.update({"urn": id_fichier})
    return hateoas

def test_recup_hateoas():
    """ utiliser PYTEST pour tester """
    assert recup_hateoas("a", "b") == {'method': 'get', 'url': 'a', 'urn': 'b'}
