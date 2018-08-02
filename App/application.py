#!/usr/bin/env python3

import gi
import dataread
import lcd
import grapher
import bluetoothio
import datetime
import matplotlib.pyplot as plt
import threading
from multiprocessing import Process


gi.require_version('Gtk', '3.0')
from gi.repository import GLib, GObject, Gtk


class Application(Gtk.Application):

    UPDATE_INTERVAL = 25000
    LCD_INTERVAL = 1000

    def __init__(self):
        self.window = Gtk.Window(title='TDR')
        self.window.connect('destroy', Gtk.main_quit)
        self.window.set_resizable(False)
        self.window.set_size_request(500, 400)
        self.window.set_position(Gtk.WindowPosition.CENTER)

        self.container = Gtk.Fixed()
        self.window.add(self.container)

        self.label = Gtk.Label()
        self.button = Gtk.Button(label='Press me')
        self.button.connect('clicked', Application.button_clicked)

        self.container.put(self.button, 300, 300)
        self.container.put(self.label, 200, 100)

        self.window.show_all()

        self.datareader1 = dataread.DataRead('/dev/ttyACM0')
        self.datareader2 = dataread.DataRead('/dev/ttyACM1')
        self.bluetoothdv = bluetoothio.BluetoothIO()
        
        self.lcd1 = lcd.LCD(0x3f)
        #self.lcd2 = lcd.LCD(address ?)

        self.graphprocess = Process(target=grapher.update_graph, args=[''])


    @staticmethod
    def update_bluetooth(btdevice):
        while True:
            btdevice.wait_for_connection()

            try:
                while True:
                    data = btdevice.read()
                    if len(data) == 0: break
                    
                    print("Received " + data)
                    
            except IOError:
                pass

            btdevice.close()


    @staticmethod
    def set_text(app):
        data1 = app.datareader1.read_input()
        data2 = app.datareader2.read_input()

        data = {**data1, **data2}

        for i in dataread.DataRead.POSSIBLE_DATA:
            if i not in data:
                data[i] = 0

        data['TIME'] = datetime.datetime.now().strftime('%H:%M:%S %d/%m/%Y')
        stringdata = ''
        
        for key, val in data.items():
            stringdata += key + ': ' + str(val) + '\n'

        app.label.set_text(stringdata)
        app.bluetoothdv.write(str(data).replace("'", '"'))
        
        with open('register.json', 'r') as file:
            read = file.read()

        with open('register.json', 'w+') as file:
            read = read[:read.find(']')]
            register = read + '\t,' + str(data).replace("'", '"') + '\n]'
            file.write(register)

        if (app.graphprocess.is_alive()):
            app.graphprocess.terminate()

        app.graphprocess = Process(target=grapher.update_graph, args=[register])
        app.graphprocess.start()
        
        return True


    @staticmethod
    def button_clicked(button):
        print('Button clicked')
    

    def update_lcd(self):
        self.lcd1.send_string('Hello LCD1!', lcd.LCD.LINE_1)
        #self.lcd2.send_string('Hello LCD2!', lcd.LCD.LINE_1)


    def run(self):
        GObject.threads_init()
        GLib.timeout_add(Application.UPDATE_INTERVAL, Application.set_text, self)
        GLib.timeout_add(Application.LCD_INTERVAL, Application.update_lcd, self)

        btthread = threading.Thread(target=Application.update_bluetooth, args=[self.bluetoothdv])
        btthread.daemon = True
        btthread.start()

        Gtk.main()


if __name__ == '__main__':
    Application().run()
