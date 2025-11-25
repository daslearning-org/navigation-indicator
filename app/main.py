from kivy.app import App
from kivy.uix.label import Label
from kivy.clock import Clock
from kivy.utils import platform

## Global definitions
__version__ = "0.0.1"

# Import necessary Android components only when running on Android
if platform == 'android':
    from jnius import autoclass
    
    # 1. Import necessary Java classes
    Intent = autoclass('android.content.Intent')
    IntentFilter = autoclass('android.content.IntentFilter')
    Context = autoclass('android.content.Context')
    
    # PythonActivity gives us access to the main Activity context
    PythonActivity = autoclass('org.kivy.android.PythonActivity')

# Global reference to hold the BroadcastReceiver instance
br_instance = None 

class NavApp(App):
    # ... (rest of the Kivy app structure)

    def build(self):
        self.label = Label(text="Waiting for Navigation Broadcast...")
        # We now use a new function for starting the receiver:
        self.start_manual_receiver() 
        return self.label

    def start_manual_receiver(self):
        if platform == 'android':
            global br_instance
            
            # This is the Python wrapper for the Java BroadcastReceiver
            # We define it here to access Python methods from Java context
            class MapUpdateReceiver(autoclass('android.content.BroadcastReceiver')):
                def __init__(self, callback):
                    super().__init__()
                    self.callback = callback

                def onReceive(self, context, intent):
                    # This runs on a background thread. Extract data and schedule callback.
                    title = intent.getStringExtra("title")
                    text = intent.getStringExtra("text")
                    
                    # Schedule job/UI update on the Kivy main thread
                    Clock.schedule_once(lambda dt: self.process_nav_data(title, text), 0)

            # --- 1. Instantiate the Receiver and IntentFilter ---
            br_instance = MapUpdateReceiver(self.process_nav_data)
            
            # The action string MUST match the string sent by NavListener.java
            action_string = 'in.daslearning.navindi.MAP_UPDATE' 
            intent_filter = IntentFilter(action_string)

            # --- 2. Register Receiver Manually with Flag ---
            # Get the main application context
            context = PythonActivity.mActivity.getApplicationContext()
            
            # Manually call registerReceiver, passing the RECEIVER_NOT_EXPORTED flag (API 31+)
            # Note: The RECEIVER_NOT_EXPORTED constant value is 4 
            # (Context.RECEIVER_NOT_EXPORTED = 0x4)
            
            # We are calling: context.registerReceiver(br_instance, intent_filter, null, null, Context.RECEIVER_NOT_EXPORTED)
            context.registerReceiver(
                br_instance, 
                intent_filter, 
                None,  # permission (None for no special permission)
                None,  # scheduler (None for default handler)
                4      # flags: Context.RECEIVER_NOT_EXPORTED (Value is 4)
            )

            print(f"BroadcastReceiver registered for action: {action_string} with NOT_EXPORTED flag.")
            
            # --- 3. Prompt for Notification Access (Still required) ---
            self.request_notification_permission()


    # The rest of your Python code remains the same:
    # ...
    def request_notification_permission(self):
        """Opens the Android settings screen for the user to grant Notification Access."""
        if platform == 'android':
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
        if title and "Turn right" in title:
            print(">>> JOB TRIGGERED: Send Bluetooth signal for Right Turn")

if __name__ == '__main__':
    NavApp().run()