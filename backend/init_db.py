import sqlite3
import os
from pathlib import Path

# Ruta base del proyecto
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_DIR = os.path.join(BASE_DIR, 'database')

# Crear carpeta database si no existe
Path(DB_DIR).mkdir(exist_ok=True)

# Ruta de la BD
DB_PATH = os.path.join(DB_DIR, 'tienda_juegos.db')

def init_db():
    """
    Inicializa la base de datos: crea tablas e inserta plataformas base.
    """
    # Conectar (crea el archivo si no existe)
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    #  TABLA: DESARROLLADORES 
    cur.execute('''
        CREATE TABLE IF NOT EXISTS desarrolladores (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL UNIQUE,
            pais TEXT,
            sitio_web TEXT
        )
    ''')

    #  TABLA: GENEROS 
    cur.execute('''
        CREATE TABLE IF NOT EXISTS generos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL UNIQUE
        )
    ''')

    #  TABLA: PLATAFORMAS 
    cur.execute('''
        CREATE TABLE IF NOT EXISTS plataformas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL UNIQUE
        )
    ''')

    cur.execute('''
        CREATE TABLE IF NOT EXISTS juegos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            titulo TEXT NOT NULL UNIQUE,
            descripcion TEXT,
            desarrollador_id INTEGER,
            fecha_lanzamiento DATE,
            precio REAL,
            precio_oferta REAL,
            clasificacion_edad TEXT,
            activo INTEGER DEFAULT 1,
            tipo_jugador TEXT,
            FOREIGN KEY (desarrollador_id) REFERENCES desarrolladores(id)
        )
    ''')

    # ==================== TABLA: JUEGOS_GENEROS ====================
    cur.execute('''
        CREATE TABLE IF NOT EXISTS juegos_generos (
            juego_id INTEGER,
            genero_id INTEGER,
            FOREIGN KEY (juego_id) REFERENCES juegos(id),
            FOREIGN KEY (genero_id) REFERENCES generos(id),
            PRIMARY KEY (juego_id, genero_id)
        )
    ''')

    #  TABLA: JUEGOS_PLATAFORMAS 
    cur.execute('''
        CREATE TABLE IF NOT EXISTS juegos_plataformas (
            juego_id INTEGER,
            plataforma_id INTEGER,
            FOREIGN KEY (juego_id) REFERENCES juegos(id),
            FOREIGN KEY (plataforma_id) REFERENCES plataformas(id),
            PRIMARY KEY (juego_id, plataforma_id)
        )
    ''')

    #  TABLA: CHATBOT_REGLAS 
    cur.execute('''
        CREATE TABLE IF NOT EXISTS chatbot_reglas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            palabras_clave TEXT NOT NULL,
            respuesta TEXT NOT NULL,
            prioridad INTEGER DEFAULT 1,
            activo INTEGER DEFAULT 1
        )
    ''')

    #  TABLA: HISTORIAL_CONVERSACION 
    cur.execute('''
        CREATE TABLE IF NOT EXISTS historial_conversacion (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sesion_id TEXT NOT NULL,
            mensaje_usuario TEXT NOT NULL,
            respuesta_bot TEXT NOT NULL,
            fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # ==================== INSERTAR PLATAFORMAS BASE ====================
    # IMPORTANTE: Se insertan primero las plataformas base para que populate_db.py
    # pueda hacer referencia a ellas sin fallos silenciosos
    plataformas_base = ['PC', 'PlayStation 5', 'Xbox Series X', 'Nintendo Switch']

    for plat in plataformas_base:
        cur.execute(
            "INSERT OR IGNORE INTO plataformas (nombre) VALUES (?)",
            (plat,)
        )


    # Guardar cambios
    conn.commit()
    conn.close()

    print("\nBase de datos inicializada correctamente en: " + DB_PATH)

if __name__ == '__main__':
    init_db()
