from kivy.utils import platform

from os.path import join, abspath, exists, dirname
from threading import Thread
#import asyncio
#from functools import partial
import json
import time
import sys

# import locals
from services.postApi import PosiApiServer
from services.bluControl import BluetoothCon
from services.mapBrain import distance_in_meters, extract_direction, clean_text

# objects / vars
app_api_server = PosiApiServer()
bluCon = BluetoothCon()
resp_template = {
    "direction": "none",
    "distance": "none",
    "bt": "none",
    "server": "none",
}
api_started = False
blue_conn_stat = False
auto_indicator = False
config_data = {}
stearing = "right"
last_choice = "none"
# paths on android
if platform == "android":
    from jnius import autoclass, cast
    try:
        service = autoclass('org.kivy.android.PythonService').mService
        context = service.getApplicationContext()
        android_path = context.getExternalFilesDir(None).getAbsolutePath()
        config_dir = join(android_path, 'config')
        Log = autoclass('android.util.Log')
    except Exception as e:
        config_dir = abspath("/storage/emulated/0/Android/data/in.daslearning.navindi/files/config/")
        print(f"Error while accessing app internal path: {e}")
else:
    # Determine the base path for your application's resources
    if getattr(sys, 'frozen', False):
        # Running as a PyInstaller bundle
        base_path = sys._MEIPASS
    else:
        # Running in a normal Python environment
        base_path = dirname(abspath(__file__))
    config_dir = join(base_path, 'config')
config_file = join(config_dir, "config.json")
resp_file = join(config_dir, "resp.json")

# functions
def process_nav_from_api(distance, direction):
    print(f"Bluetooth command: {distance}, {direction}")
    global auto_indicator
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

def manual_controls(choice:str):
    global last_choice
    if choice != "none" and last_choice != choice:
        bluCon.send_cmd(choice)
        last_choice = choice

def api_nav_listner(item, *args):
    global resp_template
    distance_final = None
    direction_final = None
    for i in item:
        print(i[1])
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
        resp_template["direction"] = direction_final
        resp_template["distance"] = distance_final
        print(f"Got from API: {distance_final}, {direction_final}")
        if platform == "android":
            Log.i("NAV_SERVICE: ", f"{distance_final}, {direction_final}")
        process_nav_from_api(distance=distance_final, direction=direction_final)
        Thread(target=write_resp, daemon=True).start()
        #Thread(
        #    target=process_nav_from_api,
        #    kwargs={
        #        "distance": distance_final,
        #        "direction": direction_final
        #    },
        #    daemon=True
        #).start()

def write_resp():
    global resp_template
    with open(resp_file, "w") as rf:
        json.dump(resp_template, rf)

def read_config_file():
    global config_data
    if exists(config_file):
        try:
            with open(config_file, "r") as cf:
                config_data = json.load(cf)
        except Exception as e:
            print(f"Error while reading config from svc: {e}")

def api_server_control(api_stat: str):
    global api_started
    global resp_template
    if api_stat == "stop":
        app_api_server.stop()
        api_started = False
        resp_template["server"] = "stopped"
    elif api_stat == "start":
        app_api_server.start()
        api_started = True
        resp_template["server"] = "started"
    Thread(target=write_resp, daemon=True).start()

def connect_bluetooth(mac_addr:str):
    global blue_conn_stat
    global resp_template
    if len(mac_addr) == 17:
        blue_conn_stat = bluCon.connect_device(mac_addr)
        if blue_conn_stat:
            resp_template["bt"] = "connected"
        else:
            resp_template["bt"] = "failed"
        write_resp()

def nav_service_thread():
    #global vars
    global stearing
    global api_started
    global blue_conn_stat
    global config_data
    global last_choice

    write_resp() # blank the old file

    # set the api callback
    app_api_server.set_kivy_caller(api_nav_listner)

    # keep alive the service & check for requests
    while True:
        read_config_file()

        # handle bluetooth connect
        mac_addr = config_data.get("mac", "")
        bt_req = config_data.get("bt", "")
        if not blue_conn_stat and len(mac_addr) == 17 and bt_req == "connect":
            connect_bluetooth(mac_addr)
        
        #handle bt commands from buttons
        choice = config_data.get("cmd", "none")
        if choice != "none" and last_choice != choice and blue_conn_stat:
            bluCon.send_cmd(choice)
            last_choice = choice
            print(f"manual: {choice}")

        #handle api server
        server_stat = config_data.get("server", "")
        if not api_started and server_stat == "start":
            api_server_control("start")
        elif api_started and server_stat == "stop":
            api_server_control("stop")

        # handle other params
        config_stear = config_data.get("stearing", "right")
        if config_stear != stearing:
            stearing = config_stear
        
        keep_alive = config_data.get("alive", "true")
        if keep_alive == "true":
            pass
        else:
            break # stop the service

        # put a sleep
        time.sleep(0.5)

if __name__ == "__main__":
    # start the service from here
    #if platform == "android":
    #    PythonService = autoclass('org.kivy.android.PythonService')
    #    service = PythonService.mService
    #    service.setAutoRestartService(True)
    #    service.setForeground(True)
    
    # the main listener loop
    nav_service_thread()
