package in.daslearning.navindi;

import android.service.notification.NotificationListenerService;
import android.service.notification.StatusBarNotification;
import android.os.Bundle;

public class NavNotificationListener extends NotificationListenerService {

    public static NavCallback callback;

    public interface NavCallback {
        void onNavigationUpdate(String pkg, String title, String text);
    }

    public static void setCallback(NavCallback cb) {
        callback = cb;
    }

    @Override
    public void onNotificationPosted(StatusBarNotification sbn) {

        String pkg = sbn.getPackageName();

        Bundle extras = sbn.getNotification().extras;

        if (extras == null) return;

        CharSequence title = extras.getCharSequence("android.title");
        CharSequence text = extras.getCharSequence("android.text");

        if (callback != null) {
            callback.onNavigationUpdate(
                pkg,
                title != null ? title.toString() : "",
                text != null ? text.toString() : ""
            );
        }
    }
}