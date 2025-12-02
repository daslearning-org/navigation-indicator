from kivy.app import App
from kivy.uix.label import Label
from kivy.clock import Clock
from kivy.utils import platform
from jnius import autoclass, PythonJavaClass, java_method, JavaException

## Global definitions
__version__ = "0.0.1"
APP_TAG = "NavApp"

## Global classes
PythonActivity = autoclass('org.kivy.android.PythonActivity')
Context = autoclass('android.content.Context')
IntentFilter = autoclass('android.content.IntentFilter')
Log = autoclass('android.util.Log')

class UiRunnable(PythonJavaClass):
    __javaclass__ = 'java/lang/Runnable'
    __javainterfaces__ = []

    def __init__(self, outer, title, text):
        super().__init__()
        self.outer = outer
        self.title = title
        self.text = text

    @java_method('()V')
    def run(self):
        # This runs on Android UI thread; safe to interact with Python and schedule Kivy Clock
        try:
            # schedule on Kivy main loop to update UI
            Clock.schedule_once(lambda dt: self.outer.process_nav_data(self.title, self.text), 0)
        except Exception as e:
            # catch to avoid uncaught exceptions bubbling into native code
            print("UiRunnable.run error:", e)


# Module-level BroadcastReceiver subclass
class PyBR(PythonJavaClass):
    __javaclass__ = 'android/content/BroadcastReceiver'
    __javainterfaces__ = []

    def __init__(self, outer):
        super().__init__()
        self.outer = outer

    @java_method('(Landroid/content/Context;Landroid/content/Intent;)V')
    def onReceive(self, context, intent):
        # Minimal work here: extract strings, log, post Runnable to UI thread
        try:
            title = None
            text = None
            if intent:
                title = intent.getStringExtra("title")
                text = intent.getStringExtra("text")

            # Log for debugging (pure Java log call)
            try:
                Log.d(APP_TAG, f"onReceive: title={title}, text={text}")
            except Exception:
                # In some envs f-string through Java can error; fallback
                Log.d(APP_TAG, "onReceive")

            # Create a Runnable which will run on UI thread (safe)
            ui_r = UiRunnable(self.outer, title, text)
            try:
                # runOnUiThread will execute the Runnable on the main thread
                PythonActivity.mActivity.runOnUiThread(ui_r)
            except JavaException:
                # Fallback: use Clock.schedule_once directly (may be called on Java thread; catch errors)
                Clock.schedule_once(lambda dt: self.outer.process_nav_data(title, text), 0)
        except Exception as e:
            # Avoid letting exceptions bubble to native code
            print("PyBR.onReceive exception:", e)

## App start
class NavApp(App):

    def build(self):
        self.label = Label(text="Waiting for Navigation Broadcast...")
        self.start_manual_receiver() 
        return self.label

    def start_manual_receiver(self):
        if platform != 'android':
            return

        action_string = 'in.daslearning.navindi.MAP_UPDATE'

        # create filter
        intent_filter = IntentFilter()
        intent_filter.addAction(action_string)

        # create receiver and keep reference
        self._py_receiver = PyBR(self)

        # registration: prefer RECEIVER_NOT_EXPORTED, attempt multiple overloads
        try:
            self._mActivity = PythonActivity.mActivity
            try:
                self._mActivity.registerReceiver(self._py_receiver, intent_filter, Context.RECEIVER_NOT_EXPORTED)
            except JavaException:
                try:
                    self._mActivity.registerReceiver(self._py_receiver, intent_filter, None, Context.RECEIVER_NOT_EXPORTED)
                except JavaException:
                    self._mActivity.registerReceiver(self._py_receiver, intent_filter)
            print("BroadcastReceiver registered:", action_string)
            self._intent_filter = intent_filter
        except JavaException as e:
            print("Failed to register BroadcastReceiver:", e)

        # Request notification permission screen
        self.request_notification_permission()

    def on_pause(self):
        # unregister receiver
        if getattr(self, "_mActivity", None) and getattr(self, "_py_receiver", None):
            try:
                self._mActivity.unregisterReceiver(self._py_receiver)
            except JavaException:
                pass
            finally:
                try:
                    del self._py_receiver
                except Exception:
                    pass
                try:
                    del self._mActivity
                except Exception:
                    pass
        return True

    def on_broadcast(self, context, intent):
        title = intent.getStringExtra("title")
        text = intent.getStringExtra("text")
        Clock.schedule_once(lambda dt: self.process_nav_data(title, text), 0)

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