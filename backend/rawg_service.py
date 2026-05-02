import requests
from datetime import datetime, timedelta

class RAWGService:
    """
    Servicio para buscar juegos en la API de RAWG (rawg.io).
    RAWG es una base de datos gratuita de videojuegos.
    """

    BASE_URL = "https://api.rawg.io/api"
    API_KEY = "3b8954141d2e4703a8391ea37b93c702"
    CACHE_TIMEOUT = 3600  # Cache 

    def __init__(self):
        self.cache = {}

    def buscar_juego(self, nombre_juego):
        """
        Busca un juego en RAWG por nombre.
        Devuelve info del primer resultado o None si no encuentra.
        """
        if nombre_juego in self.cache:
            cached_data = self.cache[nombre_juego]
            if datetime.now() - cached_data['timestamp'] < timedelta(seconds=self.CACHE_TIMEOUT):
                return cached_data['data']

        try:
            params = {
                'search': nombre_juego,
                'key': self.API_KEY,
                'page_size': 1
            }

            response = requests.get(
                f"{self.BASE_URL}/games",
                params=params,
                timeout=5
            )

            if response.status_code != 200:
                return None

            data = response.json()
            resultados = data.get('results', [])

            if not resultados:
                self.cache[nombre_juego] = {
                    'data': None,
                    'timestamp': datetime.now()
                }
                return None

            juego = resultados[0]
            info = {
                'titulo': juego.get('name', 'Desconocido'),
                'rating': juego.get('rating', 0),
                'metacritic': juego.get('metacritic'),
                'plataformas': [p['platform']['name'] for p in juego.get('platforms', [])],
                'generos': [g['name'] for g in juego.get('genres', [])],
                'descripcion': juego.get('description_raw', 'Sin descripción disponible'),
                'imagen': juego.get('background_image'),
                'fecha_lanzamiento': juego.get('released'),
            }

            self.cache[nombre_juego] = {
                'data': info,
                'timestamp': datetime.now()
            }

            return info

        except requests.exceptions.RequestException as e:
            print(f"Error conectando a RAWG: {str(e)}")
            return None
        except Exception as e:
            print(f"Error en buscar_juego: {str(e)}")
            return None


    def buscar_multiples(self, nombre_juego, page_size=8):
        """
        Busca múltiples juegos en RAWG por nombre.
        Devuelve lista de dicts con título, rating y plataformas.
        """
        cache_key = f"multi_{nombre_juego}"
        if cache_key in self.cache:
            cached = self.cache[cache_key]
            if datetime.now() - cached['timestamp'] < timedelta(seconds=self.CACHE_TIMEOUT):
                return cached['data']

        try:
            params = {
                'search': nombre_juego,
                'key': self.API_KEY,
                'page_size': page_size,
            }
            response = requests.get(
                f"{self.BASE_URL}/games",
                params=params,
                timeout=5
            )
            if response.status_code != 200:
                return None

            resultados = response.json().get('results', [])
            if not resultados:
                return None

            juegos = [
                {
                    'titulo': j.get('name', 'Desconocido'),
                    'rating': j.get('rating', 0),
                    'plataformas': [p['platform']['name'] for p in j.get('platforms', [])],
                    'fecha_lanzamiento': j.get('released', ''),
                }
                for j in resultados
            ]

            self.cache[cache_key] = {'data': juegos, 'timestamp': datetime.now()}
            return juegos

        except Exception as e:
            print(f"Error en buscar_multiples: {str(e)}")
            return None

    def formatear_respuesta_rawg(self, juego_info):
        """
        Formatea la información de RAWG para mostrar al usuario.
        """
        if not juego_info:
            return None

        titulo = juego_info['titulo']
        plataformas = ", ".join(juego_info['plataformas']) if juego_info['plataformas'] else "Múltiples"
        generos = ", ".join(juego_info['generos']) if juego_info['generos'] else "Desconocido"
        rating = f"⭐ {juego_info['rating']}/5" if juego_info['rating'] else ""
        metacritic = f"(Metacritic: {juego_info['metacritic']})" if juego_info['metacritic'] else ""

        linea_rating = f"{rating} {metacritic}".strip() if (rating or metacritic) else ""
        respuesta = f"""📦 **{titulo}**
🎮 Plataformas: {plataformas}
🏷️  Géneros: {generos}
{linea_rating + chr(10) if linea_rating else ""}❌ No disponible actualmente en nuestra tienda."""

        return respuesta


# Instancia global del servicio
rawg_service = RAWGService()
