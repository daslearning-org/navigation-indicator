from jnius import autoclass, PythonJavaClass, java_method

BroadcastReceiver = autoclass('android.content.BroadcastReceiver')
IntentFilter = autoclass('android.content.IntentFilter')
PythonActivity = autoclass('org.kivy.android.PythonActivity')

class NavReceiver(PythonJavaClass):
    __javaclass__ = 'android/content/BroadcastReceiver'
    __javacontext__ = 'app'

    @java_method('(Landroid/content/Context;Landroid/content/Intent;)V')
    def onReceive(self, context, intent):

        title = intent.getStringExtra("title")
        text = intent.getStringExtra("text")

        print("Navigation:", title, text)

activity = PythonActivity.mActivity

receiver = NavReceiver()
filter = IntentFilter("NAVIGATION_UPDATE")

activity.registerReceiver(receiver, filter)