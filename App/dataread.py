import serial
import json
import datetime


class DataRead:

    POSSIBLE_DATA = ('CO2', 'TEMP', 'LUXES', 'GPS', 'Turbidity', 'pH', 'TEMPH2O')

    def __init__(self, port, baud=9600):
        try:
            self.ser = serial.Serial(port, baud)
            self.connected = True
        except IOError:
            print('Error: Could not open the Serial Port ' + port)
            self.connected = False


    def __del__(self):
        if self.connected:
            self.ser.close()
            self.connected = False
        
        
    def read_input(self):
        if not self.connected:
            return {}
        
        try:  
            while self.ser.in_waiting > 0:
                string = self.ser.readline().decode().strip().replace("'", '"')
            
            data = json.loads(string)
        except (UnicodeDecodeError, json.decoder.JSONDecodeError):
            data = {}
        except Exception:
            self.connected = False
            data = {}

        return data


    def write(self, data):
        if self.connected:
            self.ser.write(data)
