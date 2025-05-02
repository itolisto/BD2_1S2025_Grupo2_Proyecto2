import time
import pandas as pd
import numpy as np
import pymysql
from sqlalchemy import create_engine, text
from pymongo import MongoClient
from pymongo.errors import OperationFailure

# Configuración
MYSQL_CONFIG = {
    "user": "usac",
    "password": "password",
    "host": "localhost",
    "port": 3306,
    "db": "bases2"
}
MONGO_URI = "mongodb://localhost:27017/"
MONGO_DB = "bases2"

REPEATS = 100

# Consultas MySQL
mysql_queries = {
    "pacientes_por_categoria_edad": """
        SELECT
            CASE
                WHEN edad < 18 THEN 'Pediátrico'
                WHEN edad BETWEEN 18 AND 60 THEN 'Mediana edad'
                ELSE 'Geriátrico'
            END AS categoria_edad,
            COUNT(*) AS total_pacientes
        FROM Pacientes
        GROUP BY categoria_edad;
    """,
    "pacientes_por_habitacion": """
        SELECT h.idHabitacion, h.habitacion, COUNT(DISTINCT l.idPaciente) AS total_pacientes
        FROM Habitaciones h
        JOIN LogActividades l ON h.idHabitacion = l.idHabitacion
        GROUP BY h.idHabitacion, h.habitacion;
    """,
    "pacientes_por_genero": """
        SELECT genero, COUNT(*) AS total_pacientes
        FROM Pacientes
        GROUP BY genero;
    """,
    "top_5_edades_mas_atendidas": """
        SELECT edad, COUNT(*) AS total
        FROM Pacientes
        GROUP BY edad
        ORDER BY total DESC
        LIMIT 5;
    """,
    "top_5_edades_menos_atendidas": """
        SELECT edad, COUNT(*) AS total
        FROM Pacientes
        GROUP BY edad
        ORDER BY total ASC
        LIMIT 5;
    """,
    "top_5_habitaciones_mas_utilizadas": """
        SELECT h.idHabitacion, h.habitacion, COUNT(DISTINCT l.idPaciente) AS total
        FROM Habitaciones h
        JOIN LogActividades l ON h.idHabitacion = l.idHabitacion
        GROUP BY h.idHabitacion, h.habitacion
        ORDER BY total DESC
        LIMIT 5;
    """,
    "top_5_habitaciones_menos_utilizadas": """
        SELECT h.idHabitacion, h.habitacion, COUNT(DISTINCT l.idPaciente) AS total
        FROM Habitaciones h
        JOIN LogActividades l ON h.idHabitacion = l.idHabitacion
        GROUP BY h.idHabitacion, h.habitacion
        ORDER BY total ASC
        LIMIT 5;
    """,
    "dia_con_mas_pacientes": """
        SELECT DATE(fechaHora) AS fecha, COUNT(DISTINCT idPaciente) AS total
        FROM LogActividades
        GROUP BY DATE(fechaHora)
        ORDER BY total DESC
        LIMIT 1;
    """
}

# Consultas MongoDB
mongo_queries = {
    "pacientes_por_categoria_edad": [
        {"$group": {
            "_id": {
                "$cond": [
                    {"$lt": ["$edad", 18]}, "Pediátrico",
                    {"$cond": [{"$gt": ["$edad", 60]}, "Geriátrico", "Mediana edad"]}
                ]
            },
            "total_pacientes": {"$sum": 1}
        }}
    ],
    "pacientes_por_habitacion": [
        {"$unwind": "$actividades"},
        {"$group": {
            "_id": "$actividades.habitacion.idHabitacion",
            "total_pacientes": {"$addToSet": "$_id"}
        }},
        {"$project": {"total_pacientes": {"$size": "$total_pacientes"}}}
    ],
    "pacientes_por_genero": [
        {"$group": {"_id": "$genero", "total": {"$sum": 1}}}
    ],
    "top_5_edades_mas_atendidas": [
        {"$group": {"_id": "$edad", "total": {"$sum": 1}}},
        {"$sort": {"total": -1}},
        {"$limit": 5}
    ],
    "top_5_edades_menos_atendidas": [
        {"$group": {"_id": "$edad", "total": {"$sum": 1}}},
        {"$sort": {"total": 1}},
        {"$limit": 5}
    ],
    "top_5_habitaciones_mas_utilizadas": [
        {"$unwind": "$actividades"},
        {"$group": {
            "_id": "$actividades.habitacion.idHabitacion",
            "pacientes": {"$addToSet": "$_id"}
        }},
        {"$project": {"total": {"$size": "$pacientes"}}},
        {"$sort": {"total": -1}},
        {"$limit": 5}
    ],
    "top_5_habitaciones_menos_utilizadas": [
        {"$unwind": "$actividades"},
        {"$group": {
            "_id": "$actividades.habitacion.idHabitacion",
            "pacientes": {"$addToSet": "$_id"}
        }},
        {"$project": {"total": {"$size": "$pacientes"}}},
        {"$sort": {"total": 1}},
        {"$limit": 5}
    ],
    "dia_con_mas_pacientes": [
        {"$unwind": "$actividades"},
        {"$group": {
            "_id": {"$dateToString": {"format": "%Y-%m-%d", "date": "$actividades.fechaHora"}},
            "pacientes": {"$addToSet": "$_id"}
        }},
        {"$project": {"total": {"$size": "$pacientes"}}},
        {"$sort": {"total": -1}},
        {"$limit": 1}
    ]
}

# Conexiones
engine = create_engine(
    f"mysql+pymysql://{MYSQL_CONFIG['user']}:{MYSQL_CONFIG['password']}@{MYSQL_CONFIG['host']}:{MYSQL_CONFIG['port']}/{MYSQL_CONFIG['db']}")
mongo_client = MongoClient(MONGO_URI)
mongo_db = mongo_client[MONGO_DB]

# Resultados almacenados por consulta
timings = {}

print("🔁 Ejecutando benchmark (100 iteraciones por consulta)...")

# Benchmark MySQL
for name, query in mysql_queries.items():
    mysql_times = []
    for _ in range(REPEATS):
        start = time.time()
        with engine.connect() as conn:
            conn.execute(text(query)).fetchall()
        mysql_times.append(time.time() - start)
    timings[name] = {
        "MySQL avg (s)": round(np.mean(mysql_times), 5),
        "MySQL med (s)": round(np.median(mysql_times), 5),
        "MySQL p90 (s)": round(np.percentile(mysql_times, 90), 5),
    }

# Benchmark MongoDB
for name, pipeline in mongo_queries.items():
    mongo_times = []
    for _ in range(REPEATS):
        start = time.time()
        try:
            list(mongo_db["Pacientes"].aggregate(pipeline))
        except OperationFailure:
            mongo_times.append(None)
            continue
        mongo_times.append(time.time() - start)
    if name not in timings:
        timings[name] = {}
    valid_times = [t for t in mongo_times if t is not None]
    if valid_times:
        timings[name].update({
            "Mongo avg (s)": round(np.mean(valid_times), 5),
            "Mongo med (s)": round(np.median(valid_times), 5),
            "Mongo p90 (s)": round(np.percentile(valid_times, 90), 5),
        })
    else:
        timings[name].update({
            "Mongo avg (s)": None,
            "Mongo med (s)": None,
            "Mongo p90 (s)": None,
        })

# Mostrar resultados
df = pd.DataFrame.from_dict(timings, orient="index")
print("\n⏱️ Estadísticas de ejecución (100 repeticiones):\n")
print(df.to_markdown(tablefmt="grid"))