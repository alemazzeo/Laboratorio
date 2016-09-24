import time
import visa
import numpy as np
import matplotlib.pyplot as plt

#https://tonysyu.github.io/raw_content/matplotlib-style-gallery/gallery.html
#import matplotlib.style as pltstyle
#pltstyle.use('seaborn-white')

class SimuladorVISA:
    """
    Clase auxiliar para simular la comunicación con un dispositivo PyVISA.
    """
    def __init__(self):
        print('Simulador de dispositivo VISA')
        print('Modo de respuesta automatica: 0')
    
    def query(self, cadena, separator=''):
        print('>> ' + cadena)
        if separator == ',':
            return '0,1'
        else:
            if cadena == '*STB? 1':
                time.sleep(1)
                return 1
            elif cadena == 'SPTS?':
                return 16900
            else:
                return '0'
    
    def query_ascii_values(self, cadena, **args):
        print(cadena)
        return np.random.rand(1)[0] , np.random.rand(1)[0], 0, 0
            
    def query_binary_values(self, cadena, **args):
        print(cadena)
        return np.random.rand(100)
    
    def write(self, cadena):
        print(cadena)

class Lockin(object):
    '''
    Clase para el manejo amplificador Lockin SR830 usando PyVISA de interfaz.
    
    Parámetros
    ----------
    resource : Cadena (opcional)
       Nombre del dispositivo a utilizar. En caso de utilizar un único
       dispositivo del tipo GPIB puede omitirse este parámetro (se buscará
       automáticamente la entrada correspondiente).
    modo_simulador : Bool (opcional)
        Permite simular la comunicación con el instrumento. Utiliza la clase
        SimuladorVisa para reemplazar los comandos query y write de PyVisa.
    '''
    
    #----------------------------------------------------------------------
    # Inicializador
    #----------------------------------------------------------------------
    
    def __init__(self, resource='', modo_simulador=False):
        
        # Crea el objeto correspondiente según el modo elegido
        if modo_simulador == True:
            self._lockin = SimuladorVISA()
        else:
            
            self._lockin = None        
            
            # En caso de no recibir como parámetro la dirección del equipo
            if resource == '':
                # Busca dispositivos GPIB conectados           
                print('Buscando dispositivos compatibles...')            
                rm = visa.ResourceManager()
                dispositivos = list(rm.list_resources())
                for disp in dispositivos:
                    if disp.startswith('GPIB'):
                        resource = disp
            
                # Si la busqueda no tiene éxito genera una excepción
                if resource == '':               
                    raise ValueError('Ningun dispositivo encontrado')
        
            print('Conectando a ' + resource + '...')
        
            # Establece la conexión y devuelve la identificación del equipo.
            try:
                self._lockin = visa.ResourceManager().open_resource(resource)                
                self._idn = self._lockin.query('*IDN?')
            except visa.VisaIOError as error:
                print('Conexión interrumpida')
                raise Exception(error.description)
        
            print('Conectado a: ' + self._idn)


        #Bloquea el uso de las teclas del Lockin
        self._lockin.write('LOCL2') 
        self._lockin.write('OVRM0')
        
        # Parámetros internos del objecto accedibles mediante propiedades
               
        self._refFase = None
        self._refModo = None
        self._refFrec = None
        self._refAmpl = None
        self._refHarm = None
        self._refRslp = None
        
        self._inpModo = None
        self._inpGnd  = None
        self._inpCoup = None
        self._inpLine = None
        
        self._inpSens = None
        self._inpRmod = None
        self._inpOflt = None  
        self._inpOfsl = None
        self._inpSync = None
              
        self._stpLock = None
        
        self._ch1Modo = None
        self._ch1OutS = None
        self._ch1RatS = None        
        
        self._ch2Modo = None
#        self._ch2OutS = None
#        self._ch2RatS = None
        
#        self._offsetX = None
#        self._offsetY = None
#        self._offsetR = None
        
#        self._expandX = None
#        self._expandY = None
#        self._expandR = None        
        
        self._auxout1 = None
        self._auxout2 = None
        self._auxout3 = None
        self._auxout4 = None
        
        
        # Valores permitidos y traducciones
        
        self._tamBuffer = 16383
        
        self._crefModo = ('External', 'Internal')
        self._crefRslp = ('Sine', 'TTL Rising', 'TTL Falling')
        
        self._cinpModo = ('A', 'A-B', 'I1', 'I100')
        self._cinpGnd  = ('Float', 'Ground')
        self._cinpCoup = ('AC', 'DC')
        self._cinpLine = ('Out', 'Line In', '2xLine In', 'Both In')
        
        self._cinpRmod = ('High Reserve', 'Normal', 'Low Noise')
        self._cinpOfsl = ('6dB/oct', '12dB/oct', '18dB/oct', '24dB/oct')
        self._cinpSync = ('Off', 'On')
        
        self._cch1Modo = ('X', 'R', 'Xn', 'Aux1', 'Aux2')
        self._cch2Modo = ('Y', 'T', 'Yn', 'Aux3', 'Aux4')
        
        self._cch2RatS = ('None', 'Aux In 1', 'Aux In 2')
        self._cch2RatS = ('None', 'Aux In 3', 'Aux In 4')
        
        self._cexpandX = ('x1', 'x10', 'x100')
        self._cexpandY = ('x1', 'x10', 'x100')
        self._cexpandR = ('x1', 'x10', 'x100')       
        
        self._cch1OutS = ('Display', 'X')
        self._cch2OutS = ('Display', 'Y')        

        self._cExpand = ('x1', 'x10', 'x100')        
        
        self._cstpLock = ('Local', 'Remote', 'Local Lockout')
        
        self._strinpSens = ('2 nV/fA', '5 nV/fA', '10 nV/fA', 
                            '20 nV/fA', '50 nV/fA', '100 nV/fA', 
                            '200 nV/fA', '500 nV/fA', '1 ¼V/pA',
                            '2 ¼V/pA', '5 ¼V/pA', '10 ¼V/pA', 
                            '20 ¼V/pA', '50 ¼V/pA', '100 ¼V/pA',
                            '200 ¼V/pA', '500 ¼V/pA',  '1 mV/nA',
                            '2 mV/nA', '5 mV/nA', '10 mV/nA',
                            '20 mV/nA', '50 mV/nA', '100 mV/nA',
                             '200 mV/nA', '500 mV/nA', '1 V/¼A')
                                       
        self._floatinpSens = (2e-9, 5e-9, 10e-9, 20e-9, 50e-9, 
                              100e-9, 200e-9, 500e-9, 1e-6, 2e-6,
                              5e-6, 10e-6, 20e-6, 50e-6, 100e-6, 
                              200e-6, 500e-6, 1e-3, 2e-3, 5e-3,
                              10e-3, 20e-3, 50e-3, 100e-3, 200e-3, 
                              500e-3, 1)                               
                                       
        self._strinpOflt = ('10 us',  '30 us', '100 us', 
                            '300 us', '1 ms', '3 ms', 
                            '10 ms', '30 ms', '100 ms', 
                            '300 ms', '1 s', '3 s',
                            '10 s', '30 s', '100 s', 
                            '300 s', '1 ks', '3 ks',
                            '10 ks', '30 ks')
                                         
        self._floatinpOflt = (10e-6, 30e-6, 100e-6, 300e-6,
                              1e-3, 3e-3, 10e-3, 30e-3,
                              100e-3, 300e-3, 1.0, 3.0,
                              10.0, 30.0, 100.0,  300.0,
                              1e3, 3e3, 10e3, 30e3) 

        # Otros parámetros internos

        self._rutaGeneral = './Lockin/'
        self._rutaDatos = ''
        self._rutaImagenes = ''

        self._ejeDatos = None
        self._ejeTiempo = None    

        self._frecBarrido = None
        self._datosBarrido = None   

        self._figuras = list()
        self._datos = list()                   
    
    #----------------------------------------------------------------------
    # Destructor del objeto
    #----------------------------------------------------------------------
        
    def __del__(self):
        # Destructor del objeto
        if isinstance(self._lockin, visa.Resource):
            self._lockin.write('LOCL0') #Desbloquea el Lockin
            self._lockin.close()
            print('Conexión interrumpida')
    
    #----------------------------------------------------------------------
    # Métodos para escritura y lectura de propiedades
    #----------------------------------------------------------------------
       
    def _get_refFase(self):
        self._refFase = float(self._lockin.query('PHAS?'))
        return self._refFase
    def _set_refFase(self, fase):
        if not (-360.00 <= fase <= 729.99):
            raise ValueError('-360.00 <= fase <= 729.99')
        self._lockin.write('PHAS{0:f}'.format(fase))
        self._refFase = fase
    
    def _get_refModo(self):
        self._refModo = self._crefModo[int(self._lockin.query('FMOD?'))]
        return self._refModo
    def _set_refModo(self, modo):
        try:
            i = self._crefModo.index(modo)
        except ValueError:
            raise ValueError(self._crefModo)
        self._lockin.write('FMOD{0}'.format(i))
        self._refModo = modo
        
    def _get_refFrec(self):
        self._refFrec = float(self._lockin.query('FREQ?'))
        return self._refFrec
    def _set_refFrec(self, frec):
        if not (0.001 <= frec <= 102000):
            raise ValueError('0.001 <= frec <= 102000')
        self._lockin.write('FREQ{0:f}'.format(frec))
        self._refFrec = frec
    
    def _get_refAmpl(self):
        self._refAmpl = float(self._lockin.query('SLVL?'))
        return self._refAmpl
    def _set_refAmpl(self, ampl):
        if not (0.004 <= ampl <= 5.000):
            raise ValueError('0.004 <= ampl <= 5.000')
        self._lockin.write('SLVL{0:f}'.format(ampl))
        self._refAmpl = ampl   
    
    def _get_refHarm(self):
        self._refHarm = int(self._lockin.query('HARM?'))
        return self._refHarm
    def _set_refHarm(self, num):
        if not (isinstance(num, int) and 1 <= num <= 19999 and
                num * self._refFrec <= 102000):
            raise ValueError('1 <= num <= 19999, num * f <= 102000Hz')
        self._lockin.write('HARM{0}'.format(num))
        self._refHarm = num 
        
    def _get_refRslp(self):
        self._refRslp = self._crefRslp[int(self._lockin.query('RSLP?'))]
        return self._refRslp
    def _set_refRslp(self, modo):
        try:
            i = self._crefRslp.index(modo)
        except ValueError:
            raise ValueError(self._crefRslp)
        self._lockin.write('RSLP{0}'.format(i))
        self._refRslp = modo
   
    def _get_inpModo(self):
        self._inpModo = self._cinpModo[int(self._lockin.query('ISRC?'))]
        return self._inpModo
    def _set_inpModo(self, modo):
        try:
            i = self._cinpModo.index(modo)
        except ValueError:
            raise ValueError(self._cinpModo)
        self._lockin.write('ISRC{0}'.format(i))
        self._inpModo = modo
       
    def _get_inpGnd(self):
        self._inpGnd = self._cinpGnd[int(self._lockin.query('IGND?'))]
        return self._inpGnd
    def _set_inpGnd(self, modo):
        try:
            i = self._cinpGnd.index(modo)
        except ValueError:
            raise ValueError(self._cinpGnd)
        self._lockin.write('IGND{0}'.format(i))
        self._inpGnd = modo
       
    def _get_inpCoup(self):
        self._inpCoup = self._cinpCoup[int(self._lockin.query('ICPL?'))]
        return self._inpCoup
    def _set_inpCoup(self, modo):
        try:
            i = self._cinpCoup.index(modo)   
        except ValueError:    
            raise ValueError(self._cinpCoup)
        self._lockin.write('ICPL{0}'.format(i))
        self._inpCoup = modo
        
    def _get_inpLine(self):
        self._inpLine = self._cinpLine[int(self._lockin.query('ILIN?'))]
        return self._inpLine
    def _set_inpLine(self, modo):
        try:
            i = self._cinpLine.index(modo)    
        except ValueError: 
            raise ValueError(self._cinpLine)
        self._lockin.write('ILIN{0}'.format(i))
        self._inpLine = modo
     
    def _get_inpSens(self):
        self._inpSens = int(self._lockin.query('SENS?'))
        return self._inpSens
    def _set_inpSens(self, valor):
        if isinstance(valor,str):
            try:
                i = self._strinpSens.index(valor)    
            except ValueError:
                raise ValueError(self._strinpSens)    
        elif isinstance(valor, int):
            if 0 <= valor <= 26:
                i = valor    
            else:
                raise ValueError('0 <= valor <= 26, valor entero')        
        elif isinstance(valor, float):
            try:
                i = self._floatinpSens.index(valor)
            except ValueError:
                raise ValueError(self._floatinpSens)
        self._lockin.write('SENS{0}'.format(i))
        self._inpSens = i
        
    def _get_inpRmod(self):
        self._inpRmod = self._cinpRmod[int(self._lockin.query('RMOD?'))]
        return self._inpRmod
    def _set_inpRmod(self, modo):
        try:
            i = self._cinpRmod.index(modo)
        except ValueError:
            raise ValueError(self._cinpRmod)
        self._lockin.write('RMOD{0}'.format(i))
        self._inpRmod = modo
        
    def _get_inpOflt(self):
        self._inpOflt = int(self._lockin.query('OFLT?'))
        return self._inpOflt
    def _set_inpOflt(self, valor):
        if isinstance(valor,str):
            try:
                i = self._strinpOflt.index(valor)    
            except ValueError:
                raise ValueError(self._strinpOflt)    
        elif isinstance(valor, int):
            if 0 <= valor <= 19:  
                i = valor
            else:
                raise ValueError('0 <= valor <= 19, valor entero')               
        elif isinstance(valor, float):
            try:
                i = self._floatinpOflt.index(valor)
            except ValueError:
                raise ValueError(self._floatinpOflt)
        self._lockin.write('OFLT{0}'.format(i))
        self._inpOflt = i
        
    def _get_inpOfsl(self):
        self._inpOfsl = self._cinpOfsl[int(self._lockin.query('OFSL?'))]
        return self._inpOfsl
    def _set_inpOfsl(self, modo):
        try:
            i = self._cinpOfsl.index(modo)
        except ValueError:
            raise ValueError(self._cinpOfsl)
        self._lockin.write('OFSL{0}'.format(i))
        self._inpOfsl = modo
        
    def _get_inpSync(self):
        self._inpSync = self._cinpSync[int(self._lockin.query('SYNC?'))]
        return self._inpSync
    def _set_inpSync(self, modo):
        try:
            i = self._cinpSync.index(modo)
        except ValueError:
            raise ValueError(self._cinpSync)
        self._lockin.write('SYNC{0}'.format(i))
        self._inpSync = modo
      
    def _get_stpLock(self):
        self._stpLock = self._cstpLock[int(self._lockin.query('LOCL?'))]
        return self._stpLock
    def _set_stpLock(self, modo):
        try:
            i = self._cstpLock.index(modo)    
        except ValueError:
            raise ValueError('Local(0), Remote(1), Local Lockout(2)')
        self._lockin.write('LOCL{0}'.format(i))
        self._stpLock = modo
       
    def _get_ch1Modo(self):
        self._ch1Modo, = self._cch1Modo[int(self._lockin.query_ascii_values(
                                            'DDEF? 1', separator=",")[0])]
        return self._ch1Modo
    def _set_ch1Modo(self, modo):
        try:
            i = self._cch1Modo.index(modo)
        except ValueError:
            raise ValueError(self._cch1Modo)
        self._lockin.write('DDEF1,{0},0'.format(i))
        self._ch1Modo = modo
        
    def _get_ch2Modo(self):
        self._ch2Modo, = self._cch2Modo[int(self._lockin.query_ascii_values(
                                            'DDEF? 2', separator=",")[0])]
        return self._ch2Modo
    def _set_ch2Modo(self, modo):
        try:
            i = self._cch2Modo.index(modo)
        except ValueError:
            raise ValueError(self._cch2Modo)
        self._lockin.write('DDEF2,{0},0'.format(i))
        self._ch2Modo = modo
        
    def _get_auxout1(self):
        self._auxout1 = float(self._lockin.query('AUXV?1'))
        return self._auxout1
    def _set_auxout1(self, ampl):
        if not (-10.500 <= ampl <= 10.500):
            raise ValueError('-10.500 <= ampl <= 10.500')
        self._lockin.write('AUXV1,{0:f}'.format(ampl))
        self._auxout1 = ampl
        
    def _get_auxout2(self):
        self._auxout2 = float(self._lockin.query('AUXV?2'))
        return self._auxout2
    def _set_auxout2(self, ampl):
        if not (-10.500 <= ampl <= 10.500):
            raise ValueError('-10.500 <= ampl <= 10.500')
        self._lockin.write('AUXV2,{0:f}'.format(ampl))
        self._auxout2 = ampl
        
    def _get_auxout3(self):
        self._auxout3 = float(self._lockin.query('AUXV?3'))
        return self._auxout3
    def _set_auxout3(self, ampl):
        if not (-10.500 <= ampl <= 10.500):
            raise ValueError('-10.500 <= ampl <= 10.500')
        self._lockin.write('AUXV3,{0:f}'.format(ampl))
        self._auxout3 = ampl
        
    def _get_auxout4(self):
        self._auxout4 = float(self._lockin.query('AUXV?4'))
        return self._auxout4
    def _set_auxout4(self, ampl):
        if not (-10.500 <= ampl <= 10.500):
            raise ValueError('-10.500 <= ampl <= 10.500')
        self._lockin.write('AUXV4,{0:f}'.format(ampl))
        self._auxout4 = ampl
    
    
    
    #----------------------------------------------------------------------
    # Definición de las propiedades
    #----------------------------------------------------------------------
    refFase = property(_get_refFase, _set_refFase)    
    refModo = property(_get_refModo, _set_refModo)
    refFrec = property(_get_refFrec, _set_refFrec)
    refAmpl = property(_get_refAmpl, _set_refAmpl)
    refHarm = property(_get_refHarm, _set_refHarm)
    refRslp = property(_get_refRslp, _set_refRslp)
    
    inpModo = property(_get_inpModo, _set_inpModo)   
    inpGnd  = property(_get_inpGnd, _set_inpGnd)   
    inpCoup = property(_get_inpCoup, _set_inpCoup)   
    inpLine = property(_get_inpLine, _set_inpLine)       
    
    inpSens = property(_get_inpSens, _set_inpSens) 
    inpRmod = property(_get_inpRmod, _set_inpRmod)
    inpOflt = property(_get_inpOflt, _set_inpOflt)  
    inpOfsl = property(_get_inpOfsl, _set_inpOfsl)
    inpSync = property(_get_inpSync, _set_inpSync)     
    
    stpLock = property(_get_stpLock, _set_stpLock)
    
    ch1Modo = property(_get_ch1Modo, _set_ch1Modo)
    ch2Modo = property(_get_ch2Modo, _set_ch2Modo)
    
    auxout1 = property(_get_auxout1, _set_auxout1)
    auxout2 = property(_get_auxout2, _set_auxout2)
    auxout3 = property(_get_auxout3, _set_auxout3)
    auxout4 = property(_get_auxout4, _set_auxout4)
    
    #----------------------------------------------------------------------
    # Autofunciones (ganancia, reserva, fase y offset)
    #----------------------------------------------------------------------
    
    def autoGanacia(self):
        """ Ejecuta la funcion AutoGanancia del Lockin """
        self._lockin.write('AGAN')
        print('Ejecutando autoGanancia... ', end='')
        while not bool(self._lockin.query('*STB?1')):
            pass
        print('Finalizado')
      
    def autoReserva(self):
        """ Ejecuta la funcion AutoReserva del Lockin """        
        self._lockin.write('ARSV') 
        print('Ejecutando autoReserva... ', end='')
        while not bool(self._lockin.query('*STB?1')):
            pass
        print('Finalizado')
       
    def autoFase(self):
        """ Ejecuta la funcion AutoFase del Lockin """
        self._lockin.write('APHS')
        print('Ejecutando autoFase... ', end='')
        time.sleep(2)
        print('Finalizado')
       
    def autoOffset(self, num):
        """ 
        Ejecuta la funcion AutoGanancia del Lockin 
        
        Parámetros:
        ----------
        num : int
            Cantidad sobre la cual realizar el offset: X(1), Y(2), R(3)            
        """
        if not (num == 1 or num == 2 or num == 3):
            raise ValueError('X(1), Y(2), R(3)')     
        self._lockin.write('AOFF{0}'.format(num))
        print('Ejecutando autoOffset... ', end='')
        time.sleep(2)
        print('Finalizado')
    
    #----------------------------------------------------------------------
    # Almacenamiento del setup en el instrumento
    #----------------------------------------------------------------------
    
    def configGuardar(self, ranura=1):
        """ Guarda la configuración en la ranura indicada (1 a 9) """
        if not (isinstance(ranura, int) and  1 <= ranura <= 9):
            raise ValueError('Ranuras válidas del 1 al 9')   
        self._lockin.write('SSET{0}'.format(ranura))
        print('Configuración guardada en la ranura ' + str(ranura))
    
    def configCargar(self, ranura=1):
        """ Carga la configuración desde la ranura indicada (1 a 9) """
        if not (isinstance(ranura, int) and  1 <= ranura <= 9):
            raise ValueError('Ranuras válidas del 1 al 9')   
        self._lockin.write('RSET{0}'.format(ranura))
        print('Configuración recuperada de la ranura ' + str(ranura))
        
    #----------------------------------------------------------------------
    # Listado y almacenamiento de propiedades en la pc
    #----------------------------------------------------------------------
        
    def listarPropiedades(self, impr=print, nL=''):
        """ 
        Lista las propiedes del Lockin 
        
        Parámetros:
        ----------
        impr : function
            Función utilizada para imprimir. Por defecto utiliza el comando
            print pero en principio es posible utilizar la función write
            correspondiente a un archivo u otra similar.
        nL : str
            Cadena correspondiente al salto de línea. La función print tiene
            por defecto el fin de línea adecuado. Sin embargo la función
            write para la escritura de archivos requiere este parámetro.
        """
            
        sens = str(self._strinpSens[self.inpSens])
        oflt = str(self._strinpOflt[self.inpOflt])
        
        impr('\nPROPIEDADES:\n-----------\n')
        impr('REFERENCIA / FASE:' + nL)
        impr('Origen:_______________ ' + self.refModo + nL)
        impr('Amplitud:_____________ ' + str(self.refAmpl) + 'Vrms' + nL)
        impr('Frecuencia:___________ ' + str(self.refFrec) + 'Hz' + nL)
        impr('Fase:_________________ ' + str(self.refFase) + '°' + nL)
        impr('Armónico #:___________ ' + str(self.refHarm) + nL)
        impr('Ref externa:__________ ' + self.refRslp + nL)
        impr('\n')
        impr('ENTRADA / FILTROS:' + nL)
        impr('Origen:_______________ ' + self.inpModo + nL)
        impr('Tierra:_______________ ' + self.inpGnd + nL)
        impr('Acoplamiento:_________ ' + self.inpCoup + nL)
        impr('Filtros:______________ ' + self.inpLine + nL)
        impr('\n')
        impr('GANANCIA / TC:' + nL)
        impr('Sensibilidad:_________ ' + sens + nL)
        impr('Reserva:______________ ' + self.inpRmod + nL)
        impr('Const. tiempo:________ ' + oflt + nL)
        impr('Filtro dB/oct:________ ' + self.inpOfsl + nL)
        impr('Sincronización:_______ ' + self.inpSync + nL)
        impr('\n')
        impr('DISPLAY:' + nL)
        impr('Canal 1:______________ ' + self.ch1Modo + nL)
#        impr('Razón_________________ ' + self.ch1RatS + nL)
        impr('Canal 2:______________ ' + self.ch2Modo + nL)
#        impr('Razón:________________ ' + self.ch1RatS + nL)
        impr('\n')
        impr('SALIDAS / OFFSET:' + nL)
#        impr('Canal 1:______________ ' + self.ch1OutS + nL)
#        impr('Canal 2:______________ ' + self.ch2OutS + nL)
#        impr('Offset X:_____________ ' + str(self.offsetX) + '%' + nL)   
#        impr('Offset Y:_____________ ' + str(self.offsetY) + '%' + nL)
#        impr('Offset R:_____________ ' + str(self.offsetR) + '%' + nL)     
#        impr('Expand X:_____________ ' + self.expandX + nL)        
#        impr('Expand Y:_____________ ' + self.expandY + nL) 
#        impr('Expand R:_____________ ' + self.expandR + nL)
        impr('\n')
        impr('SALIDAS AUXILIARES:' + nL)
        impr('Auxiliar 1:___________ ' + str(self.auxout1) + 'V' + nL)
        impr('Auxiliar 2:___________ ' + str(self.auxout2) + 'V' + nL)
        impr('Auxiliar 3:___________ ' + str(self.auxout3) + 'V' + nL)
        impr('Auxiliar 4:___________ ' + str(self.auxout4) + 'V' + nL)
        impr('\n')
        impr('CONFIGURACIÓN:' + nL)
        impr('Bloc. teclas:_________ ' + self.stpLock + nL)
        
    def crearRegistro(self, archivoLog='LockinSR830.log'):
        """ Crea un registro con el nombre de archivo indicado """
        with open(archivoLog, 'w') as f:
            self.listarPropiedades(impr=f.write, nL='\n')
        
    def consultarValor(self, valor='R'):
        """ Consulta el valor indicado: 'X', 'Y', 'R' o 'T' """
        valores = {'X': 1, 'Y': 2, 'R': 3, 'T': 4}
        try:
            i = valores[valor]
        except KeyError:
            raise ValueError(valores)
        
        return float(self._lockin.query('OUTP?{0}'.format(i)))
    
    def consultarDisplay(self, display=1):
        """ Consulta el valor actual del display indicado: 1 o 2 """
        if not (display==1 or display==2):
            raise ValueError('CH1 = 1, CH2 = 2')
        return float(self._lockin.query('OUTR?{0}'.format(display)))
    
    def consultarSimultaneo(self, *parametros):
        """
        Consulta simultaneamente los valores indicados (mínimo 2, máximo 6)
        
        Valores permitidos:
        ------------------
            'X', 'Y', 'R', 'T', 
            'AuxIn1', 'AuxIn2', 'AuxIn3', 'AuxIn4', 
            'Frec', 'Ch1', 'Ch2'
        """
        
        valores = {'X': 1, 'Y': 2, 'R': 3, 'T': 4,
                   'AuxIn1': 5, 'AuxIn2': 6, 'AuxIn3': 7, 'AuxIn4': 8,
                   'Frec': 9, 'Ch1': 10, 'Ch2': 11}
        lista = list()
        try:
            for param in parametros:
                lista.append(valores[param])
        except KeyError:
            raise ValueError(valores.keys())        
        if 2 <= len(lista) <= 6:
            consulta = 'SNAP?'
            for elemento in lista[:-1]:
                consulta += str(elemento) +','
            consulta += str(lista[-1])
        else:
            raise ValueError('Mín 2 / Máx 6 parámetros')
        
        return self._lockin.query_ascii_values(consulta, separator=",")
            
    def consultarAuxiliar(self, aux=1):
        """ Consulta el valor de las entradas auxiliares (1 a 4) """
        if not (aux==1 or aux==2 or aux==3 or aux==4):
            raise ValueError('Auxiliares: 1 a 4')
        return float(self._lockin.query('OAUX?{0}'.format(aux)))
    
#    def leerBuffer(self, display=1, frecMuestreo='64 Hz', puntos = 16383,
#                   graficar=True, archivoDatos=''):
#        """
#        Vacia el buffer, adquiere la cantidad de muestras indicadas a la
#        frecuencia seleccionada y finalmente transmite el contenido.
#        
#        Parámetros:
#        ----------
#        display : int
#            Display de origen de datos: 1 o 2.
#        frecMuestreo : int, float, str
#            Selecciona la frecuencia de muestreo. Dado que los valores son
#            una lista fija, puede ingresarse el índice que figura en el
#            manual, el valor como numero flotante o la cadena de texto que
#            se corresponde.
#        puntos : int
#            Número de muestras. Máximo en self._tamBuffer (16383 por manual).
#        graficar : bool
#            Indica si al finalizar se obtiene un gráfico de vista previa.
#        archivoDatos : str
#            Nombre del archivo para el volcado de datos.
#        """
#
#        strFrecs = ('62.5 mHz', '125 mHz', '250 mHz', '500 mHz', '1 Hz', 
#                    '2 Hz', '4 Hz', '8 Hz', '16 Hz', '32 Hz', 
#                    '64 Hz', '128 Hz', '256 Hz', '512 Hz')
#        floatFrecs = (0.0625, 0.125, 0.25, 0.5, 1.0, 
#                      2.0, 4.0, 8.0, 16.0, 32.0,
#                      64.0, 128.0, 256.0, 512.0)
#                
#        if not (display==1 or display==2):
#            raise ValueError('display = 1 ó display = 2')
#        
#        if isinstance(frecMuestreo,str):
#            try:
#                i = strFrecs.index(frecMuestreo)    
#            except ValueError:
#                raise ValueError(strFrecs)    
#        elif isinstance(frecMuestreo, int):
#            if 0 <= frecMuestreo <= 14:
#                i = frecMuestreo    
#            else:
#                raise ValueError('0 <= frecMuestreo <= 14, valor entero')        
#        elif isinstance(frecMuestreo, float):
#            try:
#                i = floatFrecs.index(frecMuestreo)
#            except ValueError:
#                raise ValueError(floatFrecs)   
#        
#        self._lockin.write('SRAT{0}'.format(i))
#        
#        if not (1 <= puntos <= 16383 and isinstance(puntos, int)):
#            raise ValueError('1 <= puntos <= 16383, valor entero')
#            
#        orden = 'TRCB?' + str(display) + ',0,' + str(puntos)
#        
#        modoBuffer = int(self._lockin.query('SEND?'))
#        
#        self._lockin.write('SEND0')
#        self._lockin.write('REST')
#        print('Eliminando datos en buffer...', end='')
#        time.sleep(0.5)
#        print('Hecho.')
#        print('Iniciando volcado de datos en buffer')
#        self._lockin.write('STRT')
#        duracion = puntos / floatFrecs[i] 
#        if duracion > 3:
#            print('Duración estimada: ' + str(duracion) + 's')
#            for paso in self._barraProgreso(50):
#                time.sleep(duracion / 50)
#        print('\nVerificando estado del buffer...', end='')
#        while int(self._lockin.query('SPTS?')) < puntos:
#            time.sleep(0.1)
#        print('Completo. \nTransmitiendo datos a la PC...', end='')
#        
#        self._ejeDatos = self._lockin.query_binary_values(orden, datatype='B', 
#                                                 container=np.array)
#        self._ejeTiempo = np.linspace(0,duracion,puntos)
#        print('Lectura finalizada.')
#        
#        self._lockin.write('PAUS')
#        self._lockin.write('SEND{0}'.format(modoBuffer))       
#        
#        texto_ejeX = 'Tiempo (s)'
#        if display == 1:
#            texto_ejeY = self.ch1Modo + ' (Vrms)'
#        else:
#            if self.ch2Modo == 'T':
#                texto_ejeY = 'Fase (º)'
#            else:
#                texto_ejeY = self.ch1Modo + ' (Vrms)'
#        
#        if graficar == True:
#            titulo = 'Display - Canal ' + str(display)
#            figura = plt.figure()
#            figura.canvas.set_window_title(titulo)
#            self._figuras.append(figura)
#            ejes = figura.add_subplot(111)
#            ejes.set_title(titulo)
#            ejes.set_xlabel(texto_ejeX)
#            ejes.set_ylabel(texto_ejeY)
#            ejes.plot(self._ejeTiempo, self._ejeDatos)
#            ejes.legend(self.ch1Modo, loc='best', frameon=True,
#                            shadow=True, fancybox=True)
#            
#        if isinstance(archivoDatos, str) and len(archivoDatos) > 0:
#            datos = np.array([self._ejeTiempo, self._ejeDatos])
#            datos = datos.transpose()
#            np.savetxt(archivoDatos, datos, delimiter=',',newline='\r\n',
#                       header= texto_ejeX + ',' + texto_ejeY)
#        
#        self._datos.append([self._ejeTiempo, self._ejeDatos])      
#        
#        if graficar == False:
#            return self._ejeTiempo, self._ejeDatos
#        else:
#            return self._ejeTiempo, self._ejeDatos, figura
    
    def leerDirectoXY(self):
        """ Lectura directa utilizando el comando Fast Data Transfer """
        pass
    
    def barrerFrecuencia(self, inicio, fin, pasos, 
                         graficar, *parametros):
        """
        Barrido de frecuencia con obtención de multiples parámetros.
        Se utiliza la función consultar simultáneo al mismo tiempo que se
        barre entre la frecuencia inicial y final a un número dado de pasos.
        
        Parámetros:
        ----------
        inicio : float
            Frecuencia inicial.
        fin : float
            Frecuencia final.
        puntos : int
            Número de pasos.
        graficar : bool
            Indica si al finalizar se obtiene un gráfico de vista previa.
        parametros : tuple
            Parámetros a medir. Los valores permitidos son los mismos que
            para la función consultarSimultaneo.
        """                           
        
        self._frecBarrido = np.linspace(inicio, fin, pasos)
        self.consultarSimultaneo(*parametros)
        
        self._datosBarrido = np.zeros([pasos, len(parametros)])
            
        for i in self._barraProgreso(pasos):
            self.refFrec = self._frecBarrido[i]
            self._datosBarrido[i] = self.consultarSimultaneo(*parametros)
            
        self._datosBarrido = self._datosBarrido.transpose()
        
        if 0 < graficar <= len(parametros):
            figura = plt.figure()
            titulo = ('Barrido de frecuencia: ' + str(inicio) +
                      ' a ' + str(fin) + ' Hz')  
            figura.canvas.set_window_title(titulo)
            ejes = figura.add_subplot(111)
            ejes.set_title(titulo)
            ejes.set_xlabel('Frecuencia (Hz)')

            for i in range(graficar):
                ejes.plot(self._frecBarrido, self._datosBarrido[i])            
            
            if graficar == 1:
                if parametros[0] == 'T':
                    ejes.set_ylabel('Fase (º)')    
                else:
                    ejes.set_ylabel(parametros[0] + '(Vrms)')
                ejes.legend([parametros[0]], loc='best', frameon=True,
                            shadow=True, fancybox=True)
            else:
                ejes.set_ylabel('Tensión (Vrms)')
                ejes.legend(parametros, loc='best', frameon=True,
                            shadow=True, fancybox=True)
                
            self._figuras.append(figura)
        
        self._datos.append([self._frecBarrido, self._datosBarrido])
        
        if graficar == False:
            return self._frecBarrido, self._datosBarrido
        else:
            return self._frecBarrido, self._datosBarrido, figura
   
    def guardarDatos(self, archivoDatos, datos, nombre_columnas=''):  
        """ 
        Guarda los datos ingresados como iterable (tupla o lista) en el
        archivo indicado.
        """
        datos = np.array([datos])
        datos = datos.transpose()
        np.savetxt(archivoDatos, datos, delimiter=',',newline='\r\n',
                   header=nombre_columnas)         
    
    def cargarDatos(self, archivoDatos, unpack=True):
        """ Carga los datos del archivo indicado y puede desempacarlos """
        return np.loadtxt(archivoDatos, delimiter=',', unpack=True)
    
    def _probarTodasLasFunciones(self):
        """ Función auxiliar para pruebas """
        self.listarPropiedades()
        self.autoFase()
        self.autoGanacia()
        self.autoOffset(1)
        self.autoOffset(2)
        self.autoOffset(3)
        self.autoReserva()
        self.cargarDelInstrumento()
        self.guardarEnInstrumento() 
        
    def _barraProgreso(self, a, b=None, paso=1, texto='Progreso:', largo=30):
        """ Barra de progreso con comportamiento idéntico a range() """
        inicial = 0 if b is None else a
        actual = 0 if b is None else a
        final = a if b is None else b        
        barra = '.' * largo
        
        while actual < final:
            yield actual
            actual += paso
            
            i = int(largo * (actual - inicial) / (final - inicial))
            porcentaje = 100 * (actual - inicial) / (final - inicial)
            print('\r[%s] %s %3d%%' % (barra, texto, porcentaje), 
                  end='')
            barra = barra[:i] + '#' + barra[i+1:]