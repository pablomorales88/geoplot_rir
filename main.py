from geoplotlib.layers import BaseLayer
from geoplotlib.core import BatchPainter
import geoplotlib
from geoplotlib.colors import colorbrewer
from geoplotlib.utils import epoch_to_str, BoundingBox, read_csv
import numpy as np
import csv
import threading
import matplotlib.animation as animation
import matplotlib.pyplot as plt
import threading
import serial
import queue
import time
import sys

try:
    import ttk
    py3 = False
except ImportError:
    import tkinter.ttk as ttk
    py3 = True

import matplotlib.animation as animation
import numpy as np
from matplotlib.gridspec import GridSpec

import tkinter as tk

from matplotlib.backends.backend_tkagg import (
    FigureCanvasTkAgg, NavigationToolbar2Tk)
# Implement the default Matplotlib key bindings.
from matplotlib.backend_bases import key_press_handler
from matplotlib.figure import Figure

global data_longitud
global data_latitud
fin = 1


class ProcesamientoDeDatos():
    def __init__(self):

        self.archivo_loggin = open('loggin_vitro.log', 'w')
        self.altitud_sim = 0.0
        self.az_el_rang_sim = [0,0,0]
        self.az_sim = 0.0
        self.el_sim = 0.0
        self.rango_sim = 0.0
        self.latitud_objetivo = 0.0
        self.longitud_objetivo = 0.0



        self.counter = 0
        print("Hola Mundo")
        self.data_serial = []
        self.azimuth = 0.0
        self.elevacion = 0.0
        self.azimuth_ = 0.0
        self.elevacion_ = 0.0
        self.rango = 0
        self.altitud = 0
        self.objetivo_az_rango = [0.0, 0]  # [azimuth,rango]
        self.objetivo_el_rango = [0.0, 0]  # [elevacion,rango]
        self.rango_contador = 0




        # FIFO donde se guardan los datos leidos desde el Serial.
        self.fifo_queue = queue.Queue(100)
        self.loggin_queue = queue.Queue(10)


        threading.Thread.__init__(self)
        self.hiloTkinter = threading.Thread(target=self.tkinterGui,name='tkinterGui')
        self.hiloLeerSerial = threading.Thread(target=self.leerSerial, name='leerSerial')
        self.hiloParser = threading.Thread(target=self.parser, name='plot')
        self.hiloLoggin = threading.Thread(target=self.login, name='login')


        self.hiloLeerSerial.start()
        self.hiloParser.start()
        self.hiloTkinter.start()
        self.hiloLoggin.start()

        self.prueba = AnimatedLayer()
        geoplotlib.add_layer(self.prueba)
        geoplotlib.show()


    def login(self):
        while True:
            self.archivo_loggin.write(str(self.loggin_queue.get(block=True, timeout=None)))

    def ball_update(self):


        self.counter = self.counter + 100
        self.altitud_sim = np.sin((self.el_sim * np.pi) / 180) * self.rango_sim
        #print(self.counter)
        self.objetivo_az_rango[0] = (self.az_sim*np.pi)/180#0.785398163#self.azimuth
        self.objetivo_az_rango[1] = self.rango_sim#self.counter % 100000  # self.rango
        # self.objetivo_az_rango[1] = self.rango_contador
        self.objetivo_el_rango[0] = (self.el_sim*np.pi)/180#1.047197551#self.elevacion
        self.objetivo_el_rango[1] = self.rango_sim#self.counter % 100000  # self.rango

        self.scatter_objeto_az.set_offsets(self.objetivo_az_rango)
        self.scatter_objeto_el.set_offsets(self.objetivo_el_rango)
        # self.fig.canvas.draw()
        #self.v.set(str(self.counter))

        self.az.draw_artist(self.scatter_objeto_az)
        self.el.draw_artist(self.scatter_objeto_el)

        self.fig.canvas.blit(self.fig.bbox)
        self.fig.canvas.restore_region(self.background)

        #print("--- %s seconds ---" % (time.time() - self.start_time))
        #self.prueba.setLatLong(10,20)
        self.latitud_objetivo,self.longitud_objetivo = self.prueba.azelraToLatLong(self.az_sim,self.el_sim,self.rango_sim)
        self.value_rango.set("{0:.2f}".format(self.rango_sim))
        self.value_az.set("{0:.2f}".format(self.az_sim))
        self.value_el.set("{0:.2f}".format(self.el_sim))
        self.value_altitud.set("{0:.2f}".format(self.altitud_sim)) #Aca tiene que ir el calculo de altitud
        self.loggin_queue.put(["{0:.2f}".format(self.az_sim),"{0:.2f}".format(self.el_sim),"{0:.2f}".format(self.rango_sim),"{0:.2f}".format(self.altitud_sim), self.latitud_objetivo,self.longitud_objetivo])

    def move_active(self):
        self.start_time = time.time()
        if self.active:
            self.ball_update()
            self.root.after(0, self.move_active)  # changed from 10ms to 30ms




    def count(self):
        global counter
        self.counter += 1
        self.label.config(text=str(self.counter))
        self.label.after(1000, self.count)

    def counter_label(self, label):
        self.count()

    def tkinterGui(self):
        self.root = tk.Tk()
        self.root.title("Counting Seconds")

        self.value_az = tk.StringVar()
        self.value_el = tk.StringVar()
        self.value_rango = tk.StringVar()
        self.value_altitud = tk.StringVar()
        '''This class configures and populates the toplevel window.
                     top is the toplevel containing window.'''
        _bgcolor = '#d9d9d9'  # X11 color: 'gray85'
        _fgcolor = '#000000'  # X11 color: 'black'
        _compcolor = '#d9d9d9'  # X11 color: 'gray85'
        _ana1color = '#d9d9d9'  # X11 color: 'gray85'
        _ana2color = '#ececec'  # Closest X11 color: 'gray92'
        font10 = "-family {Segoe UI} -size 14 -weight normal -slant " \
                 "roman -underline 0 -overstrike 0"
        font11 = "-family {Segoe UI} -size 15 -weight normal -slant " \
                 "roman -underline 0 -overstrike 0"
        font12 = "-family {Tw Cen MT Condensed} -size 40 -weight bold " \
                 "-slant italic -underline 0 -overstrike 0"
        font9 = "-family {Segoe UI} -size 20 -weight normal -slant " \
                "roman -underline 0 -overstrike 0"
        self.style = ttk.Style()
        if sys.platform == "win32":
            self.style.theme_use('winnative')
        self.style.configure('.', background=_bgcolor)
        self.style.configure('.', foreground=_fgcolor)
        self.style.configure('.', font="TkDefaultFont")
        self.style.map('.', background=
        [('selected', _compcolor), ('active', _ana2color)])

        self.root.geometry("1688x959+116+34")

        self.root.title("VITRO RIR-778C")
        self.root.configure(background="#d9d9d9")


        self.fig = plt.figure(figsize=(16.90,8))


        self.gs = GridSpec(2, 2, figure=self.fig)
        self.az = self.fig.add_subplot(self.gs[:, 0], projection='polar', zorder=1)

        self.az.set_theta_zero_location("N")
        self.az.set_ylim([0, 100000])
        self.az.set_theta_direction(-1)
        self.az.grid(color='#424242', linestyle='-', linewidth='1')  # Color de la grilla
        self.scatter_objeto_az = self.az.scatter([], [], c='black', s=100, cmap='hsv', alpha=0.75)

        self.el = self.fig.add_subplot(self.gs[:, 1], projection='polar')  # gs[fila, columna]
        self.el.set_thetamin(0)
        self.el.set_thetamax(90)
        self.el.set_ylim([0, 100000])
        self.el.grid(color='#424242', linestyle='-', linewidth='1')  # Color de la grilla
        self.scatter_objeto_el = self.el.scatter([], [], c='black', s=100, cmap='hsv', alpha=0.75)

        self.Canvas1 = tk.Canvas(self.root)
        self.Canvas1.place(relx=0.0, rely=0.0, relheight=0.827, relwidth=1.003)
        self.Canvas1.configure(background="#d9d9d9")
        self.Canvas1.configure(borderwidth="2")
        self.Canvas1.configure(insertbackground="black")
        self.Canvas1.configure(relief='ridge')
        self.Canvas1.configure(selectbackground="#c4c4c4")
        self.Canvas1.configure(selectforeground="black")
        self.Canvas1.configure(width=1693)

        self.canvas = FigureCanvasTkAgg(self.fig, master=self.Canvas1)  # A tk.DrawingArea.

        self.canvas.draw()
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

        """
        self.canvas.mpl_connect("key_press_event", self.on_key_press)
        self.button = tk.Button(master=self.root, text="Quit", command=self._quit)
        self.button.pack(side=tk.BOTTOM)

        self.v = tk.StringVar()
        self.label = tk.Label(master=self.root, text="Graph Page!", textvariable=self.v)
        self.label.pack(side=tk.BOTTOM)
        """
        self.Label1 = tk.Label(self.root)
        self.Label1.place(relx=0.195, rely=0.834, height=81, width=116)
        self.Label1.configure(background="#d9d9d9")
        self.Label1.configure(disabledforeground="#a3a3a3")
        self.Label1.configure(font=font10)
        self.Label1.configure(foreground="#000000")
        self.Label1.configure(text='''Azimuth''')
        self.Label1.configure(width=116)

        self.Label2 = tk.Label(self.root)
        self.Label2.place(relx=0.361, rely=0.834, height=74, width=98)
        self.Label2.configure(background="#d9d9d9")
        self.Label2.configure(disabledforeground="#a3a3a3")
        self.Label2.configure(font=font11)
        self.Label2.configure(foreground="#000000")
        self.Label2.configure(text='''Elevacion''')
        self.Label2.configure(width=98)

        self.Label3 = tk.Label(self.root)
        self.Label3.place(relx=0.515, rely=0.834, height=74, width=93)
        self.Label3.configure(background="#d9d9d9")
        self.Label3.configure(disabledforeground="#a3a3a3")
        self.Label3.configure(font=font11)
        self.Label3.configure(foreground="#000000")
        self.Label3.configure(text='''Rango''')
        self.Label3.configure(width=93)

        self.Label4 = tk.Label(self.root)
        self.Label4.place(relx=0.681, rely=0.834, height=74, width=116)
        self.Label4.configure(background="#d9d9d9")
        self.Label4.configure(disabledforeground="#a3a3a3")
        self.Label4.configure(font=font11)
        self.Label4.configure(foreground="#000000")
        self.Label4.configure(text='''Altitud''')
        self.Label4.configure(width=116)

        self.Simulador = tk.Button(self.root)
        self.Simulador.place(relx=0.918, rely=0.928, height=54, width=97)
        self.Simulador.configure(activebackground="#ececec")
        self.Simulador.configure(activeforeground="#000000")
        self.Simulador.configure(background="#d9d9d9")
        self.Simulador.configure(disabledforeground="#a3a3a3")
        self.Simulador.configure(foreground="#000000")
        self.Simulador.configure(highlightbackground="#d9d9d9")
        self.Simulador.configure(highlightcolor="black")
        self.Simulador.configure(pady="0")
        self.Simulador.configure(text='''Simulador''')
        self.Simulador.configure(width=97)

        self.Real = tk.Button(self.root)
        self.Real.place(relx=0.918, rely=0.845, height=54, width=93)
        self.Real.configure(activebackground="#ececec")
        self.Real.configure(activeforeground="#000000")
        self.Real.configure(background="#d9d9d9")
        self.Real.configure(disabledforeground="#a3a3a3")
        self.Real.configure(foreground="#000000")
        self.Real.configure(highlightbackground="#d9d9d9")
        self.Real.configure(highlightcolor="black")
        self.Real.configure(pady="0")
        self.Real.configure(text='''Real Time''')
        self.Real.configure(width=93)

        self.Label5 = tk.Label(self.root, textvariable=self.value_az)
        self.Label5.place(relx=0.195, rely=0.918, height=51, width=114)
        self.Label5.configure(background="#d9d9d9")
        self.Label5.configure(disabledforeground="#a3a3a3")
        self.Label5.configure(font=font9)
        self.Label5.configure(foreground="#000000")
        self.Label5.configure(text='''V_AZ''')
        self.Label5.configure(width=114)

        self.Label6 = tk.Label(self.root,textvariable=self.value_el)
        self.Label6.place(relx=0.355, rely=0.918, height=53, width=131)
        self.Label6.configure(background="#d9d9d9")
        self.Label6.configure(disabledforeground="#a3a3a3")
        self.Label6.configure(font=font9)
        self.Label6.configure(foreground="#000000")
        self.Label6.configure(text='''V_EL''')
        self.Label6.configure(width=131)

        self.Label7 = tk.Label(self.root, textvariable=self.value_rango)
        self.Label7.place(relx=0.498, rely=0.918, height=53, width=166)
        self.Label7.configure(background="#d9d9d9")
        self.Label7.configure(disabledforeground="#a3a3a3")
        self.Label7.configure(font=font9)
        self.Label7.configure(foreground="#000000")
        self.Label7.configure(text='''V_RANGO''')
        self.Label7.configure(width=166)

        self.Label8 = tk.Label(self.root, textvariable=self.value_altitud)
        self.Label8.place(relx=0.681, rely=0.928, height=53, width=128)
        self.Label8.configure(activebackground="#f0f0f0")
        self.Label8.configure(background="#d9d9d9")
        self.Label8.configure(disabledforeground="#a3a3a3")
        self.Label8.configure(font=font9)
        self.Label8.configure(foreground="#000000")
        self.Label8.configure(text='''V_ALT''')
        self.Label8.configure(width=128)

        self.TLabel1 = ttk.Label(self.root)
        self.TLabel1.place(relx=-0.006, rely=0.834, height=149, width=346)
        self.TLabel1.configure(background="#d9d9d9")
        self.TLabel1.configure(foreground="#000000")
        self.TLabel1.configure(font=font12)
        self.TLabel1.configure(relief='flat')
        self.TLabel1.configure(text='''VITRO RIR-778C''')
        self.TLabel1.configure(width=346)




        self.background = self.canvas.copy_from_bbox(self.fig.bbox)
        self.active = True
        self.move_active()
        self.ball_update()
        tk.mainloop()

    def on_key_press(self, event):
        print("you pressed {}".format(event.key))
        key_press_handler(event, self.canvas, self.toolbar)



    def _quit(self):
        self.root.quit()  # stops mainloop
        self.root.destroy()  # this is necessary on Windows to prevent
        # Fatal Python Error: PyEval_RestoreThread: NULL tstate


    def parser(self):

        while True:
            if fin == 0:
                self.data_serial = str(self.fifo_queue.get(block=True, timeout=None)).split(';')
                # ["b'", 'D59D3','0','0','3FF98', '0', '0','2385', "\\r\\n'"]
                # ;29A02;0;0;3E585;0;0;25AD;
                if len(self.data_serial) > 5:

                    try:
                        self.azimuth_ = float(int(self.data_serial[1], 16) * 360) / 1048576
                        self.elevacion_ = float(int(self.data_serial[4], 16) * 360) / 1048576
                        # print(self.azimuth_)
                        self.azimuth = float(self.azimuth_ * np.pi) / 180
                        self.elevacion = float(self.elevacion_ * np.pi) / 180


                    except:
                        self.azimuth = self.azimuth
                        self.elevacion = self.elevacion

                    try:
                        self.rango = int(self.data_serial[7], 16) / 2
                        # print(self.rango)
                    except:
                        print("errorpyth")

            elif fin == 1:

                self.data_serial = str(self.fifo_queue.get(block=True, timeout=None)).split(',')
                for x in range(0, 9):  # [0,9] por la cantidad de columnadas que tiene el archivo
                    # send.append(int(row[x],16)) #paso los hex a enteros
                    #print(self.data_serial)
                    if x == 1:
                        try:
                            #print(self.data_serial[x].replace("'", ''))
                            # azimuth.append(((float(int(row[x],16)*360)/1048576)*np.pi)/180)
                            self.az_sim = float(int(self.data_serial[x].replace("'", ''), 16) * 360) / 1048576

                        except:
                            print("Error_az_sim")
                    if x == 4:
                        try:
                            #print(self.data_serial[x].replace("'", ''))
                            # elevacion.append(((float(int(row[x],16)*360)/1048576)*np.pi)/180)
                            self.el_sim = float(int(self.data_serial[x].replace("'", ''), 16) * 360) / 1048576
                        except:
                            print("Error_el_sim")

                    if x == 7:
                        try:
                            #print(self.data_serial[x].replace("'", ''))
                            self.rango_sim = int(self.data_serial[x].replace("'", ''), 16) / 2
                        except:
                            print("Error_rango_sim")

                time.sleep(0.02)
                # if self.rango_contador <= 20000:
                #    self.azimuth = float(135 * np.pi) / 180
                #    self.rango_contador = self.rango_contador + 400
                #    self.elevacion =  float(50 * np.pi) / 180

                # else:
                #    self.rango_contador = 0

                # self.rango = int(self.data_serial[7], 16)/2
                # print(self.azimuth, self.rango)

    def leerSerial(self):
        if fin == 0:
            self.ser = serial.Serial('COM31', baudrate=115200)
        elif fin == 1:
            print("Modo OFF-Line - Lectura de CSV")


        elif fin == 2:
            print("MODO IDLE")

        while True:
            if fin == 0:
                self.pParam2 = self.ser.readline()
                self.fifo_queue.put(self.pParam2)
                time.sleep(0.02)
                # print(self.pParam2)
            elif fin == 1:
                #hacer la lectura del csv t mandarlo por pParam2
                with open('C:\\Users\\pablo\\Desktop\\logsOperacionVitro\\100ms\\2018-11-15-111822.log','r') as csvFile:
                    self.reader = csv.reader(csvFile, delimiter=';')
                    for row in self.reader:
                        self.fifo_queue.put(row)
                        time.sleep(0.02)

            else:
                #No hacer Nada
                time.sleep(0.02)

    def update(self, *args):
        # if(self.counter < len(self.data_now)):
        #    self.objetivoXY = self.data_now[self.counter]
        #    self.counter = self.counter+1
        # else:
        #    self.counter = 0

        #for x in range(0, 4):
        #    try:
        #        self.text_value_vector.pop().remove()
        #    except:
        #        print("error")

        # self.text_value_vector.append(self.sal.text(0.1, 0.6, self.azimuth_, fontsize=10))
        #self.text_value_vector.append(self.sal.text(0.7, 0.6, self.elevacion_, fontsize=10))
        #self.text_value_vector.append(self.sal.text(0.1, 0.2, self.rango, fontsize=10))
        #self.text_value_vector.append(self.sal.text(0.7, 0.2, 0, fontsize=10))

        self.objetivo_az_rango[0] = self.azimuth
        self.objetivo_az_rango[1] = self.rango
        # self.objetivo_az_rango[1] = self.rango_contador
        self.objetivo_el_rango[0] = self.elevacion
        self.objetivo_el_rango[1] = self.rango

        print(self.objetivo_az_rango)
        self.scatter_objeto_az.set_offsets(self.objetivo_az_rango)
        self.scatter_objeto_el.set_offsets(self.objetivo_el_rango)
        return self.objetivo_az_rango

class AnimatedLayer(BaseLayer):

    def __init__(self):
        #self.data_lat = [-31.234]
        #self.data_long = [-64.34]

        self.frame_counter = 0
        self.latitud_target = 0.0  # +lat_vitro
        self.longitud_target = 0.0  # +long_vitro
        self.latitudes = []
        self.longitudes = []


    def invalidate(self, proj):
        #self.x, self.y = proj.lonlat_to_screen(self.data['lon'], self.data['lat'])

        self.x, self.y = proj.lonlat_to_screen([self.longitud_target], [self.latitud_target])
        self.vitro_x, self.vitro_y = proj.lonlat_to_screen([-64.2695147], [-31.434847])

    def draw(self, proj, mouse_x, mouse_y, ui_manager):
        if len(self.longitudes) >= 50:
            self.longitudes.pop(0)
            self.latitudes.pop(0)

        self.latitudes.append(self.latitud_target)
        self.longitudes.append(self.longitud_target)

        self.x, self.y = proj.lonlat_to_screen([self.longitudes], [self.latitudes])
        self.painter = BatchPainter()
        self.painter.points(self.vitro_x,
                            self.vitro_y)
        self.painter.points(self.x,#[self.frame_counter],
                            self.y, point_size=4, rounded=True)#[self.frame_counter],point_size=4, rounded=True)

        self.painter.batch_draw()
        self.frame_counter += 1

    def bbox(self):
        return BoundingBox(north=-29, west=-65, south=-32, east=-64)


    def azelraToLatLong(self,_azimuth, _elevacion, _rango):
        x_lat_point, y_lat_point, z_range_point = self.sph2cart(_azimuth, _elevacion, _rango)
        x_lat_point = (x_lat_point / 111) / 1000
        y_lat_point = (y_lat_point / 94.930) / 1000
        self.latitud_target = x_lat_point - 31.434847 #+lat_vitro
        self.longitud_target = y_lat_point - 64.2695147 #+long_vitro
        return self.latitud_target,self.longitud_target
        #self.x, self.y = proj.lonlat_to_screen(self.data_long, self.data_lat)

    def sph2cart(self,az_point, el_point, r_point):
        rcos_theta = r_point * np.cos((el_point * np.pi) / 180)
        x_2 = rcos_theta * np.cos((az_point * np.pi) / 180)
        y_2 = rcos_theta * np.sin((az_point * np.pi) / 180)
        z_2 = r_point * np.sin((el_point * np.pi) / 180)
        return x_2, y_2, z_2

if __name__ == '__main__':
    ProcesamientoDeDatos()

