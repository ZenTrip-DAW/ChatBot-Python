from flask import Flask, request, jsonify, session, send_from_directory
from flask_cors import CORS
import sqlite3
import os
import unicodedata
import re
import random
from datetime import datetime
from uuid import uuid4
from backend.config import DB_PATH, FLASK_CONFIG, CHATBOT_CONFIG, PLATAFORMA_MAP, GENEROS_MAP, PLATAFORMAS_SIN_JUEGOS
from backend.rawg_service import rawg_service


# INICIALIZACIÓN DE FLASK Y CONFIGURACIÓN


app = Flask(__name__)
app.secret_key = FLASK_CONFIG['SECRET_KEY']

CORS(app)

# UTILIDADES

def normalizar(texto):
    """
    Normaliza un texto: elimina tildes, puntuación y convierte a minúsculas.
    Ejemplo: "¿Cuánto cuesta God of War?" → "cuanto cuesta god of war"
    """
    if not texto:
        return ""
    texto_normalizado = unicodedata.normalize('NFKD', texto)
    texto_sin_tildes = ''.join([c for c in texto_normalizado if not unicodedata.combining(c)])
# Eliminar puntuaión
    texto_sin_puntuacion = ''.join(c for c in texto_sin_tildes if c.isalnum() or c.isspace())
    return texto_sin_puntuacion.lower().strip()

def obtener_conexion_bd():
    """Abre una conexión a la base de datos SQLite."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  
    return conn

def inicializar_sesion():
    """
    Inicializa la sesión del usuario si es la primera vez.
    Genera un ID único para el usuario y establece el estado inicial.
    """
    if 'usuario_id' not in session:
        session['usuario_id'] = str(uuid4())
        session['estado'] = 'inicio'
        session.modified = True

# BÚSQUEDA EN REGLAS DEL CHATBOT

def buscar_en_reglas(mensaje_normalizado, conn):
    """
    Busca en la tabla 'chatbot_reglas' por palabras clave.
    Devuelve la respuesta con mayor prioridad si encuentra coincidencias.
    """
    cur = conn.cursor()
    cur.execute("SELECT palabras_clave, respuesta, prioridad FROM chatbot_reglas WHERE activo = 1")
    reglas = cur.fetchall()

    palabras_ignoradas = {'juegos', 'juego', 'que'}
    palabras_mensaje = set(mensaje_normalizado.split())  

    mejor_coincidencia = None
    mejor_prioridad = -1

    for palabra_clave, respuesta, prioridad in reglas:
        for palabra in palabra_clave.split():
            if palabra in palabras_ignoradas:
                continue
            if palabra in palabras_mensaje:  
                if prioridad > mejor_prioridad:
                    mejor_coincidencia = respuesta
                    mejor_prioridad = prioridad
                break

    return mejor_coincidencia

# BÚSQUEDA DE JUEGO CONCRETO

def buscar_juego_concreto(mensaje_normalizado, conn):
    """
    Busca un juego específico en la BD.
    1º intenta buscar la frase completa
    2º busca palabra por palabra (sin stopwords)
    3º busca palabra por palabra (incluso con stopwords como articulos)
    Devuelve el primer juego encontrado con sus plataformas y descripción.
    """
    cur = conn.cursor()
    stopwords = CHATBOT_CONFIG['STOPWORDS']

    palabras = [p for p in mensaje_normalizado.split() if p not in stopwords]

    plataformas_keys = set(PLATAFORMA_MAP.keys())
    generos_keys = set(GENEROS_MAP.keys())
    palabras_especiales = plataformas_keys | generos_keys

    if palabras and all(p in palabras_especiales for p in palabras):
        return None

    if len(palabras) <= 2 and any(p in palabras_especiales for p in palabras):
        if len([p for p in palabras if p in palabras_especiales]) >= 1:
            palabras_no_especiales = [p for p in palabras if p not in palabras_especiales]
            if not palabras_no_especiales or len(palabras_no_especiales) <= 1:
                return None

    if not palabras:
        palabras = mensaje_normalizado.split()

    if not palabras:
        return None

    if len(palabras) > 1:
        frase_completa = ' '.join(palabras)
        cur.execute("""
            SELECT id, titulo, descripcion, precio, precio_oferta, clasificacion_edad, activo
            FROM juegos
            WHERE LOWER(titulo) LIKE ?
            ORDER BY activo DESC, titulo
        """, (f'%{frase_completa}%',))
        juegos = cur.fetchall()
        if len(juegos) == 1:
            return formatear_juego(juegos[0], conn)
        elif len(juegos) > 1:
            return formatear_lista_juegos(juegos, frase_completa)

    for palabra in palabras:
        if len(palabra) > 2:
            cur.execute("""
                SELECT id, titulo, descripcion, precio, precio_oferta, clasificacion_edad, activo
                FROM juegos
                WHERE LOWER(titulo) LIKE ?
                ORDER BY activo DESC, titulo
            """, (f'%{palabra}%',))
            juegos = cur.fetchall()
            if len(juegos) == 1:
                return formatear_juego(juegos[0], conn)
            elif len(juegos) > 1:
                return formatear_lista_juegos(juegos, palabra)

    return None

def formatear_juego(juego, conn):
    """
    Formatea la información de un juego para mostrar al usuario.
    Incluye: precio (con oferta), plataformas y descripción.
    """
    cur = conn.cursor()
    juego_id = juego['id']

    cur.execute("""
        SELECT p.nombre
        FROM plataformas p
        JOIN juegos_plataformas jp ON p.id = jp.plataforma_id
        WHERE jp.juego_id = ?
    """, (juego_id,))
    plataformas = [row['nombre'] for row in cur.fetchall()]

    precio_texto = formatear_precio(juego['precio'], juego['precio_oferta'])

    plataformas_str = ", ".join(plataformas) if plataformas else "No especificado"
    respuesta = f"""📦 **{juego['titulo']}**
💰 Precio: {precio_texto}
🖥️  Plataformas: {plataformas_str}
📝 {juego['descripcion']}"""

    return respuesta

def formatear_lista_juegos(juegos, termino):
    """Formatea una lista de juegos de una saga con disponibilidad."""
    respuesta = f"Encontré {len(juegos)} juego(s) con '{termino}':\n\n"
    for j in juegos:
        precio = formatear_precio(j['precio'], j['precio_oferta'])
        if j['activo'] == 1:
            respuesta += f"• {j['titulo']} — {precio} ✅\n"
        else:
            respuesta += f"• {j['titulo']} — ❌ No disponible\n"
    return respuesta


def formatear_precio(precio, precio_oferta):
    """
    Formatea el precio correctamente.
    - Si es 0.0: muestra "GRATIS"
    - Si hay oferta: muestra "X€ (en oferta: Y€)"
    """
    if precio == 0.0:
        return "GRATIS"

    precio_texto = f"{precio}€"

    if precio_oferta:
        precio_texto += f" (en oferta: {precio_oferta}€)"

    return precio_texto


# BÚSQUEDA POR MODO DE JUEGO (solitario / online)

MODO_MAP = {
    'solitario': {
        'keywords': {'solitario', 'solo', 'single', 'player', 'offline',
                     'compania', 'jugador', 'campaña', 'campana', 'historia'},
        'titulos': [
            'The Witcher 3: Wild Hunt', 'Red Dead Redemption 2', "Baldur's Gate 3",
            'Cyberpunk 2077', 'Death Stranding 2', 'God of War Ragnarok',
            "Marvel's Spider-Man 2", 'Hogwarts Legacy', 'Alan Wake 2', 'Avowed',
            'Hollow Knight', 'Hades II', 'Stardew Valley',
        ],
        'titulo_respuesta': 'jugar en solitario',
    },
    'multijugador': {
        'keywords': {'multijugador', 'multiplayer', 'coop', 'cooperativo', 'cooperativa',
                     'amigos', 'local', 'compartida', 'juntos', 'compartido'},
        'titulos': [
            'Elden Ring', 'It Takes Two', 'Overcooked 2',
            'A Way Out', 'Helldivers 2', 'Palworld',
            'Sea of Thieves', 'Portal 2', 'Dredge', 'Grounded',
        ],
        'titulo_respuesta': 'jugar en multijugador',
    },
    'online': {
        'keywords': {'online', 'linea', 'internet', 'conexion', 'red',
                     'pvp', 'competitivo', 'ranking', 'torneos'},
        'titulos': [
            'Call of Duty: Black Ops 6', 'Valorant', 'Counter-Strike 2',
            'Apex Legends', 'Rocket League', 'Overwatch 2',
            'League of Legends', 'Dota 2', 'PUBG', 'Marvel Rivals',
        ],
        'titulo_respuesta': 'jugar online competitivo',
    },
}

def buscar_por_modo(mensaje_normalizado, conn):
    """
    Detecta modo de juego (solitario/multijugador/online) y busca dinámicamente en BD.
    Respeta filtros de plataforma y género si los menciona.
    """
    cur = conn.cursor()

    modo_detectado = None
    palabras_mensaje = set(mensaje_normalizado.split())
    for modo, datos in MODO_MAP.items():
        if any(k in palabras_mensaje for k in datos['keywords']):
            modo_detectado = modo
            break

    if not modo_detectado:
        return None

    tipo_jugador_map = {
        'solitario': 'single_player',
        'multijugador': 'cooperativo',
        'online': 'competitivo'
    }
    tipo_jugador = tipo_jugador_map[modo_detectado]

    plataforma, genero = _detectar_plataforma_genero(mensaje_normalizado)

    query = "SELECT titulo, precio, precio_oferta FROM juegos WHERE activo = 1 AND tipo_jugador = ?"
    params = [tipo_jugador]

    if plataforma:
        query += " AND plataforma = ?"
        params.append(plataforma)

    if genero:
        query += " AND genero = ?"
        params.append(genero)

    query += " ORDER BY RANDOM() LIMIT 10"

    cur.execute(query, params)
    juegos = cur.fetchall()

    if not juegos:
        plat_str = f" de {plataforma}" if plataforma else ""
        gen_str = f" de {genero}" if genero else ""
        modo_texto = MODO_MAP[modo_detectado]['titulo_respuesta']
        return f"No tenemos juegos para {modo_texto}{plat_str}{gen_str} en este momento."

    datos = MODO_MAP[modo_detectado]
    respuesta = f"🎮 **Juegos para {datos['titulo_respuesta']}:**\n\n"

    for juego in juegos:
        precio = formatear_precio(juego['precio'], juego['precio_oferta'])
        respuesta += f"• {juego['titulo']} — {precio}\n"

    return respuesta



# UTILIDAD: Extraer rango de precio del mensaje

def extraer_rango_precio(mensaje_normalizado):
    """
    Extrae rango de precio del mensaje.
    Devuelve (precio_min, precio_max) o None si no hay precio detectado.
    """
    msg = mensaje_normalizado

    match_entre = re.search(r'entre\s+(\d+)\s+y\s+(\d+)', msg)
    match_max = re.search(r'(?:menos de|menos|hasta(?: de)?|por menos de|maximo|menores de|menores)\s+(\d+)', msg)
    match_min = re.search(r'(?:mas de|mas|minimo|desde|mayores de|mayores)\s+(\d+)', msg)
    match_aprox = re.search(
        r'(?:que valga[n]?|que vale[n]?|que cueste[n]?|que cuesta[n]?|de unos|por unos)\s+(\d+)'
        r'|(?<!\w)(?:de|por)\s+(\d+)\s*(?:euros?)'
        r'|(?<!\w)a\s+(\d+)\s+(?:euros?)',
        msg
    ) if not match_entre and not match_max and not match_min else None

    if match_aprox:
        valor = float(match_aprox.group(1) or match_aprox.group(2) or match_aprox.group(3))
        return (valor - 2, valor + 1, f"de {valor:.0f}€")

    precio_min = precio_max = None

    if match_entre:
        precio_min = float(match_entre.group(1))
        precio_max = float(match_entre.group(2))
    elif match_max:
        precio_max = float(match_max.group(1))
    elif match_min:
        precio_min = float(match_min.group(1))

    if precio_min is None and precio_max is None:
        return None

    return (precio_min, precio_max, None)

# BUSQUEDA POR PRECIO

def buscar_por_precio(mensaje_normalizado, conn):
    """
    Detecta búsquedas por rango de precio y devuelve juegos del catálogo.
    Patrones: 'menos de X', 'hasta X', 'entre X y Y', 'mas de X',
              'de X euros', 'que valga/cueste/vale/cuesta X'.
    """
    msg = mensaje_normalizado

    match_entre = re.search(r'entre\s+(\d+)\s+y\s+(\d+)', msg)
    match_max   = re.search(r'(?:menos de|menos|hasta(?: de)?|por menos de|maximo)\s+(\d+)', msg)
    match_min   = re.search(r'(?:mas de|mas|minimo|desde)\s+(\d+)', msg)
    match_aprox = re.search(
        r'(?:que valga[n]?|que vale[n]?|que cueste[n]?|que cuesta[n]?|de unos|por unos)\s+(\d+)'
        r'|(?<!\w)(?:de|por)\s+(\d+)\s*(?:euros?)'
        r'|(?<!\w)a\s+(\d+)\s+(?:euros?)',
        msg
    ) if not match_entre and not match_max and not match_min else None

    if match_aprox:
        valor = float(match_aprox.group(1) or match_aprox.group(2) or match_aprox.group(3))
        cur = conn.cursor()
        margen = 2.0
        cur.execute("""
            SELECT titulo, precio, precio_oferta FROM juegos
            WHERE activo = 1 AND precio BETWEEN ? - ? AND ? + 1
            ORDER BY precio ASC
        """, (valor, margen, valor))
        juegos = cur.fetchall()
        if not juegos:
            cur.execute("""
                SELECT titulo, precio, precio_oferta FROM juegos
                WHERE activo = 1 AND precio BETWEEN ? - 10 AND ? + 1
                ORDER BY precio ASC
            """, (valor, valor))
            juegos = cur.fetchall()
        if not juegos:
            return f"No tenemos juegos cerca de {valor:.0f}€ en este momento."
        if len(juegos) > 10:
            juegos = random.sample(juegos, 10)
            juegos = sorted(juegos, key=lambda j: j['precio'])
        respuesta = f"Aquí tienes juegos de {valor:.0f}€:\n\n"
        for j in juegos:
            precio = formatear_precio(j['precio'], j['precio_oferta'])
            respuesta += f"• {j['titulo']} — {precio}\n"
        return respuesta

    precio_min = precio_max = None

    if match_entre:
        precio_min = float(match_entre.group(1))
        precio_max = float(match_entre.group(2))
    elif match_max:
        precio_max = float(match_max.group(1))
    elif match_min:
        precio_min = float(match_min.group(1))

    if precio_min is None and precio_max is None:
        return None

    cur = conn.cursor()

    if precio_min is not None and precio_max is not None:
        cur.execute("""
            SELECT titulo, precio, precio_oferta FROM juegos
            WHERE precio BETWEEN ? AND ? AND activo = 1
            ORDER BY precio ASC
        """, (precio_min, precio_max))
        label = f"entre {precio_min:.0f}\u20ac y {precio_max:.0f}\u20ac"
    elif precio_max is not None:
        cur.execute("""
            SELECT titulo, precio, precio_oferta FROM juegos
            WHERE precio <= ? AND activo = 1
            ORDER BY precio ASC
        """, (precio_max,))
        label = f"menos de {precio_max:.0f}\u20ac"
    else:
        cur.execute("""
            SELECT titulo, precio, precio_oferta FROM juegos
            WHERE precio >= ? AND activo = 1
            ORDER BY precio ASC
        """, (precio_min,))
        label = f"mas de {precio_min:.0f}\u20ac"

    juegos = cur.fetchall()

    if not juegos:
        return f"No tenemos juegos {label} en este momento."

    if len(juegos) > 10:
        juegos = random.sample(juegos, 10)
        juegos = sorted(juegos, key=lambda j: j['precio'])

    respuesta = f"Juegos {label}:\n\n"
    for j in juegos:
        precio = formatear_precio(j['precio'], j['precio_oferta'])
        respuesta += f"\u2022 {j['titulo']} \u2014 {precio}\n"

    return respuesta

# BÚSQUEDA DE MÚLTIPLES VERSIONES (sagas)

VERSION_TRIGGERS = {
    'versiones', 'version', 'todos', 'todas', 'coleccion',
    'ediciones', 'edicion', 'completos', 'completas', 'saga',
    'lista', 'listado', 'entregas',
}

def buscar_versiones_juego(mensaje_normalizado, conn):
    """
    Detecta búsquedas de múltiples versiones de una saga.
    Extrae el nombre del juego, llama a RAWG con múltiples resultados
    y muestra cada uno indicando si está disponible en catálogo.
    """
    palabras = mensaje_normalizado.split()
    if not any(p in VERSION_TRIGGERS for p in palabras):
        return None

    ruido = set(CHATBOT_CONFIG['STOPWORDS']) | VERSION_TRIGGERS | {'de', 'los', 'las', 'del', 'al', 'le', 'lo'}
    nombre_palabras = [p for p in palabras if p not in ruido and len(p) > 2]
    if not nombre_palabras:
        return None

    nombre_juego = ' '.join(nombre_palabras)
    resultados = rawg_service.buscar_multiples(nombre_juego, page_size=8)
    if not resultados:
        return None

    cur = conn.cursor()
    respuesta = f"🎮 **Versiones encontradas para '{nombre_juego}':**\n\n"
    encontrado_alguno = False

    for juego_rawg in resultados:
        titulo = juego_rawg['titulo']
        cur.execute("""
            SELECT precio, precio_oferta, activo FROM juegos
            WHERE LOWER(titulo) LIKE ?
            LIMIT 1
        """, (f'%{titulo.lower()}%',))
        en_bd = cur.fetchone()

        if en_bd and en_bd['activo'] == 1:
            precio = formatear_precio(en_bd['precio'], en_bd['precio_oferta'])
            respuesta += f"• {titulo} — {precio} ✅\n"
        else:
            respuesta += f"• {titulo} — ❌ No disponible\n"
        encontrado_alguno = True

    return respuesta if encontrado_alguno else None

#BÚSQUEDA POR FILTROS COMBINADOS (precio + plataforma/género)

def buscar_por_filtros_combinados(mensaje_normalizado, conn):
    """
    Busca juegos aplicando múltiples filtros simultáneamente:
    - Precio + Plataforma
    - Precio + Género
    - Precio + Plataforma + Género

    Devuelve None si no hay combinación válida.
    """
    rango_precio = extraer_rango_precio(mensaje_normalizado)
    if not rango_precio:
        return None  

    precio_min, precio_max, precio_label = rango_precio

    if precio_label:
        price_part = precio_label
    elif precio_min is not None and precio_max is not None:
        price_part = f"entre {precio_min:.0f}€ y {precio_max:.0f}€"
    elif precio_max is not None:
        price_part = f"hasta {precio_max:.0f}€"
    else:
        price_part = f"desde {precio_min:.0f}€"

    plataforma_detectada = None
    for palabra_usuario, nombre_bd in PLATAFORMA_MAP.items():
        if palabra_usuario in mensaje_normalizado:
            plataforma_detectada = nombre_bd
            break

    genero_detectado = None
    for palabra_usuario, nombre_bd in GENEROS_MAP.items():
        if palabra_usuario in mensaje_normalizado:
            genero_detectado = nombre_bd
            break

    if not plataforma_detectada and not genero_detectado:
        return None

    if not genero_detectado:
        tema = _extraer_tema_desconocido(mensaje_normalizado)
        if tema:
            partes = [f"de {tema}"]
            if precio_label:
                partes.append(precio_label)
            if plataforma_detectada:
                partes.append(f"para {plataforma_detectada}")
            return f"No tenemos juegos {' '.join(partes)} en nuestro catálogo.\n\nPuedo ayudarte con géneros como:\n• Acción, Aventura, RPG, Terror, Deportes\n• Plataformas, Puzzle, Estrategia, Simulación\n• Indie, Sandbox, Multijugador..."

    cur = conn.cursor()
    respuesta = ""

    if plataforma_detectada and genero_detectado:
        if precio_min is not None and precio_max is not None:
            cur.execute("""
                SELECT DISTINCT j.titulo, j.precio, j.precio_oferta
                FROM juegos j
                JOIN juegos_plataformas jp ON j.id = jp.juego_id
                JOIN plataformas p ON jp.plataforma_id = p.id
                JOIN juegos_generos jg ON j.id = jg.juego_id
                JOIN generos g ON jg.genero_id = g.id
                WHERE p.nombre = ? AND g.nombre = ?
                  AND j.precio BETWEEN ? AND ? AND j.activo = 1
                ORDER BY j.precio ASC
            """, (plataforma_detectada, genero_detectado, precio_min, precio_max))
            label = f"{price_part} de {genero_detectado.lower()} para {plataforma_detectada}"
        elif precio_max is not None:
            cur.execute("""
                SELECT DISTINCT j.titulo, j.precio, j.precio_oferta
                FROM juegos j
                JOIN juegos_plataformas jp ON j.id = jp.juego_id
                JOIN plataformas p ON jp.plataforma_id = p.id
                JOIN juegos_generos jg ON j.id = jg.juego_id
                JOIN generos g ON jg.genero_id = g.id
                WHERE p.nombre = ? AND g.nombre = ?
                  AND j.precio <= ? AND j.activo = 1
                ORDER BY j.precio ASC
            """, (plataforma_detectada, genero_detectado, precio_max))
            label = f"{price_part} de {genero_detectado.lower()} para {plataforma_detectada}"
        else:  
            cur.execute("""
                SELECT DISTINCT j.titulo, j.precio, j.precio_oferta
                FROM juegos j
                JOIN juegos_plataformas jp ON j.id = jp.juego_id
                JOIN plataformas p ON jp.plataforma_id = p.id
                JOIN juegos_generos jg ON j.id = jg.juego_id
                JOIN generos g ON jg.genero_id = g.id
                WHERE p.nombre = ? AND g.nombre = ?
                  AND j.precio >= ? AND j.activo = 1
                ORDER BY j.precio ASC
            """, (plataforma_detectada, genero_detectado, precio_min))
            label = f"{price_part} de {genero_detectado.lower()} para {plataforma_detectada}"

    elif plataforma_detectada:
        if precio_min is not None and precio_max is not None:
            cur.execute("""
                SELECT DISTINCT j.titulo, j.precio, j.precio_oferta
                FROM juegos j
                JOIN juegos_plataformas jp ON j.id = jp.juego_id
                JOIN plataformas p ON jp.plataforma_id = p.id
                WHERE p.nombre = ? AND j.precio BETWEEN ? AND ? AND j.activo = 1
                ORDER BY j.precio ASC
            """, (plataforma_detectada, precio_min, precio_max))
            label = f"{price_part} para {plataforma_detectada}"
        elif precio_max is not None:
            cur.execute("""
                SELECT DISTINCT j.titulo, j.precio, j.precio_oferta
                FROM juegos j
                JOIN juegos_plataformas jp ON j.id = jp.juego_id
                JOIN plataformas p ON jp.plataforma_id = p.id
                WHERE p.nombre = ? AND j.precio <= ? AND j.activo = 1
                ORDER BY j.precio ASC
            """, (plataforma_detectada, precio_max))
            label = f"{price_part} para {plataforma_detectada}"
        else:  
            cur.execute("""
                SELECT DISTINCT j.titulo, j.precio, j.precio_oferta
                FROM juegos j
                JOIN juegos_plataformas jp ON j.id = jp.juego_id
                JOIN plataformas p ON jp.plataforma_id = p.id
                WHERE p.nombre = ? AND j.precio >= ? AND j.activo = 1
                ORDER BY j.precio ASC
            """, (plataforma_detectada, precio_min))
            label = f"{price_part} para {plataforma_detectada}"

    else:  
        if precio_min is not None and precio_max is not None:
            cur.execute("""
                SELECT DISTINCT j.titulo, j.precio, j.precio_oferta
                FROM juegos j
                JOIN juegos_generos jg ON j.id = jg.juego_id
                JOIN generos g ON jg.genero_id = g.id
                WHERE g.nombre = ? AND j.precio BETWEEN ? AND ? AND j.activo = 1
                ORDER BY j.precio ASC
            """, (genero_detectado, precio_min, precio_max))
            label = f"de {genero_detectado.lower()} {price_part}"
        elif precio_max is not None:
            cur.execute("""
                SELECT DISTINCT j.titulo, j.precio, j.precio_oferta
                FROM juegos j
                JOIN juegos_generos jg ON j.id = jg.juego_id
                JOIN generos g ON jg.genero_id = g.id
                WHERE g.nombre = ? AND j.precio <= ? AND j.activo = 1
                ORDER BY j.precio ASC
            """, (genero_detectado, precio_max))
            label = f"de {genero_detectado.lower()} {price_part}"
        else:  
            cur.execute("""
                SELECT DISTINCT j.titulo, j.precio, j.precio_oferta
                FROM juegos j
                JOIN juegos_generos jg ON j.id = jg.juego_id
                JOIN generos g ON jg.genero_id = g.id
                WHERE g.nombre = ? AND j.precio >= ? AND j.activo = 1
                ORDER BY j.precio ASC
            """, (genero_detectado, precio_min))
            label = f"de {genero_detectado.lower()} {price_part}"

    juegos = cur.fetchall()

    if not juegos:
        return f"No tenemos juegos {label} en este momento."

    if len(juegos) > 10:
        juegos = random.sample(juegos, 10)
        juegos = sorted(juegos, key=lambda j: j['precio'])

    respuesta = f"🎮 **Juegos {label}:**\n\n"
    for j in juegos:
        precio = formatear_precio(j['precio'], j['precio_oferta'])
        respuesta += f"• {j['titulo']} — {precio}\n"

    return respuesta

# OFERTAS Y NOVEDADES

OFERTA_KEYWORDS = {'oferta', 'ofertas', 'descuento', 'descuentos', 'rebaja', 'rebajas', 'promocion', 'promociones'}
NOVEDAD_KEYWORDS = {'novedad', 'novedades', 'nuevo', 'nuevos', 'nueva', 'nuevas', 'reciente', 'recientes',
                    'lanzamiento', 'lanzamientos', 'estreno', 'estrenos', 'ultimo', 'ultimos', 'ultima', 'ultimas'}

def _detectar_plataforma_genero(msg):
    plataforma = next((v for k, v in PLATAFORMA_MAP.items() if k in msg), None)
    genero = next((v for k, v in GENEROS_MAP.items() if k in msg), None)
    return plataforma, genero

def _extraer_tema_desconocido(msg):
    """Devuelve la primera palabra de contenido del mensaje que no es plataforma, género, ni stopword.
    Se usa para detectar géneros/actividades desconocidas como 'baile', 'cocina', etc."""
    stopwords = set(CHATBOT_CONFIG['STOPWORDS']) | {
        'juego', 'juegos', 'para', 'de', 'en', 'sobre', 'con', 'un', 'una',
        'euros', 'euro', 'precio', 'barato', 'baratos', 'gratis', 'gratuito',
        'oferta', 'ofertas', 'descuento', 'rebaja', 'novedad', 'novedades',
        'menos', 'mas', 'hasta', 'entre', 'maximo', 'minimo', 'desde',
    }
    conocidas = set(PLATAFORMA_MAP.keys()) | set(GENEROS_MAP.keys())
    for palabra in msg.split():
        if palabra not in stopwords and palabra not in conocidas and len(palabra) > 3 and palabra.isalpha():
            return palabra
    return None

def buscar_en_oferta(mensaje_normalizado, conn):
    palabras = set(mensaje_normalizado.split())
    if not (palabras & OFERTA_KEYWORDS):
        return None

    cur = conn.cursor()
    plataforma, genero = _detectar_plataforma_genero(mensaje_normalizado)

    if plataforma and genero:
        cur.execute("""
            SELECT DISTINCT j.titulo, j.precio, j.precio_oferta
            FROM juegos j
            JOIN juegos_plataformas jp ON j.id = jp.juego_id
            JOIN plataformas p ON jp.plataforma_id = p.id
            JOIN juegos_generos jg ON j.id = jg.juego_id
            JOIN generos g ON jg.genero_id = g.id
            WHERE p.nombre = ? AND g.nombre = ?
              AND j.precio_oferta IS NOT NULL AND j.activo = 1
            ORDER BY j.precio_oferta ASC
        """, (plataforma, genero))
        label = f"de {genero.lower()} en oferta para {plataforma}"
    elif plataforma:
        cur.execute("""
            SELECT DISTINCT j.titulo, j.precio, j.precio_oferta
            FROM juegos j
            JOIN juegos_plataformas jp ON j.id = jp.juego_id
            JOIN plataformas p ON jp.plataforma_id = p.id
            WHERE p.nombre = ? AND j.precio_oferta IS NOT NULL AND j.activo = 1
            ORDER BY j.precio_oferta ASC
        """, (plataforma,))
        label = f"en oferta para {plataforma}"
    elif genero:
        cur.execute("""
            SELECT DISTINCT j.titulo, j.precio, j.precio_oferta
            FROM juegos j
            JOIN juegos_generos jg ON j.id = jg.juego_id
            JOIN generos g ON jg.genero_id = g.id
            WHERE g.nombre = ? AND j.precio_oferta IS NOT NULL AND j.activo = 1
            ORDER BY j.precio_oferta ASC
        """, (genero,))
        label = f"de {genero.lower()} en oferta"
    else:
        cur.execute("""
            SELECT titulo, precio, precio_oferta FROM juegos
            WHERE precio_oferta IS NOT NULL AND activo = 1
            ORDER BY precio_oferta ASC
        """)
        label = "en oferta"

    juegos = cur.fetchall()
    if not juegos:
        return f"No tenemos juegos {label} en este momento."

    if len(juegos) > 10:
        juegos = random.sample(juegos, 10)
        juegos = sorted(juegos, key=lambda j: j['precio_oferta'])

    respuesta = f"🏷️ **Juegos {label}:**\n\n"
    for j in juegos:
        precio = formatear_precio(j['precio'], j['precio_oferta'])
        respuesta += f"• {j['titulo']} — {precio}\n"
    return respuesta


def buscar_novedades(mensaje_normalizado, conn):
    palabras = set(mensaje_normalizado.split())
    if not (palabras & NOVEDAD_KEYWORDS):
        return None

    cur = conn.cursor()
    plataforma, genero = _detectar_plataforma_genero(mensaje_normalizado)

    if plataforma and genero:
        cur.execute("""
            SELECT DISTINCT j.titulo, j.precio, j.precio_oferta
            FROM juegos j
            JOIN juegos_plataformas jp ON j.id = jp.juego_id
            JOIN plataformas p ON jp.plataforma_id = p.id
            JOIN juegos_generos jg ON j.id = jg.juego_id
            JOIN generos g ON jg.genero_id = g.id
            WHERE p.nombre = ? AND g.nombre = ? AND j.activo = 1
            ORDER BY j.fecha_lanzamiento DESC
            LIMIT 10
        """, (plataforma, genero))
        label = f"novedades de {genero.lower()} para {plataforma}"
    elif plataforma:
        cur.execute("""
            SELECT DISTINCT j.titulo, j.precio, j.precio_oferta
            FROM juegos j
            JOIN juegos_plataformas jp ON j.id = jp.juego_id
            JOIN plataformas p ON jp.plataforma_id = p.id
            WHERE p.nombre = ? AND j.activo = 1
            ORDER BY j.fecha_lanzamiento DESC
            LIMIT 10
        """, (plataforma,))
        label = f"novedades para {plataforma}"
    elif genero:
        cur.execute("""
            SELECT DISTINCT j.titulo, j.precio, j.precio_oferta
            FROM juegos j
            JOIN juegos_generos jg ON j.id = jg.juego_id
            JOIN generos g ON jg.genero_id = g.id
            WHERE g.nombre = ? AND j.activo = 1
            ORDER BY j.fecha_lanzamiento DESC
            LIMIT 10
        """, (genero,))
        label = f"novedades de {genero.lower()}"
    else:
        cur.execute("""
            SELECT titulo, precio, precio_oferta FROM juegos
            WHERE activo = 1
            ORDER BY fecha_lanzamiento DESC
            LIMIT 10
        """)
        label = "novedades"

    juegos = cur.fetchall()
    if not juegos:
        return f"No tenemos {label} en este momento."

    respuesta = f"🆕 **Últimas {label}:**\n\n"
    for j in juegos:
        precio = formatear_precio(j['precio'], j['precio_oferta'])
        respuesta += f"• {j['titulo']} — {precio}\n"
    return respuesta


# BÚSQUEDA DE LISTA DE CATEGORÍAS

CATEGORIA_TRIGGERS = {
    'categoria', 'categorias', 'genero', 'generos', 'tipo', 'tipos',
    'estilo', 'estilos', 'lista', 'listado'
}

def buscar_lista_categorias(mensaje_normalizado, conn):
    """
    Detecta cuando el usuario pregunta por lista de categorías/géneros disponibles.
    Triggers: "categoría", "géneros", "tipos", "estilos", "lista"
    Devuelve todos los géneros disponibles con juegos activos.
    """
    palabras = set(mensaje_normalizado.split())

    tiene_trigger = bool(palabras & CATEGORIA_TRIGGERS)

    if not tiene_trigger:
        return None

    cur = conn.cursor()
    cur.execute("""
        SELECT DISTINCT g.nombre
        FROM generos g
        JOIN juegos_generos jg ON g.id = jg.genero_id
        JOIN juegos j ON jg.juego_id = j.id
        WHERE j.activo = 1
        ORDER BY g.nombre
    """)

    generos = [r['nombre'] for r in cur.fetchall()]

    if not generos:
        return "No tenemos categorías disponibles en este momento."

    lista = '\n'.join(f'• {g}' for g in generos)
    return f"🎮 **Categorías disponibles:**\n\n{lista}"

#  BÚSQUEDA POR PLATAFORMA O GÉNERO

def buscar_por_plataforma_o_genero(mensaje_normalizado, conn, offset=0):
    """
    Detecta si el usuario pregunta por plataforma o género.
    Devuelve tupla (respuesta, paginacion).
    """
    cur = conn.cursor()

    palabras_mensaje = set(mensaje_normalizado.split())
    for kw, nombre in PLATAFORMAS_SIN_JUEGOS.items():
        if kw in palabras_mensaje:
            respuesta = (f"No tenemos juegos para {nombre}.\n\n"
                    f"Actualmente tenemos juegos para:\n"
                    f"\u2022 PlayStation 5\n"
                    f"\u2022 Xbox Series X\n"
                    f"\u2022 Nintendo Switch\n"
                    f"\u2022 PC")
            return respuesta, {'activo': False}

    plataforma_detectada = None
    for palabra_usuario, nombre_bd in PLATAFORMA_MAP.items():
        if palabra_usuario in mensaje_normalizado:
            plataforma_detectada = nombre_bd
            break

    genero_detectado = None
    for palabra_usuario, nombre_bd in GENEROS_MAP.items():
        if palabra_usuario in mensaje_normalizado:
            genero_detectado = nombre_bd
            break

    if plataforma_detectada and genero_detectado:
        return None, None

    if plataforma_detectada:
        tema = _extraer_tema_desconocido(mensaje_normalizado)
        if tema:
            return (f"No tenemos juegos de {tema} para {plataforma_detectada}.\n\n"
                    f"Puedo ayudarte con géneros como:\n"
                    f"• Acción, Aventura, RPG, Terror, Deportes\n"
                    f"• Plataformas, Puzzle, Estrategia, Simulación\n"
                    f"• Indie, Sandbox, Multijugador..."), {'activo': False}
        return buscar_por_plataforma(plataforma_detectada, conn, offset)

    if genero_detectado:
        return buscar_por_genero(genero_detectado, conn, offset)

    match_tema = re.search(r'\bjuegos?\s+(?:de|para|sobre)\s+([a-záéíóúñ]+)', mensaje_normalizado)
    if match_tema:
        tema = match_tema.group(1)
        return (f"No tenemos juegos de {tema} en nuestro catálogo.\n\n"
                f"Puedo ayudarte con géneros como:\n"
                f"• Acción, Aventura, RPG, Terror, Deportes\n"
                f"• Plataformas, Puzzle, Estrategia, Simulación\n"
                f"• Indie, Sandbox, Multijugador..."), {'activo': False}

    if ' para ' in mensaje_normalizado:
        return (f"No he reconocido esa plataforma.\n\n"
                f"Las plataformas disponibles son:\n"
                f"• PlayStation 5 (ps5, playstation)\n"
                f"• Xbox Series X (xbox)\n"
                f"• Nintendo Switch (switch, nintendo)\n"
                f"• PC (pc, windows, steam)"), {'activo': False}

    return None, None

def buscar_por_plataforma(plataforma, conn, offset=0):
    """
    Busca hasta 5 juegos disponibles en una plataforma específica.
    Soporta paginación con offset.
    Devuelve (respuesta, paginacion) donde paginacion es dict con metadata.
    """
    cur = conn.cursor()

    cur.execute("""
        SELECT COUNT(*) as total
        FROM juegos j
        JOIN juegos_plataformas jp ON j.id = jp.juego_id
        JOIN plataformas p ON jp.plataforma_id = p.id
        WHERE p.nombre = ? AND j.activo = 1
    """, (plataforma,))
    total = cur.fetchone()['total']

    cur.execute("""
        SELECT DISTINCT j.titulo, j.precio, j.precio_oferta
        FROM juegos j
        JOIN juegos_plataformas jp ON j.id = jp.juego_id
        JOIN plataformas p ON jp.plataforma_id = p.id
        WHERE p.nombre = ? AND j.activo = 1
        ORDER BY j.titulo
        LIMIT 5 OFFSET ?
    """, (plataforma, offset))

    juegos = cur.fetchall()

    paginacion = {'activo': False}
    if not juegos:
        if offset > 0:
            return "No hay más juegos disponibles.", paginacion
        return None, None

    respuesta = f"🎮 **Juegos disponibles para {plataforma}:**\n\n"
    for j in juegos:
        precio = formatear_precio(j['precio'], j['precio_oferta'])
        respuesta += f"• {j['titulo']} - {precio}\n"

    if offset + 5 < total:
        paginacion = {
            'activo': True,
            'offset_siguiente': offset + 5,
            'tipo': 'plataforma',
            'valor': plataforma
        }

    return respuesta, paginacion

def buscar_por_genero(genero, conn, offset=0):
    """
    Busca hasta 5 juegos de un género específico.
    Soporta paginación con offset.
    Devuelve (respuesta, paginacion) donde paginacion es dict con metadata.
    """
    cur = conn.cursor()

    cur.execute("""
        SELECT COUNT(*) as total
        FROM juegos j
        JOIN juegos_generos jg ON j.id = jg.juego_id
        JOIN generos g ON jg.genero_id = g.id
        WHERE g.nombre = ? AND j.activo = 1
    """, (genero,))
    total = cur.fetchone()['total']

    paginacion = {'activo': False}
    if total == 0:
        cur.execute("""
            SELECT DISTINCT g.nombre
            FROM generos g
            JOIN juegos_generos jg ON g.id = jg.genero_id
            JOIN juegos j ON jg.juego_id = j.id
            WHERE j.activo = 1
            ORDER BY g.nombre
        """)
        disponibles = [r['nombre'] for r in cur.fetchall()]
        lista = '\n'.join(f'• {g}' for g in disponibles)
        return (f"No tenemos juegos de {genero} en catálogo.\n\n"
                f"Géneros que sí tenemos:\n\n{lista}"), paginacion

    if offset > 0 and offset >= total:
        return "No hay más juegos disponibles.", paginacion

    cur.execute("""
        SELECT DISTINCT j.titulo, j.precio, j.precio_oferta
        FROM juegos j
        JOIN juegos_generos jg ON j.id = jg.juego_id
        JOIN generos g ON jg.genero_id = g.id
        WHERE g.nombre = ? AND j.activo = 1
        ORDER BY j.titulo
        LIMIT 5 OFFSET ?
    """, (genero, offset))

    juegos = cur.fetchall()

    respuesta = f"🎮 **Juegos de {genero}:**\n\n"
    for j in juegos:
        precio = formatear_precio(j['precio'], j['precio_oferta'])
        respuesta += f"• {j['titulo']} - {precio}\n"

    if offset + 5 < total:
        paginacion = {
            'activo': True,
            'offset_siguiente': offset + 5,
            'tipo': 'genero',
            'valor': genero
        }

    return respuesta, paginacion

def buscar_por_plataforma_y_genero(mensaje_normalizado, conn, offset=0):
    """
    Busca juegos que sean de una plataforma específica Y un género específico.
    Se llama cuando se detectan ambos en el mensaje.
    Soporta paginación con offset.
    Devuelve (respuesta, paginacion) donde paginacion es dict con metadata.
    """
    cur = conn.cursor()

    plataforma_detectada = None
    for palabra_usuario, nombre_bd in PLATAFORMA_MAP.items():
        if palabra_usuario in mensaje_normalizado:
            plataforma_detectada = nombre_bd
            break

    genero_detectado = None
    for palabra_usuario, nombre_bd in GENEROS_MAP.items():
        if palabra_usuario in mensaje_normalizado:
            genero_detectado = nombre_bd
            break

    if not (plataforma_detectada and genero_detectado):
        return None, None

    cur.execute("""
        SELECT COUNT(*) as total
        FROM juegos j
        JOIN juegos_plataformas jp ON j.id = jp.juego_id
        JOIN plataformas p ON jp.plataforma_id = p.id
        JOIN juegos_generos jg ON j.id = jg.juego_id
        JOIN generos g ON jg.genero_id = g.id
        WHERE p.nombre = ? AND g.nombre = ? AND j.activo = 1
    """, (plataforma_detectada, genero_detectado))
    total = cur.fetchone()['total']

    paginacion = {'activo': False}
    if total == 0:
        return f"No tenemos juegos de {genero_detectado.lower()} para {plataforma_detectada} en este momento.", paginacion

    if offset > 0 and offset >= total:
        return "No hay más juegos disponibles.", paginacion

    cur.execute("""
        SELECT DISTINCT j.titulo, j.precio, j.precio_oferta
        FROM juegos j
        JOIN juegos_plataformas jp ON j.id = jp.juego_id
        JOIN plataformas p ON jp.plataforma_id = p.id
        JOIN juegos_generos jg ON j.id = jg.juego_id
        JOIN generos g ON jg.genero_id = g.id
        WHERE p.nombre = ? AND g.nombre = ? AND j.activo = 1
        ORDER BY j.titulo
        LIMIT 5 OFFSET ?
    """, (plataforma_detectada, genero_detectado, offset))

    juegos = cur.fetchall()

    respuesta = f"🎮 **Juegos de {genero_detectado.lower()} para {plataforma_detectada}:**\n\n"
    for j in juegos:
        precio = formatear_precio(j['precio'], j['precio_oferta'])
        respuesta += f"• {j['titulo']} - {precio}\n"

    if offset + 5 < total:
        paginacion = {
            'activo': True,
            'offset_siguiente': offset + 5,
            'tipo': 'plataforma_genero',
            'plataforma': plataforma_detectada,
            'genero': genero_detectado
        }

    return respuesta, paginacion

# RECOMENDACIONES POR CATEGORÍA

RECOMENDACION_TRIGGERS = {
    'recomienda', 'recomiendame', 'recomendame', 'recomendacion', 'recomendaciones',
    'sugiere', 'sugiereme', 'sugerencia', 'sugerencias', 'recomiendas',
    'que jugar', 'que deberia', 'que podria',
}

def recomendar_juegos(mensaje_normalizado, conn):
    """
    Si hay género/plataforma en el mensaje → recomienda juegos de esa categoría.
    Si no hay categoría → recomienda un juego de 5 géneros distintos al azar.
    """
    palabras = set(mensaje_normalizado.split())
    tiene_trigger = (
        palabras & RECOMENDACION_TRIGGERS
        or 'recomiend' in mensaje_normalizado
        or 'sugier' in mensaje_normalizado
        or 'suger' in mensaje_normalizado
    )
    if not tiene_trigger:
        return None

    cur = conn.cursor()

    genero_pedido = None
    for kw, nombre_genero in GENEROS_MAP.items():
        if kw in mensaje_normalizado:
            genero_pedido = nombre_genero
            break

    plataforma_pedida = None
    if not genero_pedido:
        for kw, nombre_plat in PLATAFORMA_MAP.items():
            if kw in mensaje_normalizado:
                plataforma_pedida = nombre_plat
                break

    if genero_pedido:
        cur.execute("""
            SELECT j.titulo, j.precio, j.precio_oferta
            FROM juegos j
            JOIN juegos_generos jg ON j.id = jg.juego_id
            JOIN generos g ON jg.genero_id = g.id
            WHERE g.nombre = ? AND j.activo = 1
            ORDER BY RANDOM()
            LIMIT 5
        """, (genero_pedido,))
        juegos = cur.fetchall()
        if not juegos:
            return None
        respuesta = f"🎮 **Recomendaciones de {genero_pedido}:**\n\n"
        for j in juegos:
            precio = formatear_precio(j['precio'], j['precio_oferta'])
            respuesta += f"• {j['titulo']} — {precio}\n"
        respuesta += "\n¿Te interesa alguno? ¡Pregúntame más sobre él!"
        return respuesta

    if plataforma_pedida:
        cur.execute("""
            SELECT j.titulo, j.precio, j.precio_oferta
            FROM juegos j
            JOIN juegos_plataformas jp ON j.id = jp.juego_id
            JOIN plataformas p ON jp.plataforma_id = p.id
            WHERE p.nombre = ? AND j.activo = 1
            ORDER BY RANDOM()
            LIMIT 5
        """, (plataforma_pedida,))
        juegos = cur.fetchall()
        if not juegos:
            return None
        respuesta = f"🎮 **Recomendaciones para {plataforma_pedida}:**\n\n"
        for j in juegos:
            precio = formatear_precio(j['precio'], j['precio_oferta'])
            respuesta += f"• {j['titulo']} — {precio}\n"
        respuesta += "\n¿Te interesa alguno? ¡Pregúntame más sobre él!"
        return respuesta

    cur.execute("""
        SELECT DISTINCT g.nombre
        FROM generos g
        JOIN juegos_generos jg ON g.id = jg.genero_id
        JOIN juegos j ON jg.juego_id = j.id
        WHERE j.activo = 1
        ORDER BY g.nombre
    """)
    generos = [row['nombre'] for row in cur.fetchall()]
    if not generos:
        return None

    seleccionados = random.sample(generos, min(5, len(generos)))
    respuesta = "🎮 **Aquí tienes algunas recomendaciones de distintas categorías:**\n\n"
    for genero in seleccionados:
        cur.execute("""
            SELECT j.titulo, j.precio, j.precio_oferta
            FROM juegos j
            JOIN juegos_generos jg ON j.id = jg.juego_id
            JOIN generos g ON jg.genero_id = g.id
            WHERE g.nombre = ? AND j.activo = 1
            ORDER BY RANDOM()
            LIMIT 1
        """, (genero,))
        juego = cur.fetchone()
        if juego:
            precio = formatear_precio(juego['precio'], juego['precio_oferta'])
            respuesta += f"• {genero}: {juego['titulo']} — {precio}\n"

    respuesta += "\n¿Te interesa alguno en particular? ¡Pregúntame más sobre él!"
    return respuesta


# FLUJO DE CONVERSACIÓN

def obtener_respuesta_chatbot(mensaje, estado_actual, offset=0):
    """
    Orquesta los 4 niveles de búsqueda en orden y devuelve (respuesta, estado, paginacion).
    Orden: 1) Juego específico 2) Plataforma/Género 3) RAWG (API externa) 4) Reglas
    También gestiona el flujo de conversación mediante estados.
    offset: número de resultados a saltar (para paginación).
    """
    conn = obtener_conexion_bd()

    mensaje_normalizado = normalizar(mensaje)

    palabras_mensaje = set(mensaje_normalizado.split())
    for kw, nombre in PLATAFORMAS_SIN_JUEGOS.items():
        if kw in palabras_mensaje:
            respuesta = (f"No tenemos juegos para {nombre}.\n\n"
                    f"Actualmente tenemos juegos para:\n"
                    f"• PlayStation 5\n"
                    f"• Xbox Series X\n"
                    f"• Nintendo Switch\n"
                    f"• PC")
            conn.close()
            return respuesta, 'menu', {'activo': False}

    respuesta = buscar_en_oferta(mensaje_normalizado, conn)
    if respuesta:
        conn.close()
        return respuesta, 'menu', {'activo': False}

    respuesta = buscar_novedades(mensaje_normalizado, conn)
    if respuesta:
        conn.close()
        return respuesta, 'menu', {'activo': False}

    respuesta = buscar_por_filtros_combinados(mensaje_normalizado, conn)
    if respuesta:
        conn.close()
        return respuesta, 'menu', {'activo': False}

    respuesta = buscar_por_precio(mensaje_normalizado, conn)
    if respuesta:
        conn.close()
        return respuesta, 'menu', {'activo': False}

    respuesta = recomendar_juegos(mensaje_normalizado, conn)
    if respuesta:
        conn.close()
        return respuesta, 'menu', {'activo': False}

    respuesta = buscar_lista_categorias(mensaje_normalizado, conn)
    if respuesta:
        conn.close()
        return respuesta, 'menu', {'activo': False}

    respuesta = buscar_versiones_juego(mensaje_normalizado, conn)
    if respuesta:
        conn.close()
        return respuesta, 'menu', {'activo': False}

    respuesta = buscar_juego_concreto(mensaje_normalizado, conn)
    if respuesta:
        conn.close()
        return respuesta, 'juego_encontrado', {'activo': False}

    respuesta, paginacion = buscar_por_plataforma_y_genero(mensaje_normalizado, conn, offset)
    if respuesta:
        conn.close()
        return respuesta, 'menu', paginacion

    respuesta, paginacion = buscar_por_plataforma_o_genero(mensaje_normalizado, conn, offset)
    if respuesta:
        conn.close()
        return respuesta, 'menu', paginacion

    respuesta = buscar_por_modo(mensaje_normalizado, conn)
    if respuesta:
        conn.close()
        return respuesta, 'menu', {'activo': False}

    palabras = [p for p in mensaje_normalizado.split() if p not in CHATBOT_CONFIG['STOPWORDS']]

    palabras_reglas = ['recomienda', 'recomiendame', 'recomendame', 'recomendacion', 'recomendaciones', 'sugiere', 'sugiereme', 'sugerencia', 'baratos', 'economicos', 'gratis', 'gratuitos', 'multijugador', 'coop', 'horror', 'terror', 'miedo', 'rpg', 'rol', 'roleplay', 'shooter', 'fps', 'disparos', 'tiros', 'deporte', 'deportes', 'futbol', 'baloncesto', 'lucha', 'pelea', 'peleas', 'fighting', 'combate', 'sandbox', 'construccion', 'aventura', 'aventuras', 'accion', 'estrategia', 'tactica', 'casual', 'relajante', 'survival', 'supervivencia', 'royale', 'simulacion', 'simulador', 'puzzle', 'rompecabezas', 'plataforma', 'plataformas', 'roguelike', 'roguelite', 'rogue', 'metroidvania', 'cartas', 'mundo abierto', 'open world', 'battle royale', 'hack and slash', 'open', 'world', 'portatil', 'nintendo', 'hola', 'holi', 'hey', 'saludos', 'buenas', 'buenos', 'adios', 'despedida', 'hasta', 'ciao', 'tal', 'onda', 'ey', 'ei', 'ola', 'baile', 'danza', 'novedades', 'nuevos', 'recientes', 'lanzamientos', 'estreno', 'lanzamiento', 'nuevo', 'novedad', 'ultimos', 'ultimo', 'reciente', 'oferta', 'ofertas', 'promocion', 'promociones', 'descuento', 'descuentos', 'rebaja', 'rebajas', 'sigilo', 'stealth', 'anime', 'manga', 'soulslike', 'souls', 'zombis', 'zombies', 'cozy', 'acogedor', 'gestion', 'moba', 'mmorpg', 'mmo', 'tirador', 'exploracion', 'pvp', 'jcj', 'rts', '4x', 'tower defense', 'defensa de torres', 'city builder', 'ps3', 'ps4', 'ps2', 'ps1', 'psx', 'psp', 'vita', 'xbox one', 'xbox 360', 'wii', '3ds', 'gameboy', 'gba', 'android', 'ios', 'movil', 'vr', 'dreamcast', 'sega', 'euros', 'euro', 'presupuesto', 'barato', 'online', 'linea', 'solitario', 'single', 'offline', 'tipos', 'categorias', 'categoria', 'generos', 'genero', 'estilos', 'estilo', 'clases', 'listado', 'lista',
                       'goty', 'premiado', 'famoso', 'mejor', 'top',                          
                       'ninos', 'familia', 'familiar', 'infantil', 'nino', 'pequenos',        
                       'indie', 'independente', 'independiente', 'independientes',             
                       'historia', 'narrativa', 'trama', 'argumento', 'guion',                
                       'ayuda', 'soporte', 'contacto', 'problema', 'asistencia',          
                       'clasico', 'antiguo', 'vintage', 'clasicos',                         
                       'racing', 'conduccion', 'conducir', 'coches',                          
                       'bestseller', 'popular', 'trending', 'vendidos', 'recomendados',       
                       'regalo', 'regalos', 'regalar', 'sorpresa', 'presente',               
                       'requisitos', 'especificaciones', 'minimos', 'hardware', 'configuracion',  
                       'duda', 'pregunta', 'dudas', 'confuso', 'entiendo',                  
                       'puntuacion', 'valoracion', 'metacritic', 'review', 'critica', 'analisis', 'score'] 
    tiene_palabra_regla = any(palabra in mensaje_normalizado for palabra in palabras_reglas)

    if palabras and len(palabras) <= 2 and not tiene_palabra_regla:  
        juego_rawg = rawg_service.buscar_juego(mensaje)
        if juego_rawg:
            respuesta = rawg_service.formatear_respuesta_rawg(juego_rawg)
            conn.close()
            return respuesta, 'menu', {'activo': False}

    respuesta = buscar_en_reglas(mensaje_normalizado, conn)
    if respuesta:
        conn.close()
        return respuesta, 'menu', {'activo': False}

    respuesta_default = (
        "❌ No he encontrado ese juego en nuestro catálogo. "
        "Puedes preguntarme por:\n"
        "• Otros juegos específicos\n"
        "• Una plataforma (PS5, Xbox, Switch, PC)\n"
        "• Un género (RPG, acción, horror, deportes...)\n"
        "• Juegos baratos, gratis, multijugador, etc."
    )

    conn.close()
    return respuesta_default, 'menu', {'activo': False}

def guardar_en_historial(usuario_id, mensaje_usuario, respuesta_bot):
    """
    Guarda la conversación en la tabla 'historial_conversacion' para análisis posterior.
    """
    conn = obtener_conexion_bd()
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO historial_conversacion (sesion_id, mensaje_usuario, respuesta_bot, fecha)
        VALUES (?, ?, ?, ?)
    """, (usuario_id, mensaje_usuario, respuesta_bot, datetime.now()))

    conn.commit()
    conn.close()

# ENDPOINT: POST /chat

@app.route('/api/chat', methods=['POST'])
def chat():
    """
    Endpoint principal del chatbot.
    Recibe: {"mensaje": "..."}
    Devuelve: {"respuesta": "..."}
    """
    try:
        inicializar_sesion()

        data = request.get_json()
        if not data or 'mensaje' not in data:
            return jsonify({'error': 'Falta el campo "mensaje"'}), 400

        mensaje_usuario = data['mensaje'].strip()
        offset = data.get('offset', 0)

        if not mensaje_usuario:
            return jsonify({'error': 'El mensaje no puede estar vacío'}), 400

        if session.get('estado') == 'inicio':
            session['estado'] = 'menu'
            session.modified = True
            respuesta = (
                "¡Hola! 👋 Bienvenido a la tienda de videojuegos.\n\n"
                "Soy tu asistente chatbot. Puedo ayudarte a:\n"
                "• 🎮 Buscar un juego específico\n"
                "• 💰 Mostrar precios y ofertas\n"
                "• 🖥️  Listar juegos por plataforma (PS5, Xbox, Switch, PC)\n"
                "• 🏷️  Listar juegos por género (RPG, acción, horror...)\n"
                "• 📋 Recomendarte juegos\n\n"
                "¿En qué puedo ayudarte?"
            )
            paginacion = {'activo': False}
        else:
            respuesta, nuevo_estado, paginacion = obtener_respuesta_chatbot(mensaje_usuario, session.get('estado'), offset=offset)
            session['estado'] = nuevo_estado
            session.modified = True

        guardar_en_historial(session['usuario_id'], mensaje_usuario, respuesta)

        response_data = {'respuesta': respuesta}
        if paginacion and paginacion.get('activo'):
            response_data['paginacion'] = paginacion
        return jsonify(response_data)

    except Exception as e:
        print(f"Error en /chat: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': 'Error interno del servidor'}), 500


# RUTAS ADICIONALES (OPCIONALES)

@app.route('/health', methods=['GET'])
def health():
    """
    Endpoint de salud: verifica que la aplicación está funcionando.
    """
    return jsonify({'status': 'OK', 'mensaje': 'Chatbot funcionando correctamente'})

@app.route('/')
def index():
    """Sirve el archivo index.html"""
    return send_from_directory('frontend', 'index.html')

@app.route('/css/<path:filename>')
def serve_css(filename):
    """Sirve archivos CSS"""
    return send_from_directory('frontend/css', filename)

@app.route('/js/<path:filename>')
def serve_js(filename):
    """Sirve archivos JavaScript"""
    return send_from_directory('frontend/js', filename)

@app.route('/img/<path:filename>')
def serve_img(filename):
    """Sirve imágenes"""
    return send_from_directory('frontend/img', filename)

# INICIALIZACIÓN AL ARRANCAR

def init_db_if_needed():
    """
    Inicializa la BD si no existe.
    Se ejecuta automáticamente al arrancar la app.
    """
    if not os.path.exists(DB_PATH):
        print("Base de datos no encontrada. Ejecutando init_db.py...")
        os.system('python init_db.py')

with app.app_context():
    init_db_if_needed()


if __name__ == '__main__':
    host = FLASK_CONFIG['HOST']
    port = FLASK_CONFIG['PORT']
    debug = FLASK_CONFIG['DEBUG']

    
    print(f"Servidor: http://{host}:{port}")
    

    app.run(host=host, port=port, debug=debug)
