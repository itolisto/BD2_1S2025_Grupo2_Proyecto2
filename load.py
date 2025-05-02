import pandas as pd
from sqlalchemy import create_engine
from pymongo import MongoClient
import pymysql

# Configuración de conexión MySQL
MYSQL_USER = "usac"
MYSQL_PASSWORD = "password"
MYSQL_HOST = "localhost"
MYSQL_PORT = "3306"
MYSQL_DB = "bases2"

# Configuración de conexión MongoDB
MONGO_URI = "mongodb://localhost:27017/"
MONGO_DB = "bases2"

# 1. Leer archivos Excel
pacientes = pd.read_excel("Pacientes.xlsx")
habitaciones = pd.read_excel("Habitaciones.xlsx")
log_actividades1 = pd.read_excel("LogActividades1.xlsx")
log_actividades2 = pd.read_excel("LogActividades2.xlsx")
log_habitacion = pd.read_excel("LogHabitacion.xlsx")

log_actividades = pd.concat([log_actividades1, log_actividades2], ignore_index=True)
log_actividades['fechaHora'] = pd.to_datetime(log_actividades['fechaHora'])
log_habitacion['fechaHora'] = pd.to_datetime(log_habitacion['fechaHora'])

# 2. Insertar en MySQL
print("Insertando datos en MySQL...")
engine = create_engine(f"mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DB}")

pacientes.to_sql("Pacientes", engine, if_exists="replace", index=False)
habitaciones.to_sql("Habitaciones", engine, if_exists="replace", index=False)
log_actividades.to_sql("LogActividades", engine, if_exists="replace", index=False)
log_habitacion.to_sql("LogHabitaciones", engine, if_exists="replace", index=False)

print("Datos insertados en MySQL.")

# 3. Insertar en MongoDB
print("Insertando datos en MongoDB...")
client = MongoClient(MONGO_URI)
mongo_db = client[MONGO_DB]
mongo_db.drop_collection("Pacientes")
mongo_db.drop_collection("Habitaciones")

# Construir documentos de pacientes con actividades embebidas
habitacion_map = habitaciones.set_index("idHabitacion")["nombre"].to_dict()

pacientes_docs = []
for _, row in pacientes.iterrows():
    actividades_paciente = log_actividades[log_actividades["idPaciente"] == row["idPaciente"]]
    actividades = []
    for _, act in actividades_paciente.iterrows():
        actividades.append({
            "fechaHora": act["fechaHora"],
            "actividad": act["actividad"],
            "habitacion": {
                "idHabitacion": int(act["idHabitacion"]),
                "nombre": habitacion_map.get(act["idHabitacion"], "Desconocida")
            }
        })
    pacientes_docs.append({
        "_id": int(row["idPaciente"]),
        "edad": int(row["edad"]),
        "genero": row["genero"],
        "actividades": actividades
    })

# Construir documentos de habitaciones con estados embebidos
habitaciones_docs = []
for _, row in habitaciones.iterrows():
    estados = log_habitacion[log_habitacion["idHabitacion"] == row["idHabitacion"]]
    estados_list = []
    for _, est in estados.iterrows():
        estados_list.append({
            "fechaHora": est["fechaHora"],
            "estado": est["estado"]
        })
    habitaciones_docs.append({
        "_id": int(row["idHabitacion"]),
        "nombre": row["nombre"],
        "estados": estados_list
    })

# Insertar en MongoDB
mongo_db.Pacientes.insert_many(pacientes_docs)
mongo_db.Habitaciones.insert_many(habitaciones_docs)

print("Datos insertados en MongoDB.")
