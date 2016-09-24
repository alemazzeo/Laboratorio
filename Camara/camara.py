# -*- coding: utf-8 -*-
"""
Created on Wed Aug 17 21:36:40 2016

@author: Alejandro
"""

import cv2
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import animation
from scipy.optimize import curve_fit
from time import time

class Camara(object):  
    """
    Clase para la utilización de una cámara web orientada a
    la medición automatica de patrones o distancias.
    
    Parámetros
    ----------
    camara : 
       Dispositivo a utilizar
    x0, y0 : 
       Sistema de referencia para mediciones
    x1, y1 : 
       Coordenada donde comienza la lectura
    x2, y2 : 
       Coordenada donde termina la lectura
    unidad : 
       Nombre de la unidad de distancia utilizada
    razon : 
       Cantidad de pixels cada 1 unidad de distancia
       (ej : 480 pixels = 1 metro)
    direccion :
       Horizontal, vertical o libre (no implementada)       
    """
    def __init__(self, camara=0, x0=0, y0=0, x1=0, y1=240, x2=639, y2=240, 
                 unidad='m', razon=480, direccion='Horizontal'):
                
        # Configuracion de cámara y verificación
        self._camara = cv2.VideoCapture(camara)
        assert self._camara.isOpened() == True , "Dispositivo no disponible"
        
        # Recupera información del dispositivo
        self._ancho = self._camara.get(cv2.CAP_PROP_FRAME_WIDTH)
        self._alto = self._camara.get(cv2.CAP_PROP_FRAME_HEIGHT)
        
        # Parámetros recibidos
        self._unidad = unidad
        self._razon = razon
        self._direccion = direccion
        self._x0 = x0
        self._y0 = y0
        self._x1 = x1
        self._y1 = y1
        self._x2 = x2
        self._y2 = y2
        
        # Parámetros internos
        self._eje_x = None
        self._eje_y = None
        
        self._imagen = None
        self._capa_dibujo = None
        self._gray = None
        
        self._calibrando = False
        self._dibujando = False
        
        # Verificación de los parámetros recibidos
        assert 0 <= x0 < self._ancho
        assert 0 <= x1 < self._ancho
        assert 0 <= x2 < self._ancho
        assert 0 <= y0 < self._alto
        assert 0 <= y1 < self._alto
        assert 0 <= y2 < self._alto
        assert self._razon > 0
    
    def __del__(self):
        """
        Libera la cámara y elimina las ventanas abiertas
        (ATENCION: elimina todas las ventanas correspondientes a OpenCV)
        """
        self._camara.release()
        cv2.destroyAllWindows()   
        
    def _calcular_distancia(self, x1=0, x2=0, y1=0, y2=0):
        """        
        Calcula la distancia entre coordenadas
        Por defecto utiliza las ultimas coordenadas internas
        """
        if x1==0 & x2==0 & y1==0 & y2==0:                
            return ((self._x2 - self._x1) ** 2 + 
                    (self._y2 - self._y1) ** 2) ** 0.5
        else:
            return ((x2 - x1) ** 2 + (y2 - y1) ** 2) ** 0.5    
        
    def _calcular_distancia2(self, x1=0, x2=0, y1=0, y2=0):
        """        
        Calcula el cuadrado de la distancia entre coordenadas
        Por defecto (todos ceros) utiliza las ultimas coordenadas internas
        """
        if x1==0 & x2==0 & y1==0 & y2==0:                
            return ((self._x2 - self._x1) ** 2 + 
                    (self._y2 - self._y1) ** 2)
        else:
            return ((x2 - x1) ** 2 + (y2 - y1) ** 2)
    
    def _obtener_coordenadas(self, event, x, y, flags, direccion='Libre'):
        """
        Rutina para el evento onMouse de cv2.setMouseCallback
        
        Permite dibujar una linea sobre una imagen y establecer los
        parametros internos x1, y1, x2, y2
        
        El primer clic congela la imagen y marca el inicio de una flecha
        La misma acompaña el movimiento del mouse hasta el segundo clic.
        Los puntos obtenidos quedan guardados como self._x1, etc.
        
        Parámetros
        ----------
        direccion : 
           Permite restringir o no la direccion de la flecha:          
           'Horizontal', 'Vertical', 'Libre'  
        otros : 
           Automáticos al utilizar cv2.setMouseCallback
        """
        
        # Al soltar el boton izquierdo (ignora el arrastre)
        if event == cv2.EVENT_LBUTTONUP:
            # Si aun no comenzo a dibujar la linea
            if self._dibujando == False: 
                # Setea las primeras coordenadas                            
                self._x1 = x
                self._y1 = y
                # Activa el modo "dibujando"
                self._dibujando = True
                # Imprime la coordenadas en pantalla
                print ('x1: '+ str(x) + '    y1: '+ str(y))
            
            # Caso contrario
            else:             
                # Guarda la segunda coordenada segun la direccion elegido
                if direccion == 'Horizontal':
                    self._x2 = x
                    self._y2 = self._y1 
                elif direccion == 'Vertical':
                    self._x2 = self._x1
                    self._y2 = y
                elif direccion == 'Libre':
                    self._x2 = x
                    self._y2 = y   
                   
                # Imprime la coordenadas en pantalla
                print ('x2: '+ str(self._x2) + '    y2: '+ str(self._y2))                
                # Da por terminado el modo dibujo y la calibración
                self._dibujando = False
                self._calibrando = False    
        
        # Al mover el mouse
        elif event == cv2.EVENT_MOUSEMOVE:
            # Si el modo "dibujando" esta activado
            if self._dibujando == True:
                # Realiza una copia de la imagen actual
                # sobre la cual se dibujara la flecha
                self._capa_dibujo = self._imagen.copy()
                
                # Dibuja la flecha segun la direccion elegido
                if direccion == 'Horizontal':
                    cv2.arrowedLine(self._capa_dibujo,(self._x1,self._y1),
                                    (x,self._y1),(255,255,255))
                elif direccion == 'Vertical':
                    cv2.arrowedLine(self._capa_dibujo,(self._x1,self._y1),
                                    (self._x1,y),(255,255,255))
                elif direccion == 'Libre':
                    cv2.arrowedLine(self._capa_dibujo,(self._x1,self._y1),
                                    (x,y),(255,255,255))
                
                # Actualiza la imagen de la ventana
                cv2.imshow('Calibrando',self._capa_dibujo)
                    
    def calibrar(self, distancia=0, unidad='', direccion=''):
        """
        Método de calibración para la adquisicion de patrones.
        
        Permite calibrar la relacion pixel / distancia en funcion de dos
        puntos conocidos.
        
        Tambien permite verificar distancias y configurar los parámetros
        internos x1, y1, x2, y2 para, por ejemplo, definir la región de
        análisis por defecto para el método perfil_intensidad
        
        Es la forma correcta de modificar la dirección del análisis o
        la unidad utilizada, ya que dichas modificaciones deberían verse 
        acompañadas de una recalibración.
        
        Si no se especifica la dirección del análisis se utiliza la última
        configurada (por defecto 'Horizontal'). 
        
        Parámetros
        ----------
        distancia : 
           distancia para calibración
           
           0 => no configurar nueva distancia.  
           devuelve entonces la distancia seleccionada
           permite verificar la escala o medir <a ojo>
           
        unidad : 
           Permite modificar la unidad de distancia utilizada
        direccion : 
           Permite restringir o no la dirección del análisis:
           
           'Horizontal', 'Vertical', 'Libre' -> No implementado aún                        
        """  
        
        # Si la unidad o la direccion se vio modificada
        # reconfigura los parámetros internos
        if unidad != '':
            self._unidad = unidad           
        if direccion != '':
            self._direccion = direccion
            
        # Verifica que no se introduzcan distancias negativas       
        assert distancia >= 0
        
        # Activa el modo "calibrando"
        self._calibrando = True
        # Abre una nueva ventana
        cv2.namedWindow('Calibrando')
        # Configura como respuesta del mouse a _obtener_coordenadas
        # Pasa como parámetro la direccion de analisis
        cv2.setMouseCallback('Calibrando',self._obtener_coordenadas,
                             self._direccion)
        
        while self._calibrando == True:                       
            
            # Mientras no comience el modo "dibujando"
            if self._dibujando == False:
               # Captura y muestra imágenes de la cámara
               _, self._imagen = self._camara.read()
               cv2.imshow('Calibrando',self._imagen)
            
            # Invoca el método waitKey y en caso de que la tecla pulsada
            # corresponda a escape, da por terminado el bucle
            # Ver documentación de waitKey
            if cv2.waitKey(1) & 0xFF == 27:
                break
        
        # Cierra la ventana utilizada para calibrar
        cv2.destroyWindow('Calibrando')
        
        # Si no se configuro una distancia
        if distancia == 0:
            # Calcula y devuelve la distancia medida
            distancia = self._calcular_distancia() / self._razon
            print ('Distancia: ' + str(distancia))        
        
        else:
            # De lo contrario configura la nueva relacion e informa
            self._razon = self._calcular_distancia() / distancia    
            print (str(self._razon) + ' pixels = 1 ' + self._unidad) 
            
    def perfil_intensidad(self, x0=0, y0=0, x1=0, y1=0, x2=0, y2=0):
        """
        Método para analizar una linea de la imagen levantando el perfil
        de intensidades de la misma
        
        Parámetros
        ----------
        <coords>  : 
           coordenadas del análisis (por defecto las calibradas)
           
           *(algunas pueden ser ignoradas en función de respetar
           la dirección de analisis configurada)*
                    
           ej: si la dirección es horizontal la coordenada y2
           es irrelevante                   
        """    
        # Configura los parámetros por defecto
        if x1==0 & x2==0 & y1==0 & y2==0:    
            x0 = self._x0
            y0 = self._y0
            x1 = self._x1
            y1 = self._y1
            x2 = self._x2
            y2 = self._y2
        
        # Captura la imagen actual y la convierte a escala de grises
        _, self._imagen = self._camara.read()
        self._gray = cv2.cvtColor(self._imagen,cv2.COLOR_BGR2GRAY)
        
        # Calcula los datos acorde a la dirección de análisis
        if self._direccion == 'Horizontal':
            self._eje_x = np.arange(0,(x2-x1),1) / self._razon
            self._eje_y = self._gray[y1,x1:x2]
        elif self._direccion == 'Vertical':
            self._eje_x = np.arange(0,(y2-y1),1) / self._razon
            self._eje_y = self._gray[x1,y1:y2]    
        elif self._direccion == 'Libre':
            pass
        
        return self._eje_x, self._eje_y
    
    def graficar_intensidad(self, x1=0, y1=0, x2=0, y2=0):
        """
        Método para analizar una linea de la imagen levantando el perfil
        de intensidades de la misma en forma dinámica (ANIMACIÓN)
        
        Parámetros
        ----------
        <coords> : 
           coordenadas del análisis (por defecto las calibradas)
           
           *algunas pueden ser ignoradas en función de respetar
           la dirección de analisis configurada*
           
           ej: si la dirección es horizontal la coordenada y2
           es irrelevante
                    
        """
        # Advertencia para IPyhon
        print ('La animación requiere la configuración: %matplolib qt')
        print ('Puede volver al modo inline tipeando %matplolib inline')
        
        # Configura los parámetros por defecto
        if x1==0 & x2==0 & y1==0 & y2==0:    
            x0 = self._x0
            y0 = self._y0
            x1 = self._x1
            y1 = self._y1
            x2 = self._x2
            y2 = self._y2       
        
        # Tutorial utilizado para implementar matplotlib animation en:
        # ----------------------------------------------
        # https://jakevdp.github.io/blog/2012/08/18/
        #       /matplotlib-animation-tutorial/
        # ----------------------------------------------
        
        # Configura la figura
        fig1 = plt.figure()
        
        # Obtiene un primer conjunto de datos mediante perfil_intensidad()
        eje_x, eje_y = self.perfil_intensidad(x0, y0, x1, y1, x2, y2)
        
        # Genera un subplot dentro de la figura
        subplot = fig1.add_subplot(111,xlim=(eje_x[0],eje_x[-1]),ylim=(0,255))
        
        # Genera un plot vacio recuperando el objeto
        perfil, = subplot.plot([],[])
        # Utiliza el objeto generado por el plot y le configura como
        # datos los obtenidos del perfil de intensidades
        perfil.set_data(eje_x, eje_y)

        # La función init permite a la animación conocer los elementos
        # que se actualizaran en los siguientes cuadros
        def init():
            perfil.set_data([],[])
            return perfil,

        # La funcion animate genera el cuadro siguiente a mostrar
        def animate(i):
            eje_x, eje_y = self.perfil_intensidad()
            perfil.set_data(eje_x, eje_y)
            return perfil,

        # Funcion que genera la animacion a partir de init y animate.
        # El parámetro blit=True permite a la animación actualizar
        # sólo los cambios entre el cuadro anterior y el siguiente
        # aumentando el rendimiento de la misma

        anim = animation.FuncAnimation(fig1, animate, init_func=init,
                                   interval=30, blit=True)
        plt.show()
        
        return anim       
        
    def captura(self, color='Color'):
        # Realiza y devuelve una captura de imagen
        _, captura = self._camara.read()
        return captura
        
    def color_a_gris(self, imagen):
        # Recibe una imagen color y la devuelve en escala de grises
        return cv2.cvtColor(imagen,cv2.COLOR_BGR2GRAY)
        
    def guardar(self, nombre_archivo='captura.jpg', imagen=None):
        # Guarda la imagen recibida en un archivo
        if imagen is None:
            cv2.imwrite(nombre_archivo, imagen)
        else:
            cv2.imwrite(nombre_archivo, self._imagen)
        
        