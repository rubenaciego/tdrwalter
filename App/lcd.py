import smbus
import time

class LCD:

    WIDTH = 16   # Maximum characters per line

    # Define some device constants
    CHR = 1 # Mode - Sending data
    CMD = 0 # Mode - Sending command

    LINE_1 = 0x80 # LCD RAM address for the 1st line
    LINE_2 = 0xC0 # LCD RAM address for the 2nd line
    LINE_3 = 0x94 # LCD RAM address for the 3rd line
    LINE_4 = 0xD4 # LCD RAM address for the 4th line

    BACKLIGHT  = 0x08  # On
    NO_BACKLIGHT = 0x00  # Off

    ENABLE = 0b00000100 # Enable bit

    # Timing constants
    E_PULSE = 0.0005
    E_DELAY = 0.0005

    
    def __init__(self, i2c_address):
        self.I2C_ADDR = i2c_address # I2C device address
        self.backlight = True
        self.connected = True

        #Open I2C interface
        #self.bus = smbus.SMBus(0)  # Rev 1 Pi uses 0

        self.bus = smbus.SMBus(1) # Rev 2 Pi uses 1

        try:
            # Initialise display
            self.send_byte(0x33, LCD.CMD) # 110011 Initialise
            self.send_byte(0x32, LCD.CMD) # 110010 Initialise
            self.send_byte(0x06, LCD.CMD) # 000110 Cursor move direction
            self.send_byte(0x0C, LCD.CMD) # 001100 Display On,Cursor Off, Blink Off 
            self.send_byte(0x28, LCD.CMD) # 101000 Data length, number of lines, font size
            self.send_byte(0x01, LCD.CMD) # 000001 Clear display
            self.connected = True

        except Exception:
            self.connected = False
            return

        time.sleep(LCD.E_DELAY)


    def send_byte(self, bits, mode):
        # Send byte to data pins
        # bits = the data
        # mode = 1 for data
        #        0 for command

        if not self.connected:
            return

        bits_high = mode | (bits & 0xF0) | (LCD.BACKLIGHT if self.backlight else LCD.NO_BACKLIGHT)
        bits_low = mode | ((bits<<4) & 0xF0) | (LCD.BACKLIGHT if self.backlight else LCD.NO_BACKLIGHT)

        # High bits

        self.bus.write_byte(self.I2C_ADDR, bits_high)
        self.toggle_enable(bits_high)

        # Low bits

        self.bus.write_byte(self.I2C_ADDR, bits_low)
        self.toggle_enable(bits_low)
        

    def toggle_enable(self, bits):
        # Toggle enable
        if not self.connected:
            return

        time.sleep(LCD.E_DELAY)
        self.bus.write_byte(self.I2C_ADDR, (bits | LCD.ENABLE))
        time.sleep(LCD.E_PULSE)
        self.bus.write_byte(self.I2C_ADDR, (bits & ~LCD.ENABLE))
        time.sleep(LCD.E_DELAY)
        

    def send_string(self, message, line):
        # Send string to display
        if not self.connected:
            return

        message = message.ljust(LCD.WIDTH, " ")

        self.send_byte(line, LCD.CMD)

        for i in range(LCD.WIDTH):
            self.send_byte(ord(message[i]), LCD.CHR)
