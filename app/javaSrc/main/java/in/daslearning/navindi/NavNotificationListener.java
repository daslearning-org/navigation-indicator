package in.daslearning.navindi;

import android.service.notification.NotificationListenerService;
import android.service.notification.StatusBarNotification;
import android.os.Bundle;
import android.app.Notification;
import android.util.Log;

import android.graphics.drawable.Drawable;
import android.graphics.drawable.BitmapDrawable;
import android.graphics.Bitmap;
import android.graphics.Canvas;
import android.graphics.drawable.Icon;

public class NavNotificationListener extends NotificationListenerService {

    public static NavCallback callback;

    public interface NavCallback {
        void onNavigationUpdate(String pkg, String title, String text, String bigtext);
    }

    public static void setCallback(NavCallback cb) {
        callback = cb;
        Log.d("NAVINDI", "Python callback registered");
    }

    public static void clearCallback() {
        callback = null;
        Log.d("NAVINDI", "Callback cleared");
    }

    static String iconToDirection(Bitmap bitmap){
        Bitmap small = Bitmap.createScaledBitmap(bitmap, 32, 32, true);

        // Grayscale checkup
        int width = small.getWidth();
        int height = small.getHeight();
        int[][] binary = new int[width][height];

        for (int x = 0; x < width; x++) {
            for (int y = 0; y < height; y++) {
                int pixel = small.getPixel(x, y);

                int r = (pixel >> 16) & 0xff;
                int g = (pixel >> 8) & 0xff;
                int b = pixel & 0xff;

                int brightness = (r + g + b) / 3;

                // threshold
                binary[x][y] = brightness > 150 ? 1 : 0;
            }
        }

        // Detect the direction
        int sumX = 0, sumY = 0, count = 0;
        for (int x = 0; x < width; x++) {
            for (int y = 0; y < height; y++) {
                if (binary[x][y] == 1) {
                    sumX += x;
                    sumY += y;
                    count++;
                }
            }
        }
        float centerX = sumX / (float) count;
        float centerY = sumY / (float) count;
        //Log.d("NAVINDI", "Center: (" + centerX + ", " + centerY + ")");

        // Convert that to text
        float midX = width / 2f;
        float midY = height / 2f;

        float maxDist = -1;
        int tipX = -1, tipY = -1;
        for (int x = 0; x < width; x++) {
            for (int y = 0; y < height; y++) {
            
                if (binary[x][y] == 1) {

                    float dx = x - midX;
                    float dy = y - midY;

                    float dist = dx * dx + dy * dy;  // no sqrt needed

                    if (dist > maxDist) {
                        maxDist = dist;
                        tipX = x;
                        tipY = y;
                    }
                }
            }
        }

        //Log.d("NAVINDI", "Tip: (" + tipX + ", " + tipY + ")");

        // top count
        int topCount = 0;
        for (int x = 0; x < width; x++) {
            for (int y = 0; y < height; y++) {
                if (binary[x][y] == 1 && y < height / 3) {
                    topCount++;
                }
            }
        }
        //Log.d("NAVINDI", "TopCount=" + topCount);

        float dx = tipX - midX;
        float dy = tipY - midY;
        String direction;
        if (topCount > 50) {
            direction = "U-TURN";
        }
        // Bottom-heavy → LEFT / RIGHT
        else if (dy > height * 0.2) {
            if (dx > 0) {
                direction = "LEFT";
            }
            else {
                direction = "RIGHT";
            }
        }
        // Top → STRAIGHT
        else {
            direction = "straight";
        }
        //Log.d("NAVINDI", "Direction: " + direction);

        return direction;
    }

    @Override
    public void onNotificationPosted(StatusBarNotification sbn) {

        //Log.d("NAVINDI", "Notification from: " + sbn.getPackageName());
        String pkg = sbn.getPackageName();

        Bundle extras = sbn.getNotification().extras;
        CharSequence titleCs = extras.getCharSequence(Notification.EXTRA_TITLE);
        CharSequence textCs  = extras.getCharSequence(Notification.EXTRA_TEXT);
        CharSequence bigCs   = extras.getCharSequence(Notification.EXTRA_BIG_TEXT);
        String title = titleCs != null ? titleCs.toString() : "";
        String text  = textCs  != null ? textCs.toString()  : "";
        String big   = bigCs   != null ? bigCs.toString()   : "";

        // Get the icon for G-Maps
        if(
            pkg.equals("com.google.android.apps.maps")
          ){
            Icon icon = sbn.getNotification().getLargeIcon();
            if (icon != null) {
                try {
                    Drawable drawable = icon.loadDrawable(getApplicationContext());

                    Bitmap bitmap;

                    if (drawable instanceof BitmapDrawable) {
                        bitmap = ((BitmapDrawable) drawable).getBitmap();
                    }
                    else {
                        // fallback (important!)
                        bitmap = Bitmap.createBitmap(
                            drawable.getIntrinsicWidth(),
                            drawable.getIntrinsicHeight(),
                            Bitmap.Config.ARGB_8888
                        );
                        Canvas canvas = new Canvas(bitmap);
                        drawable.setBounds(0, 0, canvas.getWidth(), canvas.getHeight());
                        drawable.draw(canvas);
                    }

                    //Log.d("NAVINDI", "Arrow bitmap extracted: " + bitmap.getWidth() + "x" + bitmap.getHeight());

                    big = iconToDirection(bitmap);
                    //Log.d("NAVINDI", "Icon Direction: " + big);

                }
                catch (Exception e) {
                    Log.d("NAVINDI", "Icon extraction failed: " + e);
                }
            }
        }

        // Debug to check the keys
        //for (String key : extras.keySet()) {
        //    Log.d("NAVINDI", key + " = " + extras.get(key));
        //}

        if (callback != null) {
            //Log.d("NAVINDI", "Calling Python callback");
            callback.onNavigationUpdate(
                pkg,
                title,
                text,
                big
            );
        }
        //else{
        //    Log.d("NAVINDI", "Callback is empty!!");
        //}
    }
}