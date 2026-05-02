import sqlite3
import os

# Ruta base del proyecto
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, 'database', 'tienda_juegos.db')

conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()

# ── Desarrolladores ───────────────────────────────────────────
devs = [
    ('Sony Santa Monica', 'USA', 'https://sms.playstation.com'),
    ('Insomniac Games', 'USA', 'https://insomniac.games'),
    ('Larian Studios', 'Belgica', 'https://larian.com'),
    ('Square Enix', 'Japon', 'https://square-enix.com'),
    ('Bandai Namco', 'Japon', 'https://bandainamcoent.com'),
    ('Activision', 'USA', 'https://activision.com'),
    ('EA Sports', 'USA', 'https://ea.com'),
    ('Mojang', 'Suecia', 'https://minecraft.net'),
    ('Epic Games', 'USA', 'https://epicgames.com'),
    ('Supergiant Games', 'USA', 'https://supergiantgames.com'),
    ('Team Cherry', 'Australia', 'https://teamcherry.com.au'),
    ('ConcernedApe', 'USA', 'https://stardewvalley.net'),
    ('Remedy Entertainment', 'Finlandia', 'https://remedygames.com'),
    ('Arrowhead', 'Suecia', 'https://arrowheadgamestudios.com'),
    ('Pocketpair', 'Japon', 'https://pocketpair.jp'),
    ('Konami', 'Japon', 'https://konami.com'),
    ('2K Games', 'USA', 'https://2k.com'),
    ('Nintendo', 'Japon', 'https://nintendo.com'),
    ('Blizzard', 'USA', 'https://blizzard.com'),
    ('Respawn Entertainment', 'USA', 'https://respawn.com'),
    ('WB Games', 'USA', 'https://wbgames.com'),
    ('Capcom', 'Japon', 'https://capcom.com'),
    ('Rockstar Games', 'USA', 'https://rockstargames.com'),
    ('CD Projekt Red', 'Polonia', 'https://cdprojektred.com'),
    ('Ubisoft', 'Francia', 'https://ubisoft.com'),
    ('Atlus', 'Japon', 'https://atlus.com'),
    ('Ryu Ga Gotoku', 'Japon', 'https://ryu-ga-gotoku.com'),
    ('FromSoftware', 'Japon', 'https://fromsoftware.jp'),
    ('Vanillaware', 'Japon', 'https://vanillaware.com'),
    ('MachineGames', 'Suecia', 'https://machinegames.com'),
    ('Obsidian Entertainment', 'USA', 'https://obsidian.net'),
    ('Yacht Club Games', 'USA', 'https://yachtclubgames.com'),
    ('Bioware', 'Canada', 'https://bioware.com'),
    ('GSC Game World', 'Ucrania', 'https://gsc.com.ua'),
    ('LocalThunk', 'Canada', 'https://localthunk.com'),
    ('Kojima Productions', 'Japon', 'https://kojimapro.com'),
    ('Dirge Digital', 'USA', 'https://dirgedigital.com'),
    ('Mattel Games', 'USA', 'https://mattel.com'),
    ('Pink Squared', 'USA', 'https://pinksquared.com'),
    ('Naughty Dog', 'USA', 'https://naughtydog.com'),
    ('IO Interactive', 'Dinamarca', 'https://ioi.dk'),
    ('Saber Interactive', 'USA', 'https://saberinteractive.com'),
    ('Avalanche Studios', 'Suecia', 'https://avalanchestudios.com'),
    ('Firaxis Games', 'USA', 'https://firaxis.com'),
    ('SEGA', 'Japon', 'https://sega.com'),
    ('Deep Silver', 'Austria', 'https://deepsilver.com'),
    ('Guerrilla Games', 'Holanda', 'https://guerrilla-games.com'),
    ('Santa Monica Studio', 'USA', 'https://sms.playstation.com'),
    ('Playground Games', 'Reino Unido', 'https://playground-games.com'),
    ('Bungie', 'USA', 'https://bungie.net'),
    ('Turtle Rock Studios', 'USA', 'https://turtlerockstudios.com'),
    ('Rocksteady', 'Reino Unido', 'https://rocksteadyltd.com'),
    ('Thatgamecompany', 'USA', 'https://thatgamecompany.com'),
    ('Devolver Digital', 'USA', 'https://devolverdigital.com'),
    ('Annapurna Interactive', 'USA', 'https://annapurnainteractive.com'),
    ('Motion Twin', 'Francia', 'https://motion-twin.com'),
    ('Tarn Adams', 'USA', 'https://bay12games.com'),
    ('Curve Games', 'Reino Unido', 'https://curve.games'),
    ('Daedalic Entertainment', 'Alemania', 'https://daedalic.com'),
    ('Klei Entertainment', 'Canada', 'https://klei.com'),
    ('Haemimont Games', 'Bulgaria', 'https://haemimontgames.com'),
    ('Raw Fury', 'Suecia', 'https://rawfury.com'),
    ('Nihon Falcom', 'Japon', 'https://falcom.co.jp'),
    ('Spike Chunsoft', 'Japon', 'https://spike-chunsoft.com'),
]
for d in devs:
    cur.execute("INSERT OR IGNORE INTO desarrolladores (nombre, pais, sitio_web) VALUES (?,?,?)", d)
conn.commit()

cur.execute("SELECT nombre, id FROM desarrolladores")
dev_map = {r[0]: r[1] for r in cur.fetchall()}

# ── Géneros ───────────────────────────────────────────────────
generos = [
    'Lucha',
    'Simulacion',
    'Survival',
    'Roguelike',
    'Metroidvania',
    'Sandbox',
    'Hack and Slash',
    'Social Sim',
    'First-Person',
    'Cartas',
    'Plataforma',
    'Sci-Fi',
    'Fantasy',
    'Accion',
    'Aventura',
    'RPG',
    'Horror',
    'FPS',
    'Deportes',
    'Battle Royale',
    'Estrategia',
    'Puzzle',
    'Casual',
    'Mundo Abierto',
    'Tactica',
    'Musica',
    'Carreras',
    'Terror',
    'Sigilo',
    'MOBA',
    'Narrativo',
]
for g in generos:
    cur.execute("INSERT OR IGNORE INTO generos (nombre) VALUES (?)", (g,))
conn.commit()

cur.execute("SELECT nombre, id FROM generos")
gen_map = {r[0]: r[1] for r in cur.fetchall()}

cur.execute("SELECT nombre, id FROM plataformas")
plat_map = {r[0]: r[1] for r in cur.fetchall()}
PC   = plat_map.get('PC')
PS5  = plat_map.get('PlayStation 5')
XBOX = plat_map.get('Xbox Series X')
NS   = plat_map.get('Nintendo Switch')

# ── Juegos ────────────────────────────────────────────────────
juegos = [
    # (titulo, descripcion, dev_id, fecha, precio, precio_oferta, clasificacion_edad, tipo_jugador)
    ('God of War: Ragnarok', 'Continua la epica nordica de Kratos y Atreus en un mundo al borde del apocalipsis.', dev_map['Sony Santa Monica'], '2022-11-09', 59.99, 29.99, 'PEGI 18', 'single_player'),
    ("Marvel's Spider-Man 2", 'Peter Parker y Miles Morales se enfrentan a Venom en un Nueva York espectacular.', dev_map['Insomniac Games'], '2023-10-20', 69.99, 49.99, 'PEGI 16', 'single_player'),
    ("Baldur's Gate 3", 'El RPG definitivo con libertad total. Miles de decisiones y combate por turnos.', dev_map['Larian Studios'], '2023-08-03', 59.99, None, 'PEGI 18', 'cooperativo'),
    ('Final Fantasy VII Rebirth', 'Segunda parte del remake de FFVII con mundo abierto enorme y combate espectacular.', dev_map['Square Enix'], '2024-02-29', 69.99, 49.99, 'PEGI 16', 'single_player'),
    ('Tekken 8', 'El mejor juego de lucha de la saga con graficos next-gen y nuevo sistema de calor.', dev_map['Bandai Namco'], '2024-01-26', 69.99, 39.99, 'PEGI 12', 'competitivo'),
    ('Street Fighter 6', 'Regresa el clasico con modo mundo abierto, nuevos personajes y multijugador online.', dev_map['Capcom'], '2023-06-02', 59.99, 29.99, 'PEGI 12', 'competitivo'),
    ('Resident Evil 4 Remake', 'Remake del clasico survival horror con graficos modernos y jugabilidad renovada.', dev_map['Capcom'], '2023-03-24', 59.99, 24.99, 'PEGI 18', 'single_player'),
    ("Dragon's Dogma 2", 'RPG de accion en mundo abierto con un sistema de peones unicos y combate epico.', dev_map['Capcom'], '2024-03-22', 59.99, 39.99, 'PEGI 18', 'single_player'),
    ('Call of Duty: Black Ops 6', 'El shooter mas esperado del ano con campana cinematica y multijugador adictivo.', dev_map['Activision'], '2024-10-25', 69.99, None, 'PEGI 18', 'competitivo'),
    ('EA Sports FC 25', 'El simulador de futbol mas realista con licencias oficiales de las mejores ligas.', dev_map['EA Sports'], '2024-09-27', 69.99, 39.99, 'PEGI 3', 'competitivo'),
    ('NBA 2K25', 'La experiencia de baloncesto definitiva con el modo MyCareer y la Ciudad mejorados.', dev_map['2K Games'], '2024-09-06', 69.99, 34.99, 'PEGI 3', 'competitivo'),
    ('Minecraft', 'El juego de construccion sandbox mas vendido de la historia. Crea tu mundo.', dev_map['Mojang'], '2011-11-18', 26.95, None, 'PEGI 7', 'cooperativo'),
    ('Fortnite', 'Battle Royale gratuito con 100 jugadores, construccion y eventos unicos.', dev_map['Epic Games'], '2017-09-26', 0.0, None, 'PEGI 12', 'competitivo'),
    ('Apex Legends', 'Battle Royale gratuito con heroes unicos y habilidades especiales.', dev_map['Respawn Entertainment'], '2019-02-04', 0.0, None, 'PEGI 16', 'competitivo'),
    ('Rocket League', 'Futbol con coches cohete. Facil de aprender, dificil de dominar.', dev_map['Epic Games'], '2015-07-07', 0.0, None, 'PEGI 3', 'competitivo'),
    ('Hades II', 'Roguelike de accion con narrativa increible, sucesor del aclamado Hades original.', dev_map['Supergiant Games'], '2024-05-06', 29.99, None, 'PEGI 12', 'single_player'),
    ('Hollow Knight', 'Metroidvania desafiante en un reino subterraneo de insectos con arte precioso.', dev_map['Team Cherry'], '2017-02-24', 14.99, 7.49, 'PEGI 7', 'single_player'),
    ('Stardew Valley', 'Gestiona tu granja, explora minas, haz amigos y crea la vida que suenas.', dev_map['ConcernedApe'], '2016-02-26', 13.99, None, 'PEGI 3', 'casual'),
    ('Alan Wake 2', 'Thriller psicologico y survival horror con narrativa cinematografica unica.', dev_map['Remedy Entertainment'], '2023-10-27', 49.99, 24.99, 'PEGI 18', 'single_player'),
    ('Helldivers 2', 'Shooter cooperativo en el que defiendes la democracia contra hordas alienigenas.', dev_map['Arrowhead'], '2024-02-08', 39.99, None, 'PEGI 16', 'cooperativo'),
    ('Palworld', 'Captura criaturas Pal, construye bases y sobrevive en este mundo de accion sandbox.', dev_map['Pocketpair'], '2024-01-19', 29.99, None, 'PEGI 12', 'cooperativo'),
    ('Silent Hill 2 Remake', 'El remake del legendario survival horror con graficos modernos y camara al hombro.', dev_map['Konami'], '2024-10-08', 59.99, None, 'PEGI 18', 'single_player'),
    ('The Legend of Zelda: Tears of the Kingdom', 'Explora Hyrule y los cielos con poderes unicos en esta epica aventura.', dev_map['Nintendo'], '2023-05-12', 59.99, None, 'PEGI 7', 'single_player'),
    ('Diablo IV', 'El rey del hack and slash regresa con un mundo oscuro, abierto y brutal.', dev_map['Blizzard'], '2023-06-06', 59.99, 29.99, 'PEGI 18', 'cooperativo'),
    ('Overwatch 2', 'Hero shooter gratuito con mas de 30 heroes y modos de juego variados.', dev_map['Blizzard'], '2022-10-04', 0.0, None, 'PEGI 12', 'competitivo'),
    ('Red Dead Redemption 2', 'La historia definitiva del salvaje oeste con un mundo abierto sin igual.', dev_map['Rockstar Games'], '2018-10-26', 59.99, 14.99, 'PEGI 18', 'single_player'),
    ('The Witcher 3: Wild Hunt', 'El RPG de mundo abierto mas premiado, con historia epica y mundo vivo.', dev_map['CD Projekt Red'], '2015-05-19', 39.99, 9.99, 'PEGI 18', 'single_player'),
    ('Hogwarts Legacy', 'Vive tu propia aventura en el mundo magico de Harry Potter en el siglo XIX.', dev_map['WB Games'], '2023-02-10', 59.99, 29.99, 'PEGI 12', 'single_player'),
    ('Star Wars Outlaws', 'Se la primera forajida de Star Wars en este juego de mundo abierto.', dev_map['Ubisoft'], '2024-08-30', 69.99, 49.99, 'PEGI 16', 'single_player'),
    ('It Takes Two', 'Juego cooperativo obligatorio para dos jugadores, ganador del GOTY 2021.', dev_map['EA Sports'], '2021-03-26', 39.99, 9.99, 'PEGI 12', 'cooperativo'),
    ('Metaphor: ReFantazio', 'RPG de estrategia con narrativa cinematografica en un mundo fantastico lleno de intriga politica.', dev_map['Atlus'], '2024-10-11', 59.99, None, 'PEGI 16', 'single_player'),
    ('Indiana Jones and the Great Circle', 'Aventura en primera persona donde eres Indiana Jones buscando artefactos antiguos.', dev_map['MachineGames'], '2024-12-09', 59.99, None, 'PEGI 16', 'single_player'),
    ('Dragon Age: The Veilguard', 'RPG epico con decisiones que moldean tu historia en el mundo de Thedas.', dev_map['Bioware'], '2024-10-31', 59.99, None, 'PEGI 16', 'single_player'),
    ('Persona 5 Royal', 'JRPG con sistema de personas unico, combate por turnos y narrativa cautivadora.', dev_map['Atlus'], '2022-01-19', 59.99, 34.99, 'PEGI 16', 'single_player'),
    ('Like a Dragon: Infinite Wealth', 'Aventura urbana intensa con combates frenéticos y una historia emotiva.', dev_map['Ryu Ga Gotoku'], '2024-01-26', 59.99, 29.99, 'PEGI 18', 'single_player'),
    ('Unicorn Overlord', 'Estrategia tactica de contos de hadas con arte pixelart hermoso y 100+ horas de contenido.', dev_map['Vanillaware'], '2024-03-08', 49.99, 29.99, 'PEGI 12', 'single_player'),
    ('S.T.A.L.K.E.R. 2: Heart of Chornobyl', 'FPS postapocalitico atmosférico en la zona de exclusión de Chernóbil.', dev_map['GSC Game World'], '2024-11-20', 69.99, None, 'PEGI 18', 'single_player'),
    ('Avowed', 'RPG de fantasía oscura en primera persona con magia y exploración inmersiva.', dev_map['Obsidian Entertainment'], '2025-02-18', 69.99, None, 'PEGI 18', 'single_player'),
    ('Shovel Knight: Dig', 'Plataformero excavador con roguelike elements y retro vibes increibles.', dev_map['Yacht Club Games'], '2023-09-27', 20.0, 10.0, 'PEGI 7', 'single_player'),
    ('Balatro', 'Juego de cartas y poquér roguelike adictivo y altamente estratégico.', dev_map['LocalThunk'], '2024-02-20', 19.99, None, 'PEGI 3', 'single_player'),
    ('Silent Hill f', 'Survival horror japonés con atmosfera pesada y enemigos terrorificos.', dev_map['Konami'], '2024-10-18', 49.99, None, 'PEGI 18', 'single_player'),
    ("Dragon's Lair Trilogy", 'Juego de accion arcade clasico remasterizado en HD con precioso pixel art.', dev_map['Dirge Digital'], '2024-05-03', 29.99, 14.99, 'PEGI 12', 'single_player'),
    ('Death Stranding 2', 'Adventure futurista con simulación de transportes e interacción online asincronica.', dev_map['Kojima Productions'], '2025-01-17', 69.99, None, 'PEGI 16', 'single_player'),
    ('Barbie Dreamhouse Adventure', 'Ayuda a Barbie a limpiar y decorar su mansion de ensueño. Colorido y divertido para todas las edades.', dev_map['Mattel Games'], '2012-10-09', 29.99, 14.99, 'PEGI 3', 'single_player'),
    ('Barbie Horse Adventures: Riding Camp', 'Monta a caballo, participa en competencias y cuida a tus caballos en este juego hipetico para fans de Barbie.', dev_map['Pink Squared'], '2006-09-22', 24.99, 9.99, 'PEGI 3', 'single_player'),
    ('Barbie Fashion Show', 'Crea conjuntos de moda, participa en pasarelas y demuestra tu estilo en el mundo de la moda.', dev_map['Mattel Games'], '2006-10-31', 19.99, 7.99, 'PEGI 3', 'single_player'),
    ('Barbie Princess and the Popstar', 'Vive la aventura de Barbie siendo princesa y popstar. Música, magia y diversión garantizadas.', dev_map['Mattel Games'], '2012-03-14', 24.99, 12.49, 'PEGI 3', 'single_player'),
    ('Barbie and Ken Vacation Paradise', 'Disfruta de vacaciones tropicales con Ken. Resuelve puzles y desafios en una isla paradisiaca.', dev_map['Mattel Games'], '2011-03-10', 22.99, 11.49, 'PEGI 3', 'single_player'),
    ('The Last of Us Part I', 'Remake del clasico de Naughty Dog. Joel y Ellie en un mundo post-apocaliptico devastador.', dev_map['Naughty Dog'], '2022-09-02', 59.99, 29.99, 'PEGI 18', 'single_player'),
    ('The Last of Us Part II Remastered', 'La historia de Ellie continua en esta remasterizacion con contenido extra y mejoras visuales.', dev_map['Naughty Dog'], '2024-01-19', 49.99, None, 'PEGI 18', 'single_player'),
    ('Hitman World of Assassination', 'El agente 47 en su mision mas ambiciosa. Sandbox de sigilo con niveles enormes.', dev_map['IO Interactive'], '2023-01-26', 59.99, 19.99, 'PEGI 18', 'single_player'),
    ('Horizon Forbidden West', 'Aloy explora un mundo peligroso lleno de maquinas y civilizaciones misteriosas.', dev_map['Guerrilla Games'], '2022-02-18', 59.99, 24.99, 'PEGI 16', 'single_player'),
    ('Forza Horizon 5', 'El simulador de carreras en mundo abierto mas bonito. Mexico con 500+ coches.', dev_map['Playground Games'], '2021-11-09', 59.99, 29.99, 'PEGI 3', 'competitivo'),
    ('Suicide Squad: Kill the Justice League', 'Shooter cooperativo donde los villanos deben matar a los heroes de DC.', dev_map['Rocksteady'], '2024-02-02', 59.99, 19.99, 'PEGI 16', 'cooperativo'),
    ("Marvel's Midnight Suns", 'Juego de estrategia tactica con heroes Marvel y sistema de cartas innovador.', dev_map['Firaxis Games'], '2022-12-02', 59.99, 14.99, 'PEGI 12', 'single_player'),
    ('Dead Island 2', 'Mata zombies en Los Angeles con armas artesanales y humor irreverente.', dev_map['Deep Silver'], '2023-04-21', 49.99, 19.99, 'PEGI 18', 'cooperativo'),
    ('Sonic Frontiers', 'Sonic en su primera aventura de mundo abierto con combate renovado.', dev_map['SEGA'], '2022-11-08', 49.99, 14.99, 'PEGI 7', 'single_player'),
    ('Like a Dragon: Ishin', 'Spinoff historico de la saga Yakuza ambientado en el Japon feudal.', dev_map['Ryu Ga Gotoku'], '2023-02-21', 49.99, 24.99, 'PEGI 18', 'single_player'),
    ('Warhammer 40K: Space Marine 2', 'Accion brutal en tercera persona. Lidera a los Ultramarines contra hordas del Caos.', dev_map['Saber Interactive'], '2024-09-09', 49.99, None, 'PEGI 18', 'cooperativo'),
    ('Jusant', 'Juego de escalada contemplatvo con historia emotiva y mundo vertical unico.', dev_map['Annapurna Interactive'], '2023-10-31', 24.99, 12.49, 'PEGI 7', 'single_player'),
    ('Outer Wilds', 'Exploracion espacial sin igual. Descubre el misterio de una galaxia en un bucle temporal.', dev_map['Annapurna Interactive'], '2019-05-28', 24.99, 9.99, 'PEGI 7', 'single_player'),
    ('Disco Elysium', 'RPG narrativo revolucionario. Eres un detective amnesiaco en una ciudad llena de politica.', dev_map['Devolver Digital'], '2019-10-15', 39.99, 9.99, 'PEGI 18', 'single_player'),
    ('Dave the Diver', 'Pesca durante el dia, gestiona un restaurante de sushi por la noche. Sorprendente y adictivo.', dev_map['Devolver Digital'], '2023-06-28', 19.99, 9.99, 'PEGI 7', 'single_player'),
    ('Trails into Reverie', 'JRPG epico con combate por turnos y narrativa compleja de Nihon Falcom.', dev_map['Nihon Falcom'], '2022-07-08', 49.99, 24.99, 'PEGI 12', 'single_player'),
    ("No Man's Sky", 'Exploracion espacial infinita con bases, naves y planetas procedurales. Enormemente mejorado.', dev_map['Curve Games'], '2016-08-12', 29.99, 14.99, 'PEGI 7', 'cooperativo'),
    ('Dead Cells', 'Roguelike-metroidvania frenético. Cada muerte te hace mas fuerte. Maestria pura.', dev_map['Motion Twin'], '2018-08-07', 24.99, 9.99, 'PEGI 16', 'single_player'),
    ('Hades', 'El roguelike perfecto. Escapa del inframundo con estilo. Narrativa integrada genial.', dev_map['Supergiant Games'], '2020-09-17', 24.99, 12.49, 'PEGI 12', 'single_player'),
    ('Celeste', 'Plataformero preciso y emotivo. Una chica sube una montana mientras supera sus miedos.', dev_map['Annapurna Interactive'], '2018-01-25', 19.99, 4.99, 'PEGI 7', 'single_player'),
    ('Tunic', 'Aventura isometrica como los Zelda clasicos. Descifra misterios con un zorro adorable.', dev_map['Annapurna Interactive'], '2022-03-16', 29.99, 14.99, 'PEGI 7', 'single_player'),
    ('Return of the Obra Dinn', 'Resuelve las muertes de 60 marineros con logica deductiva unica. Arte de 1-bit precioso.', dev_map['Devolver Digital'], '2018-10-18', 19.99, 9.99, 'PEGI 12', 'single_player'),
    ('Vampire Survivors', 'Bullet hell minimalista adictivo. Sobrevive hordas de monstruos con armas que se combinan.', dev_map['Devolver Digital'], '2022-10-20', 4.99, None, 'PEGI 12', 'single_player'),
    ("Don't Starve Together", 'Survival de dibujos animados macabros. Cooperativo y muy dificil.', dev_map['Klei Entertainment'], '2016-04-21', 14.99, 4.99, 'PEGI 7', 'cooperativo'),
    ('Oxygen Not Included', 'Simulador de colonia espacial extremadamente profundo. Para mentes estrategicas.', dev_map['Klei Entertainment'], '2019-07-30', 24.99, 9.99, 'PEGI 3', 'single_player'),
    ('Grounded', 'Sobrevive encogido en el jardin de tu casa. Cooperativo con amigos y mucho crafteo.', dev_map['Obsidian Entertainment'], '2022-09-27', 29.99, 14.99, 'PEGI 12', 'cooperativo'),
    ('The Forgotten City', 'Aventura narrativa en Roma antigua. Viaja en el tiempo para evitar una maldicion.', dev_map['Annapurna Interactive'], '2021-07-28', 24.99, 9.99, 'PEGI 16', 'single_player'),
    ('Norco', 'Point-and-click narrativo en el sur de Louisiana. Atmosfera unica y poesia visual.', dev_map['Raw Fury'], '2022-03-24', 14.99, 7.49, 'PEGI 16', 'single_player'),
    ('Hardspace: Shipbreaker', 'Desmonta naves espaciales para ganarte la vida. Simulador laboral relajante y peculiar.', dev_map['Raw Fury'], '2022-09-29', 24.99, 9.99, 'PEGI 12', 'single_player'),
    ('Prodeus', 'FPS retro brutal estilo Doom con graficos modernos. Violencia pixelada frenética.', dev_map['Devolver Digital'], '2022-10-11', 19.99, 9.99, 'PEGI 18', 'single_player'),
    ('Danganronpa Trilogy', 'Novelas visuales de misterio. Resuelve crimenes en una escuela donde matar es obligatorio.', dev_map['Spike Chunsoft'], '2020-09-18', 29.99, 14.99, 'PEGI 16', 'single_player'),
    ('Untitled Goose Game', 'Se un ganso horrible que arruina el dia de todos los vecinos del pueblo. Brillante.', dev_map['Annapurna Interactive'], '2019-09-20', 14.99, 7.49, 'PEGI 3', 'single_player'),
    ('A Short Hike', 'Exploracion tranquila en una isla. Sube una montana, habla con aves. Perfecto en 2 horas.', dev_map['Annapurna Interactive'], '2019-07-30', 7.99, None, 'PEGI 3', 'single_player'),
    ('Baba Is You', 'Puzzle genial donde cambias las reglas del propio juego moviendo bloques de texto.', dev_map['Devolver Digital'], '2019-03-13', 14.99, 7.49, 'PEGI 3', 'single_player'),
    ('Minit', 'Aventura en la que cada vida dura 60 segundos. Descubre secretos en fragmentos.', dev_map['Devolver Digital'], '2018-04-03', 9.99, 4.99, 'PEGI 3', 'single_player'),
    ('Papers Please', 'Eres inspector de inmigracion en un pais totalitario. Moral y dilemas en cada sello.', dev_map['Devolver Digital'], '2013-08-08', 9.99, 4.99, 'PEGI 12', 'single_player'),
    ('Into the Breach', 'Estrategia tactica de ciencia ficcion perfecta. 8 unidades, tablero 8x8, decision imposible.', dev_map['Devolver Digital'], '2018-02-27', 14.99, 7.49, 'PEGI 7', 'single_player'),
    ('Loop Hero', 'Roguelike estrategico donde reconstruyes el mundo colocando cartas. Muy original.', dev_map['Devolver Digital'], '2021-03-04', 14.99, 4.99, 'PEGI 12', 'single_player'),
    ('Katana ZERO', 'Plataformero de accion neo-noir con narrativa fragmentada. Estilo y sustancia.', dev_map['Devolver Digital'], '2019-04-18', 14.99, 7.49, 'PEGI 18', 'single_player'),
    ('Carrion', 'Eres el monstruo. Devora humanos, escapa del laboratorio y crece.', dev_map['Devolver Digital'], '2020-07-23', 19.99, 9.99, 'PEGI 18', 'single_player'),
    ('Moonlighter', 'De dia gestionas tu tienda. De noche eres un aventurero en mazmorras. Genial bucle.', dev_map['Devolver Digital'], '2018-05-29', 19.99, 4.99, 'PEGI 12', 'single_player'),
    ('Spiritfarer', 'Gestiona un ferry para espiritus que cruzan al mas alla. Emotivo y precioso.', dev_map['Raw Fury'], '2020-08-18', 29.99, 9.99, 'PEGI 7', 'cooperativo'),
    ('Path of Exile 2', 'ARPG free-to-play con profundidad enorme. El sucesor espiritual de Diablo.', dev_map['Epic Games'], '2024-12-06', 0.0, None, 'PEGI 16', 'cooperativo'),
    ('Warframe', 'Shooter de accion en tercera persona gratuito con personajes llamados Warframes.', dev_map['Epic Games'], '2013-03-25', 0.0, None, 'PEGI 16', 'cooperativo'),
    ('Genshin Impact', 'RPG de mundo abierto animado y gratuito. Explora Teyvat con personajes coleccionables.', dev_map['Epic Games'], '2020-09-28', 0.0, None, 'PEGI 12', 'cooperativo'),
]
for j in juegos:
    cur.execute("""
        INSERT OR IGNORE INTO juegos (titulo, descripcion, desarrollador_id, fecha_lanzamiento, precio, precio_oferta, clasificacion_edad, activo, tipo_jugador)
        VALUES (?,?,?,?,?,?,?,1,?)
    """, j)
conn.commit()

cur.execute("SELECT titulo, id FROM juegos")
juego_map = {r[0]: r[1] for r in cur.fetchall()}

# ── Géneros por juego ─────────────────────────────────────────
juego_generos = {
    'God of War: Ragnarok': ['Accion', 'Aventura'],
    "Marvel's Spider-Man 2": ['Accion', 'Aventura', 'Mundo Abierto'],
    "Baldur's Gate 3": ['RPG', 'Estrategia'],
    'Final Fantasy VII Rebirth': ['RPG', 'Accion'],
    'Tekken 8': ['Lucha', 'Accion'],
    'Street Fighter 6': ['Lucha', 'Accion'],
    'Resident Evil 4 Remake': ['Horror', 'Accion'],
    "Dragon's Dogma 2": ['RPG', 'Accion', 'Mundo Abierto'],
    'Call of Duty: Black Ops 6': ['FPS', 'Accion'],
    'EA Sports FC 25': ['Deportes', 'Simulacion'],
    'NBA 2K25': ['Deportes', 'Simulacion'],
    'Minecraft': ['Sandbox', 'Survival'],
    'Fortnite': ['Battle Royale', 'Accion'],
    'Apex Legends': ['Battle Royale', 'FPS'],
    'Rocket League': ['Deportes'],
    'Hades II': ['Roguelike', 'Accion'],
    'Hollow Knight': ['Metroidvania', 'Aventura'],
    'Stardew Valley': ['Simulacion', 'RPG'],
    'Alan Wake 2': ['Horror', 'Aventura'],
    'Helldivers 2': ['Accion', 'FPS'],
    'Palworld': ['Sandbox', 'Survival', 'Accion'],
    'Silent Hill 2 Remake': ['Horror', 'Aventura'],
    'The Legend of Zelda: Tears of the Kingdom': ['Aventura', 'Accion', 'Mundo Abierto'],
    'Diablo IV': ['Hack and Slash', 'RPG', 'Accion'],
    'Overwatch 2': ['FPS', 'Accion'],
    'Red Dead Redemption 2': ['Accion', 'Aventura', 'Mundo Abierto'],
    'The Witcher 3: Wild Hunt': ['RPG', 'Accion', 'Mundo Abierto'],
    'Hogwarts Legacy': ['RPG', 'Aventura', 'Mundo Abierto'],
    'Star Wars Outlaws': ['Accion', 'Aventura', 'Mundo Abierto'],
    'It Takes Two': ['Accion', 'Aventura'],
    'Metaphor: ReFantazio': ['RPG', 'Estrategia'],
    'Indiana Jones and the Great Circle': ['Accion', 'Aventura', 'Mundo Abierto'],
    'Dragon Age: The Veilguard': ['RPG', 'Accion', 'Mundo Abierto'],
    'Persona 5 Royal': ['RPG', 'Aventura'],
    'Like a Dragon: Infinite Wealth': ['Accion', 'Aventura'],
    'Unicorn Overlord': ['Estrategia', 'RPG'],
    'S.T.A.L.K.E.R. 2: Heart of Chornobyl': ['FPS', 'Survival', 'Mundo Abierto'],
    'Avowed': ['RPG', 'Accion', 'Mundo Abierto'],
    'Shovel Knight: Dig': ['Accion', 'Plataforma'],
    'Balatro': ['Estrategia', 'Cartas'],
    'Silent Hill f': ['Horror', 'Aventura'],
    "Dragon's Lair Trilogy": ['Accion', 'Aventura'],
    'Death Stranding 2': ['Accion', 'Aventura'],
    'Barbie Dreamhouse Adventure': ['Simulacion', 'Aventura', 'Casual'],
    'Barbie Horse Adventures: Riding Camp': ['Simulacion', 'Aventura'],
    'Barbie Fashion Show': ['Simulacion', 'Casual'],
    'Barbie Princess and the Popstar': ['Aventura', 'Casual'],
    'Barbie and Ken Vacation Paradise': ['Puzzle', 'Aventura'],
    'The Last of Us Part I': ['Accion', 'Aventura', 'Horror'],
    'The Last of Us Part II Remastered': ['Accion', 'Aventura', 'Horror'],
    'Hitman World of Assassination': ['Accion', 'Sigilo'],
    'Horizon Forbidden West': ['Accion', 'Aventura', 'Mundo Abierto'],
    'Forza Horizon 5': ['Carreras', 'Simulacion'],
    'Suicide Squad: Kill the Justice League': ['Accion', 'Aventura'],
    "Marvel's Midnight Suns": ['Estrategia', 'RPG', 'Accion'],
    'Dead Island 2': ['Accion', 'Survival', 'Horror'],
    'Sonic Frontiers': ['Accion', 'Aventura', 'Mundo Abierto'],
    'Like a Dragon: Ishin': ['Accion', 'Aventura'],
    'Warhammer 40K: Space Marine 2': ['Accion', 'FPS'],
    'Jusant': ['Aventura', 'Puzzle'],
    'Outer Wilds': ['Aventura', 'Sandbox'],
    'Disco Elysium': ['RPG', 'Narrativo'],
    'Dave the Diver': ['Aventura', 'Simulacion', 'RPG'],
    'Trails into Reverie': ['RPG', 'Estrategia'],
    "No Man's Sky": ['Aventura', 'Sandbox', 'Survival'],
    'Dead Cells': ['Roguelike', 'Metroidvania', 'Accion'],
    'Hades': ['Roguelike', 'Accion'],
    'Celeste': ['Plataforma', 'Aventura'],
    'Tunic': ['Accion', 'Aventura'],
    'Return of the Obra Dinn': ['Puzzle', 'Narrativo'],
    'Vampire Survivors': ['Roguelike', 'Accion'],
    "Don't Starve Together": ['Survival', 'Sandbox'],
    'Oxygen Not Included': ['Simulacion', 'Estrategia'],
    'Grounded': ['Survival', 'Accion', 'Sandbox'],
    'The Forgotten City': ['Aventura', 'Narrativo'],
    'Norco': ['Aventura', 'Narrativo'],
    'Hardspace: Shipbreaker': ['Simulacion', 'Sandbox'],
    'Prodeus': ['FPS', 'Accion'],
    'Danganronpa Trilogy': ['Narrativo', 'Puzzle'],
    'Untitled Goose Game': ['Puzzle', 'Casual'],
    'A Short Hike': ['Aventura', 'Casual'],
    'Baba Is You': ['Puzzle'],
    'Minit': ['Aventura', 'Puzzle'],
    'Papers Please': ['Narrativo', 'Simulacion'],
    'Into the Breach': ['Estrategia', 'Tactica'],
    'Loop Hero': ['Roguelike', 'Estrategia'],
    'Katana ZERO': ['Accion', 'Plataforma'],
    'Carrion': ['Accion', 'Horror'],
    'Moonlighter': ['RPG', 'Roguelike'],
    'Spiritfarer': ['Aventura', 'Simulacion'],
    'Path of Exile 2': ['RPG', 'Hack and Slash', 'Accion'],
    'Warframe': ['Accion', 'FPS'],
    'Genshin Impact': ['RPG', 'Aventura', 'Mundo Abierto'],
}
for titulo, genres in juego_generos.items():
    jid = juego_map.get(titulo)
    if not jid:
        continue
    for g in genres:
        gid = gen_map.get(g)
        if gid:
            cur.execute("INSERT OR IGNORE INTO juegos_generos VALUES (?,?)", (jid, gid))
conn.commit()

# ── Plataformas por juego ─────────────────────────────────────
juego_plats = {
    'God of War: Ragnarok': [PC, PS5],
    "Marvel's Spider-Man 2": [PS5],
    "Baldur's Gate 3": [PC, PS5],
    'Final Fantasy VII Rebirth': [PS5],
    'Tekken 8': [PC, PS5, XBOX],
    'Street Fighter 6': [PC, PS5, XBOX],
    'Resident Evil 4 Remake': [PC, PS5, XBOX],
    "Dragon's Dogma 2": [PC, PS5, XBOX],
    'Call of Duty: Black Ops 6': [PC, PS5, XBOX],
    'EA Sports FC 25': [PC, PS5, XBOX, NS],
    'NBA 2K25': [PC, PS5, XBOX, NS],
    'Minecraft': [PC, PS5, XBOX, NS],
    'Fortnite': [PC, PS5, XBOX, NS],
    'Apex Legends': [PC, PS5, XBOX],
    'Rocket League': [PC, PS5, XBOX, NS],
    'Hades II': [PC],
    'Hollow Knight': [PC, PS5, XBOX, NS],
    'Stardew Valley': [PC, PS5, XBOX, NS],
    'Alan Wake 2': [PC, PS5, XBOX],
    'Helldivers 2': [PC, PS5],
    'Palworld': [PC, XBOX],
    'Silent Hill 2 Remake': [PC, PS5],
    'The Legend of Zelda: Tears of the Kingdom': [NS],
    'Diablo IV': [PC, PS5, XBOX],
    'Overwatch 2': [PC, PS5, XBOX],
    'Red Dead Redemption 2': [PC, PS5, XBOX],
    'The Witcher 3: Wild Hunt': [PC, PS5, XBOX, NS],
    'Hogwarts Legacy': [PC, PS5, XBOX, NS],
    'Star Wars Outlaws': [PC, PS5, XBOX],
    'It Takes Two': [PC, PS5, XBOX],
    'Metaphor: ReFantazio': [PC, PS5],
    'Indiana Jones and the Great Circle': [PC, XBOX],
    'Dragon Age: The Veilguard': [PC, PS5, XBOX],
    'Persona 5 Royal': [PC, PS5],
    'Like a Dragon: Infinite Wealth': [PC, PS5, XBOX],
    'Unicorn Overlord': [PC, PS5, XBOX, NS],
    'S.T.A.L.K.E.R. 2: Heart of Chornobyl': [PC, XBOX],
    'Avowed': [PC, XBOX],
    'Shovel Knight: Dig': [PC, PS5, XBOX, NS],
    'Balatro': [PC, PS5, XBOX, NS],
    'Silent Hill f': [PC, PS5],
    "Dragon's Lair Trilogy": [PC, PS5, XBOX, NS],
    'Death Stranding 2': [PC, PS5],
    'Barbie Dreamhouse Adventure': [PC, PS5, XBOX, NS],
    'Barbie Horse Adventures: Riding Camp': [PC, PS5, XBOX],
    'Barbie Fashion Show': [PC, PS5, XBOX, NS],
    'Barbie Princess and the Popstar': [PC, PS5, XBOX, NS],
    'Barbie and Ken Vacation Paradise': [PC, PS5, XBOX, NS],
    'The Last of Us Part I': [PC, PS5],
    'The Last of Us Part II Remastered': [PS5],
    'Hitman World of Assassination': [PC, PS5, XBOX],
    'Horizon Forbidden West': [PC, PS5],
    'Forza Horizon 5': [PC, XBOX],
    'Suicide Squad: Kill the Justice League': [PC, PS5, XBOX],
    "Marvel's Midnight Suns": [PC, PS5, XBOX],
    'Dead Island 2': [PC, PS5, XBOX],
    'Sonic Frontiers': [PC, PS5, XBOX, NS],
    'Like a Dragon: Ishin': [PC, PS5, XBOX],
    'Warhammer 40K: Space Marine 2': [PC, PS5, XBOX],
    'Jusant': [PC, PS5, XBOX],
    'Outer Wilds': [PC, PS5, XBOX],
    'Disco Elysium': [PC, PS5, XBOX],
    'Dave the Diver': [PC, NS],
    'Trails into Reverie': [PC, PS5],
    "No Man's Sky": [PC, PS5, XBOX],
    'Dead Cells': [PC, PS5, XBOX, NS],
    'Hades': [PC, PS5, XBOX, NS],
    'Celeste': [PC, PS5, XBOX, NS],
    'Tunic': [PC, PS5, XBOX],
    'Return of the Obra Dinn': [PC, PS5, XBOX, NS],
    'Vampire Survivors': [PC, PS5, XBOX, NS],
    "Don't Starve Together": [PC, PS5, XBOX],
    'Oxygen Not Included': [PC],
    'Grounded': [PC, XBOX],
    'The Forgotten City': [PC, PS5, XBOX],
    'Norco': [PC],
    'Hardspace: Shipbreaker': [PC, PS5, XBOX],
    'Prodeus': [PC, PS5, XBOX],
    'Danganronpa Trilogy': [PC, PS5],
    'Untitled Goose Game': [PC, PS5, XBOX, NS],
    'A Short Hike': [PC, NS],
    'Baba Is You': [PC, NS],
    'Minit': [PC, PS5, XBOX, NS],
    'Papers Please': [PC],
    'Into the Breach': [PC, NS],
    'Loop Hero': [PC],
    'Katana ZERO': [PC, PS5, XBOX, NS],
    'Carrion': [PC, PS5, XBOX, NS],
    'Moonlighter': [PC, PS5, XBOX, NS],
    'Spiritfarer': [PC, PS5, XBOX, NS],
    'Path of Exile 2': [PC, PS5, XBOX],
    'Warframe': [PC, PS5, XBOX],
    'Genshin Impact': [PC, PS5],
}
for titulo, plats in juego_plats.items():
    jid = juego_map.get(titulo)
    if not jid:
        continue
    for pid in plats:
        if pid:
            cur.execute("INSERT OR IGNORE INTO juegos_plataformas VALUES (?,?)", (jid, pid))
conn.commit()

# ── Reglas del chatbot ────────────────────────────────────────
cur.execute("DELETE FROM chatbot_reglas")
reglas = [
    ('buenos dias manana madrugada', '¡Buenos días! ¿Qué juego estás buscando? Puedo ayudarte con precios, recomendaciones o lo que necesites.', 12),
    ('tardes tarde mediodia', '¡Buenas tardes! ¿En qué puedo ayudarte? Dime qué tipo de juego buscas o pregúntame lo que quieras.', 12),
    ('noches noche', '¡Buenas noches! ¿Buscas algo para jugar esta noche? Cuéntame y te ayudo.', 12),
    ('hola holi holii holiis saludos saludo buenas ola hey ey ei', '¡Hola! ¿Qué necesitas? Puedo ayudarte a buscar juegos, mostrar precios, o recomendarte algo.', 11),
    ('tal como estas pasa onda', '¡Aquí andamos! ¿Qué juego estás buscando? Cuéntame y te ayudo a encontrar algo.', 10),
    ('juegos baratos economicos precio bajo', 'Tenemos juegos desde 0 euros! Hollow Knight por 14.99, Stardew Valley por 13.99, y muchos gratuitos como Fortnite, Apex Legends y Rocket League.', 10),
    ('recomendacion recomienda que juego', 'Depende de lo que busques: para accion te recomiendo God of War Ragnarok o Spider-Man 2. Para RPG, Baldurs Gate 3 o The Witcher 3. Para multijugador, Helldivers 2 o It Takes Two.', 9),
    ('juegos para dos jugadores cooperativo coop', 'Para jugar en compania tienes It Takes Two, Baldurs Gate 3, Helldivers 2, Minecraft o Stardew Valley en modo cooperativo.', 9),
    ('juegos horror terror miedo', 'En horror tenemos Silent Hill 2 Remake, Resident Evil 4 Remake y Alan Wake 2. Todos excelentes si te gustan los sustos.', 9),
    ('juegos rpg rol', 'En RPG destacan Baldurs Gate 3, The Witcher 3, Dragon Dogma 2, Diablo IV y Final Fantasy VII Rebirth.', 9),
    ('juegos fps shooter disparos', 'Para shooters tenemos Call of Duty Black Ops 6, Valorant, Counter-Strike 2, Apex Legends y Helldivers 2.', 9),
    ('juegos mundo abierto open world', 'En mundo abierto tenemos GTA VI, Red Dead Redemption 2, The Witcher 3, Cyberpunk 2077, Hogwarts Legacy y Zelda Tears of the Kingdom.', 9),
    ('juegos gratis free to play gratuitos', 'Tenemos varios juegos completamente gratuitos: Fortnite, Apex Legends, Rocket League, Valorant, Counter-Strike 2, Marvel Rivals y Overwatch 2.', 9),
    ('juegos nintendo switch portatil', 'Para Nintendo Switch tenemos Zelda Tears of the Kingdom, Minecraft, Stardew Valley, Hollow Knight, EA Sports FC 25 y mas.', 9),
    ('juegos playstation ps5', 'Para PS5 tienes exclusivos como God of War Ragnarok, Spider-Man 2 y Final Fantasy VII Rebirth, ademas de todos los multiplataforma.', 9),
    ('juegos xbox', 'En Xbox Series X tienes Palworld, Call of Duty, Tekken 8, Diablo IV y todos los juegos multijugador multiplataforma.', 9),
    ('juegos deportes futbol baloncesto', 'En deportes tenemos EA Sports FC 25 para futbol y NBA 2K25 para baloncesto. Rocket League es futbol con coches.', 8),
    ('juegos lucha pelea combate', 'Para juegos de lucha tenemos Tekken 8 y Street Fighter 6, ambos con modos online y offline.', 8),
    ('juegos sandbox construccion', 'Para sandbox y construccion tienes Minecraft, Palworld y Stardew Valley.', 8),
    ('oferta descuento rebajado mas barato', 'Tenemos muchos juegos en oferta: The Witcher 3 a 9.99, Red Dead Redemption 2 a 14.99, Hollow Knight a 7.49, It Takes Two a 9.99 y muchos mas.', 10),
    ('mejor juego goty premiado', 'Los juegos mas premiados son Baldurs Gate 3 (GOTY 2023), The Witcher 3 (clasico) e It Takes Two (GOTY 2021).', 8),
    ('juego ninos familia familiar', 'Para los mas pequenos o en familia: Minecraft, Stardew Valley, Hollow Knight, Rocket League y Zelda Tears of the Kingdom.', 8),
    ('juegos indie independentes', 'Tenemos grandes indies: Hollow Knight, Hades II, Shovel Knight Dig, Balatro y Stardew Valley. Juegos especiales con mucha personalidad.', 9),
    ('juegos con buena historia narrativa', 'Para historias epicas: The Witcher 3, Red Dead Redemption 2, Baldurs Gate 3, Alan Wake 2, Death Stranding 2 y Like a Dragon Infinite Wealth.', 9),
    ('juegos estrategia tactica', 'En estrategia tenemos: Unicorn Overlord, Metaphor ReFantazio, Baldurs Gate 3 y Diablo IV con combate táctico.', 8),
    ('adios despedida hasta luego ciao', '¡Hasta luego! Gracias por visitar nuestra tienda. Vuelve cuando quieras. 😊', 11),
    ('ayuda soporte contacto problema', '¿Necesitas ayuda? Puedes contactarnos en overplayed@info.com o visitarnos en Alcalá de Henares. Estamos de lunes a sábado de 10:00 a 21:00.', 10),
    ('juegos pc windows ordenador computadora', 'Para PC tenemos: Alan Wake 2, Apex Legends, Avowed, Baldurs Gate 3, Balatro, Counter-Strike 2, Cyberpunk 2077, Diablo IV, Final Fantasy VII, Fortnite y muchos más.', 9),
    ('juegos multijugador online multiplayer', 'Para jugar online tienes: Call of Duty, Valorant, Counter-Strike 2, Apex Legends, Rocket League, Helldivers 2, Overwatch 2 y Palworld.', 9),
    ('juegos puzzle rompecabezas logica', 'Para puzzles tenemos: Balatro, Shovel Knight Dig, Portal 2 y Tetris Effect. Juegos que ejercitan la mente.', 8),
    ('juegos retro clasico antiguo vintage', 'Clásicos que siguen valiendo la pena jugar: Tetris Effect, Shovel Knight, Hollow Knight (indie moderno con estilo retro) y más.', 8),
    ('juegos racing carreras conduccion conducir', 'Para carreras tenemos: Le Mans Ultimate, F1 25, Forza Motorsport y Rocket League (futbol con coches).', 8),
    ('mas vendidos bestseller popular trending', 'Los más vendidos ahora son: Baldurs Gate 3, The Witcher 3, Call of Duty Black Ops 6, Dragon Dogma 2 y GTA VI.', 9),
    ('juegos sin conexion offline local single player', 'Perfecto para jugar sin internet: The Witcher 3, Red Dead Redemption 2, Baldurs Gate 3, Cyberpunk 2077, Death Stranding 2.', 8),
    ('juegos dos jugadores local couch coop', 'Para jugar en el sofá: It Takes Two, A Way Out, Minecraft cooperativo, Mario Party (Nintendo) y más.', 9),
    ('cuanto cuesta precio costo valor', 'Los precios varían. ¿Qué juego buscas? Tenemos desde 0€ (Fortnite) hasta 69.99€ (lanzamientos nuevos). Muchos están en oferta.', 9),
    ('regalos regalo para regalar sorpresa', 'Para regalar depende de gustos: God of War para fans de acción, Stardew Valley para relajarse, Minecraft para creatividad, o Zelda para Nintendo.', 8),
    ('sistema requisitos especificaciones minimos', 'Los requisitos varían por juego. PC necesita GPU/CPU modernas para juegos AAA. Consulta en Steam o pregunta por un juego específico.', 8),
    ('duda pregunta dudas confuso no entiendo', 'Claro, dime qué necesitas y te ayudaré. Puedo buscar juegos por nombre, plataforma, género, precio o hacer recomendaciones. ¿Qué buscas?', 10),
    ('novedades nuevos recientes lanzamientos estreno 2025 2026', 'Últimas novedades: GTA VI, Death Stranding 2, Final Fantasy VII Rebirth, Dragon Dogma 2, Avowed y Metaphor ReFantazio.', 9),
    ('juegos accion aventura plataformas', 'En acción y aventura tenemos: God of War Ragnarok, Spider-Man 2, Hogwarts Legacy, Alan Wake 2 y Death Stranding 2.', 8),
    ('puntuacion nota valoracion rating metacritic review', 'Pregúntame por un juego específico y te digo su puntuación en Metacritic y valoración de usuarios.', 7),
]

for r in reglas:
    cur.execute("""
        INSERT OR IGNORE INTO chatbot_reglas (palabras_clave, respuesta, prioridad, activo)
        VALUES (?, ?, ?, 1)
    """, r)

conn.commit()

# ── Índices únicos ─────────────────────────────────────────────
cur.execute("CREATE UNIQUE INDEX IF NOT EXISTS ux_desarrolladores_nombre ON desarrolladores (nombre)")
cur.execute("CREATE UNIQUE INDEX IF NOT EXISTS ux_juegos_titulo ON juegos (titulo)")
cur.execute("CREATE UNIQUE INDEX IF NOT EXISTS ux_juegos_generos ON juegos_generos (juego_id, genero_id)")
cur.execute("CREATE UNIQUE INDEX IF NOT EXISTS ux_juegos_plataformas ON juegos_plataformas (juego_id, plataforma_id)")
conn.commit()

# ── Resumen ────────────────────────────────────────────────────
cur.execute("SELECT COUNT(*) FROM juegos")
total_juegos = cur.fetchone()[0]

cur.execute("SELECT COUNT(*) FROM chatbot_reglas")
total_reglas = cur.fetchone()[0]

cur.execute("SELECT COUNT(*) FROM generos")
total_generos = cur.fetchone()[0]



conn.close()
print("Datos insertados con éxito")