# -*- coding: utf-8 -*-

import time
import numpy as np
import matplotlib.style
import matplotlib.pyplot as plt
from instrumentos import Lockin

#%% Se crea un Lockin
loc1 = Lockin()

#%% Primera medicion

nombres = ('Vacio', 'Bronce13mm', 'Aluminio13mm', 'Aluminio9mm', 'Cobre9mm4')

for nombre in nombres:
    input('Medicion: ' + nombre + '. Presione enter...' )
    loc1.crearRegistro(nombre + '.log')
    f, datos, fig = loc1.barrerFrecuencia(100,20000,100,2,'X','Y')
    fig.savefig(nombre + '.png')
    loc1.guardarDatos(nombre + '.csv',[f,datos[0],datos[1]],'F,X,Y')


#%% Segunda medición

nombres = ('Vacio', 'Bronce13mm', 'Aluminio13mm', 'Aluminio9mm', 'Cobre9mm4')

for nombre in nombres:
    input('Medicion: ' + nombre + '. Presione enter...' )
    loc1.crearRegistro(nombre + '.log')
    f, datos, fig = loc1.barrerFrecuencia(100,20000,2000,2,'X','Y')
    fig.savefig(nombre + '.png')
    loc1.guardarDatos(nombre + '.csv',[f,datos[0],datos[1]],'F,X,Y')

#%% Tercera medición
nombres = ('0cm', '1cm', '2cm', '3cm', '4cm', '5cm', '6cm', '7cm', 
           '8cm', '9cm')

for nombre in nombres:
    input('Medicion: ' + nombre + '. Presione enter...' )
    loc1.crearRegistro(nombre + '.log')
    f, datos, fig = loc1.barrerFrecuencia(100,20000,100,3,'X','Y','R')
    fig.savefig(nombre + '.png')
    loc1.guardarDatos(nombre + '.csv',[f,datos[0],datos[1]],'F,X,Y,R')

#%% Tercera medición medios centimetros
nombres = ('0.5cm', '1.5cm', '2.5cm', '3.5cm', '4.5cm', '5.5cm', '6.5cm', 
           '7.5cm', '8.5cm', '9.5cm')

for nombre in nombres:
    input('Medicion: ' + nombre + '. Presione enter...' )
    loc1.crearRegistro(nombre + '.log')
    f, datos, fig = loc1.barrerFrecuencia(100,20000,100,3,'X','Y','R')
    fig.savefig(nombre + '.png')
    loc1.guardarDatos(nombre + '.csv',[f,datos[0],datos[1]],'F,X,Y,R')


#%% Cuarta medición

N = 700
datos = np.zeros(N)
for i in loc1._barraProgreso(N):
    datos[i] = loc1.consultarValor(valor='R')


#%% Quinta medición

nombres = ('Vacio', 'Bronce13mm', 'Aluminio13mm', 'Aluminio9mm', 'Cobre9mm4')

for nombre in nombres:
    input('Medicion: ' + nombre + '. Presione enter...' )
    loc1.crearRegistro(nombre + '.log')
    f, datos, fig = loc1.barrerFrecuencia(100,20000,200,1,'T','R','X','Y')
    fig.savefig(nombre + '.png')
    loc1.guardarDatos(nombre + '.csv',[f,datos[0],datos[1]],'F,Theta,R,X,Y')

#%% Sexta medición

nombres = ('Vacio', 'Acero')

for nombre in nombres:
    input('Medicion: ' + nombre + '. Presione enter...' )
    loc1.crearRegistro(nombre + '.log')
    f, datos, fig = loc1.barrerFrecuencia(100,20000,1000,1,'T','R','X','Y')
    fig.savefig(nombre + '.png')
    loc1.guardarDatos(nombre + '.csv',[f,datos[0],datos[1]],'F,Theta,R,X,Y')

