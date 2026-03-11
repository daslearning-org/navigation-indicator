from jnius import autoclass, cast
from kivy.utils import platform

from os.path import join, abspath, exists
from threading import Thread
import asyncio
from functools import partial
import json
import time

# import locals
from postApi import PosiApiServer
from bluControl import BluetoothCon
from mapBrain import distance_in_meters, extract_direction, clean_text

# objects / vars
app_api_server = PosiApiServer()
bluCon = BluetoothCon()
api_started = False
blue_conn_stat = False
config_data = None
stearing = "right"
# paths on android
try:
    context = autoclass('org.kivy.android.PythonActivity').mActivity
    android_path = context.getExternalFilesDir(None).getAbsolutePath()
    config_dir = join(android_path, 'config')
except Exception as e:
    config_dir = abspath("/storage/emulated/0/Android/data/in.daslearning.navindi/files/config/")
    print(f"Error while accessing app internal path: {e}")
config_file = join(config_dir, "config.json")
resp_file = join(config_dir, "resp.json")

# functions
def process_nav_from_api(distance, direction):
    if distance > 0 and distance <= 60:
        if direction == "left":
            bluCon.send_cmd("left")
            auto_indicator = True
        elif direction == "right":
            bluCon.send_cmd("right")
            auto_indicator = True
        elif direction == "u-turn":
            if stearing == "right":
                bluCon.send_cmd("u-right")
            else:
                bluCon.send_cmd("u-left")
            auto_indicator = True
        elif direction == "straight":
            bluCon.send_cmd("off")
            auto_indicator = False
    elif distance > 60 and auto_indicator:
        bluCon.send_cmd("off")
        auto_indicator = False

def api_nav_listner(item):
    distance_final = None
    direction_final = None
    for i in item:
        #print(i[1])
        txt = str(i[1]).lower()
        distance_tmp = distance_in_meters(txt)
        direction_tmp = extract_direction(txt)
        if distance_tmp:
            distance_final = distance_tmp
        if direction_tmp:
            direction_final = direction_tmp
        if distance_tmp and direction_tmp:
            break # got both direction & distance to process
    if distance_final and direction_final:
        Thread(
            target=process_nav_from_api,
            kwargs={
                "distance": distance_final,
                "direction": direction_final
            },
            daemon=True
        ).start()

def read_config_file():
    global config_data
    if exists(config_file):
        with open(config_file, "r") as cf:
            config_data = json.load(cf)

def api_server_control(api_stat: str):
    global api_started
    if api_stat == "stop":
        app_api_server.stop()
        api_started = False
    elif api_stat == "start":
        app_api_server.start()
        api_started = True

def connect_bluetooth():
    global blue_conn_stat
    if config_data:
        mac_addr = config_data.get("mac", "")
        if len(mac_addr) == 17:
            blue_conn_stat = bluCon.connect_device(mac_addr)

def service_listner():
    global config_data
    global api_started
    global blue_conn_stat
    while True:
        read_config_file()

        # handle bluetooth
        mac_addr = config_data.get("mac", "")
        if not blue_conn_stat and len(mac_addr) == 17:
            blue_conn_stat = bluCon.connect_device(mac_addr)
        
        #handle api server
        server_stat = config_data.get("server", "")

        # put a sleep
        time.sleep(2)

