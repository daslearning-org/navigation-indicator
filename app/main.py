import os
os.environ['KIVY_GL_BACKEND'] = 'sdl2'
import sys
from threading import Thread

from kivymd.app import MDApp
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.navigationdrawer import MDNavigationDrawerMenu
#from kivymd.uix.filemanager import MDFileManager
from kivymd.uix.label import MDLabel
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDFlatButton, MDFloatingActionButton

from kivy.clock import Clock
from kivy.utils import platform
from kivy.core.window import Window
from kivy.metrics import dp, sp
from kivy.lang import Builder
from kivy.properties import StringProperty, NumericProperty, ObjectProperty, BooleanProperty

if platform == "android":
    from jnius import autoclass, cast

# IMPORTANT: Set this property for keyboard behavior
Window.softinput_mode = "below_target"

## Global definitions
__version__ = "0.0.1" # App version

# Determine the base path for your application's resources
if getattr(sys, 'frozen', False):
    # Running as a PyInstaller bundle
    base_path = sys._MEIPASS
else:
    # Running in a normal Python environment
    base_path = os.path.dirname(os.path.abspath(__file__))
kv_file_path = os.path.join(base_path, 'main_layout.kv')

# import local screens
from screens.setting import SettingsBox
from screens.init_screen import ConfigInput
from screens.nav_screen import NavMainBox

# import local APIs
from postApi import PosiApiServer, clean_text
from bluControl import BluetoothCon

## define custom kivymd classes
class ContentNavigationDrawer(MDNavigationDrawerMenu):
    screen_manager = ObjectProperty()
    nav_drawer = ObjectProperty()

class MainScreenBox(MDBoxLayout):
    top_pad = NumericProperty(0)
    bottom_pad = NumericProperty(0)
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if platform == "android":
            try:
                from android.display_cutout import get_height_of_bar
                self.top_pad = int(get_height_of_bar('status'))
                self.bottom_pad = int(get_height_of_bar('navigation'))
            except Exception as e:
                print(f"Failed android 15 padding: {e}")
                self.top_pad = 32
                self.bottom_pad = 48

### Main App
class NavIndicatorApp(MDApp):
    is_api_server_on = BooleanProperty(False)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.test_var = None
        self.wake_lock = None

    def build(self):
        self.theme_cls.primary_palette = "Blue"
        self.theme_cls.accent_palette = "Orange"
        return Builder.load_file(kv_file_path)

    def on_start(self):
        # paths setup
        if platform == "android":
            # permissions
            from android.permissions import check_permission, request_permissions, Permission
            sdk_version = 28
            try:
                VERSION = autoclass('android.os.Build$VERSION')
                sdk_version = VERSION.SDK_INT
                print(f"Android SDK: {sdk_version}")
            except Exception as e:
                print(f"Could not check the android SDK version: {e}")
            permissions = [Permission.BLUETOOTH, Permission.BLUETOOTH_ADMIN, Permission.BLUETOOTH_CONNECT, Permission.WAKE_LOCK]
            request_permissions(permissions)
            try:
                self.acquire_wakelock()
            except Exception as e:
                self.show_toast_msg(f"Screen on setup error: {e}", is_error=True)
            # paths on android
            context = autoclass('org.kivy.android.PythonActivity').mActivity
            android_path = context.getExternalFilesDir(None).getAbsolutePath()
            self.config_dir = os.path.join(android_path, 'config')
            self.internal_storage = android_path
            try:
                Environment = autoclass("android.os.Environment")
                self.external_storage = Environment.getExternalStorageDirectory().getAbsolutePath()
            except Exception:
                self.external_storage = os.path.abspath("/storage/emulated/0/")
        else:
            self.internal_storage = os.path.expanduser("~")
            self.external_storage = os.path.expanduser("~")
            self.config_dir = os.path.join(self.user_data_dir, 'config')
        os.makedirs(self.config_dir, exist_ok=True)
        self.config_path = os.path.join(self.config_dir, 'config.json')
        self.api_url = "http://127.0.0.1:8089/nav/" # to be updated as using a config file
        # set app specific objects / vars
        self.result_txt = self.root.ids.nav_main_box.ids.result_text
        self.app_api_server = PosiApiServer()
        self.app_api_server.set_kivy_caller(self.api_callback)
        self.bluCon = BluetoothCon(platform)
        self.blu_ok = False
        try:
            self.blu_ok = self.bluCon.connect_device("1C:69:20:31:05:FE") # need to make it dynamic
        except Exception as e:
            print(f"Error in bluetooth connection: {e}")
        if(self.blu_ok):
            self.show_toast_msg("Bluetooth connection success")

    def acquire_wakelock(self):
        if self.wake_lock:
            return  # already acquired
        PythonActivity = autoclass("org.kivy.android.PythonActivity")
        Context = autoclass("android.content.Context")
        activity = PythonActivity.mActivity
        PowerManager = autoclass("android.os.PowerManager")
        power_manager = cast(PowerManager, activity.getSystemService(Context.POWER_SERVICE))
        # Create wakelock (use PowerManager.FULL_WAKE_LOCK for full wakelock)
        self.wake_lock = power_manager.newWakeLock(
            PowerManager.FULL_WAKE_LOCK, "MyApp::WakeLockTag"
        )
        self.wake_lock.acquire()
        print("WakeLock acquired")

    def release_wakelock(self):
        if self.wake_lock and self.wake_lock.isHeld():
            self.wake_lock.release()
            self.wake_lock = None
            print("WakeLock released")

    def api_callback(self, item):
        full_text = ""
        for i in item:
            print(i[1])
            txt = clean_text(i[1])
            full_text = full_text + f"{txt}, "
        self.result_txt.text = full_text

    def toggle_api_server(self):
        toggle_btn = self.root.ids.nav_main_box.ids.start_app_server_btn
        if self.is_api_server_on:
            self.app_api_server.stop()
            self.is_api_server_on = False
            toggle_btn.text = "Sart Server"
            toggle_btn.icon = "play"
            toggle_btn.md_bg_color = "gray"
        else:
            self.app_api_server.start()
            self.is_api_server_on = True
            toggle_btn.text = "Stop Server"
            toggle_btn.icon = "stop"
            toggle_btn.md_bg_color = "orange"

    def esp_api(self, title:str="", text:str=""): # to be updated with actual ESP API later
        import requests
        try:
            requests.post(
                self.api_url,
                json={"title": title, "text": text}
            )
        except Exception as e:
            print(f"An API error: {e}")

    def indicatior_light(self, instance, choice:str = "None"):
        btn_txt_update = self.root.ids.nav_main_box.ids.btn_text
        api_text = ""
        #print(instance.md_bg_color)
        if instance.md_bg_color == [0.5019607843137255, 0.5019607843137255, 0.5019607843137255, 1.0]: # gray
            self.turn_off_all()
            Clock.schedule_once(lambda dt: self.bluCon.send_cmd(choice))
            instance.md_bg_color = "orange"
            btn_txt_update.text = f"{choice} is ON"
            api_text = f"{choice} is ON for API"
        else:
            self.turn_off_all()
            Clock.schedule_once(lambda dt: self.bluCon.send_cmd("off"))
            instance.md_bg_color = "gray"
            btn_txt_update.text = "All OFF"
            api_text = f"{choice} is OFF for API"
        # Call the ESP API
        Thread(
            target=self.esp_api,
            kwargs={
                "title": "test_id",
                "text": api_text
            },
            daemon=True
        ).start()

    def turn_off_all(self):
        btn_group = [
            self.root.ids.nav_main_box.ids.left_u_turn_btn,
            self.root.ids.nav_main_box.ids.park_btn,
            self.root.ids.nav_main_box.ids.stop_btn,
            self.root.ids.nav_main_box.ids.right_u_turn_btn,
            self.root.ids.nav_main_box.ids.left_turn_btn,
            self.root.ids.nav_main_box.ids.right_turn_btn,
        ]
        for btn in btn_group:
            btn.md_bg_color = "gray"

    def show_toast_msg(self, message, is_error=False, duration=3):
        from kivymd.uix.snackbar import MDSnackbar
        bg_color = (0.2, 0.6, 0.2, 1) if not is_error else (0.8, 0.2, 0.2, 1)
        MDSnackbar(
            MDLabel(
                text = message,
                font_style = "Subtitle1"
            ),
            md_bg_color=bg_color,
            y=dp(24),
            pos_hint={"center_x": 0.5},
            duration=duration
        ).open()

    def show_text_dialog(self, title, text="", buttons=[]):
        self.txt_dialog = MDDialog(
            title=title,
            text=text,
            buttons=buttons
        )
        self.txt_dialog.open()

    def txt_dialog_closer(self, instance):
        if self.txt_dialog:
            self.txt_dialog.dismiss()

    def open_link(self, instance, url):
        import webbrowser
        webbrowser.open(url)

    def update_link_open(self, instance):
        self.txt_dialog_closer(instance)
        self.open_link(instance=instance, url="https://github.com/daslearning-org/navigation-indicator/releases")

    def update_checker(self, instance=None):
        buttons = [
            MDFlatButton(
                text="Cancel",
                theme_text_color="Custom",
                text_color=self.theme_cls.primary_color,
                on_release=self.txt_dialog_closer
            ),
            MDFlatButton(
                text="Releases",
                theme_text_color="Custom",
                text_color="green",
                on_release=self.update_link_open
            ),
        ]
        self.show_text_dialog(
            "Check for update",
            f"Your version: {__version__}",
            buttons
        )

    ## run on app exit
    def on_stop(self):
        if platform == "android":
            try:
                self.release_wakelock()
            except Exception as e:
                self.show_toast_msg(f"Screen on setup error: {e}", is_error=True)

if __name__ == '__main__':
    NavIndicatorApp().run()
