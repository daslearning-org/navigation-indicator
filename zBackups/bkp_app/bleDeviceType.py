from jnius import autoclass

BluetoothAdapter = autoclass('android.bluetooth.BluetoothAdapter')
BluetoothDevice = autoclass('android.bluetooth.BluetoothDevice')

adapter = BluetoothAdapter.getDefaultAdapter()

device = adapter.getRemoteDevice("AA:BB:CC:DD:EE:FF")

device_type = device.getType()

if device_type == BluetoothDevice.DEVICE_TYPE_CLASSIC:
    print("Classic Bluetooth")

elif device_type == BluetoothDevice.DEVICE_TYPE_LE:
    print("BLE only")

elif device_type == BluetoothDevice.DEVICE_TYPE_DUAL:
    print("Dual mode (Classic + BLE)")