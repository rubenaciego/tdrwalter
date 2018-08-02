import serial
import json
import datetime


class DataRead:

    def __init__(self):

        try:
            self.ser = serial.Serial('/dev/ttyACM0', 9600)
        except IOError:
            print('IOError: Could not open the Serial Port')


    def __del__(self):
        try:
            self.ser.close()
        except Exception:
            pass
        
        
    def read_input(self):
        try:
            data = json.loads(self.ser.readline().decode().strip().replace("'", '"'))
        except (UnicodeDecodeError, json.decoder.JSONDecodeError, Exception):
            data = {}

        data['TIME'] = datetime.datetime.now().strftime('%H:%M:%S %d/%m/%Y')
        stringdata = ''
        
        for key, val in data.items():
            stringdata += key + ': ' + str(val) + '\n'

        return (stringdata, str(data))
