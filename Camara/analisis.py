# -*- coding: utf-8 -*-
"""
Created on Fri Aug 19 16:27:48 2016

@author: Alejandro
"""
from scipy import signal
from scipy.optimize import curve_fit
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.style as style
from matplotlib import animation

class Difraccion(object):
    """
    Análisis para difracción de una rendija en una dimension bajo la
    aproximación de Fraunhofer.

    Parámetros
    ----------
    eje_x : 1D array
       Eje correspondiente a la coordenada espacial
    eje_y : 1D array
       Eje correspondiente a la coordenada de intensidad
    orden : int opcional
       Número del último orden percibido (orden principal = 0)
    long_onda : float opcional
       Longitud de onda del LASER en la unidad de distancia utilizada
    distancia_pantalla : float opcional
       Distancia entre la rendija y la pantalla en la unidad de distancia
    unidad : str opcional
        Nombre de la unidad de distancia utilizada                      
    """
    def __init__(self, eje_x, eje_y, long_onda=670e-9,
                 distancia_pantalla=2, unidad='m'):                
        
        assert len(eje_x) == len(eje_y)
        
        self._eje_x = np.asarray(eje_x)
        self._eje_y = np.asarray(eje_y)
        
        self._len = len(eje_x)
        self._centro = None
        self._long_onda = long_onda
        self._distancia_pantalla = distancia_pantalla
        self._unidad = unidad
        
        self._interfranja = None
        self._error_interfranja = None
        self._franjas_contadas = None
        self._amplitud = None
        self._rendija = None
        self._red_calibracion = None       
        
        self._ancho_central = None
        self._minimos = None 
        self._minimos_izquierda = None
        self._minimos_derecha = None
        self._orden_tolerado = None
        
        self._factor_tolerancia = 0.3
       
        assert 0 < long_onda
        assert 0 < distancia_pantalla
        
    def configurar_experimento(self):
        pass
     
    def analizar_patron(self, orden_dinamico=True, umbral=0.5):
        """
        Análisis automático del patrón introducido
        
        Parámetros:
        -----------
        orden_dinamico : bool opcional
            Permite al método alterar dinámicamente el número de
            ordenes analizados.
            
        Retorna:
        --------
        1D array
           eje_x
        1D array           
           eje_y
        1D array
           maximos
        1D array
           minimos
        """
        
        # NOTA: En general, la información se guarda en self una vez que se
        #       tradujo al eje x. Hasta entonces las variables internas del
        #       método analizar_patron corresponden a índices del eje y
        
        # Encuentra el valor máximo en la grafica
        maximo_absoluto = np.max(self._eje_y)
        
        # Utiliza un porcentaje del valor máximo para estimar el ancho del
        # pico central
        cota = maximo_absoluto * umbral
        ancho_picos = len(self._eje_y[self._eje_y > cota]) / 2
        
        # Genera un intervalo para la deteccion de los picos
        # como el ancho esperado +/- %25
        ap1 = ancho_picos * 0.75
        ap2 = ancho_picos * 1.25        
        
        # Busca los mínimos locales
        # La conversión a np.array facilita la manipulación posterior
                                                   
        minimos = np.array(signal.find_peaks_cwt(-self._eje_y, 
                                                 np.arange(ap1,ap2)))
        
        # Asumiendo que el máximo principal de un sinc^2 satura al
        # instrumento (para un sinc[x]^2 la intensidad del primer orden 
        # se reduce al 5% del orden cero)
        
        # Busca el primer punto saturado
        primera_saturacion = np.argmax(self._eje_y)
        
        # Separa los minimos respecto del centro de saturacion
        minimos_izquierda = minimos[minimos < primera_saturacion]
        minimos_derecha = minimos[minimos > primera_saturacion]
         
        # Determina la ubicación (índice) de los mínimos centrales
        # (último de la izquierda y primero de la derecha)
        minimo_central_izq = minimos_izquierda[-1]
        minimo_central_der = minimos_derecha[0]
        
        # Calcula el ancho central (sin informacion del eje x aun)
        ancho_central = minimo_central_der - minimo_central_izq
        # Calcula la posición del maximo_central en el array del eje y
        maximo_central = np.int((minimo_central_izq + ancho_central / 2)) 
        
        # Obtiene la posicion del centro para el eje x
        self._centro = self._eje_x[maximo_central]
        
        # Desplaza el origen del eje x al máximo central
        self._eje_x -= self._centro
        
        if orden_dinamico == True:       
            # Recalcula los máximos y mínimos utilizando la información
            # del primer orden en caso de que el número de ordenes visibles
            # no este fijo (por ejemplo si la rendija es variable)
            ancho_picos = ancho_central / 8
            ap1 = ancho_picos * 0.5
            ap2 = ancho_picos * 1                                                    
            minimos = np.array(signal.find_peaks_cwt(-self._eje_y, 
                                                     np.arange(ap1,ap2))) 
            minimos_izquierda = minimos[minimos < primera_saturacion]
            minimos_derecha = minimos[minimos > primera_saturacion]
        
        # Convierte y almacena la informacion de los máximos y mínimos
        # al nuevo eje x
        self._minimos = self._eje_x[minimos]
        
        # Recupera y ordena los mínimos respecto del orden cero
        self._minimos_izquierda = -self._minimos[self._minimos < 0][::-1] 
        self._minimos_derecha = self._minimos[self._minimos > 0]
        
        # Calcula las distancias entre minimos
        distancias = self._minimos[1:] - self._minimos[0:-1]
        # Toma el promedio
        promedio = distancias.mean()
        # Identifica mayores al 150% como posibles franjas perdidas
        problematicos = distancias[distancias > promedio * 1.5]
        # Divide por 2 las distancias en busca de candidatos
        problematicos = problematicos / 2
        # Los agrega a la lista de distancias
        distancias = np.append(distancias, problematicos)
        distancias = np.append(distancias, problematicos)
        # Elimina menores al 50% del promedio
        distancias = distancias[promedio * 0.5 < distancias]
        # Elimina mayores al 150% del promedio
        distancias = distancias[distancias < promedio * 1.5]
        
        # Calcula la interfranja como el promedio de las distancias válidas
        self._interfranja = distancias.mean()
        # Calcula el error como el 25% dividido el número de franjas
        self._error_interfranja = self._interfranja * 0.25 / len(distancias)
        # Almacena el número de franjas contadas
        self._franjas_contadas = len(distancias)
                        
        # Tamaño de la rendija
        self._rendija = (self._distancia_pantalla * self._long_onda /
                         self._interfranja)
        
        return (self._eje_x , self._eje_y , self._rendija, 
                self._minimos)
    
    def reporte(self):
        print('\nRESULTADOS')
        print('----------')
        print('    Rendija: ' + str(self._rendija) + self._unidad)
        print('    Interfranja promedio: ' + str(self._interfranja)
              + self._unidad)
        print('    Interfranja 1er orden: ' + str(self._minimos_derecha[0])
              + self._unidad)   
    
    def graficar(self, umbral=0.5):
        # Grafica el resultado del análisis
        
        self.analizar_patron(umbral=umbral)
        
        figura = plt.figure()
        ax = figura.add_subplot(111)
        ax.set_xlabel('Distancia (' + self._unidad + ')')
        ax.set_ylabel('Intensidad')
        ax.plot(self._eje_x * 1000 , self._eje_y, 'k')
        for minimo in self._minimos:
            ax.axvline(minimo * 1000, c='k', ls='--')
        self.reporte()
    
    def analisis_dinamico(self, func, *args):
        # Grafica en forma dinamica el resultado del análisis      
        
        self._eje_x, self._eje_y = func(*args)
        
        self.analizar_patron()
        bbox_props = dict(boxstyle="round,pad=0.3", fc="white", ec="b", lw=2)
        figura = plt.figure()
        ax = figura.add_subplot(111)
        ax.set_xlabel('Distancia (' + self._unidad + ')')
        ax.set_ylabel('Intensidad')
        
        datos, = ax.plot(self._eje_x , self._eje_y)
        datos.set_data(self._eje_x , self._eje_y)
        txtRendija = ax.text(0.05, 0.9, '', 
                             bbox=bbox_props,
                             transform=ax.transAxes)
        txtContadas = ax.text(0.05, 0.8, '', 
                              bbox=bbox_props,
                              transform=ax.transAxes)
        
        def init():
            datos.set_data([],[])
            txtRendija.set_text("")
            txtContadas.set_text("")
            graficos = list()
            graficos.append(datos)
            graficos.append(txtRendija)
            return graficos
        
        def animate(i):
        
            self._eje_x, self._eje_y = func(*args)
            self.analizar_patron()
            x = self._eje_x
            y = self._eje_y
            datos.set_data(x, y)
            graficos = list()

            linea = ax.axvline(0, c='b', ls='--')
            graficos.append(linea)
            texto1 = "Rendija: {0:.5e} {1:s}".format(self._rendija, 
                                                self._unidad)
            texto2 = "Franjas válidas: {0}".format(self._franjas_contadas)
            txtRendija.set_text(texto1)
            txtContadas.set_text(texto2)
            
            for minimo in self._minimos:
                linea = ax.axvline(minimo, c='b', ls='--')
                graficos.append(linea)
            graficos.append(txtRendija)
            graficos.append(txtContadas)
            graficos.append(datos)                
            return graficos
            
        anim = animation.FuncAnimation(figura, animate, init_func=init,
                                   interval=1500, blit=True)
        plt.show()
        return anim