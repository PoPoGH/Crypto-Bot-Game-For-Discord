import os
import gettext
from mysql_functions import Error

DEBUG_MODE = False  # Activez ou désactivez le mode de débogage

# Fonction pour obtenir l'objet translator
def get_translator(user_language):
    localedir = os.path.join(os.path.dirname(__file__), 'lang')
    try:
        translation = gettext.translation('messages', localedir=localedir, languages=[user_language])
    except FileNotFoundError:
        translation = gettext.translation('messages', localedir=localedir, languages=['en'], fallback=True)
        if DEBUG_MODE:
            print(f"Fichier de traduction pour la langue '{user_language}' non trouvé, fallback sur l'anglais.")

    # Installation de la traduction dans le namespace global
    translation.install()

    if DEBUG_MODE:
        print(f"Langue de l'utilisateur : {user_language}")
    
    return translation
