# Chatbot - Tienda de Videojuegos


Bienvenido a nuestro chatbot.

## Descripción del Proyecto

### **Flask API**
Hemos utilizado **Flask Api** para crear una **API RESTful** que maneja las solicitudes de los usuarios.

### **Sistema de Reglas**
Hemos implementado un endpoint que recibe las preguntas de los usuarios y devuelve respuestas generadas a través de **reglas**, ya que con ChatterBot se nos complicó y vimos más sencillo y efectivo hacerlo con reglas.

### **Base de Datos - SQLite**
La base de datos la hicimos con **SQLite**, donde almacenamos las preguntas y respuestas para mejorar la experiencia del usuario a lo largo del tiempo. También incorporamos muchas reglas y elementos que no tenemos para hacer comparaciones e indicarle al usuario que no disponemos de lo que pide.


## Lista de funcionalidades

¿Qué funcionalidades tiene el chatbot?

- Búsqueda de juego específico
- Búsqueda por plataforma (PS5, Xbox, Switch, PC)
- Búsqueda por género (RPG, acción, horror, etc.)
- Búsqueda por rango de precio
- Filtros combinados (precio + plataforma/género)
- Recomendaciones personalizadas
- Búsqueda de sagas (múltiples versiones)
- Búsqueda por modo de juego (solitario/online)
- Lista de categorías disponibles
- Sistema de sesiones de usuario
- Historial de conversaciones
- Normalización de texto (tildes, puntuación)
- Paginación de resultados
- Detección de plataformas sin juegos
- Integración RAWG API para juegos no en catálogo

## Ejemplos de Preguntas

¿Qué puedes preguntarle al chatbot?

- ¿Tienes el juego de la Barbie?
- ¿Juego de aventura?
- ¿Qué categoría de juegos tienes?
- ¿Qué juegos tienes para PC?
- Dime juegos baratos
- Juegos por menos de 50 euros

## Integración con RAWG API

Lo que también incorporamos ha sido la **API de RAWG** para obtener información actualizada sobre los videojuegos, como precios, plataformas y géneros. Esto nos permite proporcionar respuestas más precisas y relevantes a las preguntas de los usuarios. 

Si el juego no lo tenemos en nuestra base de datos, el chatbot puede buscarlo en la **API de RAWG** y ofrecer información sobre él.

## Paginación

Al devolver una lista de juegos también implementamos **paginación**. Al darle al botón **+** se cargan más juegos. Esto lo hicimos para mejorar la experiencia del usuario y evitar sobrecargar la interfaz con demasiada información de una sola vez.

##  Estructura del Proyecto

```
ChatBot/
├──  app.py                       # Servidor Flask principal - lógica del chatbot
│
├──  backend/
│   ├── config.py                 # Configuración (BD, mapa de plataformas, géneros)
│   ├── rawg_service.py           # Servicio para integración con API RAWG
│   ├── init_db.py                # Inicializador de base de datos
│   └── populate_db.py            # Script para poblar datos iniciales
│
├──  frontend/
│   ├── index.html                # Interfaz web del chatbot (Bootstrap 5)
│   ├── css/
│   │   └── app.css               # Estilos personalizados
│   ├── js/
│   │   └── app.js                # Lógica del cliente (AJAX, UI)
│   └── img/
│       └── *.png, *.webp         # Imágenes y assets
│
├──  database/
│   └── tienda_juegos.db          # Base de datos SQLite con juegos y catálogo
```

##  Flujo de Funcionamiento

1. **Usuario escribe pregunta** → Interfaz web (JavaScript)
2. **Se envía al servidor** → API REST en Flask (`/api/chat`)
3. **Procesamiento en servidor:**
   -  Normalización del texto (sin tildes, minúsculas)
   -  Búsqueda en 4 niveles (juego, plataforma/género, RAWG, reglas)
   -  Consulta a base de datos SQLite
   -  Si no encuentra, consulta RAWG API
4. **Respuesta al cliente** → JSON con resultado
5. **Renderizado en UI** → Muestra juegos, precios, plataformas

##  Archivos Clave

| Archivo | Función |
|---------|----------|
| **app.py** | Lógica principal del chatbot, búsquedas multinivel, orquestación de respuestas |
| **config.py** | Mapeos de plataformas, géneros, palabras clave y configuración global |
| **rawg_service.py** | Búsqueda externa en RAWG.io con caché inteligente |
| **index.html** | Interfaz web responsiva con Bootstrap |
| **app.js** | Comunicación con servidor, historial de chat, paginación |
| **tienda_juegos.db** | SQLite con tablas: juegos, plataformas, géneros, relaciones |

##  Tecnologías Utilizadas

### Backend
- **Python 3.x** 
- **Flask 3.0.0** 
- **Flask-CORS 4.0.0** 
- **SQLite3** 
- **Requests 2.31.0** 

### Frontend
- **HTML5**
- **Bootstrap 5.3.3**
- **Bootstrap Icons**
- **JavaScript vanilla** 

### APIs Externas
- **RAWG API**

##  Instrucciones de Instalación

### Crear entorno virtual (recomendado)
```bash
# En Windows
python -m venv venv
venv\Scripts\activate

# En Mac/Linux
python3 -m venv venv
source venv/bin/activate
```

### Instalar dependencias
```bash
pip install -r requirements.txt
```

### Inicializar la base de datos
```bash
# Crear tablas y esquema (importante para despues llenar la base de datos)
python backend/init_db.py

# Poblar datos (juegos, desarrolladores, géneros, reglas del chatbot)
python backend/populate_db.py
```

### Ejecutar el servidor
```bash
python app.py
```

**El servidor estará disponible en:** `http://localhost:5001`

### Abrir en el navegador
```
http://localhost:5001
```



