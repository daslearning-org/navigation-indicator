package in.daslearning.navindi;

import android.app.Service;
import android.app.Notification;
import android.app.NotificationChannel;
import android.app.NotificationManager;
import android.content.Intent;
import android.os.Build;
import android.os.IBinder;

public class NavindiService extends Service {

    private static final String CHANNEL_ID = "navindi_service";

    @Override
    public void onCreate() {
        super.onCreate();

        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            NotificationChannel channel =
                    new NotificationChannel(
                            CHANNEL_ID,
                            "Navigation Service",
                            NotificationManager.IMPORTANCE_DEFAULT
                    );

            NotificationManager manager =
                    getSystemService(NotificationManager.class);

            manager.createNotificationChannel(channel);
        }

        Notification notification;

        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            notification = new Notification.Builder(this, CHANNEL_ID)
                    .setContentTitle("Navigation Indicator")
                    .setContentText("Navigation service running")
                    .setSmallIcon(android.R.drawable.ic_dialog_map)
                    .build();
        } else {
            notification = new Notification.Builder(this)
                    .setContentTitle("Navigation Indicator")
                    .setContentText("Navigation service running")
                    .setSmallIcon(android.R.drawable.ic_dialog_map)
                    .build();
        }

        startForeground(1, notification);
    }

    @Override
    public int onStartCommand(Intent intent, int flags, int startId) {

        Intent pythonIntent =
                new Intent(this, org.kivy.android.PythonService.class);

        pythonIntent.putExtra("serviceEntrypoint", "navService.py");

        startService(pythonIntent);

        return START_STICKY;
    }

    @Override
    public IBinder onBind(Intent intent) {
        return null;
    }
}