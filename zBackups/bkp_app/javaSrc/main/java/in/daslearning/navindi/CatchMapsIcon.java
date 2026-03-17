import android.graphics.drawable.Drawable;
import android.graphics.drawable.BitmapDrawable;
import android.graphics.Bitmap;
import android.graphics.Canvas;
import android.graphics.drawable.Icon;

// Use previous code + this
Icon icon = sbn.getNotification().getLargeIcon();

if (icon != null) {
    try {
        Drawable drawable = icon.loadDrawable(getApplicationContext());

        Bitmap bitmap;

        if (drawable instanceof BitmapDrawable) {
            bitmap = ((BitmapDrawable) drawable).getBitmap();
        } else {
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

        Log.d("NAVINDI", "Arrow bitmap extracted: " +
                bitmap.getWidth() + "x" + bitmap.getHeight());

        // 🔥 Now you can send this to Python or process it

    } catch (Exception e) {
        Log.d("NAVINDI", "Icon extraction failed: " + e);
    }
}

// ****** Now check the logic *******
Bitmap small = Bitmap.createScaledBitmap(bitmap, 32, 32, true);

// Step 3: Convert to Grayscale + Threshold
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
int left = 0, right = 0, top = 0, bottom = 0;

for (int x = 0; x < width; x++) {
    for (int y = 0; y < height; y++) {

        if (binary[x][y] == 1) {

            if (x < width / 3) left++;
            if (x > 2 * width / 3) right++;

            if (y < height / 3) top++;
            if (y > 2 * height / 3) bottom++;
        }
    }
}

// Convert that to text
String direction;

if (right > left && right > top && right > bottom) {
    direction = "RIGHT";
}
else if (left > right && left > top && left > bottom) {
    direction = "LEFT";
}
else if (top > bottom) {
    direction = "STRAIGHT";
}
else if (bottom > top && (left > right || right > left)) {
    direction = "UTURN";
}
else {
    direction = "UNKNOWN";
}
// debug tips
Log.d("NAVINDI", "L=" + left + " R=" + right + " T=" + top + " B=" + bottom);
Log.d("NAVINDI", "Direction: " + direction);

