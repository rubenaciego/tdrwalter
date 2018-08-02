from bluetooth import *
import subprocess
import shlex


class BluetoothIO:

    def __init__(self):
        # Otherwise bluetooth doesn't work        
        os.system('rfkill unblock all && hciconfig hci0 up')

        self.server_sock = BluetoothSocket(RFCOMM)
        self.server_sock.bind(("", PORT_ANY))
        self.server_sock.listen(1)
        self.closed = True

        self.port = self.server_sock.getsockname()[1]

        UUID = "94f39d29-7d6d-437d-973b-fba39e49d4ee"

        advertise_service(self.server_sock, "RaspiServer",
                          service_id = UUID,
                          service_classes = [UUID, SERIAL_PORT_CLASS],
                          profiles = [SERIAL_PORT_PROFILE], 
                          #protocols = [OBEX_UUID] 
                          )


    def wait_for_connection(self):
        print("Waiting for bluetooth connection on RFCOMM channel %d" % self.port)

        self.client_sock, client_info = self.server_sock.accept()
        print("Accepted Bluetooth connection from ", client_info)
        self.closed = False


    def close(self):
        print("Bluetooth device disconnected")
        self.client_sock.close()
        self.server_sock.close()
        self.closed = True
        

    def write(self, data):
        if not self.closed:
            self.client_sock.send(data)


    def read(self):
        if not self.closed:
            return self.client_sock.recv(1024)
