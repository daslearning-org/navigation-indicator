from kivy.app import App
from kivy.uix.label import Label
from kivy.clock import Clock
from kivy.utils import platform

## Global definitions
__version__ = "0.0.1"

# Global reference to keep the receiver alive
br = None

class MainApp(App):
    def build(self):
        self.label = Label(text="Waiting for Navigation...")
        self.start_service()
        return self.label

    def start_service(self):
        if platform == 'android':
            from jnius import autoclass
            from android.broadcast import BroadcastReceiver

            # 1. Listener Callback
            def on_broadcast(context, intent):
                title = intent.getStringExtra("title")
                text = intent.getStringExtra("text")
                # Update UI on main thread
                Clock.schedule_once(lambda dt: self.update_ui(title, text), 0)

            # 2. Register Receiver
            global br
            br = BroadcastReceiver(
                on_broadcast, actions=['in.daslearning.navindi.MAP_UPDATE']
            )
            br.start()

            # 3. Prompt user to enable permission (Crucial!)
            self.request_notification_permission()

    def request_notification_permission(self):
        from jnius import autoclass
        PythonActivity = autoclass('org.kivy.android.PythonActivity')
        Settings = autoclass('android.provider.Settings')
        Intent = autoclass('android.content.Intent')
        
        # Check if permission is granted (simplified check)
        # In production, check 'enabled_notification_listeners' in Settings.Secure first
        
        # Open the Settings screen for user to grant permission
        intent = Intent(Settings.ACTION_NOTIFICATION_LISTENER_SETTINGS)
        PythonActivity.mActivity.startActivity(intent)

    def update_ui(self, title, text):
        self.label.text = f"Nav Update:\n{title}\n{text}"
        # TRIGGER YOUR JOB HERE
        if "Right" in str(title):
            print("TRIGGER: Turning Right job initiated")

if __name__ == '__main__':
    MainApp().run()