from jnius import autoclass

Intent = autoclass('android.content.Intent')
Settings = autoclass('android.provider.Settings')
Uri = autoclass('android.net.Uri')

activity = autoclass('org.kivy.android.PythonActivity').mActivity

intent = Intent(Settings.ACTION_REQUEST_IGNORE_BATTERY_OPTIMIZATIONS)
intent.setData(Uri.parse("package:" + activity.getPackageName()))
activity.startActivity(intent)
