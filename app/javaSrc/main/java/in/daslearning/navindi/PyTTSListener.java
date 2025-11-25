package in.daslearning.navindi;

import android.service.notification.NotificationListenerService;
import android.service.notification.StatusBarNotification;
import android.content.Intent;
import android.os.Bundle;
import android.app.Notification;
import android.util.Log;

public class NavListener extends NotificationListenerService {

    @Override
    public void onNotificationPosted(StatusBarNotification sbn) {
        // Filter for Google Maps (com.google.android.apps.maps)
        if (sbn.getPackageName().equals("com.google.android.apps.maps")) {
            Bundle extras = sbn.getNotification().extras;
            String title = extras.getString(Notification.EXTRA_TITLE);
            String text = extras.getString(Notification.EXTRA_TEXT);

            if (title != null || text != null) {
                // Broadcast this to Python
                Intent intent = new Intent("org.test.myapp.MAP_UPDATE");
                intent.putExtra("title", title);
                intent.putExtra("text", text);
                sendBroadcast(intent);
            }
        }
    }

    @Override
    public void onNotificationRemoved(StatusBarNotification sbn) {
        // Optional: Handle removal
    }
}
