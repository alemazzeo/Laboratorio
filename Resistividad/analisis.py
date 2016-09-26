# -*- coding: utf-8 -*-

import numpy as np
import matplotlib.pyplot as plt
#import matplotlib.style as pltstyle
import matplotlib.ticker as mtick
from scipy import stats
#pltstyle.use('seaborn-white')

#%% CARGA DE DATOS

import os
#os.chdir(r'/Susceptibilidad y conductividad/Datos (día 2)')

muestras = ('Vacio', 'Bronce13mm', 'Aluminio13mm', 'Aluminio9mm', 'Cobre9mm4')

ruta = {
'Primera medición - 100 pts': 
    ('Vacio', 'Bronce13mm', 'Aluminio13mm', 'Aluminio9mm', 'Cobre9mm4'),
'Segunda medición - 2000 pts':
    ('Vacio', 'Bronce13mm', 'Aluminio13mm', 'Aluminio9mm', 'Cobre9mm4'),
'Tercera medición (distancia) - 100 pts':
    ('0cm', '1cm', '2cm', '3cm', '4cm', '5cm', '6cm', '7cm', '8cm', '9cm'),
'Cuarta medición - Distancia a mano':
    ('Distancia a mano',),
'Quinta medición':
    ('Vacio', 'Bronce13mm', 'Aluminio13mm', 'Aluminio9mm', 'Cobre9mm4'),
'Sexta medición':
    ('Vacio', 'Acero')}

carpeta = ('Primera medición - 100 pts',
            'Segunda medición - 2000 pts',
            'Tercera medición (distancia) - 100 pts',
            'Cuarta medición - Distancia a mano',
            'Quinta medición',
            'Sexta medición')

medicion = list()        
for i in range(6):
    medicion.append(dict())
    for archivo in ruta[carpeta[i]]:
        rutaCompleta = './' + carpeta[i] + '/' + archivo + '.csv'
        print('medicion[' + str(i) + ']["' + archivo + '"] = ' + rutaCompleta)
        medicion[i].update({archivo: np.loadtxt(rutaCompleta, delimiter=',',
                                                unpack=True)})
                                                
#%% RESTAR VACIO, CALCULA RESISTIVIDAD Y GRAFICA

def Resistividad(numero, muestra, diametro, inicio=0, fin=2000, 
                 vacio='Vacio', graficar=True):
    """
    Devuelve la resta entre la medición de la muestra y el vacio
    
    Parámetros:
    ----------
    numero : int
        Número de la medicion del 1 al 6.
    muestra : str
        Nombre de la muestra, por ej. 'Aluminio13mm'.
    diametro : float
        Diámetro de la muestra.
    inicio : int
        Comienzo de la lectura.
    fin : int
        Final de la lectura.
    vacio : str
        Nombre de la muestra utilizada como referencia de vacío.
    graficar : bool
        Opción para habilitar / deshabilitar los gráficos.
    """

    frec = medicion[numero - 1][muestra][0]
    x_vacio = medicion[numero - 1][vacio][1]
    y_vacio = medicion[numero - 1][vacio][2]
    x_muestra = medicion[numero - 1][muestra][1]
    y_muestra = medicion[numero - 1][muestra][2]

       
    x_rotado = x_muestra - x_vacio
    y_rotado = y_muestra - y_vacio
    
    x = x_rotado * np.cos(np.pi * 50/180) + y_rotado * np.sin(np.pi * 50/180)
    y = -x_rotado * np.sin(np.pi * 50/180) + y_rotado * np.cos(np.pi * 50/180)
    
    d = ((2*2.82e-8)/(3.95e-6*frec))**0.5
    z = -y/x
    #slopexy, interceptxy = stats.linregress(x,y)[0:2]
    
    w = -0.01 + 3.06 * z - 0.105 * z**2 + 0.167 * z**3
    slopefrecw, interceptfrecw = stats.linregress(frec[inicio:fin],
                                                  w[inicio:fin])[0:2]
    ajuste = frec*slopefrecw + interceptfrecw
    radio = diametro / 2
    Rho = ((3.95e-6)*(radio**2)) / slopefrecw
    
     
    if graficar==True:
        
        #print('Slope: ' + str(slopefrecw))
        
        figura1 = plt.figure()
        titulo = (muestra + ': "X, Y vs. Frec"')  
        figura1.canvas.set_window_title(titulo)
        ejes1 = figura1.add_subplot(111)
        ejes1.set_title(titulo)       
        ejes1.set_xlabel('Frecuencia (Hz)')
        ejes1.set_ylabel('Tensión (V)')
        ejes1.plot(frec[inicio:fin],x[inicio:fin], 'go', label='X')
        ejes1.plot(frec[inicio:fin],y[inicio:fin], 'go', label='Y')
        ejes1.legend(loc='best')
    
        figura2 = plt.figure()
        titulo = (muestra + ': "-Y/X vs. Frec"')  
        figura2.canvas.set_window_title(titulo)
        ejes2 = figura2.add_subplot(111)
        ejes2.set_title(titulo)       
        ejes2.set_xlabel('Frecuencia (Hz)')
        ejes2.set_ylabel('$\\frac{-Y}{X}$')
        ejes2.plot(frec[inicio:fin], z[inicio:fin], 'go', label='-Y/X')
        ejes2.legend(loc='best')
    
        figura3 = plt.figure()
        titulo = (muestra + ': "W vs. Frec"')  
        figura3.canvas.set_window_title(titulo)
        ejes3 = figura3.add_subplot(111)
        ejes3.set_title(titulo)       
        ejes3.set_xlabel('Frecuencia (Hz)')
        ejes3.set_ylabel('$W(\\frac{-Y}{X})$')
        ejes3.plot(frec[inicio:fin], w[inicio:fin], 'go', label='W(-Y/X)')
        ejes3.plot(frec[inicio:fin], ajuste[inicio:fin], 'b', label='Ajuste')
        ejes3.legend(loc='best')
    
    return x, y, Rho
    
#%% CALCULA RESISTIVIDAD EN INTERVALOS MOVILES DE N PUNTOS

def PruebaIntervalos(numero, muestra, diametro, ventana=100, 
                     inicio=0, fin=2000):
    """ Permite calcular la resistividad tomando una ventana móvil """
    
    resultado = list()
    frecuencia = list()
    frec = medicion[numero - 1][muestra][0]
    
    for i in range(inicio,fin-ventana):
        x, y , Rho = Resistividad(numero, muestra, diametro, 
                                  inicio=i, fin=i+ventana, graficar=False)
        resultado.append(Rho)
        frecuencia.append(frec[i])
    
    figura = plt.figure(0)
    eje = figura.add_subplot(111)
    eje.set_title = 'Intervalos'
    eje.plot(frecuencia,resultado, 'go', label='Resistividad')
    eje.yaxis.set_major_formatter(mtick.FormatStrFormatter('%.2e'))
    eje.set_xlabel('Frecuencia (Hz)')
    eje.set_ylabel('$Resistividad (\\omega)$')
    eje.legend(loc='best')
    
    return resultado
                                  
    
    
#%% RESTAR VACIO Y GRAFICA EN FUNCIÓN DE DISTANCIA

def Distancia(numero, distancia, vacio='Vacio'):
    """
    Devuelve la resta entre la medición de la muestra y el vacio.
    
    Parámetros:
    ----------
    numero : int
        Número de la medicion del 1 al 6.
    distancia : str
        Distancia, por ej. '0cm'.
    vacio : str
        Nombre de la muestra utilizada como referencia de vacío.
    """

    frec = medicion[numero - 1][distancia][0]
    x_vacio = medicion[0][vacio][1]
    y_vacio = medicion[0][vacio][2]
    x_distancia = medicion[numero - 1][distancia][1]
    y_distancia = medicion[numero - 1][distancia][2]

    x = x_distancia - x_vacio
    y = y_distancia - y_vacio
    z = x/y
    #slopexy, interceptxy = stats.linregress(x,y)[0:2]
    
    plt.figure(0)
    plt.plot(frec,x, 'go', label=distancia)
    plt.legend(loc='best')
    plt.figure(0)
    plt.plot(frec,y, 'go', label=distancia)
    plt.legend(loc='best')
    
    plt.figure(1)
    plt.plot(x, y, 'go', label=distancia)
   
    plt.figure(2)    
    plt.plot(frec, z, 'go', label=distancia)
    plt.legend(loc='best')
    
    return x, y  

