from fastapi import FastAPI, HTTPException, Depends, Query
from pydantic import BaseModel
import aiomysql
from typing import List, Optional
import os
from dotenv import load_dotenv
from pymongo import MongoClient

# Cargar variables de entorno desde el archivo .env
load_dotenv()

app = FastAPI()

DB_CONFIG = {
    "host": os.getenv('DBSERVICE'),
    "user": os.getenv('DB_USER'),
    "password": os.getenv('DB_PASSWORD'),
    "db": os.getenv('DB_NAME')
}

async def get_db_connection():
    return await aiomysql.connect(**DB_CONFIG)



MONGO_URI = os.getenv("MONGO_URI")
MONGO_DB = os.getenv("MONGO_DB")
mongo_client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
mongo_db = mongo_client[MONGO_DB]

### MYSQL

# ---- 1. Total de pacientes que llegan a la clínica por edad catalogados por lassiguientes categorías
# a. Pediátrico: menores de 18 años
# b. Mediana edad: entre 18 y 60 años
# c. Geriátrico: mayores de 60 años ----

@app.get("/pacientes_por_categoria_edad")
async def obtener_pacientes_por_categoria_edad():
    query = """
        SELECT
            CASE
                WHEN edad < 18 THEN 'Pediátrico'
                WHEN edad BETWEEN 18 AND 60 THEN 'Mediana edad'
                ELSE 'Geriátrico'
            END AS categoria_edad,
            COUNT(*) AS total_pacientes
        FROM Pacientes
        GROUP BY categoria_edad;
    """
    try:
        conn = await get_db_connection()
        async with conn.cursor(aiomysql.DictCursor) as cursor:
            await cursor.execute(query)
            result = await cursor.fetchall()
        conn.close()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")


### mongo 1

@app.get("/pacientes_por_categoria_edad_mongo")
def pacientes_por_categoria_edad_mongo():
    pipeline = [
        {
            "$group": {
                "_id": {
                    "$cond": [
                        {"$lt": ["$edad", 18]}, "Pediátrico",
                        {"$cond": [{"$gt": ["$edad", 60]}, "Geriátrico", "Mediana edad"]}
                    ]
                },
                "total_pacientes": {"$sum": 1}
            }
        },
        {
            "$project": {
                "categoria_edad": "$_id",
                "total_pacientes": 1,
                "_id": 0
            }
        }
    ]
    try:
        result = list(mongo_db["Pacientes"].aggregate(pipeline))
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))




# ------ 2. Cantidad de pacientes que pasan por cada habitación ------

@app.get("/pacientes_por_habitacion")
async def obtener_pacientes_por_habitacion():
    query = """
        SELECT h.idHabitacion, h.habitacion, COUNT(DISTINCT l.idPaciente) AS total_pacientes
                FROM Habitaciones h
                JOIN LogActividades l ON h.idHabitacion = l.idHabitacion
                GROUP BY h.idHabitacion, h.habitacion;
    """
    try:
        conn = await get_db_connection()
        async with conn.cursor(aiomysql.DictCursor) as cursor:
            await cursor.execute(query)
            result = await cursor.fetchall()
        conn.close()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")


### mongo 2

@app.get("/pacientes_por_habitacion_mongo")
def pacientes_por_habitacion_mongo():
    pipeline = [
        { "$unwind": "$actividades" },
        {
            "$group": {
            "_id": "$actividades.habitacion.idHabitacion",
            "nombre_habitacion": { "$first": "$actividades.habitacion.nombre" },
            "pacientes_unicos": { "$addToSet": "$_id" }
            }
        },
        {
            "$project": {
            "habitacion": "$nombre_habitacion",
            "total_pacientes": { "$size": "$pacientes_unicos" },
            "_id": 0
            }
        },
        { "$sort": { "total_pacientes": -1 } }
    ]
    try:
        result = list(mongo_db["Pacientes"].aggregate(pipeline))
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))




# ------ 3. Cantidad de pacientes que llegan a la clínica, agrupados por género ------

@app.get("/pacientes_por_genero")
async def obtener_pacientes_por_genero():
    query = """
         SELECT genero, COUNT(*) AS total_pacientes
        FROM Pacientes
        GROUP BY genero;
    """
    try:
        conn = await get_db_connection()
        async with conn.cursor(aiomysql.DictCursor) as cursor:
            await cursor.execute(query)
            result = await cursor.fetchall()
        conn.close()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

### mongo 3

@app.get("/pacientes_por_genero_mongo")
def pacientes_por_genero_mongo():
    pipeline = [
        {
            "$group": {
                "_id": "$genero",
                "total_pacientes": {"$sum": 1}
            }
        },
        {
            "$project": {
                "genero": "$_id",
                "total_pacientes": 1,
                "_id": 0
            }
        }
    ]
    try:
        result = list(mongo_db["Pacientes"].aggregate(pipeline))
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ------ 4. Top 5 edades más atendidas en la clínica ------

@app.get("/top_5_edades_mas_atendidas")
async def obtener_top_5_edades_mas_atendidas():
    query = """
        SELECT edad, COUNT(*) AS total
        FROM Pacientes
        GROUP BY edad
        ORDER BY total DESC
        LIMIT 5;
    """
    try:
        conn = await get_db_connection()
        async with conn.cursor(aiomysql.DictCursor) as cursor:
            await cursor.execute(query)
            result = await cursor.fetchall()
        conn.close()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")


### mongo 4


@app.get("/top_5_edades_mas_atendidas_mongo")
def top_5_edades_mas_atendidas_mongo():
    pipeline = [
        {
            "$group": {
                "_id": "$edad",
                "total_pacientes": {"$sum": 1}
            }
        },
        {
            "$sort": {"total_pacientes": -1}
        },
        {
            "$limit": 5
        },
        {
            "$project": {
                "edad": "$_id",
                "total_pacientes": 1,
                "_id": 0
            }
        }
    ]
    try:
        result = list(mongo_db["Pacientes"].aggregate(pipeline))
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



# ------ 5. Top 5 edades menos atendidas en la clínica ------

    
@app.get("/top_5_edades_menos_atendidas")
async def obtener_top_5_edades_menos_atendidas():
    query = """
        SELECT edad, COUNT(*) AS total
        FROM Pacientes
        GROUP BY edad
        ORDER BY total ASC
        LIMIT 5;
    """
    try:
        conn = await get_db_connection()
        async with conn.cursor(aiomysql.DictCursor) as cursor:
            await cursor.execute(query)
            result = await cursor.fetchall()
        conn.close()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")


### mongo 5

@app.get("/top_5_edades_menos_atendidas_mongo")
def top_5_edades_menos_atendidas_mongo():
    pipeline = [
        {"$group": {"_id": "$edad", "total_pacientes": {"$sum": 1}}},
        {"$sort": {"total_pacientes": 1}},
        {"$limit": 5},
        {"$project": {"edad": "$_id", "total_pacientes": 1, "_id": 0}}
    ]
    try:
        result = list(mongo_db["Pacientes"].aggregate(pipeline))
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    
# ------ 6. Top 5 habitaciones más utilizadas ------

@app.get("/top_5_habitaciones_mas_utilizadas")
async def obtener_top_5_habitaciones_mas_utilizadas():
    query = """
        SELECT h.idHabitacion, h.habitacion, COUNT(DISTINCT l.idPaciente) AS total
        FROM Habitaciones h
        JOIN LogActividades l ON h.idHabitacion = l.idHabitacion
        GROUP BY h.idHabitacion, h.habitacion
        ORDER BY total DESC
        LIMIT 5;
    """
    try:
        conn = await get_db_connection()
        async with conn.cursor(aiomysql.DictCursor) as cursor:
            await cursor.execute(query)
            result = await cursor.fetchall()
        conn.close()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

#### mongo 6


@app.get("/top_5_habitaciones_mas_utilizadas_mongo")
def top_5_habitaciones_mas_utilizadas_mongo():
    pipeline = [
        {"$unwind": "$actividades"},
        {
            "$group": {
                "_id": "$actividades.habitacion.idHabitacion",
                "nombre_habitacion": {"$first": "$actividades.habitacion.nombre"},
                "pacientes_unicos": {"$addToSet": "$_id"}
            }
        },
        {
            "$project": {
                "habitacion": "$nombre_habitacion",
                "total_pacientes": {"$size": "$pacientes_unicos"},
                "_id": 0
            }
        },
        {"$sort": {"total_pacientes": -1}},
        {"$limit": 5}
    ]
    try:
        result = list(mongo_db["Pacientes"].aggregate(pipeline))
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ------ 7. Top 5 habitaciones menos utilizadas ------

@app.get("/top_5_habitaciones_menos_utilizadas")
async def obtener_top_5_habitaciones_menos_utilizadas():
    query = """
        SELECT h.idHabitacion, h.habitacion, COUNT(DISTINCT l.idPaciente) AS total
        FROM Habitaciones h
        JOIN LogActividades l ON h.idHabitacion = l.idHabitacion
        GROUP BY h.idHabitacion, h.habitacion
        ORDER BY total ASC
        LIMIT 5;
    """
    try:
        conn = await get_db_connection()
        async with conn.cursor(aiomysql.DictCursor) as cursor:
            await cursor.execute(query)
            result = await cursor.fetchall()
        conn.close()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")


### mongo 7


@app.get("/top_5_habitaciones_menos_utilizadas_mongo")
def top_5_habitaciones_menos_utilizadas_mongo():
    pipeline = [
        {"$unwind": "$actividades"},
        {
            "$group": {
                "_id": "$actividades.habitacion.idHabitacion",
                "nombre_habitacion": {"$first": "$actividades.habitacion.nombre"},
                "pacientes_unicos": {"$addToSet": "$_id"}
            }
        },
        {
            "$project": {
                "habitacion": "$nombre_habitacion",
                "total_pacientes": {"$size": "$pacientes_unicos"},
                "_id": 0
            }
        },
        {"$sort": {"total_pacientes": 1}},
        {"$limit": 5}
    ]
    try:
        result = list(mongo_db["Pacientes"].aggregate(pipeline))
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ------ 8. Día con más pacientes en la clínica ------

@app.get("/dia_con_mas_pacientes")
async def obtener_dia_con_mas_pacientes():
    query = """
        SELECT DATE(fechaHora) AS fecha, COUNT(DISTINCT idPaciente) AS total
        FROM LogActividades
        GROUP BY DATE(fechaHora)
        ORDER BY total DESC
        LIMIT 1;
    """
    try:
        conn = await get_db_connection()
        async with conn.cursor(aiomysql.DictCursor) as cursor:
            await cursor.execute(query)
            result = await cursor.fetchall()
        conn.close()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")


#### mongo 8

@app.get("/dia_con_mas_paciente_mongo")
def dia_con_mas_paciente_mongo():
    pipeline = [
        {"$unwind": "$actividades"},
        {
            "$group": {
                "_id": {"$dateToString": {"format": "%Y-%m-%d", "date": "$actividades.fechaHora"}},
                "pacientes_unicos": {"$addToSet": "$_id"}
            }
        },
        {
            "$project": {
                "fecha": "$_id",
                "total_pacientes": {"$size": "$pacientes_unicos"},
                "_id": 0
            }
        },
        {"$sort": {"total_pacientes": -1}},
        {"$limit": 1}
    ]
    try:
        result = list(mongo_db["Pacientes"].aggregate(pipeline))
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



@app.get("/")
async def root():
    return {"message": "Ready API python fastapi"}

