#!/usr/bin/env python3

import gi
import dataread
import lcd
import grapher
import bluetoothio
import matplotlib.pyplot as plt
import threading


gi.require_version('Gtk', '3.0')
from gi.repository import GLib, GObject, Gtk


class Application(Gtk.Application):

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

        self.datareader = dataread.DataRead()
        self.bluetoothdv = bluetoothio.BluetoothIO()
##        self.lcd1 = lcd.LCD(0x3f)


    @staticmethod
    def read_bt(btio):
      try:
        
        while True:
            data = btio.read()
            if len(data) == 0: break
            
            print("Received [%s]" % data)
            
      except IOError:
          pass

      btio.close()
      return False


    @staticmethod
    def set_text(label, func, btio):
        text = func()
        label.set_text(text[0])
        btio.write(text[1])
        
        with open('register.json', 'r') as file:
            read = file.read()

        with open('register.json', 'w+') as file:
            read = read[:read.find(']')]
            data = read + '\t' + text[1] + ',\n]'
            file.write(data)
            print('\nData:\n' + data)

    
##        grapher.update_graph(data)
        
        return True


    @staticmethod
    def button_clicked(button):
        print('Button clicked')


    def run(self):
        GObject.threads_init()
        GLib.timeout_add(5000, Application.set_text, self.label, self.datareader.read_input, self.bluetoothdv)
##        GLib.timeout_add(1000, update_lcd)
        thread = threading.Thread(target=Application.read_bt, args=[self.bluetoothdv])
        thread.daemon = True
        thread.start()
        Gtk.main()


def update_lcd():
    self.lcd1.send_string('Hello world!', lcd.LCD.LINE_1)


if __name__ == '__main__':
    Application().run()
