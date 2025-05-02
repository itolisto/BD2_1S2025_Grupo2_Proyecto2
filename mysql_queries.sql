-- 1. Total de pacientes por categoría de edad (Pediátrico, Mediana edad, Geriátrico)

SELECT
  CASE
    WHEN edad < 18 THEN 'Pediátrico'
    WHEN edad BETWEEN 18 AND 60 THEN 'Mediana edad'
    ELSE 'Geriátrico'
  END AS categoria_edad,
  COUNT(*) AS total_pacientes
FROM Pacientes
GROUP BY categoria_edad;

-- 2. Cantidad de pacientes que pasan por cada habitación

SELECT h.nombre AS habitacion,
       COUNT(DISTINCT a.idPaciente) AS total_pacientes
FROM Habitaciones AS h
JOIN LogActividades AS a
  ON a.idHabitacion = h.idHabitacion
GROUP BY h.idHabitacion, h.nombre;

-- 3. Cantidad de pacientes que llegan a la clínica, agrupados por género

SELECT genero, COUNT(*) AS total_pacientes
FROM Pacientes
GROUP BY genero;

-- 4. Top 5 edades más atendidas en la clínica

SELECT edad, COUNT(*) AS total_pacientes
FROM Pacientes
GROUP BY edad
ORDER BY total_pacientes DESC
LIMIT 5;

-- 5. Top 5 edades menos atendidas en la clínica

SELECT edad, COUNT(*) AS total_pacientes
FROM Pacientes
GROUP BY edad
ORDER BY total_pacientes ASC
LIMIT 5;

-- 6. Top 5 habitaciones más utilizadas

SELECT h.nombre AS habitacion,
       COUNT(DISTINCT a.idPaciente) AS pacientes_atendidos
FROM Habitaciones AS h
LEFT JOIN LogActividades AS a
  ON a.idHabitacion = h.idHabitacion
GROUP BY h.idHabitacion, h.nombre
ORDER BY pacientes_atendidos DESC
LIMIT 5;

-- 7. Top 5 habitaciones menos utilizadas

SELECT h.nombre AS habitacion,
       COUNT(DISTINCT a.idPaciente) AS pacientes_atendidos
FROM Habitaciones AS h
LEFT JOIN LogActividades AS a
  ON a.idHabitacion = h.idHabitacion
GROUP BY h.idHabitacion, h.nombre
ORDER BY pacientes_atendidos ASC
LIMIT 5;

-- 8. Día con más pacientes en la clínica

SELECT DATE(a.fechaHora) AS fecha,
       COUNT(DISTINCT a.idPaciente) AS pacientes_unicos
FROM LogActividades AS a
GROUP BY DATE(a.fechaHora)
ORDER BY pacientes_unicos DESC
LIMIT 1;
