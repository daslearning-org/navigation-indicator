from jnius import autoclass, PythonJavaClass, java_method
from android import mActivity
import time

BluetoothAdapter = autoclass('android.bluetooth.BluetoothAdapter')
BluetoothGattCallback = autoclass('android.bluetooth.BluetoothGattCallback')
UUID = autoclass('java.util.UUID')

SERVICE_UUID = UUID.fromString("6E400001-B5A3-F393-E0A9-E50E24DCCA9E")
RX_UUID = UUID.fromString("6E400002-B5A3-F393-E0A9-E50E24DCCA9E")


class GattCallback(PythonJavaClass):
    __javaclass__ = 'android/bluetooth/BluetoothGattCallback'

    def __init__(self, ble):
        super().__init__()
        self.ble = ble

    @java_method('(Landroid/bluetooth/BluetoothGatt;II)V')
    def onConnectionStateChange(self, gatt, status, newState):
        print("Connection state changed:", newState)

        # STATE_CONNECTED = 2
        if newState == 2:
            print("Connected. Discovering services...")
            gatt.discoverServices()

    @java_method('(Landroid/bluetooth/BluetoothGatt;I)V')
    def onServicesDiscovered(self, gatt, status):
        print("Services discovered")

        service = gatt.getService(SERVICE_UUID)

        if service is None:
            print("Service not found")
            return

        self.ble.rx_char = service.getCharacteristic(RX_UUID)
        self.ble.ready = True
        print("BLE ready")


class BLEClient:

    def __init__(self, mac_address):

        self.context = mActivity
        self.adapter = BluetoothAdapter.getDefaultAdapter()

        self.device = self.adapter.getRemoteDevice(mac_address)

        self.gatt = None
        self.rx_char = None
        self.ready = False

        self.callback = GattCallback(self)

    def connect(self):

        print("Connecting...")

        self.gatt = self.device.connectGatt(
            self.context,
            False,
            self.callback
        )

    def send(self, message):

        if not self.ready:
            print("BLE not ready yet")
            return

        data = bytearray(message, 'utf-8')

        self.rx_char.setValue(data)
        self.gatt.writeCharacteristic(self.rx_char)

        print("Sent:", message)


# Example usage
if __name__ == "__main__":
    """
    Use this is ESP32 side
    Service
    6E400001-B5A3-F393-E0A9-E50E24DCCA9E

    RX (write)
    6E400002-B5A3-F393-E0A9-E50E24DCCA9E

    TX (notify)
    6E400003-B5A3-F393-E0A9-E50E24DCCA9E
    """
    ble = BLEClient("AA:BB:CC:DD:EE:FF")  # ESP32 MAC

    ble.connect()

    time.sleep(5)

    ble.send("HELLO ESP32")

