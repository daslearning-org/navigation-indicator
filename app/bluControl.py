from kivy.clock import Clock

class BluetoothCon():

    def __init__(self, platform:str = "android"):
        self.platform = platform
        self.connect_ok = False
    
    def connect_device(self, mac):
        stat = False
        if self.platform == "android":
            from jnius import autoclass
            BluetoothAdapter = autoclass('android.bluetooth.BluetoothAdapter')
            UUID = autoclass('java.util.UUID')
            SPP_UUID = "00001101-0000-1000-8000-00805F9B34FB"
            bt_adapter = BluetoothAdapter.getDefaultAdapter()
            device = bt_adapter.getRemoteDevice(mac)
            socket = device.createRfcommSocketToServiceRecord(
                UUID.fromString(SPP_UUID)
            )
            socket.connect()
            self.bt_out = socket.getOutputStream()
            bt_in = socket.getInputStream()
            print("Connected to: ", mac)
            self.connect_ok = True
        return stat
    
    def send_cmd(self, cmd):
        if self.platform == "android" and self.connect_ok:
            self.bt_out.write(bytearray(cmd + "\n", 'utf-8'))
            return True
        else:
            return False
