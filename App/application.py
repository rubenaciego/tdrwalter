#!/usr/bin/env python3

import dataread
import lcd
import grapher
import bluetoothio

import gi
import datetime
import threading
import os
import matplotlib.pyplot as plt
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

        self.graph_label = Gtk.Label(label='Graph settings:')
        self.container.put(self.graph_label, 400, 360)

        self.graph_win = Gtk.CheckButton(label='Display graphs')
        self.graph_win.connect('toggled', Application.checkbox_toggle)
        self.container.put(self.graph_win, 420, 390)

        self.sizex_entry = Gtk.Entry()
        self.sizex_entry.connect('changed', self.on_size_changed)
        self.container.put(self.sizex_entry, 420, 440)

        self.sizey_entry = Gtk.Entry()
        self.sizey_entry.connect('changed', self.on_size_changed)
        self.container.put(self.sizey_entry, 420, 480)

        self.sizex_entry.set_text(str(grapher.sizex))
        self.sizey_entry.set_text(str(grapher.sizey))

        self.container.put(Gtk.Label(label='X size for graphics (inches)'),
                           600, 440)
        self.container.put(Gtk.Label(label='Y size for graphics (inches)'),
                           600, 480)

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


    def on_size_changed(self, widget):
        value = widget.get_text().strip()
        value = ''.join([i for i in value if i in '0123456789'])
        widget.set_text(value)

        if value == '':
            value = 0
        else:
            value = int(value)

        if widget == self.sizex_entry:
            grapher.sizex = value
        elif widget == self.sizey_entry:
            grapher.sizey = value


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
                    
                    print("Received " + str(data))
                    
            except IOError:
                pass

            app.bluetoothdv.close()
            app.bluetooth_label.set_text('Bluetooth: disconnected')
            app.bluetoothdv = bluetoothio.BluetoothIO()


    @staticmethod
    def set_text(app):
        data1 = app.datareader1.read_input()
        data2 = app.datareader2.read_input()

        if not app.datareader1.connected:
            app.datareader1 = dataread.DataRead('/dev/ttyACM0')
        if not app.datareader2.connected:
            app.datareader2 = dataread.DataRead('/dev/ttyACM1')

        app.update_arduino_label()

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
    def checkbox_toggle(button):
        grapher.showgraph = button.get_active()


    @staticmethod
    def clear_reg_button_clicked(button):

        def on_response(widget, response):
            if response == Gtk.ResponseType.YES:
                with open('register.json', 'w') as file:
                    file.write('[\n]')
                
                print('Register deleted')

            widget.destroy()
            

        msgbox = Gtk.MessageDialog(parent=button.get_toplevel(),
                                   flags=Gtk.DialogFlags.MODAL,
                                   type=Gtk.MessageType.WARNING,
                                   buttons=Gtk.ButtonsType.YES_NO,
                                   message_format='Are you sure that you want to delete the whole register?')

        msgbox.connect('response', on_response)
        msgbox.show()
        
    

    def update_lcd(self):
        # Maybe it should try to reconnect the LCDs
        # if it is disconnected

        self.lcd1.send_string('Hello LCD1!', lcd.LCD.LINE_1)
        self.lcd2.send_string('Hello LCD2!', lcd.LCD.LINE_1)

        self.update_lcd_label()


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
