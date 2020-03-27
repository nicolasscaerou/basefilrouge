# APPCONVERT - Projet filrouge de Nicolas SCAËROU

Le site web de l'application se trouve à l'adresse suivante:
[CLIQUEZ ICI](http://99.81.225.203:56056)

# SWAGGER

L'interface swagger de test "client" se trouve dans l'onglet "swagger" de ce site web.

# RAPPORT

Le rapport de mon projet filrouge se trouve dans l'onglet "rapport" de ce site web.

# TEST
Des fichiers pour tester l'application vous sont proposés dans le répertoire appconvert/test/files.

Voici un premier curl à faire à faire avec un fichier csv nommé "test.csv":

```bash
curl -X POST "http://99.81.225.203:56056/api/fichier" -H "accept: application/json" -H "Content-Type: multipart/form-data" -F "data=@test.csv;type=text/csv"
```
