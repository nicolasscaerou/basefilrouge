# coding: utf-8
""" Ajout de la fonctionnalité permettant de récupérer des données EXIF choisies sur une image"""

from PIL import ExifTags

NOMTAG = dict([(value, key) for key, value in ExifTags.TAGS.items()])

# http://www.exiv2.org/tags.html
# liste des tags qu'on veut récupérer
NOMTAG[1] = 'GPS_latitude'
NOMTAG[4] = 'GPS_longitude'
NOMTAG[256] = 'ImageWidth'
NOMTAG[257] = 'ImageLength'
NOMTAG[258] = 'BitsPerSample'
NOMTAG[270] = 'ImageDescription'
NOMTAG[272] = 'HardwareModel'
NOMTAG[305] = 'Software'
NOMTAG[306] = 'DateTime'
NOMTAG[315] = 'Artist'
NOMTAG[33432] = 'Copyright'
NOMTAG[37510] = 'UserComment'
NOMTAG[40962] = 'PixelXDimension'
NOMTAG[40963] = 'PixelYDimension'
NOMTAG[40091] = 'XPTitle'
NOMTAG[40092] = 'XPComment'
NOMTAG[40093] = 'XPAuthor'
NOMTAG[40094] = 'XPKeywords'
NOMTAG[40095] = 'XPSubject'
NOMTAG[40961] = 'ColorSpace'
NOMTAG[42035] = 'HardwareBrand'
NOMTAG[42036] = 'LensModel'

def get_labeled_exif(exif):
    labeled = {}
    for (key, val) in exif.items():
        labeled[ExifTags.TAGS.get(key)] = val

    return labeled


def convert_exif_to_dict(exif):
    """
        transforme la liste des exif en dictionnaire
    """
    data = {}

    if exif is None:
        return data

    for key, value in exif.items():
        if key in NOMTAG and type(value) is str:
            data[NOMTAG[key]] = value
        #else:
        #    data[key] = value

    # These fields are in UCS2/UTF-16, convert to something usable within python
    for key in ['XPTitle', 'XPComment', 'XPAuthor', 'XPKeywords', 'XPSubject']:
        if key in data:
            data[key] = data[key].decode('utf-16').rstrip('\x00')

    return data

def recuperer_exiftags(image):
    """
        fonction qui renvoie un dictionnaire à partir d'éléments d'une UFI
    """

    image.verify()
    exif = image._getexif()
    labeled = get_labeled_exif(exif)

    if image.format in ['JPEG', 'JPG', 'PNG', 'TIFF']:
        exif = convert_exif_to_dict(image._getexif())
    else:
        exif = None

    return exif
