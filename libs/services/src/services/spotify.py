import locale
import os

from dotenv import load_dotenv
from spotipy import Spotify
from spotipy.oauth2 import SpotifyOAuth

load_dotenv()


def obtener_accept_language():
    # Inicializa con la configuración regional del sistema operativo
    try:
        locale.setlocale(locale.LC_ALL, '')
    except locale.Error:
        pass
    
    # Obtiene el código de la configuración actual
    loc, _ = locale.getlocale()
    
    # Si no se detecta, busca en las variables de entorno o usa un valor por defecto
    if not loc:
        loc = os.getenv('LANG') or os.getenv('LC_ALL') or 'en_US'
        
    # Limpia la codificación (ej. 'es_MX.UTF-8' -> 'es_MX') y cambia '_' por '-'
    idioma_limpio = loc.split('.')[0]
    return idioma_limpio.replace('_', '-')


spotify = Spotify(
    auth_manager=SpotifyOAuth(
        scope = [
            'playlist-read-private',
            'playlist-modify-private',
        ],
    ),
    language=obtener_accept_language()
)
