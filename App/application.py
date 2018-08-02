#!/usr/bin/env python3

import gi
import dataread
import lcd
import grapher
import bluetoothio
import datetime
import matplotlib.pyplot as plt
import threading
import os
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
        self.window.set_size_request(800, 600)
        self.window.set_position(Gtk.WindowPosition.CENTER)

        self.container = Gtk.Fixed()
        self.window.add(self.container)

        self.bluetooth_label = Gtk.Label(label='Bluetooth: not connected')
        self.container.put(self.bluetooth_label, 50, 50)

        self.data_label = Gtk.Label(label='Current data:')
        self.container.put(self.data_label, 50, 150)
        
        self.label = Gtk.Label()
        self.container.put(self.label, 100, 210)

        self.arduino_label = Gtk.Label(label='Arduino 1: not connected\nArduino 2: not connected')
        self.container.put(self.arduino_label, 500, 210)

        self.lcd_label = Gtk.Label(label='LCD 1: not connected\nLCD 2: not connected')
        self.container.put(self.lcd_label, 500, 270)

        self.clear_reg_button = Gtk.Button(label='Clear register')
        self.clear_reg_button.connect('clicked', Application.clear_reg_button_clicked)
        self.container.put(self.clear_reg_button, 100, 500)

        self.window.show_all()

        self.datareader1 = dataread.DataRead('/dev/ttyACM0')
        self.datareader2 = dataread.DataRead('/dev/ttyACM1')
        self.bluetoothdv = bluetoothio.BluetoothIO()
        
        self.lcd1 = lcd.LCD(0x3f)
        #self.lcd2 = lcd.LCD(address ?)

        self.graphprocess = Process(target=grapher.update_graph, args=[''])

        if not os.path.exists('register.json'):
            with open('register.json', 'w') as file:
                file.write('[\n]')


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
            register = read + '\t' + (',' if read.find('{') != -1 else '') + str(data).replace("'", '"') + '\n]'
            file.write(register)

        if (app.graphprocess.is_alive()):
            app.graphprocess.terminate()

        app.graphprocess = Process(target=grapher.update_graph, args=[register])
        app.graphprocess.start()
        
        return True


    @staticmethod
    def clear_reg_button_clicked(button):
        print('Clear register clicked')
    

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
