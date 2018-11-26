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
        self.text_axes_rango = []
        self.text_vector = []
        self.text_value_vector = []





        # FIFO donde se guardan los datos leidos desde el Serial.
        self.fifo_queue = queue.Queue(100)



        threading.Thread.__init__(self)
        self.hiloTkinter = threading.Thread(target=self.tkinterGui,name='tkinterGui')
        self.hiloLeerSerial = threading.Thread(target=self.leerSerial, name='leerSerial')
        self.hiloParser = threading.Thread(target=self.parser, name='plot')
        #self.hiloMatplotlib = threading.Thread(target=self.matplotlibGui,name='matplotlibGui')
        self.hiloLeerSerial.start()
        self.hiloParser.start()
        self.hiloTkinter.start()
        #self.hiloMatplotlib.start()





        #geoplotlib.add_layer(AnimatedLayer())
        #geoplotlib.show()







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

        self.fig = plt.figure(constrained_layout=True)
        self.gs = GridSpec(2, 2, figure=self.fig)
        self.az = self.fig.add_subplot(self.gs[:, 0], projection='polar', zorder=1)

        self.az.set_theta_zero_location("N")
        self.az.set_ylim([0, 100000])
        self.az.set_theta_direction(-1)
        self.az.grid(color='#424242', linestyle='-', linewidth='1')  # Color de la grilla
        self.scatter_objeto_az = self.az.scatter([], [], c='black', s=100, cmap='hsv', alpha=0.75)

        self.el = self.fig.add_subplot(self.gs[0, 1], projection='polar')  # gs[fila, columna]
        self.el.set_thetamin(0)
        self.el.set_thetamax(90)
        self.el.set_ylim([0, 100000])
        self.el.grid(color='#424242', linestyle='-', linewidth='1')  # Color de la grilla
        self.scatter_objeto_el = self.el.scatter([], [], c='black', s=100, cmap='hsv', alpha=0.75)

        self.sal = self.fig.add_subplot(self.gs[1, 1])  # gs[fila, columna]
        self.text_vector.append(self.sal.text(0.1, 0.7, r'Azimuth', fontsize=12))
        self.text_vector.append(self.sal.text(0.7, 0.7, r'Elevacion', fontsize=12))
        self.text_vector.append(self.sal.text(0.1, 0.3, r'Rango', fontsize=12))
        self.text_vector.append(self.sal.text(0.7, 0.3, r'Altitud', fontsize=12))

        self.text_value_vector.append(self.sal.text(0, 0.6, 0, fontsize=8))
        self.text_value_vector.append(self.sal.text(0.7, 0.6, 0, fontsize=8))
        self.text_value_vector.append(self.sal.text(0.0, 0.2, 0, fontsize=8))
        self.text_value_vector.append(self.sal.text(0.7, 0.2, 0, fontsize=8))

        print(self.text_value_vector)

        self.sal.axis('off')

        self.canvas = FigureCanvasTkAgg(self.fig, master=self.root)  # A tk.DrawingArea.
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

        self.canvas.mpl_connect("key_press_event", self.on_key_press)
        self.button = tk.Button(master=self.root, text="Quit", command=self._quit)
        self.button.pack(side=tk.BOTTOM)

        #self.background = self.canvas.copy_from_bbox(self.az.bbox)

        #self.fig.canvas.blit(self.fig.bbox)

        #self.fig.canvas.restore_region(self.background)

        #self.root.after(0, self.matplotlibGui())
        #tk.mainloop()



    def on_key_press(self, event):
        print("you pressed {}".format(event.key))
        key_press_handler(event, self.canvas, self.toolbar)



    def _quit(self):
        self.root.quit()  # stops mainloop
        self.root.destroy()  # this is necessary on Windows to prevent
        # Fatal Python Error: PyEval_RestoreThread: NULL tstate

    def matplotlibGui(self):
        ""

            # actualizacion d  el dibujo

        while True:
            time.sleep(1)

            for x in range(0, 4):
                try:
                    self.text_value_vector.pop().remove()
                except:
                    print("error")
            print("asdasd")
            self.text_value_vector.append(self.sal.text(0.1, 0.6, 30, fontsize=10))
            self.text_value_vector.append(self.sal.text(0.7, 0.6, 40, fontsize=10))
            self.text_value_vector.append(self.sal.text(0.1, 0.2, 10000, fontsize=10))
            self.text_value_vector.append(self.sal.text(0.7, 0.2, 0, fontsize=10))

            self.objetivo_az_rango[0] = self.azimuth
            self.objetivo_az_rango[1] = self.rango
            # self.objetivo_az_rango[1] = self.rango_contador
            self.objetivo_el_rango[0] = self.elevacion
            self.objetivo_el_rango[1] = self.rango

            print(self.objetivo_az_rango)
            self.scatter_objeto_az.set_offsets(self.objetivo_az_rango)
            self.scatter_objeto_el.set_offsets(self.objetivo_el_rango)




    def parser(self):

        while fin == 0:
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

        while fin == 1:
            self.azimut = 180
            self.elevacion = 70
            self.rango = 20000

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
        print("entra")
        # time.sleep(0.1)
        while fin == 0:
            self.pParam2 = self.ser.readline()
            self.fifo_queue.put(self.pParam2)
            time.sleep(0.02)
            # print(self.pParam2)

    def update(self, *args):
        # if(self.counter < len(self.data_now)):
        #    self.objetivoXY = self.data_now[self.counter]
        #    self.counter = self.counter+1
        # else:
        #    self.counter = 0
        for x in range(0, 4):
            try:
                self.text_value_vector.pop().remove()
            except:
                print("error")

        self.text_value_vector.append(self.sal.text(0.1, 0.6, self.azimuth_, fontsize=10))
        self.text_value_vector.append(self.sal.text(0.7, 0.6, self.elevacion_, fontsize=10))
        self.text_value_vector.append(self.sal.text(0.1, 0.2, self.rango, fontsize=10))
        self.text_value_vector.append(self.sal.text(0.7, 0.2, 0, fontsize=10))

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
        self.data_lat = [-31.234]
        self.data_long = [-64.34]

        self.frame_counter = 0
        print(self.data_long)


    def invalidate(self, proj):
        #self.x, self.y = proj.lonlat_to_screen(self.data['lon'], self.data['lat'])
        print("algo")
        self.x, self.y = proj.lonlat_to_screen(self.data_long, self.data_lat)
        self.vitro_x, self.vitro_y = proj.lonlat_to_screen([-64.2695147], [-31.434847])

    def draw(self, proj, mouse_x, mouse_y, ui_manager):

        self.painter = BatchPainter()
        self.painter.points(self.vitro_x,
                            self.vitro_y)
        self.painter.points(self.x,#[self.frame_counter],
                            self.y,)#[self.frame_counter],point_size=4, rounded=True)

        self.painter.batch_draw()
        self.frame_counter += 1

    def bbox(self):
        return BoundingBox(north=-29, west=-65, south=-32, east=-64)





if __name__ == '__main__':
    ProcesamientoDeDatos()

