CREATE TABLE Pacientes (
  idPaciente    INT          PRIMARY KEY,
  edad          INT          NOT NULL,
  genero        VARCHAR(20)  NOT NULL
);

CREATE TABLE Habitaciones (
  idHabitacion  INT          PRIMARY KEY,
  nombre        VARCHAR(100) NOT NULL
);

CREATE TABLE LogActividades (
  idLogActividad  INT           AUTO_INCREMENT PRIMARY KEY,
  idPaciente      INT           NOT NULL,
  idHabitacion    INT           NOT NULL,
  fechaHora       DATETIME      NOT NULL,
  actividad       VARCHAR(255)  NOT NULL,
  FOREIGN KEY (idPaciente)   REFERENCES Pacientes(idPaciente),
  FOREIGN KEY (idHabitacion) REFERENCES Habitaciones(idHabitacion)
);

CREATE TABLE LogHabitaciones (
  idLogHabitacion  INT           AUTO_INCREMENT PRIMARY KEY,
  idHabitacion     INT           NOT NULL,
  fechaHora        DATETIME      NOT NULL,
  estado           VARCHAR(100)  NOT NULL,
  FOREIGN KEY (idHabitacion) REFERENCES Habitaciones(idHabitacion)
);
