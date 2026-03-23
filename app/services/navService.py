from kivy.utils import platform

from os.path import join, abspath, exists, dirname
from threading import Thread
#import asyncio
#from functools import partial
import json
import time
import sys

# import locals
from services.postApi import PosiApiServer, NavData
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
    "auto_mode": "none",
}
api_started = False
auto_mode_stat = False
blue_conn_stat = False
bt_connecting = False
auto_indicator = False
config_data = {}
stearing = "right"
last_choice = "none"
mac_set = None

# for android
if platform == "android":
    from jnius import autoclass, PythonJavaClass, java_method
    # set path
    try:
        service = autoclass('org.kivy.android.PythonService').mService
        context = service.getApplicationContext()
        android_path = context.getExternalFilesDir(None).getAbsolutePath()
        config_dir = join(android_path, 'config')
        Log = autoclass('android.util.Log')
    except Exception as e:
        config_dir = abspath("/storage/emulated/0/Android/data/in.daslearning.navindi/files/config/")
        print(f"Error while accessing app internal path: {e}")

    try:
        # notification listener code for android
        NavListener = autoclass('in.daslearning.navindi.NavNotificationListener')

        class MyNavCallback(PythonJavaClass):
            __javainterfaces__ = [
                'in/daslearning/navindi/NavNotificationListener$NavCallback'
            ]
            __javacontext__ = 'app'

            @java_method('(Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;)V')
            def onNavigationUpdate(self, pkg, title, text, bigText):
                #print("Package:", pkg)
                #print("Title:", title)
                #print("Text:", text)
                pkg = pkg.strip()
                if pkg in ["com.google.android.apps.maps", "com.virtualmaze.offlinemapnavigationtracker", "net.osmand"]:
                    item = NavData(title=title, text=text, big_text=bigText)
                    Thread(
                        target=api_nav_listner,
                        kwargs={
                            "item": item
                        },
                        daemon=True
                    ).start()
        # now bind the service
    except Exception as e:
        print(f"Error while setting up notification listerner: {e}")

# for other platforms
else:
    # Determine the base path for your application's resources
    if getattr(sys, 'frozen', False):
        # Running as a PyInstaller bundle
        base_path = sys._MEIPASS
    else:
        # Running in a normal Python environment
        base_path = dirname(abspath(__file__))
    config_dir = join(base_path, 'config')
if not exists(config_dir):
    import os
    os.makedirs(config_dir, exist_ok=True)
config_file = join(config_dir, "config.json")
resp_file = join(config_dir, "resp.json")

#### functions ####

def fire_few_off_commands():
    """ This will fire few off commands to the bt/ble device. It will be helpful BLE devices. """
    global auto_indicator
    for i in range(3):
        if not auto_indicator:
            bluCon.send_cmd("off")
            time.sleep(0.5)

def process_nav_from_api(distance, direction):
    """ This will send bt/ble command based on distance & direction. """
    #print(f"Bluetooth command: {distance}, {direction}")
    global auto_indicator
    global mac_set
    global bt_connecting
    global last_choice

    bt_check = bluCon.check_bl_stat()
    if not bt_check and not bt_connecting and mac_set:
        connect_bluetooth(mac_set)
    if distance >= 0 and distance < 61 and bt_check:
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
    elif distance >= 61 and auto_indicator and bt_check:
        bluCon.send_cmd("off")
        auto_indicator = False
        if bluCon.ble_device:
            Thread(target=fire_few_off_commands, daemon=True).start()
            print("Firing BLE turn off...")

def manual_controls(choice:str):
    global last_choice
    global mac_set
    global bt_connecting
    bt_check = bluCon.check_bl_stat()
    if not bt_check and not bt_connecting and mac_set:
        connect_bluetooth(mac_set)
    if choice != "none" and last_choice != choice and bt_check:
        bluCon.send_cmd(choice)
        last_choice = choice

def dayNightControl():
    import time
    current_time = int(time.strftime("%H%M"))
    if current_time < 1730 and current_time > 530 :
        control = "day"
    else:
        control = "night"
    bluCon.send_cmd(control)

def api_nav_listner(item, *args):
    global resp_template
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
        resp_template["direction"] = direction_final
        resp_template["distance"] = distance_final
        #print(f"Got from API: {distance_final}, {direction_final}")
        process_nav_from_api(distance=distance_final, direction=direction_final)
        Thread(target=write_resp, daemon=True).start()

def write_resp():
    """ Write the response json on file. """
    global resp_template
    with open(resp_file, "w") as rf:
        json.dump(resp_template, rf)

def read_config_file():
    """ Read the command file from file (Instrunctions from main app). """
    global config_data
    if exists(config_file):
        try:
            with open(config_file, "r") as cf:
                config_data = json.load(cf)
        except Exception as e:
            print(f"Error while reading config from svc: {e}")

def api_server_control(api_stat: str):
    """ Turns API server on/off """
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

def auto_mode(control: str):
    """ Start the automatic navigation notification read & ble control operation. """
    global auto_mode_stat
    global resp_template
    if control == "stop":
        try:
            NavListener.clearCallback()
            auto_mode_stat = False
            resp_template["auto_mode"] = "stopped"
        except Exception as e:
            print(f"Error during clearing callback: {e}")
    elif control == "start":
        try:
            callback = MyNavCallback()
            NavListener.setCallback(callback)
            auto_mode_stat = True
            resp_template["auto_mode"] = "started"
        except Exception as e:
            print(f"Error during callback setup: {e}")
    Thread(target=write_resp, daemon=True).start()

def connect_bluetooth(mac_addr:str):
    global blue_conn_stat
    global resp_template
    global mac_set
    global bt_connecting
    if len(mac_addr) == 17:
        bt_connecting = True
        blue_conn_stat = bluCon.connect_device(mac_addr)
        if blue_conn_stat:
            resp_template["bt"] = "connected"
            mac_set = mac_addr
            Thread(target=dayNightControl, daemon=True).start()
        else:
            resp_template["bt"] = "failed"
        write_resp()
    bt_connecting = False

def nav_service_thread():
    #global vars
    global stearing
    global api_started
    global blue_conn_stat
    global config_data
    global last_choice
    global bt_connecting
    global auto_mode_stat

    write_resp() # blank the old file

    # set the api callback
    app_api_server.set_kivy_caller(api_nav_listner)

    # keep alive the service & check for requests
    while True:
        read_config_file()

        # handle bluetooth connect
        mac_addr = config_data.get("mac", "")
        bt_req = config_data.get("bt", "")
        if not blue_conn_stat and not bt_connecting and len(mac_addr) == 17 and bt_req == "connect":
            connect_bluetooth(mac_addr)
        
        #handle bt commands from buttons
        choice = config_data.get("cmd", "none")
        if choice != "none" and last_choice != choice and blue_conn_stat:
            bluCon.send_cmd(choice)
            last_choice = choice
            #print(f"manual: {choice}")

        #handle api server
        server_stat = config_data.get("server", "")
        if not api_started and server_stat == "start":
            api_server_control("start")
        elif api_started and server_stat == "stop":
            api_server_control("stop")

        #handle auto mode
        control = config_data.get("auto_mode", "")
        if not auto_mode_stat and control == "start" and platform == "android":
            auto_mode("start")
        elif auto_mode_stat and control == "stop" and platform == "android":
            auto_mode("stop")

        # handle other params
        config_stear = config_data.get("stearing", "right")
        if config_stear != stearing:
            stearing = config_stear
        
        keep_alive = config_data.get("alive", "true")
        if keep_alive == "true":
            pass
        else:
            break # stop the service

        #sys.stdout.flush()
        # put a sleep
        time.sleep(0.5)

if __name__ == "__main__":
    # start the service from here (if required)

    # the main listener loop
    nav_service_thread()
