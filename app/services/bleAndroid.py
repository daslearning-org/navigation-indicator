from jnius import autoclass, PythonJavaClass, java_method
from android import mActivity

BLEHelperPy = autoclass('in.daslearning.navindi.BLEHelper')
print("Loaded:", BLEHelperPy)

class MyBLEListener(PythonJavaClass):
    __javainterfaces__ = ['in/daslearning/navindi/BLEListener']

    def __init__(self):
        super().__init__()

    @java_method('()V')
    def onConnected(self):
        print("Connected to ESP32")

    @java_method('()V')
    def onReady(self):
        print("BLE ready (write characteristic found)")

    @java_method('(Ljava/lang/String;)V')
    def onMessage(self, msg):
        print("Received:", msg)


class BLEClient:

    def __init__(self):
        listener = MyBLEListener()
        self.helper = BLEHelperPy(listener)

    def connect(self, mac):
        self.helper.connect(mActivity, mac)

    def send(self, msg):
        self.helper.send(msg)