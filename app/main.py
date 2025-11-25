from kivy.app import App
from kivy.uix.label import Label
from kivy.clock import Clock
from kivy.utils import platform

## Global definitions
__version__ = "0.0.1"

## App start
class NavApp(App):

    def build(self):
        self.label = Label(text="Waiting for Navigation Broadcast...")
        self.start_manual_receiver() 
        return self.label

    def start_manual_receiver(self):
        if platform == 'android':
            from android.broadcast import BroadcastReceiver
            # action must match exactly what you send from Java
            action_string = 'in.daslearning.navindi.MAP_UPDATE'

            self.br = BroadcastReceiver(
                callback=self.on_broadcast,
                actions=[action_string]
            )
            self.br.start()
            print(f"BroadcastReceiver registered for action: {action_string}")

            self.request_notification_permission()

    def on_broadcast(self, context, intent):
        title = intent.getStringExtra("title")
        text = intent.getStringExtra("text")
        Clock.schedule_once(lambda dt: self.process_nav_data(title, text), 0)

    def on_pause(self):
        if hasattr(self, 'br'):
            self.br.stop()
        return True

    # The rest of your Python code remains the same:
    def request_notification_permission(self):
        """Opens the Android settings screen for the user to grant Notification Access."""
        if platform == 'android':
            from jnius import autoclass, java_method
            # Re-import just in case, though defined globally above
            PythonActivity = autoclass('org.kivy.android.PythonActivity') 
            Settings = autoclass('android.provider.Settings')
            Intent = autoclass('android.content.Intent')
            
            intent = Intent(Settings.ACTION_NOTIFICATION_LISTENER_SETTINGS)
            PythonActivity.mActivity.startActivity(intent)

    def process_nav_data(self, title, text):
        """
        Runs on the Kivy main thread to update UI or trigger your job.
        """
        self.label.text = f"Nav Update:\nInstruction: {title}\nDistance: {text}"
        
        # 🚦 YOUR JOB TRIGGER LOGIC HERE 🚦
        if title and "right" in title:
            print(">>> JOB TRIGGERED: Send Bluetooth signal for Right Turn")

if __name__ == '__main__':
    NavApp().run()