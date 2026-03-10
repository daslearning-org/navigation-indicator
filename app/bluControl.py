from kivy.clock import Clock

class BluetoothCon():

    def __init__(self, platform:str = "android"):
        self.platform = platform
        self.connect_ok = False

    def bl_on(self):
        stat = False
        if self.platform == "android":
            try:
                from jnius import autoclass
                BluetoothAdapter = autoclass('android.bluetooth.BluetoothAdapter')
                bt_adapter = BluetoothAdapter.getDefaultAdapter()
                if bt_adapter and bt_adapter.isEnabled():
                    stat = True
            except Exception as e:
                print(f"Error while checking bluetooth on/off status: {e}")
        return stat

    def request_enable_bl(self):
        stat = False
        if self.platform == "android":
            bl_on = self.bl_on()
            if bl_on:
                return True
            try:
                from jnius import autoclass
                #from android import activity
                PythonActivity = autoclass('org.kivy.android.PythonActivity')
                Intent = autoclass('android.content.Intent')
                BluetoothAdapter = autoclass('android.bluetooth.BluetoothAdapter')
                REQUEST_ENABLE_BT = 1
                bt_adapter = BluetoothAdapter.getDefaultAdapter()
                enableBtIntent = Intent(BluetoothAdapter.ACTION_REQUEST_ENABLE)
                PythonActivity.mActivity.startActivityForResult(enableBtIntent, REQUEST_ENABLE_BT)
                stat = True
            except Exception as e:
                print(f"Error while turning bluetooth ON: {e}")
        return stat

    def list_devices(self):
        result = []
        if self.platform == "android":
            try:
                from jnius import autoclass
                BluetoothAdapter = autoclass('android.bluetooth.BluetoothAdapter')
                bt_adapter = BluetoothAdapter.getDefaultAdapter()
                devices = bt_adapter.getBondedDevices().toArray()
                for dev in devices:
                    name = dev.getName()
                    addr = dev.getAddress()
                    result.append((name, addr))
            except Exception as e:
                print(f"Error in Bluetooth device listing: {e}")
        return result

    def connect_device(self, mac):
        stat = False
        if self.platform == "android":
            try:
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
                stat = True
            except Exception as e:
                print(f"Error while conencting to ESP32: {e}")
        return stat

    def send_cmd(self, cmd, *args):
        stat = False
        if self.platform == "android" and self.connect_ok:
            try:
                self.bt_out.write(bytearray(cmd + "\n", 'utf-8'))
                stat = True
            except Exception as e:
                print(f"Error while send msg to ESP: {e}")
        return stat
