# -*- coding: utf-8 -*-
import sqlite3

#################################################################
# Ejercicio 1 - Crear base de datos
#################################################################

sqlite_connection = sqlite3.connect('interfaz.db')

#################################################################
# Ejercicio 2 - Insertar valores
#################################################################


sqlite_cursor = sqlite_connection.cursor()
sqlite_cursor.execute('CREATE TABLE padron(\
                        dni INT PRIMARY KEY NOT NULL,\
                        nombre CHAR(50) NOT NULL,\
                        edad INT NOT NULL,\
                        residencia TEXT NOT NULL)')
sqlite_connection.commit()

personas = [(323421234, 'Paola', 25, 'Buenos Aires'),
            (323421235, 'Ezequiel', 22, 'Buenos Aires'),
            (323421236, 'Pamela', 24, 'Buenos Aires'),
            (323421237, 'Ignacio', 50, 'Buenos Aires'),
            (323421238, 'Talia', 49, 'Buenos Aires'),
            (323421239, 'Armando', 18, 'Buenos Aires'),
            (323421210, 'Pedro', 70, 'Buenos Aires'),
            (323421211, 'Ines', 65, 'Buenos Aires'),
            (323421212, 'Santiago', 60, 'Buenos Aires'),
            (323421213, 'Tomas', 22, 'Cordoba'),
            (323421214, 'Octavio', 23, 'Buenos Aires'),
            (323421215, 'Luciano', 25, 'Cordoba'),
            (323421216, 'Esteban', 24, 'Buenos Aires'),
            (323421217, 'Ramiro', 27, 'Cordoba'),
            (323421218, 'Agustin', 21, 'Cordoba')]

sqlite_cursor.executemany('INSERT INTO padron VALUES (?, ?, ?, ?)', personas)
sqlite_connection.commit()

#################################################################
# Ejercicio 3 - Realizar consutlas sobre la base de datos
#################################################################


print ('Nombre de personas con edad menor a 30')

for row in sqlite_cursor.execute('SELECT nombre FROM padron WHERE edad < 30'):
    print(row[0])


sqlite_cursor.execute('SELECT COUNT(*) FROM padron WHERE residencia = \'Cordoba\'')
print('')
print('Cantidad de personas que viven en Cordoba: ' + str(sqlite_cursor.fetchone()[0]))

##################################################################
# Ejercicio 4 - Realizar actualizaciones sobre los datos cargados
##################################################################

sqlite_cursor.execute('UPDATE padron SET residencia = \'Cordoba Capital\' WHERE residencia = \'Cordoba\'')
sqlite_connection.commit()

##################################################################
# Ejercicio 5 - Borrar algunos de los registros cargados 
##################################################################

sqlite_cursor.execute('DELETE FROM padron WHERE dni = 323421234')
sqlite_cursor.execute('DELETE FROM padron WHERE nombre = \'Ezequiel\'')
sqlite_connection.commit()

##################################################################
# Ejercicio 6 - Mostrar todas las tablas definidas en la BD 
##################################################################
print('')
print('Tablas:')

for row in sqlite_cursor.execute('SELECT name FROM sqlite_master WHERE type=\'table\''):
    print row[0]

##################################################################
# Ejercicio 7 - Agregar algunos indices en la tabla
##################################################################

sqlite_cursor.execute('CREATE UNIQUE INDEX index_dni on padron (dni)')
sqlite_cursor.execute('CREATE INDEX index_edad ON padron (edad)')
sqlite_connection.commit()

##################################################################
# Ejercicio 8 - Listar todas las tablas de la BD
# Ejercicio 9 - Listar indices existentes
# Ejercicio 10 - Listar columnas de las tablas
##################################################################
print('')
print('Lista de tablas')
print('')

for row in sqlite_cursor.execute('SELECT name FROM sqlite_master WHERE type=\'table\''):
    print 'Tabla: ' + row[0]
    print('')
    columns = []
    for row_two in sqlite_cursor.execute('PRAGMA table_info(\''+row[0]+'\')'):
        columns.append(row_two[1])
    print(' | '.join(columns))
    for row_data in sqlite_cursor.execute('SELECT * FROM ' +row[0]):
        print row_data
