package in.daslearning.navindi;

import android.service.notification.NotificationListenerService;
import android.service.notification.StatusBarNotification;
import android.os.Bundle;
import android.app.Notification;
import android.util.Log;

public class NavNotificationListener extends NotificationListenerService {

    public static NavCallback callback;

    public interface NavCallback {
        void onNavigationUpdate(String pkg, String title, String text);
    }

    public static void setCallback(NavCallback cb) {
        callback = cb;
        Log.d("NAVINDI", "Python callback registered");
    }

    @Override
    public void onNotificationPosted(StatusBarNotification sbn) {

        Log.d("NAVINDI", "Notification from: " + sbn.getPackageName());
        String pkg = sbn.getPackageName();

        Bundle extras = sbn.getNotification().extras;
        CharSequence titleCs = extras.getCharSequence(Notification.EXTRA_TITLE);
        CharSequence textCs  = extras.getCharSequence(Notification.EXTRA_TEXT);
        CharSequence bigCs   = extras.getCharSequence(Notification.EXTRA_BIG_TEXT);
        String title = titleCs != null ? titleCs.toString() : "";
        String text  = textCs  != null ? textCs.toString()  : "";
        String big   = bigCs   != null ? bigCs.toString()   : "";
        Log.d("NAVINDI", "Title=" + title);
        Log.d("NAVINDI", "Text=" + text);
        Log.d("NAVINDI", "BigText=" + big);

        if (callback != null) {
            Log.d("NAVINDI", "Calling Python callback");
            callback.onNavigationUpdate(
                pkg,
                title,
                text
            );
        }
        else{
            Log.d("NAVINDI", "Callback is empty!!");
        }
    }
}