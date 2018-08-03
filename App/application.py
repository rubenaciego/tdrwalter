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

        self.bluetooth_label = Gtk.Label(label='Bluetooth: disconnected')
        self.container.put(self.bluetooth_label, 50, 50)

        self.data_label = Gtk.Label(label='Current data:')
        self.container.put(self.data_label, 50, 150)
        
        self.label = Gtk.Label()
        self.container.put(self.label, 100, 210)

        self.arduino_label = Gtk.Label()
        self.container.put(self.arduino_label, 500, 210)

        self.lcd_label = Gtk.Label()
        self.container.put(self.lcd_label, 500, 270)

        self.clear_reg_button = Gtk.Button(label='Clear register')
        self.clear_reg_button.connect('clicked', Application.clear_reg_button_clicked)
        self.container.put(self.clear_reg_button, 100, 500)

        self.window.show_all()

        self.datareader1 = dataread.DataRead('/dev/ttyACM0')
        self.datareader2 = dataread.DataRead('/dev/ttyACM1')
        self.bluetoothdv = bluetoothio.BluetoothIO()
        
        self.lcd1 = lcd.LCD(0x3f)
        self.lcd2 = lcd.LCD(0x28)

        self.update_arduino_label()
        self.update_lcd_label()

        self.graphprocess = Process(target=grapher.update_graph, args=[''])

        if not os.path.exists('register.json'):
            with open('register.json', 'w') as file:
                file.write('[\n]')


    def update_arduino_label(self):
        ardu_str = 'Arduino 1: '

        if self.datareader1.connected:
            ardu_str += 'connected\n'
        else:
            ardu_str += 'disconnected\n'

        ardu_str += 'Arduino 2: '

        if self.datareader2.connected:
            ardu_str += 'connected'
        else:
            ardu_str += 'disconnected'

        self.arduino_label.set_text(ardu_str)


    def update_lcd_label(self):
        lcd_str = 'LCD 1: '

        if self.lcd1.connected:
            lcd_str += 'connected\n'
        else:
            lcd_str += 'disconnected\n'

        lcd_str += 'LCD 2: '

        if self.lcd2.connected:
            lcd_str += 'connected'
        else:
            lcd_str += 'disconnected'

        self.lcd_label.set_text(lcd_str)


    @staticmethod
    def update_bluetooth(app):
        while True:
            app.bluetoothdv.wait_for_connection()
            app.bluetooth_label.set_text('Bluetooth: connected')

            try:
                while True:
                    data = app.bluetoothdv.read()
                    if len(data) == 0: break
                    
                    print("Received " + data)
                    
            except IOError:
                pass

            app.bluetoothdv.close()
            app.bluetooth_label.set_text('Bluetooth: disconnected')


    @staticmethod
    def set_text(app):
        data1 = app.datareader1.read_input()
        data2 = app.datareader2.read_input()

        if app.datareader1.connected:
            app.datareader1 = dataread.DataRead('/dev/ttyACM0')
        if app.datareader2.connected:
            app.datareader2 = dataread.DataRead('/dev/ttyACM1')

        data.update_arduino_label()

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
        # Maybe it should try to reconnect the LCD
        # if it is disconnected

        self.lcd1.send_string('Hello LCD1!', lcd.LCD.LINE_1)
        self.lcd2.send_string('Hello LCD2!', lcd.LCD.LINE_1)

        update_lcd()


    def run(self):
        GObject.threads_init()
        GLib.timeout_add(Application.UPDATE_INTERVAL, Application.set_text, self)
        GLib.timeout_add(Application.LCD_INTERVAL, Application.update_lcd, self)

        btthread = threading.Thread(target=Application.update_bluetooth, args=[self])
        btthread.daemon = True
        btthread.start()

        Gtk.main()


if __name__ == '__main__':
    Application().run()
