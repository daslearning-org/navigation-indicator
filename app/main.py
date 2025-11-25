from kivy.app import App
from kivy.uix.label import Label
from kivy.clock import Clock
from kivy.utils import platform

if platform == 'android':
    from jnius import autoclass, java_method
    from jnius import PythonJavaClass  # <-- NEW REQUIRED IMPORT

    # 1. Import necessary Java classes
    Intent = autoclass('android.content.Intent')
    IntentFilter = autoclass('android.content.IntentFilter')
    Context = autoclass('android.content.Context')
    PythonActivity = autoclass('org.kivy.android.PythonActivity')

    # -------------------------------------------------------------------
    # THE CRUCIAL CHANGE STARTS HERE
    # We use PythonJavaClass to properly define the BroadcastReceiver subclass
    # This resolves the "__javaclass__ definition missing" error.
    # -------------------------------------------------------------------
    class MapUpdateReceiver(PythonJavaClass):
        # This defines the native Java class we are implementing/extending
        __javaclass__ = 'android/content/BroadcastReceiver'
        # Specify the interfaces (methods) that Android will call
        __javainterfaces__ = ['org/kivy/android/PythonActivity$StateListener'] # Sometimes needed for PyActivity

        # Initialize our Python object
        def __init__(self, callback, **kwargs):
            super(MapUpdateReceiver, self).__init__(**kwargs)
            self.callback = callback

        @java_method('(Landroid/content/Context;Landroid/content/Intent;)V')
        def onReceive(self, context, intent):
            """
            This is the native Java onReceive method being implemented in Python.
            The signature '(Landroid/content/Context;Landroid/content/Intent;)V' is mandatory.
            """
            # This runs on a background thread. Extract data and schedule callback.
            title = intent.getStringExtra("title")
            text = intent.getStringExtra("text")

            # Schedule job/UI update on the Kivy main thread
            Clock.schedule_once(lambda dt: self.callback(title, text), 0)

# -------------------------------------------------------------------

# Global reference to hold the BroadcastReceiver instance
br_instance = None 

## App start
class NavApp(App):
    # ... (rest of the Kivy app structure)

    def build(self):
        self.label = Label(text="Waiting for Navigation Broadcast...")
        self.start_manual_receiver() 
        return self.label

    def start_manual_receiver(self):
        if platform == 'android':
            global br_instance
            
            # --- 1. Instantiate the Receiver and IntentFilter ---
            # Instantiate the class we defined above
            br_instance = MapUpdateReceiver(self.process_nav_data) 
            
            # The rest of the registration logic is the same (and correct):
            action_string = 'in.daslearning.navindi.MAP_UPDATE' 
            intent_filter = IntentFilter(action_string)

            # --- 2. Register Receiver Manually with Flag ---
            context = PythonActivity.mActivity.getApplicationContext()
            
            # Context.RECEIVER_NOT_EXPORTED is value 4
            context.registerReceiver(
                br_instance, 
                intent_filter, 
                None,  
                None,  
                4      
            )

            print(f"BroadcastReceiver registered for action: {action_string} with NOT_EXPORTED flag.")
            
            # --- 3. Prompt for Notification Access ---
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