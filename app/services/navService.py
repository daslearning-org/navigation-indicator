from jnius import autoclass, cast
from kivy.utils import platform

# import locals
from postApi import PosiApiServer
from bluControl import BluetoothCon
from mapBrain import distance_in_meters, extract_direction, clean_text

# objects / vars
app_api_server = PosiApiServer()
bluCon = BluetoothCon()
api_started = False

def control_callback(item):
    global api_started
    api_stat = item.get("api", "none")
    if api_stat == "stop":
        app_api_server.stop()
        api_started = False


