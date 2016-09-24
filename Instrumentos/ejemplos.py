# -*- coding: utf-8 -*-
"""
Created on Tue Sep 13 22:07:01 2016

@author: Alejandro
"""
import time
import numpy as np
import matplotlib.style
import matplotlib.pyplot as plt
from instrumentos import Lockin

#%% Se crea un Lockin en modo simulador
loc1 = Lockin(modo_simulador=True)

#%% Se listan las propiedades del Lockin
loc1.listarPropiedades()

# Se ejecutan autofunciones
loc1.autoFase()
loc1.autoGanacia()
loc1.autoOffset(1)
loc1.autoOffset(2)
loc1.autoOffset(3)
loc1.autoReserva()

#%% Se modifican las propiedades

loc1.refAmpl = 1
loc1.refFase = 0
loc1.refFrec = 1000
loc1.refHarm = 1
loc1.refModo = 'Internal'
loc1.refRslp = 'Sine'

loc1.auxout1 = 0
loc1.auxout2 = 0
loc1.auxout3 = 0
loc1.auxout4 = 0

loc1.inpCoup = 'AC'
loc1.inpGnd = 'Float'
loc1.inpLine = 'Out'
loc1.inpModo = 'A'
loc1.inpOfsl = '12dB/oct'
loc1.inpOflt = '100 ms'
loc1.inpRmod = 'Low Noise'
loc1.inpSens = 1.0
loc1.inpSync = 'Off'

loc1.ch1Modo = 'X'
loc1.ch2Modo = 'Y'

#%% Crea un archivo .log con los parámetros utilizados
    
loc1.crearRegistro(archivoLog='LockinSR830.log')

#%% Lecturas simples

print('Entrada 1: ' + str(loc1.consultarAuxiliar(aux=1)) + 'V')
print('Entrada 2: ' + str(loc1.consultarAuxiliar(aux=2)) + 'V')
print('Entrada 3: ' + str(loc1.consultarAuxiliar(aux=3)) + 'V')
print('Entrada 4: ' + str(loc1.consultarAuxiliar(aux=4)) + 'V')

print('Canal 1: ' + loc1.ch1Modo + '=' + str(loc1.consultarDisplay(canal=1)))
print('Canal 2: ' + loc1.ch2Modo + '=' + str(loc1.consultarDisplay(canal=2)))

print('Valor de R: ' + str(loc1.consultarValor(valor='R')))

#%% Lectura simultánea

parametros = 'Frec', 'X', 'Y', 'R'
resultados = loc1.consultarSimultaneo(*parametros)

for i in range(len(parametros)):
    print(parametros[i] + ' = ' + str(resultados[i]))
    
#%% Barrido de frecuencia
    
parametros = 'X', 'Y', 'R'
resultados = loc1.barrerFrecuencia(100,200,100,2,*parametros)
    
#%% Lectura del buffer

x, y, fig = loc1.leerBuffer(canal=1, frecMuestreo='64 Hz', puntos = 100, 
                            graficar=True, archivoDatos='Buffer.csv')
                        
#%% Almacenamiento y carga de datos
                        
loc1.guardarDatos(archivoDatos='Datos.csv', datos=[x,y], nombre_columnas='X, Y')
x2, y2 = loc1.cargarDatos(archivoDatos='Datos.csv')
