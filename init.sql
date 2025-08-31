-- Crear tabla de mascotas
CREATE TABLE IF NOT EXISTS mascotas (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(50) NOT NULL,
    especie VARCHAR(30) NOT NULL,
    edad INT NOT NULL
);

-- Insertar datos de ejemplo
INSERT INTO mascotas (nombre, especie, edad) VALUES
('Firulais', 'Perro', 4),
('Misu', 'Gato', 2),
('Rocky', 'Perro', 7),
('Nala', 'Gato', 3);
